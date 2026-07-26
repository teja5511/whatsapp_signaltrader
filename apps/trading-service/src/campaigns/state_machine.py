from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from src.campaigns.constants import ALLOWED_TRANSITIONS, TERMINAL_STATES, TRIGGER_SYSTEM
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
                from_state, to_state, f"Transition from '{from_state}' to '{to_state}' is not allowed."
            )

    @staticmethod
    def is_valid_transition(from_state: str, to_state: str) -> bool:
        try:
            CampaignStateMachine.validate_transition(from_state, to_state)
            return True
        except InvalidStateTransitionError:
            return False


def validate_state_transition(from_state: str, to_state: str) -> None:
    CampaignStateMachine.validate_transition(from_state, to_state)


def apply_transition(
    db: Session,
    campaign,
    to_state: str,
    reason_code: str,
    reason: str,
    trigger_type: str = TRIGGER_SYSTEM,
    trigger_reference_id: Optional[str] = None,
    correlation_id: Optional[str] = None,
    triggered_by: str = "SYSTEM",
    bump_version: bool = True,
) -> bool:
    """The single supported way to change a campaign's state.

    Validates against the transition matrix, writes the audit row and bumps the
    optimistic-concurrency version. Returns False when the campaign is already
    in ``to_state`` (idempotent no-op); raises on a forbidden transition.
    """
    # Imported here to avoid a circular import at module load.
    from src.database.models import CampaignStateTransitionModel

    previous = campaign.current_state
    if previous == to_state:
        return False

    CampaignStateMachine.validate_transition(previous, to_state)

    campaign.current_state = to_state
    if bump_version:
        campaign.version += 1

    now_utc = datetime.now(timezone.utc)
    campaign.updated_at = now_utc

    db.add(CampaignStateTransitionModel(
        campaign_id=campaign.id,
        from_state=previous,
        to_state=to_state,
        reason_code=reason_code,
        reason=reason,
        triggered_by=triggered_by,
        trigger_type=trigger_type,
        trigger_reference_id=trigger_reference_id,
        correlation_id=correlation_id,
        transitioned_at=now_utc,
    ))
    db.flush()
    return True
