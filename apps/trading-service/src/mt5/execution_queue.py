"""Single-Writer Durable Execution Queue."""

import json
from uuid import uuid4
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import select
from src.database.models import MT5ExecutionBatchModel, MT5ExecutionJobModel
from src.mt5.constants import (
    JOB_QUEUED, JOB_RUNNING, JOB_SUCCEEDED, JOB_FAILED, JOB_BLOCKED, JOB_OUTCOME_UNKNOWN, JOB_CANCELLED,
    BATCH_QUEUED, BATCH_RUNNING, BATCH_SUCCEEDED, BATCH_PARTIALLY_PLACED, BATCH_FAILED
)

class MT5ExecutionQueue:
    """Manages persistent queuing and single-writer job locking in SQLite."""

    @staticmethod
    def create_batch_and_jobs(
        db: Session,
        campaign_id: str,
        campaign_version: int,
        planning_fingerprint: str,
        jobs_data: List[Dict[str, Any]]
    ) -> Tuple[MT5ExecutionBatchModel, List[MT5ExecutionJobModel]]:
        batch_id = str(uuid4())
        now_utc = datetime.now(timezone.utc)

        batch = MT5ExecutionBatchModel(
            id=batch_id,
            campaign_id=campaign_id,
            campaign_version=campaign_version,
            planning_fingerprint=planning_fingerprint,
            status=BATCH_QUEUED,
            total_jobs=len(jobs_data),
            completed_jobs=0,
            failed_jobs=0,
            created_at=now_utc,
            updated_at=now_utc
        )
        db.add(batch)
        db.flush()

        jobs = []
        for idx, item in enumerate(jobs_data):
            job_id = str(uuid4())
            job = MT5ExecutionJobModel(
                id=job_id,
                batch_id=batch_id,
                campaign_id=campaign_id,
                planned_entry_id=item.get("planned_entry_id"),
                operation_type=item.get("operation_type", "PLACE_PENDING_ORDER"),
                idempotency_key=item["idempotency_key"],
                status=JOB_QUEUED,
                priority=item.get("priority", 10 + idx),
                attempt_count=0,
                max_attempts=item.get("max_attempts", 1),
                payload_json=json.dumps(item.get("payload", {})),
                available_at=now_utc,
                created_at=now_utc,
                updated_at=now_utc
            )
            db.add(job)
            jobs.append(job)

        db.flush()
        return batch, jobs

    @staticmethod
    def claim_next_job(
        db: Session,
        worker_id: str = "worker-1",
        lease_seconds: int = 120,
    ) -> Optional[MT5ExecutionJobModel]:
        """Claim the highest-priority queued job under a time-boxed lease.

        The lease is what makes crash recovery safe: a RUNNING job whose lease
        has expired is reclassified as OUTCOME_UNKNOWN by the recovery sweep
        rather than being handed to another worker and sent twice.
        """
        now_utc = datetime.now(timezone.utc)
        job = (
            db.query(MT5ExecutionJobModel)
            .filter(MT5ExecutionJobModel.status == JOB_QUEUED)
            .filter(MT5ExecutionJobModel.available_at <= now_utc)
            .order_by(MT5ExecutionJobModel.priority.asc(), MT5ExecutionJobModel.created_at.asc())
            .first()
        )
        if not job:
            return None

        job.status = JOB_RUNNING
        job.locked_at = now_utc
        job.locked_by = worker_id
        job.lease_expires_at = now_utc + timedelta(seconds=lease_seconds)
        job.started_at = now_utc
        job.attempt_count += 1
        job.updated_at = now_utc
        db.flush()
        return job

    @staticmethod
    def mark_outcome_unknown(db: Session, job_id: str, error_code: str, error_msg: str) -> None:
        """Terminal state for a send whose result was never confirmed.

        Counts against the batch like a failure but is never retried
        automatically and always requires manual review.
        """
        now_utc = datetime.now(timezone.utc)
        job = db.get(MT5ExecutionJobModel, job_id)
        if not job:
            return

        job.status = JOB_OUTCOME_UNKNOWN
        job.last_error_code = error_code
        job.last_error_message = error_msg
        job.requires_manual_review = True
        job.lease_expires_at = None
        job.completed_at = now_utc
        job.updated_at = now_utc

        if job.batch_id:
            batch = db.get(MT5ExecutionBatchModel, job.batch_id)
            if batch:
                batch.failed_jobs += 1
                if batch.completed_jobs + batch.failed_jobs >= batch.total_jobs:
                    batch.status = BATCH_FAILED if batch.completed_jobs == 0 else BATCH_PARTIALLY_PLACED
                batch.updated_at = now_utc
        db.flush()

    @staticmethod
    def complete_job(db: Session, job_id: str, result_dict: Dict[str, Any]) -> None:
        now_utc = datetime.now(timezone.utc)
        job = db.get(MT5ExecutionJobModel, job_id)
        if job:
            job.status = JOB_SUCCEEDED
            job.result_json = json.dumps(result_dict)
            job.lease_expires_at = None
            job.completed_at = now_utc
            job.updated_at = now_utc

            if job.batch_id:
                batch = db.get(MT5ExecutionBatchModel, job.batch_id)
                if batch:
                    batch.completed_jobs += 1
                    if batch.completed_jobs + batch.failed_jobs >= batch.total_jobs:
                        batch.status = BATCH_SUCCEEDED if batch.failed_jobs == 0 else BATCH_PARTIALLY_PLACED
                    batch.updated_at = now_utc
            db.flush()

    @staticmethod
    def fail_job(db: Session, job_id: str, error_code: str, error_msg: str) -> None:
        now_utc = datetime.now(timezone.utc)
        job = db.get(MT5ExecutionJobModel, job_id)
        if job:
            job.status = JOB_FAILED
            job.last_error_code = error_code
            job.last_error_message = error_msg
            job.lease_expires_at = None
            job.completed_at = now_utc
            job.updated_at = now_utc

            if job.batch_id:
                batch = db.get(MT5ExecutionBatchModel, job.batch_id)
                if batch:
                    batch.failed_jobs += 1
                    if batch.completed_jobs + batch.failed_jobs >= batch.total_jobs:
                        batch.status = BATCH_FAILED if batch.completed_jobs == 0 else BATCH_PARTIALLY_PLACED
                    batch.updated_at = now_utc
            db.flush()
