import random
from uuid import uuid4
from datetime import datetime, timezone
from decimal import Decimal
from typing import Dict, Any, Tuple
from sqlalchemy.orm import Session
from src.database.models import CampaignModel, SignalModel, AppSettingModel
from src.domain.schemas import AppSettingsDTO
from src.campaigns.constants import STATE_WAITING_FOR_TP, STATE_AWAITING_CONFIRMATION

class CampaignFactory:
    @staticmethod
    def generate_campaign_code(db: Session) -> str:
        date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
        for _ in range(10):
            suffix = str(uuid4())[:6].upper()
            code = f"GOLD-{date_str}-{suffix}"
            if not db.query(CampaignModel).filter(CampaignModel.campaign_code == code).first():
                return code
        return f"GOLD-{date_str}-{str(uuid4())[:8].upper()}"

    @staticmethod
    def generate_magic_number(db: Session) -> int:
        for _ in range(100):
            magic = random.randint(100000, 999999)
            if not db.query(CampaignModel).filter(CampaignModel.magic_number == magic).first():
                return magic
        return random.randint(1000000, 9999999)

    @classmethod
    def create_campaign_from_signal(
        cls,
        db: Session,
        signal_rec: SignalModel,
        settings: AppSettingsDTO,
        parent_campaign_id: str = None,
        reentry_sequence: int = 0
    ) -> Tuple[CampaignModel, str]:
        """
        Creates CampaignModel from signal.
        Returns (campaign_model, initial_state)
        """
        # Determine initial state: WAITING_FOR_TP if TP1 or TP2 missing, else AWAITING_CONFIRMATION
        is_missing_tp = (signal_rec.tp1 is None) or (signal_rec.tp2 is None)
        initial_state = STATE_WAITING_FOR_TP if is_missing_tp else STATE_AWAITING_CONFIRMATION

        entry_count = settings.entry_count
        lot_per_entry = float(settings.lot_per_entry)
        max_exposure = float(settings.max_exposure_lots)
        requested_total_lots = float(Decimal(str(entry_count)) * Decimal(str(lot_per_entry)))

        if requested_total_lots > max_exposure:
            raise ValueError(f"Requested total lots ({requested_total_lots:.2f}) exceeds maximum exposure cap ({max_exposure:.2f})")

        campaign_id = str(uuid4())
        campaign_code = cls.generate_campaign_code(db)
        magic_number = cls.generate_magic_number(db)
        now_utc = datetime.now(timezone.utc)

        campaign = CampaignModel(
            id=campaign_id,
            campaign_code=campaign_code,
            signal_id=signal_rec.id,
            parent_campaign_id=parent_campaign_id,
            reentry_sequence=reentry_sequence,
            magic_number=magic_number,
            current_state=initial_state,
            execution_mode=settings.execution_mode,
            entry_count=entry_count,
            lot_per_entry=lot_per_entry,
            total_volume=requested_total_lots,
            maximum_total_lots=max_exposure,
            requested_total_lots=requested_total_lots,
            current_stop_loss=signal_rec.stop_loss,
            tp1=signal_rec.tp1,
            tp2=signal_rec.tp2,
            has_tp_open=signal_rec.has_tp_open,
            version=1,
            created_at=now_utc,
            updated_at=now_utc
        )

        return campaign, initial_state
