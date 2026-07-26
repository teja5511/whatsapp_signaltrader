import pytest
from src.database.engine import SessionLocal
from src.parser.service import MessageParsingService
from src.orchestration.coordinator import OrchestrationCoordinator
from src.orchestration.policies import ControlPolicyManager
from src.mt5.execution_service import MT5ExecutionService
from src.mt5.execution_worker import MT5ExecutionWorker

def test_e2e_fake_confirmation_and_execution():
    """
    End-to-End Fake Pipeline:
    1. Parse WhatsApp signal
    2. Create campaign in AWAITING_CONFIRMATION
    3. User approves campaign
    4. Auto-plan 5 limit entry ladder
    5. Run preflight checks
    6. Queue MT5 execution batch
    7. Execute MT5 batch via single-writer execution worker
    """
    parse_service = MessageParsingService(session_factory=SessionLocal)
    coord = OrchestrationCoordinator(session_factory=SessionLocal)
    ctrl = ControlPolicyManager()
    mt5_service = MT5ExecutionService(session_factory=SessionLocal)
    worker = MT5ExecutionWorker(adapter=mt5_service.adapter, session_factory=SessionLocal)

    ctrl.pause_automation()
    ctrl.enable_demo_trading("ENABLE DEMO XAUUSD TRADING")

    # 1. Ingest WhatsApp Signal
    raw_text = "BUY XAUUSD @ 4010 - 4020 SL: 3995 TP1: 4040 TP2: 4060"
    msg_id = "e2e-fake-msg-1"
    parse_service.parse_and_persist(
        raw_text=raw_text,
        message_id=msg_id,
        group_id="approved-group",
        sender_id="approved-admin"
    )

    # 2. Orchestrate Message
    orch_res = coord.process_raw_message_id(msg_id)
    assert orch_res["status"] == "awaiting_confirmation"
    campaign_id = orch_res["campaign_id"]

    # 3. User Approves Campaign
    app_res = coord.approve_campaign_and_orchestrate(campaign_id, expected_version=1)
    assert app_res["status"] == "approved_planned_and_queued"
    batch_id = app_res["batch_id"]

    # 4. Worker Processes Queued MT5 Jobs
    processed_count = worker.process_next_batch(batch_id)
    assert processed_count == 5

    # 5. Verify Orders in Fake MT5 Adapter
    orders = mt5_service.adapter.orders_get()
    assert len(orders) == 5
