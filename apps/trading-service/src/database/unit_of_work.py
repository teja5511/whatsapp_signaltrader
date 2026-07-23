from typing import Callable
from sqlalchemy.orm import Session
from src.database.engine import SessionLocal
from src.database.repository import (
    SettingsRepository, WhatsAppMessageRepository, CampaignRepository, AuditLogRepository
)

class UnitOfWork:
    def __init__(self, session_factory: Callable[[], Session] = SessionLocal):
        self.session_factory = session_factory
        self.db: Session = None

    def __enter__(self):
        self.db = self.session_factory()
        self.settings = SettingsRepository(self.db)
        self.messages = WhatsAppMessageRepository(self.db)
        self.campaigns = CampaignRepository(self.db)
        self.audit = AuditLogRepository(self.db)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.rollback()
        else:
            self.commit()
        self.db.close()

    def commit(self):
        if self.db:
            self.db.commit()

    def rollback(self):
        if self.db:
            self.db.rollback()
