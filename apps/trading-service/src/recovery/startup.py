import os
import json
from uuid import uuid4
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from src.database.engine import SessionLocal
from src.database.unit_of_work import UnitOfWork
from src.database.models import (
    RecoveryActionModel, ControlStateModel, OrchestrationRunModel,
    EventOutboxModel, MT5ExecutionJobModel
)
from src.orchestration.policies import ControlPolicyManager
from src.recovery.incidents import HealthIncidentManager

class RecoveryActionResultDTO(BaseModel):
    id: str
    action_kind: str
    entity_type: str
    entity_id: str
    previous_state: Optional[str] = None
    new_state: Optional[str] = None
    detail: Dict[str, Any] = Field(default_factory=dict)
    correlation_id: str
    actor: str = "SYSTEM"
    created_at: datetime

class StartupRecoveryResultDTO(BaseModel):
    database_integrity: str = "OK"
    foreign_keys: str = "ENABLED"
    wal_mode: str = "WAL"
    control_state: Dict[str, Any] = Field(default_factory=dict)
    recovered_orchestration_runs_count: int = 0
    recovered_outbox_rows_count: int = 0
    recovered_execution_jobs_count: int = 0
    recovered_spool_files_count: int = 0
    recovery_actions: List[RecoveryActionResultDTO] = Field(default_factory=list)
    recovery_completed_at: datetime

class StartupRecoveryManager:
    def __init__(
        self,
        session_factory=SessionLocal,
        spool_dir: str = "data/spool"
    ):
        self.session_factory = session_factory
        self.spool_dir = spool_dir
        self.incident_manager = HealthIncidentManager(session_factory=session_factory)

    def run_startup_recovery(
        self,
        correlation_id: Optional[str] = None,
        session: Optional[Session] = None
    ) -> StartupRecoveryResultDTO:
        corr_id = correlation_id or f"corr-startup-{uuid4()}"
        now_utc = datetime.now(timezone.utc)
        actions: List[RecoveryActionModel] = []

        with UnitOfWork(session_factory=self.session_factory, session=session) as uow:
            # 1. Database Integrity & Pragmas
            try:
                db_check = uow.db.execute(text("PRAGMA integrity_check")).scalar()
                integrity_status = "OK" if db_check == "ok" else f"CORRUPT: {db_check}"
            except Exception as ex:
                integrity_status = f"ERROR: {str(ex)}"
                self.incident_manager.record_incident(
                    incident_kind="DATABASE_DEGRADED",
                    title="Database Integrity Check Failed",
                    severity="CRITICAL",
                    detail={"error": str(ex)},
                    session=uow.db
                )

            try:
                uow.db.execute(text("PRAGMA foreign_keys = ON;"))
                uow.db.execute(text("PRAGMA journal_mode = WAL;"))
                uow.db.execute(text("PRAGMA busy_timeout = 5000;"))
            except Exception:
                pass

            # 2. Control State Initialization
            ctrl_policy = ControlPolicyManager(session_factory=self.session_factory)
            ctrl_policy.ensure_control_state()
            ctrl = uow.db.get(ControlStateModel, 1)
            ctrl_dict = {
                "automation_state": ctrl.automation_state if ctrl else "PAUSED",
                "trading_enabled": ctrl.trading_enabled if ctrl else False,
                "mt5_execution_enabled": ctrl.mt5_execution_enabled if ctrl else False,
            }

            # 3. Recover Abandoned Orchestration Runs
            abandoned_runs = uow.db.query(OrchestrationRunModel).filter(
                OrchestrationRunModel.status.in_(["RUNNING", "IN_PROGRESS"])
            ).all()

            recovered_runs_c = len(abandoned_runs)
            for run in abandoned_runs:
                prev = run.status
                run.status = "RECOVERED_STUCK"
                run.error_code = "STARTUP_RECOVERY_ABANDONED"
                run.error_message = "Orchestration run was interrupted by service restart."
                run.completed_at = now_utc

                act = RecoveryActionModel(
                    id=str(uuid4()),
                    recovery_version="1.0.0",
                    action_kind="RECOVER_ABANDONED_ORCHESTRATION_RUN",
                    entity_type="ORCHESTRATION_RUN",
                    entity_id=run.id,
                    previous_state=prev,
                    new_state="RECOVERED_STUCK",
                    detail_json=json.dumps({"reason": "Abandoned on startup"}),
                    correlation_id=corr_id,
                    actor="SYSTEM",
                    created_at=now_utc
                )
                actions.append(act)

            # 4. Recover Outbox Rows Stuck in PUBLISHING
            stuck_outbox = uow.db.query(EventOutboxModel).filter(
                EventOutboxModel.status == "PUBLISHING"
            ).all()
            recovered_outbox_c = len(stuck_outbox)
            for ob in stuck_outbox:
                prev = ob.status
                ob.status = "PENDING"
                ob.locked_by = None
                ob.lease_expires_at = None

                act = RecoveryActionModel(
                    id=str(uuid4()),
                    recovery_version="1.0.0",
                    action_kind="RECOVER_STUCK_OUTBOX_EVENT",
                    entity_type="OUTBOX_EVENT",
                    entity_id=ob.id,
                    previous_state=prev,
                    new_state="PENDING",
                    detail_json=json.dumps({"reason": "Reset publishing lock on startup"}),
                    correlation_id=corr_id,
                    actor="SYSTEM",
                    created_at=now_utc
                )
                actions.append(act)

            # 5. Recover Execution Jobs Stuck in RUNNING -> OUTCOME_UNKNOWN
            stuck_jobs = uow.db.query(MT5ExecutionJobModel).filter(
                MT5ExecutionJobModel.status == "RUNNING"
            ).all()
            recovered_jobs_c = len(stuck_jobs)
            for job in stuck_jobs:
                prev = job.status
                job.status = "OUTCOME_UNKNOWN"
                job.error_code = "STARTUP_RECOVERY_UNKNOWN_OUTCOME"
                job.error_message = "Execution job was running when worker crashed or restarted."
                job.completed_at = now_utc

                act = RecoveryActionModel(
                    id=str(uuid4()),
                    recovery_version="1.0.0",
                    action_kind="RECOVER_STUCK_EXECUTION_JOB",
                    entity_type="EXECUTION_JOB",
                    entity_id=job.id,
                    previous_state=prev,
                    new_state="OUTCOME_UNKNOWN",
                    detail_json=json.dumps({"reason": "Marked outcome_unknown on startup"}),
                    correlation_id=corr_id,
                    actor="SYSTEM",
                    created_at=now_utc
                )
                actions.append(act)

            # 6. Recover WhatsApp Spool Files Left in DELIVERING
            recovered_spool_c = 0
            if os.path.exists(self.spool_dir):
                delivering_dir = os.path.join(self.spool_dir, "delivering")
                pending_dir = os.path.join(self.spool_dir, "pending")
                if os.path.exists(delivering_dir) and os.path.exists(pending_dir):
                    for fname in os.listdir(delivering_dir):
                        if fname.endswith(".json"):
                            src_path = os.path.join(delivering_dir, fname)
                            dst_path = os.path.join(pending_dir, fname)
                            try:
                                os.rename(src_path, dst_path)
                                recovered_spool_c += 1
                                act = RecoveryActionModel(
                                    id=str(uuid4()),
                                    recovery_version="1.0.0",
                                    action_kind="RECOVER_SPOOL_FILE",
                                    entity_type="SPOOL_FILE",
                                    entity_id=fname,
                                    previous_state="DELIVERING",
                                    new_state="PENDING",
                                    detail_json=json.dumps({"file": fname}),
                                    correlation_id=corr_id,
                                    actor="SYSTEM",
                                    created_at=now_utc
                                )
                                actions.append(act)
                            except Exception:
                                pass

            # Persist actions
            for act in actions:
                uow.db.add(act)

            uow.audit.log_event("STARTUP_RECOVERY_COMPLETED", {
                "recovered_runs": recovered_runs_c,
                "recovered_outbox": recovered_outbox_c,
                "recovered_jobs": recovered_jobs_c,
                "recovered_spool": recovered_spool_c
            })

            action_dtos = [
                RecoveryActionResultDTO(
                    id=a.id,
                    action_kind=a.action_kind,
                    entity_type=a.entity_type,
                    entity_id=a.entity_id,
                    previous_state=a.previous_state,
                    new_state=a.new_state,
                    detail=json.loads(a.detail_json) if a.detail_json else {},
                    correlation_id=a.correlation_id,
                    actor=a.actor,
                    created_at=a.created_at
                )
                for a in actions
            ]

            return StartupRecoveryResultDTO(
                database_integrity=integrity_status,
                foreign_keys="ENABLED",
                wal_mode="WAL",
                control_state=ctrl_dict,
                recovered_orchestration_runs_count=recovered_runs_c,
                recovered_outbox_rows_count=recovered_outbox_c,
                recovered_execution_jobs_count=recovered_jobs_c,
                recovered_spool_files_count=recovered_spool_c,
                recovery_actions=action_dtos,
                recovery_completed_at=now_utc
            )
