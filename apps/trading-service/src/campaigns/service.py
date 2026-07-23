import json
from datetime import datetime, timezone
from typing import Dict, Any, Tuple, Optional, List
from src.database.engine import SessionLocal
from src.database.unit_of_work import UnitOfWork
from src.database.repository import SettingsRepository
from src.database.models import (
    WhatsAppMessageModel, ParsedMessageModel, SignalModel, CampaignModel,
    CampaignStateTransitionModel, DuplicateKeyModel, CommandModel
)
from src.campaigns.constants import (
    STATE_RECEIVED, STATE_PARSED, STATE_WAITING_FOR_TP, STATE_AWAITING_CONFIRMATION,
    STATE_PLANNED, STATE_REJECTED, STATE_CANCELLED, REASON_SIGNAL_RECEIVED,
    REASON_SIGNAL_PARSED, REASON_SIGNAL_COMPLETE, REASON_MISSING_TAKE_PROFIT,
    REASON_USER_APPROVED, REASON_USER_REJECTED, REASON_EXPLICIT_REENTRY_CREATED,
    TRIGGER_WHATSAPP_MESSAGE, TRIGGER_USER_ACTION
)
from src.campaigns.errors import (
    CampaignNotFoundError, InvalidStateTransitionError, DuplicateCampaignError, ConcurrencyConflictError
)
from src.campaigns.state_machine import CampaignStateMachine
from src.campaigns.duplicate_service import DuplicateProtectionService
from src.campaigns.campaign_factory import CampaignFactory
from src.campaigns.matching import CampaignMatcher
from src.campaigns.command_attachment import CommandAttachmentHandler

class CampaignService:
    def __init__(self, session_factory=SessionLocal):
        self.session_factory = session_factory
        self.duplicate_protection = DuplicateProtectionService()

    def create_campaign_from_message(
        self,
        raw_message_id: str,
        correlation_id: Optional[str] = None
    ) -> Tuple[Dict[str, Any], bool]:
        """
        Creates a campaign from a persisted parsed message.
        Returns (campaign_dict, is_duplicate)
        """
        with UnitOfWork(session_factory=self.session_factory) as uow:
            raw_msg = uow.db.get(WhatsAppMessageModel, raw_message_id)
            if not raw_msg or not raw_msg.parsed_message:
                raise ValueError(f"Raw message '{raw_message_id}' or parsed payload not found.")

            parsed_msg = raw_msg.parsed_message
            if parsed_msg.message_type != "NEW_SIGNAL" or not parsed_msg.signal:
                raise ValueError(f"Message '{raw_message_id}' is not a valid NEW_SIGNAL.")

            sig_rec = parsed_msg.signal

            # If campaign already created for this signal, return existing
            if sig_rec.campaign:
                return self._to_campaign_dict(sig_rec.campaign), True

            # Extract parser result JSON for semantic fingerprint
            parsed_data = json.loads(parsed_msg.parsed_json)
            sig_payload = parsed_data.get("signal", {})

            semantic_fp = self.duplicate_protection.generate_semantic_fingerprint(
                instrument=sig_payload.get("instrument", "XAUUSD"),
                direction=sig_payload.get("direction", "BUY"),
                order_intent=sig_payload.get("orderIntent", "UNSPECIFIED"),
                zone_low=sig_payload.get("zoneLow", "0.0"),
                zone_high=sig_payload.get("zoneHigh", "0.0"),
                stop_loss=sig_payload.get("stopLoss"),
                tp1=sig_payload.get("tp1"),
                tp2=sig_payload.get("tp2"),
                tp_open_present=sig_payload.get("tpOpenPresent", False),
                group_id=raw_msg.group_id,
                sender_id=raw_msg.sender_id
            )

            # Check Duplicates
            settings_repo = SettingsRepository(uow.db)
            app_settings = settings_repo.get_settings()

            dup_decision, existing_campaign_id = self.duplicate_protection.check_duplicate(
                db=uow.db,
                group_id=raw_msg.group_id,
                message_id=raw_message_id,
                semantic_fingerprint=semantic_fp,
                duplicate_window_hours=24
            )

            if dup_decision in ("EXACT_DUPLICATE", "SEMANTIC_DUPLICATE") and existing_campaign_id:
                existing_camp = uow.db.get(CampaignModel, existing_campaign_id)
                if existing_camp:
                    return self._to_campaign_dict(existing_camp), True

            # Create Campaign via Factory
            campaign, initial_state = CampaignFactory.create_campaign_from_signal(
                db=uow.db,
                signal_rec=sig_rec,
                settings=app_settings
            )

            uow.db.add(campaign)
            uow.db.flush()

            # Record State Transitions
            now_utc = datetime.now(timezone.utc)
            uow.db.add(CampaignStateTransitionModel(
                campaign_id=campaign.id,
                from_state=STATE_RECEIVED,
                to_state=STATE_PARSED,
                reason_code=REASON_SIGNAL_PARSED,
                reason="Signal parsed successfully by deterministic engine",
                trigger_type=TRIGGER_WHATSAPP_MESSAGE,
                trigger_reference_id=raw_message_id,
                correlation_id=correlation_id,
                transitioned_at=now_utc
            ))

            uow.db.add(CampaignStateTransitionModel(
                campaign_id=campaign.id,
                from_state=STATE_PARSED,
                to_state=initial_state,
                reason_code=REASON_MISSING_TAKE_PROFIT if initial_state == STATE_WAITING_FOR_TP else REASON_SIGNAL_COMPLETE,
                reason="Initial campaign state assigned based on TP availability",
                trigger_type=TRIGGER_WHATSAPP_MESSAGE,
                trigger_reference_id=raw_message_id,
                correlation_id=correlation_id,
                transitioned_at=now_utc
            ))

            # Register Duplicate Keys
            self.duplicate_protection.register_duplicate_keys(
                db=uow.db,
                group_id=raw_msg.group_id,
                message_id=raw_message_id,
                semantic_fingerprint=semantic_fp,
                duplicate_window_hours=24
            )

            # Log Audit Event
            uow.audit.log_event("CAMPAIGN_CREATED", {
                "campaign_id": campaign.id,
                "campaign_code": campaign.campaign_code,
                "initial_state": initial_state,
                "message_id": raw_message_id
            })

            return self._to_campaign_dict(campaign), False

    def approve_campaign(
        self,
        campaign_id: str,
        expected_version: int = 1,
        correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        with UnitOfWork(session_factory=self.session_factory) as uow:
            campaign = uow.db.get(CampaignModel, campaign_id)
            if not campaign:
                raise CampaignNotFoundError(campaign_id)

            # Optimistic Concurrency Check
            if campaign.version != expected_version:
                raise ConcurrencyConflictError(campaign_id, expected_version)

            # State Transition Validation
            CampaignStateMachine.validate_transition(campaign.current_state, STATE_PLANNED)

            prev_state = campaign.current_state
            campaign.current_state = STATE_PLANNED
            campaign.version += 1
            now_utc = datetime.now(timezone.utc)

            uow.db.add(CampaignStateTransitionModel(
                campaign_id=campaign.id,
                from_state=prev_state,
                to_state=STATE_PLANNED,
                reason_code=REASON_USER_APPROVED,
                reason="User explicitly approved trade campaign execution",
                trigger_type=TRIGGER_USER_ACTION,
                correlation_id=correlation_id,
                transitioned_at=now_utc
            ))

            uow.audit.log_event("CAMPAIGN_APPROVED", {
                "campaign_id": campaign.id,
                "campaign_code": campaign.campaign_code,
                "new_version": campaign.version
            })

            return self._to_campaign_dict(campaign)

    def reject_campaign(
        self,
        campaign_id: str,
        reason: str = "User rejected campaign",
        expected_version: int = 1,
        correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        with UnitOfWork(session_factory=self.session_factory) as uow:
            campaign = uow.db.get(CampaignModel, campaign_id)
            if not campaign:
                raise CampaignNotFoundError(campaign_id)

            if campaign.version != expected_version:
                raise ConcurrencyConflictError(campaign_id, expected_version)

            CampaignStateMachine.validate_transition(campaign.current_state, STATE_REJECTED)

            prev_state = campaign.current_state
            campaign.current_state = STATE_REJECTED
            campaign.version += 1
            now_utc = datetime.now(timezone.utc)

            uow.db.add(CampaignStateTransitionModel(
                campaign_id=campaign.id,
                from_state=prev_state,
                to_state=STATE_REJECTED,
                reason_code=REASON_USER_REJECTED,
                reason=reason,
                trigger_type=TRIGGER_USER_ACTION,
                correlation_id=correlation_id,
                transitioned_at=now_utc
            ))

            uow.audit.log_event("CAMPAIGN_REJECTED", {
                "campaign_id": campaign.id,
                "campaign_code": campaign.campaign_code,
                "reason": reason
            })

            return self._to_campaign_dict(campaign)

    def process_message(self, raw_message_id: str) -> Dict[str, Any]:
        with UnitOfWork(session_factory=self.session_factory) as uow:
            raw_msg = uow.db.get(WhatsAppMessageModel, raw_message_id)
            if not raw_msg or not raw_msg.parsed_message:
                raise ValueError(f"Message '{raw_message_id}' or parsed payload not found.")

            parsed_msg = raw_msg.parsed_message
            if parsed_msg.message_type == "NEW_SIGNAL":
                result, _ = self.create_campaign_from_message(raw_message_id)
                return {"type": "NEW_SIGNAL", "campaign": result}

            parsed_data = json.loads(parsed_msg.parsed_json)
            cmd_payload = parsed_data.get("command") or {}
            cmd_type = cmd_payload.get("commandType")

            if not cmd_type:
                return {"type": "OTHER", "status": "no_action_required", "category": parsed_msg.message_type}

            # Match active campaign
            match_res = CampaignMatcher.match_campaign_for_command(
                db=uow.db,
                group_id=raw_msg.group_id,
                command_type=cmd_type,
                quoted_message_id=parsed_data.get("sourceMetadata", {}).get("quotedMessageId"),
                is_reply=parsed_data.get("sourceMetadata", {}).get("isReply", False)
            )

            if not match_res.campaign_id:
                uow.audit.log_event("COMMAND_MATCH_FAILED", {
                    "raw_message_id": raw_message_id,
                    "command_type": cmd_type,
                    "reason": match_res.reason
                })
                return {"type": "FOLLOW_UP_COMMAND", "status": "no_campaign_matched", "reason": match_res.reason}

            matched_campaign = uow.db.get(CampaignModel, match_res.campaign_id)
            if not matched_campaign:
                return {"type": "FOLLOW_UP_COMMAND", "status": "campaign_not_found"}

            # Re-entry Special Case
            if cmd_type == "REENTRY":
                # Create linked child campaign
                settings_repo = SettingsRepository(uow.db)
                app_settings = settings_repo.get_settings()

                child_campaign, initial_state = CampaignFactory.create_campaign_from_signal(
                    db=uow.db,
                    signal_rec=matched_campaign.signal,
                    settings=app_settings,
                    parent_campaign_id=matched_campaign.id,
                    reentry_sequence=matched_campaign.reentry_sequence + 1
                )
                uow.db.add(child_campaign)
                uow.db.flush()

                now_utc = datetime.now(timezone.utc)
                uow.db.add(CampaignStateTransitionModel(
                    campaign_id=child_campaign.id,
                    from_state=STATE_RECEIVED,
                    to_state=initial_state,
                    reason_code=REASON_EXPLICIT_REENTRY_CREATED,
                    reason=f"Explicit re-entry campaign created from parent '{matched_campaign.campaign_code}'",
                    trigger_type=TRIGGER_WHATSAPP_MESSAGE,
                    trigger_reference_id=raw_message_id,
                    transitioned_at=now_utc
                ))

                uow.audit.log_event("EXPLICIT_REENTRY_CREATED", {
                    "parent_campaign_id": matched_campaign.id,
                    "child_campaign_id": child_campaign.id,
                    "child_code": child_campaign.campaign_code
                })

                return {"type": "REENTRY", "status": "reentry_created", "child_campaign": self._to_campaign_dict(child_campaign)}

            # Attach Command
            desc, state_changed = CommandAttachmentHandler.process_command(
                db=uow.db,
                campaign=matched_campaign,
                raw_message_id=raw_message_id,
                command_type=cmd_type,
                command_payload=cmd_payload
            )

            uow.audit.log_event("COMMAND_ATTACHED", {
                "campaign_id": matched_campaign.id,
                "command_type": cmd_type,
                "description": desc
            })

            return {
                "type": "FOLLOW_UP_COMMAND",
                "status": "attached",
                "campaign_id": matched_campaign.id,
                "campaign_code": matched_campaign.campaign_code,
                "current_state": matched_campaign.current_state,
                "description": desc
            }

    def _to_campaign_dict(self, campaign: CampaignModel) -> Dict[str, Any]:
        return {
            "id": campaign.id,
            "campaign_code": campaign.campaign_code,
            "signal_id": campaign.signal_id,
            "parent_campaign_id": campaign.parent_campaign_id,
            "reentry_sequence": campaign.reentry_sequence,
            "magic_number": campaign.magic_number,
            "current_state": campaign.current_state,
            "execution_mode": campaign.execution_mode,
            "entry_count": campaign.entry_count,
            "lot_per_entry": campaign.lot_per_entry,
            "total_volume": campaign.total_volume,
            "maximum_total_lots": campaign.maximum_total_lots,
            "requested_total_lots": campaign.requested_total_lots,
            "current_stop_loss": campaign.current_stop_loss,
            "tp1": campaign.tp1,
            "tp2": campaign.tp2,
            "has_tp_open": campaign.has_tp_open,
            "version": campaign.version,
            "trading_enabled": False,
            "execution_performed": False,
            "created_at": campaign.created_at.isoformat(),
            "updated_at": campaign.updated_at.isoformat()
        }
