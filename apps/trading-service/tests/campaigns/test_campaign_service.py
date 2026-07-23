import pytest
from src.database.engine import engine, Base, SessionLocal
from src.parser.service import MessageParsingService
from src.campaigns.service import CampaignService
from src.campaigns.errors import ConcurrencyConflictError, InvalidStateTransitionError

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_full_campaign_lifecycle_and_confirmation():
    parse_service = MessageParsingService(session_factory=SessionLocal)
    camp_service = CampaignService(session_factory=SessionLocal)

    raw_signal = "Gold Sell\n4120-4128\nsl - 4136\ntp - 4112\ntp - 4104"
    _, _ = parse_service.parse_and_persist(
        raw_text=raw_signal, message_id="msg-sig-1", group_id="g1", sender_id="s1"
    )

    # 1. Create Campaign
    c_dict, is_dup = camp_service.create_campaign_from_message("msg-sig-1")
    assert is_dup is False
    assert c_dict["current_state"] == "AWAITING_CONFIRMATION"
    assert c_dict["requested_total_lots"] == 0.50

    # 2. Approve Campaign
    app_dict = camp_service.approve_campaign(c_dict["id"], expected_version=1)
    assert app_dict["current_state"] == "PLANNED"
    assert app_dict["version"] == 2
    assert app_dict["trading_enabled"] is False

    # 3. Test Optimistic Concurrency Conflict
    with pytest.raises(ConcurrencyConflictError):
        camp_service.approve_campaign(c_dict["id"], expected_version=1)

def test_incomplete_signal_initial_state_waiting_for_tp():
    parse_service = MessageParsingService(session_factory=SessionLocal)
    camp_service = CampaignService(session_factory=SessionLocal)

    raw_incomplete = "Gold Sell Limit\n3990-3998\nSl - 4008"
    _, _ = parse_service.parse_and_persist(
        raw_text=raw_incomplete, message_id="msg-sig-2", group_id="g1", sender_id="s1"
    )

    c_dict, _ = camp_service.create_campaign_from_message("msg-sig-2")
    assert c_dict["current_state"] == "WAITING_FOR_TP"
