import json
from uuid import uuid4
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any, Callable
from sqlalchemy.orm import Session
from src.database.models import DomainEventModel, EventOutboxModel
from src.events.contracts import DomainEventDTO, redact_event_payload

class OutboxPublisher:
    """Manages transactional outbox writes in SQLite."""

    @staticmethod
    def publish_domain_event(
        db: Session,
        event_type: str,
        aggregate_type: str,
        aggregate_id: str,
        correlation_id: str,
        payload: Dict[str, Any],
        campaign_id: Optional[str] = None,
        causation_id: Optional[str] = None,
        actor_type: str = "SYSTEM",
        actor_id: Optional[str] = None,
        severity: Optional[str] = None,
        **kwargs
    ) -> DomainEventModel:
        event_id = str(uuid4())
        outbox_id = str(uuid4())
        now_utc = datetime.now(timezone.utc)

        redacted_payload = redact_event_payload(payload)
        payload_json = json.dumps(redacted_payload)

        # 1. Create Domain Event
        event_rec = DomainEventModel(
            id=str(uuid4()),
            event_id=event_id,
            event_type=event_type,
            event_version="1.0",
            aggregate_type=aggregate_type,
            aggregate_id=aggregate_id,
            campaign_id=campaign_id,
            correlation_id=correlation_id,
            causation_id=causation_id,
            actor_type=actor_type,
            actor_id=actor_id,
            payload_json=payload_json,
            occurred_at=now_utc,
            created_at=now_utc
        )
        db.add(event_rec)
        db.flush()

        # 2. Create Outbox Entry
        outbox_rec = EventOutboxModel(
            id=outbox_id,
            event_id=event_id,
            status="PENDING",
            attempt_count=0,
            max_attempts=5,
            available_at=now_utc,
            created_at=now_utc
        )
        db.add(outbox_rec)
        db.flush()

        return event_rec

class OutboxDispatcher:
    """Dispatches pending outbox events to registered subscribers, WebSockets, and SSE streams."""

    def __init__(self):
        self._subscribers: List[Callable[[DomainEventDTO], None]] = []

    def subscribe(self, callback: Callable[[DomainEventDTO], None]) -> None:
        self._subscribers.append(callback)

    def process_pending_outbox(self, db: Session, limit: int = 50) -> int:
        now_utc = datetime.now(timezone.utc)
        pending = (
            db.query(EventOutboxModel)
            .filter(EventOutboxModel.status == "PENDING")
            .filter(EventOutboxModel.available_at <= now_utc)
            .order_by(EventOutboxModel.created_at.asc())
            .limit(limit)
            .all()
        )

        processed = 0
        for outbox_entry in pending:
            domain_event = db.query(DomainEventModel).filter(DomainEventModel.event_id == outbox_entry.event_id).first()
            if not domain_event:
                outbox_entry.status = "FAILED"
                outbox_entry.last_error = "Associated domain event record not found."
                continue

            event_dto = DomainEventDTO(
                event_contract_version="1.0.0",
                event_id=domain_event.event_id,
                sequence=domain_event.sequence or 0,
                event_type=domain_event.event_type,
                event_version=domain_event.event_version,
                aggregate_type=domain_event.aggregate_type,
                aggregate_id=domain_event.aggregate_id,
                campaign_id=domain_event.campaign_id,
                correlation_id=domain_event.correlation_id,
                causation_id=domain_event.causation_id,
                actor_type=domain_event.actor_type,
                actor_id=domain_event.actor_id,
                occurred_at=domain_event.occurred_at.isoformat(),
                payload=json.loads(domain_event.payload_json)
            )

            # Broadcast to in-process subscribers
            for sub in self._subscribers:
                try:
                    sub(event_dto)
                except Exception:
                    pass

            outbox_entry.status = "PUBLISHED"
            outbox_entry.published_at = now_utc
            processed += 1

        db.flush()
        return processed

global_outbox_dispatcher = OutboxDispatcher()
