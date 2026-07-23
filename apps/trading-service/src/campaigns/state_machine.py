from typing import Optional
from src.campaigns.constants import ALLOWED_TRANSITIONS, TERMINAL_STATES
from src.campaigns.errors import InvalidStateTransitionError

class CampaignStateMachine:
    @staticmethod
    def validate_transition(from_state: str, to_state: str) -> None:
        """
        Validates if transition from `from_state` to `to_state` is permitted.
        Raises InvalidStateTransitionError if forbidden.
        """
        if from_state in TERMINAL_STATES:
            raise InvalidStateTransitionError(from_state, to_state, "Cannot transition out of a terminal state.")

        allowed = ALLOWED_TRANSITIONS.get(from_state, set())
        if to_state not in allowed:
            raise InvalidStateTransitionError(
                from_state, to_state, f"Transition from '{from_state}' to '{to_state}' is not allowed in Prompt 5."
            )

    @staticmethod
    def is_valid_transition(from_state: str, to_state: str) -> bool:
        try:
            CampaignStateMachine.validate_transition(from_state, to_state)
            return True
        except InvalidStateTransitionError:
            return False
