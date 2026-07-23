import pytest
from src.database.engine import engine, Base, SessionLocal
from src.database.models import WhatsAppMessageModel
from src.campaigns.duplicate_service import DuplicateProtectionService

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_semantic_fingerprint_deterministic():
    fp1 = DuplicateProtectionService.generate_semantic_fingerprint(
        instrument="XAUUSD", direction="SELL", order_intent="UNSPECIFIED",
        zone_low="4120.00", zone_high="4128.00", stop_loss="4136.00",
        tp1="4112.00", tp2="4104.00", tp_open_present=True,
        group_id="group-1", sender_id="admin-1"
    )

    fp2 = DuplicateProtectionService.generate_semantic_fingerprint(
        instrument="xauusd", direction="sell", order_intent="unspecified",
        zone_low="4120", zone_high="4128", stop_loss="4136",
        tp1="4112.0000", tp2="4104.00000000", tp_open_present=True,
        group_id="group-1", sender_id="admin-1"
    )

    assert fp1 == fp2

def test_exact_and_semantic_duplicate_registration():
    dup_service = DuplicateProtectionService()
    db = SessionLocal()
    try:
        # Create dummy raw message first to satisfy foreign key requirement
        raw_msg = WhatsAppMessageModel(
            id="msg-101",
            group_id="group-1",
            sender_id="admin-1",
            is_admin=True,
            raw_content="Gold Sell",
            content_hash="hash-101"
        )
        db.add(raw_msg)
        db.commit()

        # Check initially not duplicate
        decision, c_id = dup_service.check_duplicate(db, "group-1", "msg-101", "fp-101")
        assert decision == "NOT_DUPLICATE"

        # Register keys
        dup_service.register_duplicate_keys(db, "group-1", "msg-101", "fp-101", 24)
        db.commit()

        # Exact Duplicate check
        dec_exact, _ = dup_service.check_duplicate(db, "group-1", "msg-101", "other-fp")
        assert dec_exact == "EXACT_DUPLICATE"

        # Semantic Duplicate check
        dec_sem, _ = dup_service.check_duplicate(db, "group-1", "new-msg-102", "fp-101")
        assert dec_sem == "SEMANTIC_DUPLICATE"
    finally:
        db.close()
