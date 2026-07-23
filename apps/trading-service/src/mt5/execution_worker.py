"""Single-Writer Background Execution Worker for MT5."""

import json
import logging
from typing import Optional, Dict, Any
from decimal import Decimal
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from src.database.engine import SessionLocal
from src.database.unit_of_work import UnitOfWork
from src.database.models import CampaignModel, PlannedEntryModel, MT5ExecutionJobModel, MT5OrderCheckModel, MT5ExecutionAttemptModel, MT5OrderRecordModel
from src.mt5.adapter import MT5AdapterInterface
from src.mt5.execution_queue import MT5ExecutionQueue
from src.mt5.contracts import Mt5OrderCheckRequestDTO, Mt5OrderSendRequestDTO
from src.campaigns.constants import (
    STATE_PLACING_ORDERS, STATE_PENDING, STATE_PARTIALLY_PLACED, STATE_FAILED
)
from src.mt5.constants import (
    JOB_SUCCEEDED, JOB_FAILED, PARTIAL_BLOCK_REMAINING
)

logger = logging.getLogger("mt5_execution_worker")

def uuid4_str() -> str:
    from uuid import uuid4
    return str(uuid4())

class MT5ExecutionWorker:
    def __init__(self, adapter: MT5AdapterInterface, session_factory=SessionLocal, worker_id: str = "single-writer-1"):
        self.adapter = adapter
        self.session_factory = session_factory
        self.worker_id = worker_id
        self.is_running = False

    def process_next_batch(self, batch_id: Optional[str] = None) -> int:
        count = 0
        while self.process_next_job():
            count += 1
        return count

    def process_next_job(self) -> bool:
        """
        Pulls and processes one queued trade execution job safely.
        Returns True if a job was processed, False if queue was empty.
        """
        with UnitOfWork(session_factory=self.session_factory) as uow:
            job = MT5ExecutionQueue.claim_next_job(uow.db, worker_id=self.worker_id)
            if not job:
                return False

            job_id = job.id
            payload = json.loads(job.payload_json)
            campaign_id = job.campaign_id
            planned_entry_id = job.planned_entry_id
            operation_type = job.operation_type

            try:
                # 1. Verify Adapter Safety & Readiness
                if not self.adapter.is_initialized():
                    self.adapter.initialize()

                acc_info = self.adapter.account_info()

                # 2. Retrieve Campaign & Entry
                campaign = uow.campaigns.get_by_id(campaign_id)
                if not campaign:
                    MT5ExecutionQueue.fail_job(uow.db, job_id, "CAMPAIGN_NOT_FOUND", f"Campaign '{campaign_id}' not found.")
                    return True

                entry = uow.db.get(PlannedEntryModel, planned_entry_id) if planned_entry_id else None

                # 3. Build & Run Order Check
                if operation_type == "PLACE_PENDING_ORDER" and entry:
                    order_type_str = "BUY_LIMIT" if campaign.signal.direction == "BUY" else "SELL_LIMIT"
                    check_req = Mt5OrderCheckRequestDTO(
                        symbol="XAUUSD",
                        volume=Decimal(str(entry.volume)),
                        order_type=order_type_str,
                        price=Decimal(str(entry.price)),
                        stop_loss=Decimal(str(entry.stop_loss)),
                        take_profit=Decimal(str(entry.take_profit)) if entry.take_profit else None,
                        magic_number=campaign.magic_number,
                        comment=f"{campaign.campaign_code}-E0{entry.ladder_index + 1}"
                    )

                    check_res = self.adapter.order_check(check_req)

                    # Persist Order Check Record
                    check_rec = MT5OrderCheckModel(
                        id=uuid4_str(),
                        job_id=job_id,
                        request_json=json.dumps(check_req.model_dump(mode="json")),
                        retcode=check_res.retcode,
                        retcode_name=check_res.retcode_name,
                        is_valid=check_res.is_valid,
                        comment=check_res.comment,
                        margin=float(check_res.margin),
                        margin_free=float(check_res.margin_free),
                        checked_at=datetime.now(timezone.utc)
                    )
                    uow.db.add(check_rec)
                    uow.db.flush()

                    if not check_res.is_valid:
                        MT5ExecutionQueue.fail_job(uow.db, job_id, "ORDER_CHECK_FAILED", check_res.comment)
                        self._handle_partial_placement_failure(uow.db, campaign)
                        return True

                    # 4. Execute Order Send (Preceded by Check)
                    send_req = Mt5OrderSendRequestDTO(
                        symbol="XAUUSD",
                        volume=Decimal(str(entry.volume)),
                        order_type=order_type_str,
                        price=Decimal(str(entry.price)),
                        stop_loss=Decimal(str(entry.stop_loss)),
                        take_profit=Decimal(str(entry.take_profit)) if entry.take_profit else None,
                        magic_number=campaign.magic_number,
                        comment=f"{campaign.campaign_code}-E0{entry.ladder_index + 1}",
                        idempotency_key=job.idempotency_key
                    )

                    send_res = self.adapter.order_send(send_req)

                    # Persist Attempt Record
                    attempt_rec = MT5ExecutionAttemptModel(
                        id=uuid4_str(),
                        job_id=job_id,
                        attempt_number=job.attempt_count,
                        order_check_id=check_rec.id,
                        retcode=send_res.retcode,
                        retcode_name=send_res.retcode_name,
                        deal_ticket=send_res.deal_ticket,
                        order_ticket=send_res.order_ticket,
                        response_json=json.dumps(send_res.model_dump(mode="json")),
                        is_success=send_res.is_success,
                        executed_at=datetime.now(timezone.utc)
                    )
                    uow.db.add(attempt_rec)

                    if send_res.is_success:
                        # Record Order
                        if send_res.order_ticket:
                            o_rec = MT5OrderRecordModel(
                                id=uuid4_str(),
                                campaign_id=campaign_id,
                                planned_entry_id=planned_entry_id,
                                ticket=send_res.order_ticket,
                                magic_number=campaign.magic_number,
                                symbol="XAUUSD",
                                order_type=order_type_str,
                                volume=float(entry.volume),
                                price=float(entry.price),
                                stop_loss=float(entry.stop_loss),
                                take_profit=float(entry.take_profit) if entry.take_profit else None,
                                comment=send_req.comment,
                                state="PLACED"
                            )
                            uow.db.add(o_rec)

                        MT5ExecutionQueue.complete_job(uow.db, job_id, send_res.model_dump(mode="json"))
                        self._update_campaign_execution_state(uow.db, campaign)
                    else:
                        MT5ExecutionQueue.fail_job(uow.db, job_id, "ORDER_SEND_FAILED", send_res.comment)
                        self._handle_partial_placement_failure(uow.db, campaign)
                else:
                    MT5ExecutionQueue.complete_job(uow.db, job_id, {"status": "success", "op": operation_type})

                return True

            except Exception as e:
                logger.error(f"Execution worker failed on job '{job_id}': {e}", exc_info=True)
                MT5ExecutionQueue.fail_job(uow.db, job_id, "WORKER_EXCEPTION", str(e))
                return True

    def _handle_partial_placement_failure(self, db: Session, campaign: CampaignModel) -> None:
        if campaign.current_state in (STATE_PLACING_ORDERS, STATE_PENDING):
            campaign.current_state = STATE_PARTIALLY_PLACED
            campaign.version += 1
            db.flush()

    def _update_campaign_execution_state(self, db: Session, campaign: CampaignModel) -> None:
        jobs = db.query(MT5ExecutionJobModel).filter(MT5ExecutionJobModel.campaign_id == campaign.id).all()
        succeeded = [j for j in jobs if j.status == JOB_SUCCEEDED]
        failed = [j for j in jobs if j.status == JOB_FAILED]

        if len(succeeded) == len(jobs) and len(jobs) > 0:
            campaign.current_state = STATE_PENDING
            campaign.version += 1
        elif len(failed) > 0 and len(succeeded) > 0:
            campaign.current_state = STATE_PARTIALLY_PLACED
            campaign.version += 1
        elif len(failed) == len(jobs) and len(jobs) > 0:
            campaign.current_state = STATE_FAILED
            campaign.version += 1
        db.flush()
