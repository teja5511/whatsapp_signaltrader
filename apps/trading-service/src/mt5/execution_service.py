"""MT5 Execution Service Orchestrator."""

import os
from typing import Optional, List, Dict, Any, Tuple
from decimal import Decimal
from datetime import datetime, timezone
from src.database.engine import SessionLocal
from src.database.unit_of_work import UnitOfWork
from src.database.models import CampaignModel, PlannedEntryModel, MT5AccountSnapshotModel, MT5SymbolSnapshotModel, MT5SyncEventModel
from src.mt5.adapter import MT5AdapterInterface
from src.mt5.fake_adapter import FakeMT5Adapter
from src.mt5.dry_run_adapter import DryRunMT5Adapter
from src.mt5.real_adapter import RealMT5Adapter
from src.mt5.execution_queue import MT5ExecutionQueue
from src.mt5.idempotency import generate_execution_idempotency_key
from src.mt5.contracts import Mt5ExecutionPreflightResultDTO, Mt5CampaignExecutionResultDTO
from src.campaigns.constants import STATE_PLANNED, STATE_PLACING_ORDERS
from src.mt5.constants import (
    MODE_FAKE, MODE_DRY_RUN, MODE_REAL, ENV_DEMO, MARGIN_HEDGING, CANONICAL_SYMBOL_XAUUSD
)

class MT5ExecutionService:
    def __init__(self, adapter: Optional[MT5AdapterInterface] = None, session_factory=SessionLocal):
        self.session_factory = session_factory
        if adapter:
            self.adapter = adapter
        else:
            mode = os.getenv("MT5_ADAPTER_MODE", MODE_FAKE).lower()
            if mode == MODE_DRY_RUN:
                self.adapter = DryRunMT5Adapter()
            elif mode == MODE_REAL:
                self.adapter = RealMT5Adapter()
            else:
                self.adapter = FakeMT5Adapter()

    def run_preflight(self, campaign_id: str) -> Mt5ExecutionPreflightResultDTO:
        with UnitOfWork(session_factory=self.session_factory) as uow:
            campaign = uow.campaigns.get_by_id(campaign_id)
            if not campaign:
                return Mt5ExecutionPreflightResultDTO(
                    campaign_id=campaign_id,
                    is_ready=False,
                    blocking_reasons=[f"Campaign '{campaign_id}' not found."]
                )

            passed = []
            blocked = []

            # Check Campaign State
            if campaign.current_state != STATE_PLANNED:
                blocked.append(f"Campaign state '{campaign.current_state}' is not PLANNED.")
            else:
                passed.append("CAMPAIGN_STATE_PLANNED")

            # Check Planned Entries Count
            if len(campaign.planned_entries) != campaign.entry_count or campaign.entry_count < 3 or campaign.entry_count > 8:
                blocked.append(f"Invalid planned entries count {len(campaign.planned_entries)} (expected {campaign.entry_count}).")
            else:
                passed.append("ENTRY_COUNT_VALID")

            # Check Total Lot Exposure
            if campaign.requested_total_lots > Decimal("2.0000"):
                blocked.append(f"Campaign requested total volume {campaign.requested_total_lots} lots exceeds 2.0000 limit.")
            else:
                passed.append("TOTAL_VOLUME_CAP_VALID")

            # Check Adapter Status & Demo Gates
            try:
                if not self.adapter.is_initialized():
                    self.adapter.initialize()
                acc_info = self.adapter.account_info()
                if acc_info.environment_kind != ENV_DEMO:
                    blocked.append(f"Account environment '{acc_info.environment_kind}' is not DEMO.")
                else:
                    passed.append("ACCOUNT_DEMO_ENVIRONMENT")

                if acc_info.margin_mode != MARGIN_HEDGING:
                    blocked.append(f"Account margin mode '{acc_info.margin_mode}' is not HEDGING.")
                else:
                    passed.append("ACCOUNT_MARGIN_HEDGING")
            except Exception as e:
                blocked.append(f"MT5 adapter preflight error: {str(e)}")

            return Mt5ExecutionPreflightResultDTO(
                campaign_id=campaign_id,
                is_ready=len(blocked) == 0,
                checks_passed=passed,
                blocking_reasons=blocked
            )

    def queue_campaign_execution(
        self,
        campaign_id: str,
        expected_version: int,
        planning_fingerprint: str,
        explicit_user_confirm: bool = True
    ) -> Tuple[Mt5CampaignExecutionResultDTO, bool]:
        if not explicit_user_confirm:
            raise ValueError("Execution requires explicit user confirmation.")

        with UnitOfWork(session_factory=self.session_factory) as uow:
            campaign = uow.campaigns.get_by_id(campaign_id)
            if not campaign:
                raise ValueError(f"Campaign '{campaign_id}' not found.")

            if campaign.version != expected_version:
                raise ValueError(f"Concurrency conflict on campaign '{campaign_id}': expected version {expected_version}, got {campaign.version}.")

            # Run Preflight
            preflight = self.run_preflight(campaign_id)
            if not preflight.is_ready:
                raise ValueError(f"Execution preflight blocked: {preflight.blocking_reasons}")

            acc_info = self.adapter.account_info()

            # Store Account Snapshot
            now_utc = datetime.now(timezone.utc)
            acc_snap = MT5AccountSnapshotModel(
                id=str(uuid4_str()),
                login=acc_info.login,
                login_masked=acc_info.login_masked,
                server=acc_info.server,
                company=acc_info.company,
                environment_kind=acc_info.environment_kind,
                margin_mode=acc_info.margin_mode,
                currency=acc_info.currency,
                leverage=acc_info.leverage,
                balance=float(acc_info.balance),
                equity=float(acc_info.equity),
                margin=float(acc_info.margin),
                margin_free=float(acc_info.margin_free),
                trade_allowed=acc_info.trade_allowed,
                trade_expert=acc_info.trade_expert,
                captured_at=now_utc
            )
            uow.db.add(acc_snap)

            # Build Jobs Payload
            jobs_payload = []
            for entry in sorted(campaign.planned_entries, key=lambda x: x.ladder_index):
                idempotency_key = generate_execution_idempotency_key(
                    campaign_id=campaign.id,
                    planning_fingerprint=planning_fingerprint,
                    planned_entry_id=entry.id,
                    campaign_version=expected_version,
                    account_login=acc_info.login,
                    account_server=acc_info.server,
                    broker_symbol=CANONICAL_SYMBOL_XAUUSD,
                    operation_type="PLACE_PENDING_ORDER"
                )
                jobs_payload.append({
                    "planned_entry_id": entry.id,
                    "operation_type": "PLACE_PENDING_ORDER",
                    "idempotency_key": idempotency_key,
                    "priority": 10 + entry.ladder_index,
                    "max_attempts": 1,
                    "payload": {
                        "campaign_id": campaign.id,
                        "planned_entry_id": entry.id,
                        "ladder_index": entry.ladder_index
                    }
                })

            # Create Batch & Queue Jobs
            batch, jobs = MT5ExecutionQueue.create_batch_and_jobs(
                db=uow.db,
                campaign_id=campaign.id,
                campaign_version=expected_version,
                planning_fingerprint=planning_fingerprint,
                jobs_data=jobs_payload
            )

            # Transition Campaign State
            campaign.current_state = STATE_PLACING_ORDERS
            campaign.version += 1
            uow.db.flush()

            uow.audit.log_event("EXECUTION_BATCH_QUEUED", {
                "campaign_id": campaign.id,
                "batch_id": batch.id,
                "jobs_count": len(jobs)
            })

            res = Mt5CampaignExecutionResultDTO(
                campaign_id=campaign.id,
                batch_id=batch.id,
                status="QUEUED",
                jobs_count=len(jobs),
                message="Execution batch queued cleanly for single-writer execution worker."
            )
            return res, False

    def synchronize_campaign(self, campaign_id: str) -> Dict[str, Any]:
        with UnitOfWork(session_factory=self.session_factory) as uow:
            campaign = uow.campaigns.get_by_id(campaign_id)
            if not campaign:
                return {"status": "not_found", "orders_count": 0, "positions_count": 0}

            active_orders = self.adapter.orders_get(magic_number=campaign.magic_number)
            active_positions = self.adapter.positions_get(magic_number=campaign.magic_number)

            now_utc = datetime.now(timezone.utc)
            sync_rec = MT5SyncEventModel(
                id=uuid4_str(),
                campaign_id=campaign_id,
                sync_type="MANUAL",
                orders_count=len(active_orders),
                positions_count=len(active_positions),
                payload_json=f'{{"orders": {len(active_orders)}, "positions": {len(active_positions)}}}',
                synced_at=now_utc
            )
            uow.db.add(sync_rec)

            return {
                "campaign_id": campaign_id,
                "orders_count": len(active_orders),
                "positions_count": len(active_positions),
                "orders": [o.model_dump(mode="json") for o in active_orders],
                "positions": [p.model_dump(mode="json") for p in active_positions]
            }

    def emergency_close_all_xauusd(self, confirmation_phrase: str, scope: str = "APPLICATION_OWNED") -> Dict[str, Any]:
        if os.getenv("MT5_CLOSE_ALL_ENABLED", "false").lower() != "true":
            raise ValueError("Emergency close-all is disabled by configuration (MT5_CLOSE_ALL_ENABLED=false).")

        if confirmation_phrase != "CLOSE ALL DEMO XAUUSD":
            raise ValueError(f"Invalid confirmation phrase '{confirmation_phrase}'.")

        acc_info = self.adapter.account_info()
        if acc_info.environment_kind != ENV_DEMO:
            raise ValueError("Emergency close-all blocked on non-demo account.")

        with UnitOfWork(session_factory=self.session_factory) as uow:
            positions = self.adapter.positions_get()
            closed_tickets = []

            for p in positions:
                if p.symbol.upper().startswith("XAUUSD") or p.symbol.upper() == "GOLD":
                    if scope == "APPLICATION_OWNED":
                        # Check magic matches an existing campaign
                        c = uow.db.query(CampaignModel).filter(CampaignModel.magic_number == p.magic_number).first()
                        if not c:
                            continue
                    if hasattr(self.adapter, "close_position"):
                        self.adapter.close_position(p.ticket)
                        closed_tickets.append(p.ticket)

            uow.audit.log_event("EMERGENCY_CLOSE_ALL_EXECUTED", {
                "scope": scope,
                "closed_tickets_count": len(closed_tickets),
                "closed_tickets": closed_tickets
            })

            return {
                "status": "success",
                "scope": scope,
                "closed_count": len(closed_tickets),
                "closed_tickets": closed_tickets
            }

def uuid4_str() -> str:
    from uuid import uuid4
    return str(uuid4())
