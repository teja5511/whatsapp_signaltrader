import json
from uuid import uuid4
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.orm import Session

from src.database.engine import SessionLocal
from src.database.unit_of_work import UnitOfWork
from src.database.models import (
    ReconciliationRunModel, ReconciliationItemModel, CampaignModel,
    MT5OrderRecordModel, MT5PositionRecordModel, MT5ExecutionJobModel, PlannedEntryModel
)
from src.mt5.adapter import MT5AdapterInterface
from src.mt5.fake_adapter import FakeMT5Adapter
from src.reconciliation.contracts import (
    ReconciliationRunDTO, ReconciliationItemDTO, ClassificationKind
)
from src.events.outbox import OutboxPublisher
from src.events.constants import EVENT_RECONCILIATION_RUN_COMPLETED

class MT5ReconciliationService:
    def __init__(
        self,
        session_factory=SessionLocal,
        adapter: Optional[MT5AdapterInterface] = None
    ):
        self.session_factory = session_factory
        self.adapter = adapter or FakeMT5Adapter()

    def run_reconciliation(
        self,
        trigger_type: str = "MANUAL",
        scope: str = "ALL",
        campaign_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        actor: str = "SYSTEM",
        session: Optional[Session] = None
    ) -> ReconciliationRunDTO:
        corr_id = correlation_id or f"corr-recon-{uuid4()}"
        now_utc = datetime.now(timezone.utc)
        run_id = str(uuid4())

        if not self.adapter.is_initialized():
            self.adapter.initialize()

        resolution = self.adapter.resolve_symbol()
        broker_symbol = resolution.broker_symbol or "XAUUSD"

        # 1. Fetch Broker State
        try:
            broker_orders = self.adapter.orders_get()
            broker_positions = self.adapter.positions_get()
        except Exception as ex:
            broker_orders = []
            broker_positions = []

        with UnitOfWork(session_factory=self.session_factory, session=session) as uow:
            # 2. Fetch Local Database State
            campaign_query = uow.db.query(CampaignModel)
            if campaign_id:
                campaign_query = campaign_query.filter(CampaignModel.id == campaign_id)
            campaigns = campaign_query.all()
            owned_magics = {c.magic_number for c in campaigns if c.magic_number is not None}
            campaign_by_magic = {c.magic_number: c for c in campaigns if c.magic_number is not None}

            order_query = uow.db.query(MT5OrderRecordModel).filter(MT5OrderRecordModel.state == "PLACED")
            if campaign_id:
                order_query = order_query.filter(MT5OrderRecordModel.campaign_id == campaign_id)
            local_orders = order_query.all()

            position_query = uow.db.query(MT5PositionRecordModel).filter(MT5PositionRecordModel.state == "OPEN")
            if campaign_id:
                position_query = position_query.filter(MT5PositionRecordModel.campaign_id == campaign_id)
            local_positions = position_query.all()

            # 3. Create Recon Run Record
            run_rec = ReconciliationRunModel(
                id=run_id,
                reconciliation_version="1.0.0",
                trigger_type=trigger_type,
                scope=scope,
                campaign_id=campaign_id,
                correlation_id=corr_id,
                actor=actor,
                status="RUNNING",
                broker_symbol=broker_symbol,
                local_order_count=len(local_orders),
                local_position_count=len(local_positions),
                broker_order_count=len(broker_orders),
                broker_position_count=len(broker_positions),
                matched_count=0,
                mismatch_count=0,
                requires_review_count=0,
                snapshot_json=json.dumps({
                    "trigger_type": trigger_type,
                    "scope": scope,
                    "broker_symbol": broker_symbol,
                    "local_orders": len(local_orders),
                    "local_positions": len(local_positions),
                    "broker_orders": len(broker_orders),
                    "broker_positions": len(broker_positions),
                }),
                started_at=now_utc
            )
            uow.db.add(run_rec)
            uow.db.flush()

            items: List[ReconciliationItemModel] = []
            matched_c = 0
            mismatch_c = 0
            review_c = 0

            # Match Orders
            broker_order_by_ticket = {o.ticket: o for o in broker_orders}
            local_order_by_ticket = {o.ticket: o for o in local_orders if o.ticket is not None}

            # Local Orders matching against Broker Orders
            for l_ord in local_orders:
                if l_ord.ticket and l_ord.ticket in broker_order_by_ticket:
                    b_ord = broker_order_by_ticket[l_ord.ticket]
                    diffs = []
                    if abs(float(l_ord.volume) - float(b_ord.volume)) > 1e-4:
                        diffs.append({"field": "volume", "local": float(l_ord.volume), "broker": float(b_ord.volume)})
                    if abs(float(l_ord.price) - float(b_ord.price_open)) > 1e-4:
                        diffs.append({"field": "price", "local": float(l_ord.price), "broker": float(b_ord.price_open)})

                    classification = ClassificationKind.MATCHED.value if not diffs else ClassificationKind.MISMATCHED.value
                    if classification == ClassificationKind.MATCHED.value:
                        matched_c += 1
                    else:
                        mismatch_c += 1

                    item = ReconciliationItemModel(
                        id=str(uuid4()),
                        reconciliation_run_id=run_id,
                        entity_type="ORDER",
                        classification=classification,
                        ticket=l_ord.ticket,
                        magic_number=l_ord.magic_number,
                        campaign_id=l_ord.campaign_id,
                        planned_entry_id=l_ord.planned_entry_id,
                        job_id=l_ord.job_id,
                        local_snapshot_json=json.dumps({"ticket": l_ord.ticket, "price": float(l_ord.price), "volume": float(l_ord.volume)}),
                        broker_snapshot_json=json.dumps({"ticket": b_ord.ticket, "price": float(b_ord.price_open), "volume": float(b_ord.volume)}),
                        differences_json=json.dumps(diffs),
                        requires_review=bool(diffs),
                        resolution_status="RESOLVED" if not diffs else "OPEN",
                        created_at=now_utc
                    )
                    items.append(item)
                    if diffs:
                        review_c += 1
                else:
                    mismatch_c += 1
                    review_c += 1
                    item = ReconciliationItemModel(
                        id=str(uuid4()),
                        reconciliation_run_id=run_id,
                        entity_type="ORDER",
                        classification=ClassificationKind.MISSING_ORDER.value,
                        ticket=l_ord.ticket,
                        magic_number=l_ord.magic_number,
                        campaign_id=l_ord.campaign_id,
                        planned_entry_id=l_ord.planned_entry_id,
                        job_id=l_ord.job_id,
                        local_snapshot_json=json.dumps({"ticket": l_ord.ticket, "price": float(l_ord.price), "volume": float(l_ord.volume)}),
                        broker_snapshot_json=None,
                        differences_json=json.dumps([{"field": "broker_order", "reason": "Order missing on broker"}]),
                        requires_review=True,
                        resolution_status="OPEN",
                        created_at=now_utc
                    )
                    items.append(item)

            # Broker Orders not in local DB
            for b_ord in broker_orders:
                if b_ord.ticket not in local_order_by_ticket:
                    is_owned = b_ord.magic_number in owned_magics
                    classification = ClassificationKind.UNEXPECTED_ORDER.value if is_owned else ClassificationKind.BROKER_ONLY.value
                    mismatch_c += 1
                    review_c += 1
                    item = ReconciliationItemModel(
                        id=str(uuid4()),
                        reconciliation_run_id=run_id,
                        entity_type="ORDER",
                        classification=classification,
                        ticket=b_ord.ticket,
                        magic_number=b_ord.magic_number,
                        campaign_id=campaign_by_magic[b_ord.magic_number].id if is_owned else None,
                        local_snapshot_json=None,
                        broker_snapshot_json=json.dumps({"ticket": b_ord.ticket, "price": float(b_ord.price_open), "volume": float(b_ord.volume)}),
                        differences_json=json.dumps([{"field": "local_order", "reason": "Order exists on broker but not in local DB"}]),
                        requires_review=True,
                        resolution_status="OPEN",
                        created_at=now_utc
                    )
                    items.append(item)

            # Match Positions
            broker_pos_by_ticket = {p.ticket: p for p in broker_positions}
            local_pos_by_ticket = {p.ticket: p for p in local_positions if p.ticket is not None}

            for l_pos in local_positions:
                if l_pos.ticket and l_pos.ticket in broker_pos_by_ticket:
                    b_pos = broker_pos_by_ticket[l_pos.ticket]
                    diffs = []
                    if abs(float(l_pos.volume) - float(b_pos.volume)) > 1e-4:
                        diffs.append({"field": "volume", "local": float(l_pos.volume), "broker": float(b_pos.volume)})
                    classification = ClassificationKind.MATCHED.value if not diffs else ClassificationKind.MISMATCHED.value
                    if classification == ClassificationKind.MATCHED.value:
                        matched_c += 1
                    else:
                        mismatch_c += 1

                    item = ReconciliationItemModel(
                        id=str(uuid4()),
                        reconciliation_run_id=run_id,
                        entity_type="POSITION",
                        classification=classification,
                        ticket=l_pos.ticket,
                        magic_number=l_pos.magic_number,
                        campaign_id=l_pos.campaign_id,
                        local_snapshot_json=json.dumps({"ticket": l_pos.ticket, "volume": float(l_pos.volume)}),
                        broker_snapshot_json=json.dumps({"ticket": b_pos.ticket, "volume": float(b_pos.volume)}),
                        differences_json=json.dumps(diffs),
                        requires_review=bool(diffs),
                        resolution_status="RESOLVED" if not diffs else "OPEN",
                        created_at=now_utc
                    )
                    items.append(item)
                    if diffs:
                        review_c += 1
                else:
                    mismatch_c += 1
                    review_c += 1
                    item = ReconciliationItemModel(
                        id=str(uuid4()),
                        reconciliation_run_id=run_id,
                        entity_type="POSITION",
                        classification=ClassificationKind.MISSING_POSITION.value,
                        ticket=l_pos.ticket,
                        magic_number=l_pos.magic_number,
                        campaign_id=l_pos.campaign_id,
                        local_snapshot_json=json.dumps({"ticket": l_pos.ticket, "volume": float(l_pos.volume)}),
                        broker_snapshot_json=None,
                        differences_json=json.dumps([{"field": "broker_position", "reason": "Position missing on broker"}]),
                        requires_review=True,
                        resolution_status="OPEN",
                        created_at=now_utc
                    )
                    items.append(item)

            for b_pos in broker_positions:
                if b_pos.ticket not in local_pos_by_ticket:
                    is_owned = b_pos.magic_number in owned_magics
                    classification = ClassificationKind.UNEXPECTED_POSITION.value if is_owned else ClassificationKind.BROKER_ONLY.value
                    mismatch_c += 1
                    review_c += 1
                    item = ReconciliationItemModel(
                        id=str(uuid4()),
                        reconciliation_run_id=run_id,
                        entity_type="POSITION",
                        classification=classification,
                        ticket=b_pos.ticket,
                        magic_number=b_pos.magic_number,
                        campaign_id=campaign_by_magic[b_pos.magic_number].id if is_owned else None,
                        local_snapshot_json=None,
                        broker_snapshot_json=json.dumps({"ticket": b_pos.ticket, "volume": float(b_pos.volume)}),
                        differences_json=json.dumps([{"field": "local_position", "reason": "Position exists on broker but not in local DB"}]),
                        requires_review=True,
                        resolution_status="OPEN",
                        created_at=now_utc
                    )
                    items.append(item)

            for itm in items:
                uow.db.add(itm)

            # 4. Finalize Run Record
            comp_time = datetime.now(timezone.utc)
            run_rec.status = "COMPLETED"
            run_rec.matched_count = matched_c
            run_rec.mismatch_count = mismatch_c
            run_rec.requires_review_count = review_c
            run_rec.completed_at = comp_time

            # 5. Domain Event Notification
            OutboxPublisher.publish_domain_event(
                db=uow.db,
                event_type=EVENT_RECONCILIATION_RUN_COMPLETED,
                aggregate_type="RECONCILIATION",
                aggregate_id=run_id,
                correlation_id=corr_id,
                payload={
                    "reconciliation_run_id": run_id,
                    "scope": scope,
                    "matched_count": matched_c,
                    "mismatch_count": mismatch_c,
                    "requires_review_count": review_c
                },
                campaign_id=campaign_id
            )

            uow.audit.log_event("RECONCILIATION_RUN_COMPLETED", {
                "run_id": run_id,
                "matched": matched_c,
                "mismatches": mismatch_c,
                "review_required": review_c
            })

            # Map DTOs
            dto_items = [
                ReconciliationItemDTO(
                    id=i.id,
                    reconciliation_run_id=i.reconciliation_run_id,
                    entity_type=i.entity_type,
                    classification=i.classification,
                    ticket=i.ticket,
                    magic_number=i.magic_number,
                    campaign_id=i.campaign_id,
                    planned_entry_id=i.planned_entry_id,
                    job_id=i.job_id,
                    local_snapshot=json.loads(i.local_snapshot_json) if i.local_snapshot_json else None,
                    broker_snapshot=json.loads(i.broker_snapshot_json) if i.broker_snapshot_json else None,
                    differences=json.loads(i.differences_json),
                    requires_review=i.requires_review,
                    resolution_status=i.resolution_status,
                    created_at=i.created_at
                )
                for i in items
            ]

            return ReconciliationRunDTO(
                id=run_rec.id,
                reconciliation_version=run_rec.reconciliation_version,
                trigger_type=run_rec.trigger_type,
                scope=run_rec.scope,
                campaign_id=run_rec.campaign_id,
                correlation_id=run_rec.correlation_id,
                actor=run_rec.actor,
                status=run_rec.status,
                broker_symbol=run_rec.broker_symbol,
                local_order_count=run_rec.local_order_count,
                local_position_count=run_rec.local_position_count,
                broker_order_count=run_rec.broker_order_count,
                broker_position_count=run_rec.broker_position_count,
                matched_count=run_rec.matched_count,
                mismatch_count=run_rec.mismatch_count,
                requires_review_count=run_rec.requires_review_count,
                snapshot_summary=json.loads(run_rec.snapshot_json),
                error_message=run_rec.error_message,
                started_at=run_rec.started_at,
                completed_at=run_rec.completed_at,
                items=dto_items
            )

    def get_runs(self, limit: int = 50, session: Optional[Session] = None) -> List[ReconciliationRunDTO]:
        with UnitOfWork(session_factory=self.session_factory, session=session) as uow:
            runs = uow.db.query(ReconciliationRunModel).order_by(ReconciliationRunModel.started_at.desc()).limit(limit).all()
            result = []
            for r in runs:
                items = [
                    ReconciliationItemDTO(
                        id=i.id,
                        reconciliation_run_id=i.reconciliation_run_id,
                        entity_type=i.entity_type,
                        classification=i.classification,
                        ticket=i.ticket,
                        magic_number=i.magic_number,
                        campaign_id=i.campaign_id,
                        planned_entry_id=i.planned_entry_id,
                        job_id=i.job_id,
                        local_snapshot=json.loads(i.local_snapshot_json) if i.local_snapshot_json else None,
                        broker_snapshot=json.loads(i.broker_snapshot_json) if i.broker_snapshot_json else None,
                        differences=json.loads(i.differences_json),
                        requires_review=i.requires_review,
                        resolution_status=i.resolution_status,
                        created_at=i.created_at
                    )
                    for i in r.items
                ]
                result.append(ReconciliationRunDTO(
                    id=r.id,
                    reconciliation_version=r.reconciliation_version,
                    trigger_type=r.trigger_type,
                    scope=r.scope,
                    campaign_id=r.campaign_id,
                    correlation_id=r.correlation_id,
                    actor=r.actor,
                    status=r.status,
                    broker_symbol=r.broker_symbol,
                    local_order_count=r.local_order_count,
                    local_position_count=r.local_position_count,
                    broker_order_count=r.broker_order_count,
                    broker_position_count=r.broker_position_count,
                    matched_count=r.matched_count,
                    mismatch_count=r.mismatch_count,
                    requires_review_count=r.requires_review_count,
                    snapshot_summary=json.loads(r.snapshot_json) if r.snapshot_json else {},
                    error_message=r.error_message,
                    started_at=r.started_at,
                    completed_at=r.completed_at,
                    items=items
                ))
            return result
