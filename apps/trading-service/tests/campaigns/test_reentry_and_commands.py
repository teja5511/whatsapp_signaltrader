import pytest
from src.database.engine import engine, Base, SessionLocal
from src.parser.service import MessageParsingService
from src.campaigns.service import CampaignService

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_delayed_tp_updates_and_reentry():
    parse_service = MessageParsingService(session_factory=SessionLocal)
    camp_service = CampaignService(session_factory=SessionLocal)

    # 1. Incomplete signal -> WAITING_FOR_TP
    raw_sig = "Gold Sell Limit\n3990-3998\nSl - 4008"
    parse_service.parse_and_persist(raw_text=raw_sig, message_id="msg-parent-sig", group_id="g1", sender_id="s1")
    c_parent, _ = camp_service.create_campaign_from_message("msg-parent-sig")
    assert c_parent["current_state"] == "WAITING_FOR_TP"

    # 2. Delayed TP1 command -> updates TP1
    parse_service.parse_and_persist(raw_text="TP1 3960", message_id="msg-tp1", group_id="g1", sender_id="s1")
    res_tp1 = camp_service.process_message("msg-tp1")
    assert res_tp1["status"] == "attached"

    # 3. Delayed TP2 command -> updates TP2 and transitions to AWAITING_CONFIRMATION
    parse_service.parse_and_persist(raw_text="TP2 3950", message_id="msg-tp2", group_id="g1", sender_id="s1")
    res_tp2 = camp_service.process_message("msg-tp2")
    assert res_tp2["status"] == "attached"

    # Verify state transition to AWAITING_CONFIRMATION
    db = SessionLocal()
    try:
        from src.database.models import CampaignModel
        updated_c = db.get(CampaignModel, c_parent["id"])
        assert updated_c.tp1 == 3960.0
        assert updated_c.tp2 == 3950.0
        assert updated_c.current_state == "AWAITING_CONFIRMATION"
    finally:
        db.close()

    # 4. Explicit Re-entry Command -> creates linked child campaign
    parse_service.parse_and_persist(raw_text="Same Zone for Re-entry", message_id="msg-reentry", group_id="g1", sender_id="s1")
    res_reentry = camp_service.process_message("msg-reentry")
    assert res_reentry["type"] == "REENTRY"
    assert res_reentry["status"] == "reentry_created"
    child_dict = res_reentry["child_campaign"]
    assert child_dict["parent_campaign_id"] == c_parent["id"]
    assert child_dict["reentry_sequence"] == 1
