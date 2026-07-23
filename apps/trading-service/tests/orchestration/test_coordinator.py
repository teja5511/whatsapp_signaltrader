import pytest
from src.database.engine import SessionLocal
from src.parser.service import MessageParsingService
from src.orchestration.coordinator import OrchestrationCoordinator
from src.orchestration.policies import ControlPolicyManager

def test_coordinator_signal_confirmation_pipeline():
    parse_service = MessageParsingService(session_factory=SessionLocal)
    coord = OrchestrationCoordinator(session_factory=SessionLocal)
    ctrl = ControlPolicyManager()

    ctrl.pause_automation()

    raw_text = "BUY XAUUSD @ 4000 - 4005 SL: 3990 TP1: 4020 TP2: 4030"
    parse_res, _ = parse_service.parse_and_persist(
        raw_text=raw_text,
        message_id="coord-msg-1",
        group_id="approved-group",
        sender_id="approved-admin"
    )

    orch_res = coord.process_raw_message_id("coord-msg-1")
    assert orch_res["status"] == "awaiting_confirmation"
    assert "campaign_id" in orch_res

    # Test Campaign User Approval
    app_res = coord.approve_campaign_and_orchestrate(orch_res["campaign_id"], expected_version=1)
    assert app_res["status"] == "approved_planned_and_queued"
    assert "batch_id" in app_res

def test_coordinator_duplicate_protection():
    parse_service = MessageParsingService(session_factory=SessionLocal)
    coord = OrchestrationCoordinator(session_factory=SessionLocal)

    raw_text = "BUY XAUUSD @ 4000 - 4005 SL: 3990 TP1: 4020 TP2: 4030"
    parse_service.parse_and_persist(
        raw_text=raw_text,
        message_id="coord-msg-2",
        group_id="approved-group",
        sender_id="approved-admin"
    )

    res1 = coord.process_raw_message_id("coord-msg-2")
    # Idempotent second processing
    res2 = coord.process_raw_message_id("coord-msg-2")
    assert res2["status"] == "idempotent_existing"
    assert res2["orchestration_run_id"] == res1["orchestration_run_id"]
