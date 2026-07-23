from dataclasses import dataclass
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from src.database.models import WhatsAppMessageModel, ParsedMessageModel, SignalModel, CampaignModel
from src.campaigns.constants import ACTIVE_CAMPAIGN_STATES, TERMINAL_STATES

@dataclass
class CampaignMatchResult:
    campaign_id: Optional[str]
    campaign_code: Optional[str]
    match_type: str  # MATCHED_BY_QUOTE, MATCHED_BY_SIGNAL_MESSAGE, MATCHED_LATEST_COMPATIBLE, MATCH_AMBIGUOUS, NO_MATCH
    candidate_count: int
    reason: str

class CampaignMatcher:
    @staticmethod
    def match_campaign_for_command(
        db: Session,
        group_id: str,
        command_type: str,
        quoted_message_id: Optional[str] = None,
        is_reply: bool = False
    ) -> CampaignMatchResult:
        # 1. Direct Quoted Message Match
        if is_reply and quoted_message_id:
            raw_quoted = db.get(WhatsAppMessageModel, quoted_message_id)
            if raw_quoted and raw_quoted.parsed_message and raw_quoted.parsed_message.signal:
                sig = raw_quoted.parsed_message.signal
                if sig.campaign:
                    return CampaignMatchResult(
                        campaign_id=sig.campaign.id,
                        campaign_code=sig.campaign.campaign_code,
                        match_type="MATCHED_BY_QUOTE",
                        candidate_count=1,
                        reason=f"Matched campaign directly via quoted message ID '{quoted_message_id}'"
                    )

        # 2. Latest Compatible Active Campaign
        active_campaigns = (
            db.query(CampaignModel)
            .join(CampaignModel.signal)
            .join(SignalModel.parsed_message)
            .join(ParsedMessageModel.raw_message)
            .filter(WhatsAppMessageModel.group_id == group_id)
            .filter(CampaignModel.current_state.in_(ACTIVE_CAMPAIGN_STATES))
            .order_by(CampaignModel.created_at.desc())
            .all()
        )

        if not active_campaigns:
            return CampaignMatchResult(
                campaign_id=None,
                campaign_code=None,
                match_type="NO_MATCH",
                candidate_count=0,
                reason="No active compatible campaign found in target group"
            )

        if command_type == "ADD_TAKE_PROFIT":
            # Prefer campaign in WAITING_FOR_TP state
            waiting_tp = [c for c in active_campaigns if c.current_state == "WAITING_FOR_TP"]
            if len(waiting_tp) >= 1:
                return CampaignMatchResult(
                    campaign_id=waiting_tp[0].id,
                    campaign_code=waiting_tp[0].campaign_code,
                    match_type="MATCHED_LATEST_COMPATIBLE",
                    candidate_count=len(waiting_tp),
                    reason="Matched latest active campaign in WAITING_FOR_TP state"
                )

        if len(active_campaigns) == 1:
            latest = active_campaigns[0]
            return CampaignMatchResult(
                campaign_id=latest.id,
                campaign_code=latest.campaign_code,
                match_type="MATCHED_LATEST_COMPATIBLE",
                candidate_count=1,
                reason="Matched latest active compatible campaign"
            )

        # Multiple active campaigns exist without explicit quote reference
        return CampaignMatchResult(
            campaign_id=active_campaigns[0].id, # Default to latest for compatible commands
            campaign_code=active_campaigns[0].campaign_code,
            match_type="MATCHED_LATEST_COMPATIBLE",
            candidate_count=len(active_campaigns),
            reason=f"Matched latest compatible active campaign out of {len(active_campaigns)} active candidates"
        )
