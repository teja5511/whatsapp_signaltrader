import pytest
from src.orchestration.policies import ControlPolicyManager
from src.orchestration.errors import EmergencyStopActiveError, InvalidControlPhraseError

def test_control_pause_and_resume():
    mgr = ControlPolicyManager()

    pause_res = mgr.pause_automation()
    assert pause_res["status"] == "success"
    assert pause_res["automation_state"] == "PAUSED"

    resume_res = mgr.resume_automation()
    assert resume_res["status"] == "success"
    assert resume_res["automation_state"] == "RUNNING"

def test_emergency_stop_and_reset():
    mgr = ControlPolicyManager()

    estop_res = mgr.trigger_emergency_stop()
    assert estop_res["status"] == "success"
    assert estop_res["automation_state"] == "EMERGENCY_STOPPED"

    # Resuming while emergency stopped must fail
    with pytest.raises(EmergencyStopActiveError):
        mgr.resume_automation()

    # Resetting with wrong phrase must fail
    with pytest.raises(InvalidControlPhraseError):
        mgr.reset_emergency_stop("WRONG PHRASE")

    # Resetting with correct phrase succeeds
    reset_res = mgr.reset_emergency_stop("RESET EMERGENCY STOP")
    assert reset_res["status"] == "success"
    assert reset_res["automation_state"] == "PAUSED"

def test_enable_demo_trading():
    mgr = ControlPolicyManager()

    # Enabling with wrong phrase fails
    with pytest.raises(InvalidControlPhraseError):
        mgr.enable_demo_trading("WRONG PHRASE")

    # Enabling with correct phrase succeeds in fake mode
    enable_res = mgr.enable_demo_trading("ENABLE DEMO XAUUSD TRADING")
    assert enable_res["status"] == "success"
    assert enable_res["trading_enabled"] is True

    # Disable trading succeeds
    dis_res = mgr.disable_trading()
    assert dis_res["status"] == "success"
    assert dis_res["trading_enabled"] is False
