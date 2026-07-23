import pytest
from src.database.engine import SessionLocal
from src.events.outbox import OutboxPublisher, global_outbox_dispatcher
from src.events.contracts import redact_event_payload
from src.database.models import DomainEventModel, EventOutboxModel

def test_payload_redaction():
    payload = {
        "campaign_id": "c-123",
        "api_token": "secret-token",
        "password": "my-password",
        "session_data": "qr-code-secret",
        "entry_count": 5
    }
    redacted = redact_event_payload(payload)
    assert redacted["campaign_id"] == "c-123"
    assert redacted["api_token"] == "[REDACTED]"
    assert redacted["password"] == "[REDACTED]"
    assert redacted["session_data"] == "[REDACTED]"
    assert redacted["entry_count"] == 5

def test_outbox_publish_and_dispatch():
    db = SessionLocal()
    try:
        ev = OutboxPublisher.publish_domain_event(
            db=db,
            event_type="TEST_EVENT",
            aggregate_type="TEST",
            aggregate_id="t-1",
            correlation_id="corr-test-1",
            payload={"foo": "bar", "password": "secret"}
        )
        db.commit()

        assert ev.event_id is not None
        assert ev.sequence is not None

        # Process outbox
        processed = global_outbox_dispatcher.process_pending_outbox(db)
        db.commit()
        assert processed == 1

        outbox_entry = db.query(EventOutboxModel).filter(EventOutboxModel.event_id == ev.event_id).first()
        assert outbox_entry.status == "PUBLISHED"
    finally:
        db.close()
