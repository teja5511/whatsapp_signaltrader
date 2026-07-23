import pytest
from src.campaigns.state_machine import CampaignStateMachine
from src.campaigns.errors import InvalidStateTransitionError

def test_allowed_transitions():
    assert CampaignStateMachine.is_valid_transition("RECEIVED", "PARSED") is True
    assert CampaignStateMachine.is_valid_transition("PARSED", "WAITING_FOR_TP") is True
    assert CampaignStateMachine.is_valid_transition("PARSED", "AWAITING_CONFIRMATION") is True
    assert CampaignStateMachine.is_valid_transition("AWAITING_CONFIRMATION", "PLANNED") is True
    assert CampaignStateMachine.is_valid_transition("AWAITING_CONFIRMATION", "REJECTED") is True
    assert CampaignStateMachine.is_valid_transition("WAITING_FOR_TP", "CANCELLED") is True

def test_forbidden_transitions():
    forbidden_pairs = [
        ("RECEIVED", "OPEN"),
        ("PARSED", "PENDING"),
        ("WAITING_FOR_TP", "OPEN"),
        ("AWAITING_CONFIRMATION", "OPEN"),
        ("PLANNED", "OPEN"),
        ("CANCELLED", "OPEN"),
        ("REJECTED", "PLANNED"),
        ("CLOSED", "OPEN")
    ]
    for from_state, to_state in forbidden_pairs:
        assert CampaignStateMachine.is_valid_transition(from_state, to_state) is False
        with pytest.raises(InvalidStateTransitionError):
            CampaignStateMachine.validate_transition(from_state, to_state)
