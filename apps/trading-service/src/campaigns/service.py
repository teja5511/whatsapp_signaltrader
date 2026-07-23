import json
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any, Tuple
from src.database.engine import SessionLocal
from src.database.unit_of_work import UnitOfWork
from src.database.models import (
    CampaignModel, WhatsAppMessageModel, ParsedMessageModel, SignalModel,
    CampaignStateTransitionModel, DuplicateKeyModel, CommandModel
)
from src.database.repository import SettingsRepository
from src.campaigns.constants import (
    STATE_RECEIVED, STATE_PARSED, STATE_WAITING_FOR_TP, STATE_AWAITING_CONFIRMATION,
    STATE_PLANNED, STATE_REJECTED, STATE_CANCELLED, STATE_FAILED,
    REASON_SIGNAL_RECEIVED, REASON_USER_APPROVED, REASON_USER_REJECTED,
    REASON_EXPLICIT_REENTRY_CREATED, TRIGGER_WHATSAPP_MESSAGE, TRIGGER_USER_ACTION
)
from src.campaigns.errors import CampaignNotFoundError, ConcurrencyConflictError, InvalidStateTransitionError
from src.campaigns.state_machine import validate_state_transition
from src.campaigns.campaign_factory import CampaignFactory
from src.campaigns.duplicate_service import DuplicateProtectionService
from src.campaigns.matching import CampaignMatcher
from src.campaigns.command_attachment import handle_command_attachment

class CampaignService:
    def __init__(self, session_factory=SessionLocal):
        self.session_factory = session_factory

    def get_campaign(self, campaign_id: str) -> Optional[Dict[str, Any]]:
        with UnitOfWork(session_factory=self.session_factory) as uow:
            c = uow.campaigns.get_by_id(campaign_id)
            if not c:
                return None
            return self._to_campaign_dict(c)

    def list_campaigns(self, limit: int = 50) -> List[Dict[str, Any]]:
        with UnitOfWork(session_factory=self.session_factory) as uow:
            campaigns = uow.campaigns.list_all(limit=limit)
            return [self._to_campaign_dict(c) for c in campaigns]

    def create_campaign_from_message(
        self,
        raw_message_id: str,
        correlation_id: Optional[str] = None
    ) -> Tuple[Dict[str, Any], bool]:
        with UnitOfWork(session_factory=self.session_factory) as uow:
            raw_msg = uow.db.get(WhatsAppMessageModel, raw_message_id)
            if not raw_msg or not raw_msg.parsed_message or not raw_msg.parsed_message.signal:
                raise ValueError(f"Message '{raw_message_id}' does not contain a valid parsed signal.")

            parsed_msg = raw_msg.parsed_message
            sig_rec = parsed_msg.signal

            # Generate Semantic Fingerprint
            sem_fp = DuplicateProtectionService.generate_semantic_fingerprint(
                instrument=sig_rec.symbol or "XAUUSD",
                direction=sig_rec.direction,
                order_intent="LIMIT",
                zone_low=str(sig_rec.entry_min),
                zone_high=str(sig_rec.entry_max),
                stop_loss=str(sig_rec.stop_loss) if sig_rec.stop_loss else None,
                tp1=str(sig_rec.tp1) if sig_rec.tp1 else None,
                tp2=str(sig_rec.tp2) if sig_rec.tp2 else None,
                tp_open_present=sig_rec.has_tp_open,
                group_id=raw_msg.group_id,
                sender_id=raw_msg.sender_id
            )

            # Check Duplicate Protection
            dedup_service = DuplicateProtectionService()
            dup_code, dup_camp_id = dedup_service.check_duplicate(
                db=uow.db,
                group_id=raw_msg.group_id,
                message_id=raw_message_id,
                semantic_fingerprint=sem_fp
            )
            if dup_code != "NOT_DUPLICATE" and sig_rec.campaign:
                return self._to_campaign_dict(sig_rec.campaign), True

            # Get Settings
            settings_repo = SettingsRepository(uow.db)
            app_settings = settings_repo.get_settings()

            # Create Campaign Model via Factory
            campaign, initial_state = CampaignFactory.create_campaign_from_signal(
                db=uow.db,
                signal_rec=sig_rec,
                settings=app_settings,
                parent_campaign_id=None,
                reentry_sequence=0
            )

            uow.campaigns.create_campaign(campaign)
            uow.db.flush()

            # Log Initial Transitions
            now_utc = datetime.now(timezone.utc)
            t1 = CampaignStateTransitionModel(
                campaign_id=campaign.id,
                from_state=STATE_RECEIVED,
                to_state=STATE_PARSED,
                reason_code=REASON_SIGNAL_RECEIVED,
                reason="Raw WhatsApp message parsed into valid signal DTO",
                trigger_type=TRIGGER_WHATSAPP_MESSAGE,
                trigger_reference_id=raw_message_id,
                correlation_id=correlation_id,
                transitioned_at=now_utc
            )

            t2 = CampaignStateTransitionModel(
                campaign_id=campaign.id,
                from_state=STATE_PARSED,
                to_state=initial_state,
                reason_code=REASON_SIGNAL_RECEIVED,
                reason=f"Campaign initialized in state {initial_state}",
                trigger_type=TRIGGER_WHATSAPP_MESSAGE,
                trigger_reference_id=raw_message_id,
                correlation_id=correlation_id,
                transitioned_at=now_utc
            )
            uow.db.add_all([t1, t2])

            # Register Duplicate Keys
            dedup_service.register_duplicate_keys(
                db=uow.db,
                group_id=raw_msg.group_id,
                message_id=raw_message_id,
                semantic_fingerprint=sem_fp
            )

            uow.audit.log_event("CAMPAIGN_CREATED", {
                "campaign_id": campaign.id,
                "campaign_code": campaign.campaign_code,
                "initial_state": initial_state,
                "entry_count": campaign.entry_count,
                "requested_total_lots": campaign.requested_total_lots
            })

            return self._to_campaign_dict(campaign), False

    def approve_campaign(
        self,
        campaign_id: str,
        expected_version: int,
        correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        with UnitOfWork(session_factory=self.session_factory) as uow:
            campaign = uow.campaigns.get_by_id(campaign_id)
            if not campaign:
                raise CampaignNotFoundError(campaign_id)

            if campaign.version != expected_version:
                raise ConcurrencyConflictError(campaign_id, expected_version, campaign.version)

            validate_state_transition(campaign.current_state, STATE_PLANNED)

            prev_state = campaign.current_state
            campaign.current_state = STATE_PLANNED
            campaign.version += 1
            now_utc = datetime.now(timezone.utc)

            uow.db.add(CampaignStateTransitionModel(
                campaign_id=campaign.id,
                from_state=prev_state,
                to_state=STATE_PLANNED,
                reason_code=REASON_USER_APPROVED,
                reason="User explicitly approved campaign via UI confirmation workflow",
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
        expected_version: int,
        reason: str = "Rejected by user",
        correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        with UnitOfWork(session_factory=self.session_factory) as uow:
            campaign = uow.campaigns.get_by_id(campaign_id)
            if not campaign:
                raise CampaignNotFoundError(campaign_id)

            if campaign.version != expected_version:
                raise ConcurrencyConflictError(campaign_id, expected_version, campaign.version)

            validate_state_transition(campaign.current_state, STATE_REJECTED)

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

                return {
                    "type": "REENTRY",
                    "status": "reentry_created",
                    "child_campaign_id": child_campaign.id,
                    "child_campaign": self._to_campaign_dict(child_campaign)
                }

            # Standard Follow-Up Command Attachment
            cmd_rec, transition_rec = handle_command_attachment(
                db=uow.db,
                campaign=matched_campaign,
                raw_message_id=raw_message_id,
                command_payload=cmd_payload
            )

            uow.db.add(cmd_rec)
            if transition_rec:
                uow.db.add(transition_rec)

            uow.audit.log_event("COMMAND_ATTACHED", {
                "campaign_id": matched_campaign.id,
                "command_type": cmd_type,
                "raw_message_id": raw_message_id
            })

            return {"type": "FOLLOW_UP_COMMAND", "status": "attached", "campaign_id": matched_campaign.id}

    def get_campaign_transitions(self, campaign_id: str) -> List[Dict[str, Any]]:
        with UnitOfWork(session_factory=self.session_factory) as uow:
            transitions = (
                uow.db.query(CampaignStateTransitionModel)
                .filter(CampaignStateTransitionModel.campaign_id == campaign_id)
                .order_by(CampaignStateTransitionModel.transitioned_at.asc())
                .all()
            )
            return [
                {
                    "id": t.id,
                    "campaign_id": t.campaign_id,
                    "from_state": t.from_state,
                    "to_state": t.to_state,
                    "reason_code": t.reason_code,
                    "reason": t.reason,
                    "trigger_type": t.trigger_type,
                    "trigger_reference_id": t.trigger_reference_id,
                    "correlation_id": t.correlation_id,
                    "transitioned_at": t.transitioned_at.isoformat()
                }
                for t in transitions
            ]

    def get_campaign_commands(self, campaign_id: str) -> List[Dict[str, Any]]:
        with UnitOfWork(session_factory=self.session_factory) as uow:
            cmds = (
                uow.db.query(CommandModel)
                .filter(CommandModel.campaign_id == campaign_id)
                .order_by(CommandModel.executed_at.asc())
                .all()
            )
            return [
                {
                    "id": c.id,
                    "campaign_id": c.campaign_id,
                    "raw_message_id": c.raw_message_id,
                    "command_type": c.command_type,
                    "parameters": json.loads(c.parameters_json),
                    "executed_at": c.executed_at.isoformat()
                }
                for c in cmds
            ]

    def _to_campaign_dict(self, c: CampaignModel) -> Dict[str, Any]:
        return {
            "id": c.id,
            "campaign_code": c.campaign_code,
            "signal_id": c.signal_id,
            "parent_campaign_id": c.parent_campaign_id,
            "reentry_sequence": c.reentry_sequence,
            "magic_number": c.magic_number,
            "current_state": c.current_state,
            "execution_mode": c.execution_mode.value if hasattr(c.execution_mode, "value") else str(c.execution_mode),
            "entry_count": c.entry_count,
            "lot_per_entry": c.lot_per_entry,
            "total_volume": c.total_volume,
            "maximum_total_lots": c.maximum_total_lots,
            "requested_total_lots": c.requested_total_lots,
            "current_stop_loss": c.current_stop_loss,
            "tp1": c.tp1,
            "tp2": c.tp2,
            "has_tp_open": c.has_tp_open,
            "version": c.version,
            "trading_enabled": False,
            "execution_performed": False,
            "created_at": c.created_at.isoformat(),
            "updated_at": c.updated_at.isoformat()
        }
