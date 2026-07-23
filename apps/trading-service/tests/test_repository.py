import pytest
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from src.database.engine import SessionLocal, Base, engine
from src.database.repository import SettingsRepository, WhatsAppMessageRepository, AuditLogRepository
from src.database.models import WhatsAppMessageModel

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_settings_repository_defaults():
    db: Session = SessionLocal()
    try:
        repo = SettingsRepository(db)
        settings = repo.get_settings()
        assert settings.entry_count == 5
        assert float(settings.lot_per_entry) == 0.10
        assert float(settings.max_exposure_lots) == 2.00
    finally:
        db.close()

def test_settings_repository_update():
    db: Session = SessionLocal()
    try:
        repo = SettingsRepository(db)
        repo.set_setting("entry_count", "6")
        db.commit()

        updated = repo.get_settings()
        assert updated.entry_count == 6
    finally:
        db.close()

def test_message_deduplication():
    db: Session = SessionLocal()
    try:
        repo = WhatsAppMessageRepository(db)
        dedup_key = "hash_123456789"
        assert not repo.is_duplicate(dedup_key)

        msg = WhatsAppMessageModel(
            id="msg-100",
            group_id="group-01",
            sender_id="admin-01",
            is_admin=True,
            raw_content="Gold Sell 4120-4128",
            content_hash="hash_123456789",
            received_at=datetime.now(timezone.utc)
        )
        repo.add_message(msg, dedup_key)
        db.commit()

        assert repo.is_duplicate(dedup_key)
    finally:
        db.close()

def test_audit_log_repository():
    db: Session = SessionLocal()
    try:
        repo = AuditLogRepository(db)
        repo.log_event("TEST_EVENT", {"key": "value"})
        db.commit()

        logs = repo.list_logs()
        assert len(logs) == 1
        assert logs[0].event_type == "TEST_EVENT"
    finally:
        db.close()
