import pytest
from decimal import Decimal
from src.database.engine import engine, Base, SessionLocal
from src.parser.service import MessageParsingService
from src.campaigns.service import CampaignService
from src.planning.service import PlanningService
from src.planning.policies import get_test_fixture_policies

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_full_planning_lifecycle():
    parse_service = MessageParsingService(session_factory=SessionLocal)
    camp_service = CampaignService(session_factory=SessionLocal)
    plan_service = PlanningService(session_factory=SessionLocal)

    raw_sig = "Gold Sell\n4120-4128\nsl - 4136\ntp - 4112\ntp - 4104"
    parse_service.parse_and_persist(raw_text=raw_sig, message_id="msg-plan-1", group_id="g1", sender_id="s1")

    # 1. Create Campaign
    c_dict, _ = camp_service.create_campaign_from_message("msg-plan-1")

    # 2. Approve Campaign
    camp_service.approve_campaign(c_dict["id"], expected_version=1)

    # 3. Plan Campaign Entries
    plan_res, is_idempotent = plan_service.plan_campaign(
        campaign_id=c_dict["id"],
        policies=get_test_fixture_policies()
    )
    assert is_idempotent is False
    assert plan_res["is_valid"] is True
    assert len(plan_res["planned_entries"]) == 5
    assert plan_res["requested_total_lots"] == "1.5000"

    # 4. Idempotent Second Call
    plan_res2, is_idempotent2 = plan_service.plan_campaign(
        campaign_id=c_dict["id"],
        policies=get_test_fixture_policies()
    )
    assert is_idempotent2 is True

    # 5. Retrieve Persisted Plan
    stored_plan = plan_service.get_campaign_plan(c_dict["id"])
    assert stored_plan["planned_entries_count"] == 5
