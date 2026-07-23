import json
from uuid import uuid4
from datetime import datetime, timezone
from typing import Dict, Any, Tuple, Optional
from sqlalchemy.orm import Session
from src.database.models import CampaignModel, CommandModel, CampaignStateTransitionModel
from src.campaigns.constants import (
    STATE_WAITING_FOR_TP, STATE_AWAITING_CONFIRMATION, STATE_CANCELLED,
    REASON_TP_UPDATE_RECEIVED, REASON_SIGNAL_COMPLETE, REASON_ADMIN_CLOSE_REQUESTED,
    REASON_ADMIN_CANCELLED, REASON_ZONE_VALID_RECEIVED, TRIGGER_WHATSAPP_MESSAGE
)

class CommandAttachmentHandler:
    @staticmethod
    def process_command(
        db: Session,
        campaign: CampaignModel,
        raw_message_id: str,
        command_type: str,
        command_payload: Dict[str, Any]
    ) -> Tuple[str, bool]:
        """
        Attaches parsed command to campaign and applies state transitions if applicable.
        Returns (result_description, state_changed)
        """
        now_utc = datetime.now(timezone.utc)
        state_changed = False
        description = f"Attached command '{command_type}' to campaign '{campaign.campaign_code}'"

        # Apply Command Logic
        if command_type == "MODIFY_STOP_LOSS":
            if command_payload.get("value"):
                new_sl = float(command_payload["value"])
                campaign.current_stop_loss = new_sl
                campaign.version += 1
                description = f"Updated stop loss for campaign '{campaign.campaign_code}' to {new_sl:.2f}"

        elif command_type == "ADD_TAKE_PROFIT":
            if command_payload.get("value"):
                new_tp = float(command_payload["value"])
                slot = command_payload.get("targetTpSlot")

                if slot == "TP1" or (campaign.tp1 is None and slot != "TP2"):
                    campaign.tp1 = new_tp
                elif slot == "TP2" or campaign.tp2 is None:
                    campaign.tp2 = new_tp

                campaign.version += 1
                description = f"Updated TP targets for campaign '{campaign.campaign_code}'"

                # Check if TP targets are now complete -> Transition WAITING_FOR_TP to AWAITING_CONFIRMATION
                if campaign.current_state == STATE_WAITING_FOR_TP and campaign.tp1 is not None and campaign.tp2 is not None:
                    campaign.current_state = STATE_AWAITING_CONFIRMATION
                    state_changed = True
                    db.add(CampaignStateTransitionModel(
                        campaign_id=campaign.id,
                        from_state=STATE_WAITING_FOR_TP,
                        to_state=STATE_AWAITING_CONFIRMATION,
                        reason_code=REASON_SIGNAL_COMPLETE,
                        reason="Delayed TP target received; signal is now complete",
                        trigger_type=TRIGGER_WHATSAPP_MESSAGE,
                        trigger_reference_id=raw_message_id,
                        transitioned_at=now_utc
                    ))

        elif command_type in ("CLOSE_CAMPAIGN", "CANCEL_SIGNAL"):
            if campaign.current_state not in (STATE_CANCELLED, "CLOSED"):
                prev_state = campaign.current_state
                campaign.current_state = STATE_CANCELLED
                campaign.version += 1
                state_changed = True
                db.add(CampaignStateTransitionModel(
                    campaign_id=campaign.id,
                    from_state=prev_state,
                    to_state=STATE_CANCELLED,
                    reason_code=REASON_ADMIN_CLOSE_REQUESTED if command_type == "CLOSE_CAMPAIGN" else REASON_ADMIN_CANCELLED,
                    reason=f"Admin command '{command_type}' cancelled active campaign",
                    trigger_type=TRIGGER_WHATSAPP_MESSAGE,
                    trigger_reference_id=raw_message_id,
                    transitioned_at=now_utc
                ))

        return description, state_changed

def handle_command_attachment(
    db: Session,
    campaign: CampaignModel,
    raw_message_id: str,
    command_payload: Dict[str, Any]
) -> Tuple[CommandModel, Optional[CampaignStateTransitionModel]]:
    cmd_type = command_payload.get("commandType", "UNKNOWN")
    CommandAttachmentHandler.process_command(
        db=db,
        campaign=campaign,
        raw_message_id=raw_message_id,
        command_type=cmd_type,
        command_payload=command_payload
    )
    now_utc = datetime.now(timezone.utc)
    cmd_rec = CommandModel(
        id=str(uuid4()),
        campaign_id=campaign.id,
        raw_message_id=raw_message_id,
        command_type=cmd_type,
        parameters_json=json.dumps(command_payload),
        executed_at=now_utc
    )
    return cmd_rec, None
