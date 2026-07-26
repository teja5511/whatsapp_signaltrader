from typing import Callable, Optional
from sqlalchemy.orm import Session
from src.database.engine import SessionLocal
from src.database.repository import (
    SettingsRepository, WhatsAppMessageRepository, CampaignRepository, AuditLogRepository
)


class UnitOfWork:
    """Transaction scope for a single logical operation.

    Passing an existing ``session`` makes this a *nested* scope: it joins the
    caller's transaction, flushes on exit and leaves commit/rollback/close to
    the owner. That is what lets the orchestrator wrap the campaign, planning
    and outbox writes for one message in a single atomic transaction instead of
    opening several competing SQLite writers.
    """

    def __init__(
        self,
        session_factory: Callable[[], Session] = SessionLocal,
        session: Optional[Session] = None,
    ):
        self.session_factory = session_factory
        self.db: Optional[Session] = session
        self._owns_session = session is None

    @property
    def is_nested(self) -> bool:
        return not self._owns_session

    def __enter__(self):
        if self.db is None:
            self.db = self.session_factory()
        self.settings = SettingsRepository(self.db)
        self.messages = WhatsAppMessageRepository(self.db)
        self.campaigns = CampaignRepository(self.db)
        self.audit = AuditLogRepository(self.db)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self._owns_session:
            # Nested scope: surface pending writes to the outer transaction but
            # never commit or close a session we do not own.
            if exc_type is None and self.db is not None:
                self.db.flush()
            return False

        if exc_type is not None:
            self.rollback()
        else:
            self.commit()
        self.db.close()
        return False

    def commit(self):
        if self.db:
            self.db.commit()

    def rollback(self):
        if self.db:
            self.db.rollback()
