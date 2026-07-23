import pytest
from decimal import Decimal
from src.database.engine import engine, Base, SessionLocal
from src.parser.service import MessageParsingService
from src.campaigns.service import CampaignService
from src.planning.service import PlanningService
from src.planning.policies import get_test_fixture_policies
from src.mt5.fake_adapter import FakeMT5Adapter
from src.mt5.execution_service import MT5ExecutionService
from src.mt5.execution_worker import MT5ExecutionWorker
from src.mt5.constants import JOB_SUCCEEDED
from src.campaigns.constants import STATE_PENDING, STATE_PARTIALLY_PLACED

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_execution_queue_worker_full_lifecycle():
    parse_service = MessageParsingService(session_factory=SessionLocal)
    camp_service = CampaignService(session_factory=SessionLocal)
    plan_service = PlanningService(session_factory=SessionLocal)

    # 1. Parse & Approve Signal
    msg_raw = "Gold Sell\n3990-3998\nsl - 4008\ntp - 3960\ntp - 3950"
    parse_service.parse_and_persist(raw_text=msg_raw, message_id="msg-mt5-exec-1", group_id="g1", sender_id="s1")
    c_dict, _ = camp_service.create_campaign_from_message("msg-mt5-exec-1")
    c_id = c_dict["id"]
    camp_service.approve_campaign(c_id, expected_version=1)

    # 2. Plan Entries
    plan_res, _ = plan_service.plan_campaign(c_id, policies=get_test_fixture_policies())
    c_planned = camp_service.get_campaign(c_id)

    # 3. Queue Execution Batch
    adapter = FakeMT5Adapter(scenario="healthy_demo_hedging")
    exec_service = MT5ExecutionService(adapter=adapter, session_factory=SessionLocal)
    worker = MT5ExecutionWorker(adapter=adapter, session_factory=SessionLocal)

    preflight = exec_service.run_preflight(c_id)
    assert preflight.is_ready is True

    exec_res, _ = exec_service.queue_campaign_execution(
        campaign_id=c_id,
        expected_version=c_planned["version"],
        planning_fingerprint=plan_res["planning_fingerprint"],
        explicit_user_confirm=True
    )
    assert exec_res.jobs_count == 5
    assert exec_res.status == "QUEUED"

    # 4. Process all 5 queued jobs with worker
    processed_count = 0
    while worker.process_next_job():
        processed_count += 1

    assert processed_count == 5
    assert len(adapter.orders_get()) == 5

    c_final = camp_service.get_campaign(c_id)
    assert c_final["current_state"] == "PENDING"

def test_execution_worker_partial_placement_on_failure():
    parse_service = MessageParsingService(session_factory=SessionLocal)
    camp_service = CampaignService(session_factory=SessionLocal)
    plan_service = PlanningService(session_factory=SessionLocal)

    msg_raw = "Gold Sell\n3990-3998\nsl - 4008\ntp - 3960\ntp - 3950"
    parse_service.parse_and_persist(raw_text=msg_raw, message_id="msg-mt5-exec-2", group_id="g1", sender_id="s1")
    c_dict, _ = camp_service.create_campaign_from_message("msg-mt5-exec-2")
    c_id = c_dict["id"]
    camp_service.approve_campaign(c_id, expected_version=1)
    plan_res, _ = plan_service.plan_campaign(c_id, policies=get_test_fixture_policies())
    c_planned = camp_service.get_campaign(c_id)

    # Inject middle send failure scenario
    adapter = FakeMT5Adapter(scenario="middle_send_failure")
    exec_service = MT5ExecutionService(adapter=adapter, session_factory=SessionLocal)
    worker = MT5ExecutionWorker(adapter=adapter, session_factory=SessionLocal)

    exec_service.queue_campaign_execution(
        campaign_id=c_id,
        expected_version=c_planned["version"],
        planning_fingerprint=plan_res["planning_fingerprint"],
        explicit_user_confirm=True
    )

    while worker.process_next_job():
        pass

    c_final = camp_service.get_campaign(c_id)
    assert c_final["current_state"] == STATE_PARTIALLY_PLACED
