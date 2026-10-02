"""Single-Writer Background Execution Worker for MT5."""

import json
import logging
import threading
import time
from typing import Optional, Dict, Any
from decimal import Decimal
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy.orm import Session

from src.database.engine import SessionLocal
from src.database.unit_of_work import UnitOfWork
from src.database.models import (
    CampaignModel, PlannedEntryModel, MT5ExecutionJobModel,
    MT5ExecutionAttemptModel, MT5OrderRecordModel, MT5PositionRecordModel,
    ControlStateModel, WorkerHeartbeatModel,
)
from src.database.types import coerce_decimal
from src.mt5.adapter import MT5AdapterInterface
from src.mt5.execution_queue import MT5ExecutionQueue
from src.mt5.contracts import Mt5OrderSendRequestDTO
from src.campaigns.constants import (
    STATE_PLACING_ORDERS, STATE_PENDING, STATE_PARTIALLY_PLACED, STATE_FAILED,
    REASON_ALL_ORDERS_PLACED, REASON_PARTIAL_PLACEMENT, REASON_PLACEMENT_FAILED,
    TRIGGER_SYSTEM,
)
from src.campaigns.state_machine import apply_transition
from src.mt5.constants import (
    JOB_SUCCEEDED, JOB_FAILED, JOB_OUTCOME_UNKNOWN, PARTIAL_BLOCK_REMAINING
)

logger = logging.getLogger("mt5_execution_worker")

WORKER_KIND = "MT5_EXECUTION"
#: How long a claimed job stays leased before recovery may reclassify it.
JOB_LEASE_SECONDS = 120


def uuid4_str() -> str:
    return str(uuid4())


class MT5ExecutionWorker:
    """Drains the execution queue one job at a time.

    Exactly one instance runs per process and the queue lease makes that safe
    across restarts: a job claimed by a worker that died is never silently
    re-sent, it is reclassified as OUTCOME_UNKNOWN for reconciliation.
    """

    def __init__(self, adapter: MT5AdapterInterface, session_factory=SessionLocal, worker_id: str = "single-writer-1"):
        self.adapter = adapter
        self.session_factory = session_factory
        self.worker_id = worker_id
        self.is_running = False
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._last_halted_check_time: float = 0.0
        self._last_halted_value: bool = False
        self._last_heartbeat_time: float = 0.0
        self._job_lock = threading.Lock()

    # -- background loop ----------------------------------------------------

    def start(self, poll_interval_seconds: float = 0.05) -> None:
        """Start the drain loop in a daemon thread. Idempotent."""
        if self.is_running:
            return
        self._stop_event.clear()
        self.is_running = True
        self._thread = threading.Thread(
            target=self._run_loop,
            args=(poll_interval_seconds,),
            name="mt5-execution-worker",
            daemon=True,
        )
        self._thread.start()
        logger.info("MT5 execution worker started (worker_id=%s)", self.worker_id)

    def stop(self, timeout_seconds: float = 10.0) -> None:
        """Signal the loop to finish the current job and exit."""
        if not self.is_running:
            return
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=timeout_seconds)
        self.is_running = False
        logger.info("MT5 execution worker stopped (worker_id=%s)", self.worker_id)

    def _run_loop(self, poll_interval_seconds: float) -> None:
        while not self._stop_event.is_set():
            try:
                self._record_heartbeat("IDLE")
                if self._execution_is_halted():
                    self._stop_event.wait(poll_interval_seconds)
                    continue
                processed = self.process_next_job()
                if not processed:
                    self._stop_event.wait(poll_interval_seconds)
            except Exception:
                logger.exception("Execution worker loop iteration failed")
                self._stop_event.wait(poll_interval_seconds)

    def _execution_is_halted(self) -> bool:
        """Emergency stop and the trading toggle gate the whole loop."""
        import time as _time
        now = _time.time()
        if (now - self._last_halted_check_time) < 2.0:
            return self._last_halted_value

        db = self.session_factory()
        is_halted = True
        try:
            ctrl = db.get(ControlStateModel, 1)
            if ctrl is not None:
                if ctrl.automation_state != "EMERGENCY_STOPPED":
                    if not (getattr(ctrl, "shutdown_state", "RUNNING") and ctrl.shutdown_state not in ("RUNNING", None)):
                        if ctrl.trading_enabled and ctrl.mt5_execution_enabled:
                            is_halted = False
        except Exception:
            is_halted = True
        finally:
            db.close()
            self._last_halted_check_time = now
            self._last_halted_value = is_halted

        return is_halted

    def _record_heartbeat(self, status: str, detail: Optional[Dict[str, Any]] = None, force: bool = False) -> None:
        import time as _time
        now = _time.time()
        if not force and (now - self._last_heartbeat_time) < 5.0:
            return

        db = self.session_factory()
        try:
            now_utc = datetime.now(timezone.utc)
            hb = db.get(WorkerHeartbeatModel, self.worker_id)
            if hb is None:
                hb = WorkerHeartbeatModel(
                    worker_id=self.worker_id,
                    worker_kind=WORKER_KIND,
                    started_at=now_utc,
                )
                db.add(hb)
            hb.status = status
            hb.detail_json = json.dumps(detail or {})
            hb.heartbeat_at = now_utc
            db.commit()
            self._last_heartbeat_time = now
        except Exception:
            db.rollback()
        finally:
            db.close()

    # -- job processing -----------------------------------------------------

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
        if not self._job_lock.acquire(blocking=False):
            return False
        try:
            return self._process_next_job_locked()
        finally:
            self._job_lock.release()

    def _process_next_job_locked(self) -> bool:
        with UnitOfWork(session_factory=self.session_factory) as uow:
            job = MT5ExecutionQueue.claim_next_job(
                uow.db, worker_id=self.worker_id, lease_seconds=JOB_LEASE_SECONDS
            )
            if not job:
                return False

            job_id = job.id
            campaign_id = job.campaign_id
            planned_entry_id = job.planned_entry_id
            operation_type = job.operation_type

            try:
                self._record_heartbeat("RUNNING", {"job_id": job_id})

                if not self.adapter.is_initialized():
                    self.adapter.initialize()

                campaign = uow.campaigns.get_by_id(campaign_id)
                if not campaign:
                    MT5ExecutionQueue.fail_job(uow.db, job_id, "CAMPAIGN_NOT_FOUND", f"Campaign '{campaign_id}' not found.")
                    return True

                entry = uow.db.get(PlannedEntryModel, planned_entry_id) if planned_entry_id else None

                if operation_type != "PLACE_PENDING_ORDER" or entry is None:
                    MT5ExecutionQueue.fail_job(
                        uow.db, job_id, "UNSUPPORTED_OPERATION",
                        f"Operation '{operation_type}' is not supported by this worker."
                    )
                    return True

                direction_str = str(campaign.signal.direction).upper().strip()
                entry_price = float(coerce_decimal(entry.price))

                # Fetch current tick price to dynamically choose LIMIT vs STOP
                try:
                    tick = self.adapter.symbol_tick("XAUUSD")
                    current_price = float(tick.ask if direction_str == "BUY" else tick.bid)
                except Exception:
                    current_price = 0.0

                if direction_str == "BUY":
                    if current_price > 0 and entry_price >= current_price:
                        order_type_str = "BUY_STOP"
                    else:
                        order_type_str = "BUY_LIMIT"
                else:  # SELL
                    if current_price > 0 and entry_price <= current_price:
                        order_type_str = "SELL_STOP"
                    else:
                        order_type_str = "SELL_LIMIT"

                comment = f"{campaign.campaign_code}-E{(entry.ladder_index + 1):02d}"
                magic = campaign.magic_number

                send_req = Mt5OrderSendRequestDTO(
                    symbol="XAUUSD",
                    volume=coerce_decimal(entry.volume),
                    order_type=order_type_str,
                    price=coerce_decimal(entry.price),
                    stop_loss=coerce_decimal(entry.stop_loss),
                    take_profit=coerce_decimal(entry.take_profit) if entry.take_profit is not None else None,
                    magic_number=magic,
                    comment=comment,
                    idempotency_key=job.idempotency_key
                )

                uow.db.commit()
                send_res = self.adapter.order_send(send_req)

                uow.db.add(MT5ExecutionAttemptModel(
                    id=uuid4_str(),
                    job_id=job_id,
                    attempt_number=job.attempt_count,
                    order_check_id=None,
                    retcode=send_res.retcode,
                    retcode_name=send_res.retcode_name,
                    deal_ticket=send_res.deal_ticket,
                    order_ticket=send_res.order_ticket,
                    response_json=json.dumps(send_res.model_dump(mode="json")),
                    is_success=send_res.is_success,
                    executed_at=datetime.now(timezone.utc)
                ))

                if send_res.is_success:
                    if send_res.order_ticket:
                        uow.db.add(MT5OrderRecordModel(
                            id=uuid4_str(),
                            campaign_id=campaign_id,
                            planned_entry_id=planned_entry_id,
                            ticket=send_res.order_ticket,
                            magic_number=magic,
                            symbol="XAUUSD",
                            order_type=order_type_str,
                            volume=coerce_decimal(entry.volume),
                            price=coerce_decimal(entry.price),
                            stop_loss=coerce_decimal(entry.stop_loss),
                            take_profit=coerce_decimal(entry.take_profit) if entry.take_profit is not None else None,
                            comment=comment,
                            state="PLACED"
                        ))
                    MT5ExecutionQueue.complete_job(uow.db, job_id, send_res.model_dump(mode="json"))
                else:
                    MT5ExecutionQueue.fail_job(uow.db, job_id, "ORDER_SEND_FAILED", send_res.comment)

                self._update_campaign_execution_state(uow.db, campaign)
                return True

            except Exception as e:
                # We cannot tell whether the broker saw the request, so the job
                # is parked for human review rather than retried.
                logger.error("Execution worker failed on job '%s': %s", job_id, e, exc_info=True)
                MT5ExecutionQueue.mark_outcome_unknown(uow.db, job_id, "WORKER_EXCEPTION", str(e))
                return True

    def _update_campaign_execution_state(self, db: Session, campaign: CampaignModel) -> None:
        """Derive the campaign state from the terminal status of its jobs."""
        jobs = db.query(MT5ExecutionJobModel).filter(MT5ExecutionJobModel.campaign_id == campaign.id).all()
        if not jobs:
            return

        succeeded = [j for j in jobs if j.status == JOB_SUCCEEDED]
        failed = [j for j in jobs if j.status == JOB_FAILED]
        unknown = [j for j in jobs if j.status == JOB_OUTCOME_UNKNOWN]
        settled = len(succeeded) + len(failed) + len(unknown)

        if settled < len(jobs):
            # Batch still in flight; leave the campaign in PLACING_ORDERS.
            return

        if unknown:
            # Never claim a clean outcome while any send is unconfirmed.
            target, reason_code, reason = (
                STATE_PARTIALLY_PLACED,
                REASON_PARTIAL_PLACEMENT,
                f"{len(unknown)} job(s) have an unconfirmed broker outcome; reconciliation required.",
            )
        elif not failed:
            target, reason_code, reason = (
                STATE_PENDING, REASON_ALL_ORDERS_PLACED,
                f"All {len(succeeded)} pending orders placed.",
            )
        elif succeeded:
            target, reason_code, reason = (
                STATE_PARTIALLY_PLACED, REASON_PARTIAL_PLACEMENT,
                f"{len(succeeded)} placed, {len(failed)} failed. {PARTIAL_BLOCK_REMAINING}",
            )
        else:
            target, reason_code, reason = (
                STATE_FAILED, REASON_PLACEMENT_FAILED,
                f"All {len(failed)} placement job(s) failed.",
            )

        apply_transition(
            db=db,
            campaign=campaign,
            to_state=target,
            reason_code=reason_code,
            reason=reason,
            trigger_type=TRIGGER_SYSTEM,
        )
