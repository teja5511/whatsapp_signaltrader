import json
from decimal import Decimal
from typing import Optional, List, Any, Dict
from sqlalchemy.orm import Session
from sqlalchemy import select
from src.database.models import (
    AppSettingModel, WhatsAppMessageModel, DuplicateKeyModel, ParsedMessageModel,
    SignalModel, CampaignModel, CampaignStateTransitionModel, PlannedEntryModel,
    PendingOrderModel, PositionModel, SystemAuditEventModel, SystemErrorModel
)
from src.domain.schemas import AppSettingsDTO

class SettingsRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_settings(self) -> AppSettingsDTO:
        records = self.db.scalars(select(AppSettingModel)).all()
        settings_dict = {}
        for r in records:
            settings_dict[r.key] = r.value

        entry_count = int(settings_dict.get("entry_count", 5))
        lot_per_entry = Decimal(settings_dict.get("lot_per_entry", "0.10"))
        max_exposure_lots = Decimal(settings_dict.get("max_exposure_lots", "2.00"))
        execution_mode = settings_dict.get("execution_mode", "CONFIRMATION")
        target_group_jid = settings_dict.get("target_group_jid")
        admin_sender_jid = settings_dict.get("admin_sender_jid")

        return AppSettingsDTO(
            entry_count=entry_count,
            lot_per_entry=lot_per_entry,
            max_exposure_lots=max_exposure_lots,
            execution_mode=execution_mode,
            target_group_jid=target_group_jid,
            admin_sender_jid=admin_sender_jid
        )

    def set_setting(self, key: str, value: str) -> None:
        setting = self.db.get(AppSettingModel, key)
        if setting:
            setting.value = value
        else:
            setting = AppSettingModel(key=key, value=value)
            self.db.add(setting)

class WhatsAppMessageRepository:
    def __init__(self, db: Session):
        self.db = db

    def is_duplicate(self, dedup_key: str) -> bool:
        return self.db.get(DuplicateKeyModel, dedup_key) is not None

    def add_message(self, msg: WhatsAppMessageModel, dedup_key: str) -> None:
        self.db.add(msg)
        self.db.flush()
        dup = DuplicateKeyModel(dedup_key=dedup_key, message_id=msg.id)
        self.db.add(dup)

class CampaignRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, campaign_id: str) -> Optional[CampaignModel]:
        return self.db.get(CampaignModel, campaign_id)

    def list_all(self, limit: int = 50) -> List[CampaignModel]:
        stmt = select(CampaignModel).order_by(CampaignModel.created_at.desc()).limit(limit)
        return list(self.db.scalars(stmt).all())

    def create_campaign(self, campaign: CampaignModel) -> CampaignModel:
        self.db.add(campaign)
        return campaign

class AuditLogRepository:
    def __init__(self, db: Session):
        self.db = db

    def log_event(self, event_type: str, payload: Dict[str, Any]) -> SystemAuditEventModel:
        event = SystemAuditEventModel(
            event_type=event_type,
            payload_json=json.dumps(payload)
        )
        self.db.add(event)
        return event

    def list_logs(self, limit: int = 50) -> List[SystemAuditEventModel]:
        stmt = select(SystemAuditEventModel).order_by(SystemAuditEventModel.created_at.desc()).limit(limit)
        return list(self.db.scalars(stmt).all())
