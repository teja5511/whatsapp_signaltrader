import pytest
from src.database.engine import engine, Base, SessionLocal
from src.parser.service import MessageParsingService
from src.database.models import WhatsAppMessageModel, ParsedMessageModel, SignalModel

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_parsing_service_persistence_and_idempotency():
    service = MessageParsingService(session_factory=SessionLocal)
    raw = "Gold Sell\n4120-4128\n\nsl - 4136\n\ntp - 4112\ntp - 4104\ntp - Open"

    # First submission
    res_dict, is_dup = service.parse_and_persist(
        raw_text=raw,
        message_id="msg-service-001",
        group_id="group-001",
        sender_id="admin-001"
    )
    assert is_dup is False
    assert res_dict["category"] == "NEW_SIGNAL"
    assert res_dict["signal"]["direction"] == "SELL"

    # Verify DB persistence
    db = SessionLocal()
    try:
        raw_msg = db.get(WhatsAppMessageModel, "msg-service-001")
        assert raw_msg is not None
        assert raw_msg.parsed_message is not None
        assert raw_msg.parsed_message.signal is not None
        assert raw_msg.parsed_message.signal.direction == "SELL"
    finally:
        db.close()

    # Second submission (Idempotency duplicate check)
    res_dup_dict, is_dup2 = service.parse_and_persist(
        raw_text=raw,
        message_id="msg-service-001",
        group_id="group-001",
        sender_id="admin-001"
    )
    assert is_dup2 is True
    assert res_dup_dict["category"] == "NEW_SIGNAL"
