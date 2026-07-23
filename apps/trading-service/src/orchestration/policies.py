from datetime import datetime, timezone
from typing import Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from src.database.engine import SessionLocal
from src.database.unit_of_work import UnitOfWork
from src.database.models import ControlStateModel
from src.orchestration.constants import (
    AUTOMATION_PAUSED, AUTOMATION_RUNNING, AUTOMATION_EMERGENCY_STOPPED,
    MODE_CONFIRMATION, MODE_AUTOMATIC, EMERGENCY_RESET_PHRASE, DEMO_TRADING_ENABLE_PHRASE
)
from src.orchestration.errors import EmergencyStopActiveError, InvalidControlPhraseError
from src.events.outbox import OutboxPublisher
from src.events.constants import (
    EVENT_AUTOMATION_STATE_CHANGED, EVENT_TRADING_CONTROL_CHANGED,
    EVENT_EMERGENCY_STOP_TRIGGERED, EVENT_EMERGENCY_STOP_RESET
)
from src.mt5.execution_service import MT5ExecutionService

class ControlPolicyManager:
    def __init__(self, session_factory=SessionLocal, mt5_service: Optional[MT5ExecutionService] = None):
        self.session_factory = session_factory
        self.mt5_service = mt5_service or MT5ExecutionService(session_factory=session_factory)
        self.ensure_control_state()

    def ensure_control_state(self) -> None:
        try:
            with UnitOfWork(session_factory=self.session_factory) as uow:
                ctrl = uow.db.get(ControlStateModel, 1)
                if not ctrl:
                    ctrl = ControlStateModel(
                        id=1,
                        automation_state=AUTOMATION_PAUSED,
                        default_execution_mode=MODE_CONFIRMATION,
                        trading_enabled=False,
                        mt5_execution_enabled=False,
                        orchestrator_enabled=True,
                        event_dispatcher_enabled=True,
                        updated_at=datetime.now(timezone.utc)
                    )
                    uow.db.add(ctrl)
        except Exception:
            pass

    def pause_automation(self, correlation_id: str = "ctrl-pause") -> Dict[str, Any]:
        with UnitOfWork(session_factory=self.session_factory) as uow:
            ctrl = uow.db.get(ControlStateModel, 1)
            old_state = ctrl.automation_state
            ctrl.automation_state = AUTOMATION_PAUSED
            ctrl.updated_at = datetime.now(timezone.utc)

            OutboxPublisher.publish_domain_event(
                db=uow.db,
                event_type=EVENT_AUTOMATION_STATE_CHANGED,
                aggregate_type="CONTROL",
                aggregate_id="1",
                correlation_id=correlation_id,
                payload={"old_state": old_state, "new_state": AUTOMATION_PAUSED}
            )

            uow.audit.log_event("AUTOMATION_PAUSED", {"old_state": old_state, "new_state": AUTOMATION_PAUSED})
            return {"status": "success", "automation_state": AUTOMATION_PAUSED}

    def resume_automation(self, correlation_id: str = "ctrl-resume") -> Dict[str, Any]:
        with UnitOfWork(session_factory=self.session_factory) as uow:
            ctrl = uow.db.get(ControlStateModel, 1)
            if ctrl.automation_state == AUTOMATION_EMERGENCY_STOPPED:
                raise EmergencyStopActiveError("Cannot resume automation while emergency stop is active. Reset emergency stop first.")

            old_state = ctrl.automation_state
            ctrl.automation_state = AUTOMATION_RUNNING
            ctrl.updated_at = datetime.now(timezone.utc)

            OutboxPublisher.publish_domain_event(
                db=uow.db,
                event_type=EVENT_AUTOMATION_STATE_CHANGED,
                aggregate_type="CONTROL",
                aggregate_id="1",
                correlation_id=correlation_id,
                payload={"old_state": old_state, "new_state": AUTOMATION_RUNNING}
            )

            uow.audit.log_event("AUTOMATION_RESUMED", {"old_state": old_state, "new_state": AUTOMATION_RUNNING})
            return {"status": "success", "automation_state": AUTOMATION_RUNNING}

    def trigger_emergency_stop(self, correlation_id: str = "ctrl-estop") -> Dict[str, Any]:
        with UnitOfWork(session_factory=self.session_factory) as uow:
            ctrl = uow.db.get(ControlStateModel, 1)
            old_state = ctrl.automation_state
            ctrl.automation_state = AUTOMATION_EMERGENCY_STOPPED
            ctrl.trading_enabled = False
            ctrl.mt5_execution_enabled = False
            ctrl.updated_at = datetime.now(timezone.utc)

            OutboxPublisher.publish_domain_event(
                db=uow.db,
                event_type=EVENT_EMERGENCY_STOP_TRIGGERED,
                aggregate_type="CONTROL",
                aggregate_id="1",
                correlation_id=correlation_id,
                payload={"old_state": old_state, "new_state": AUTOMATION_EMERGENCY_STOPPED}
            )

            uow.audit.log_event("EMERGENCY_STOP_TRIGGERED", {"old_state": old_state})
            return {"status": "success", "automation_state": AUTOMATION_EMERGENCY_STOPPED}

    def reset_emergency_stop(self, confirmation_phrase: str, correlation_id: str = "ctrl-reset-estop") -> Dict[str, Any]:
        if confirmation_phrase != EMERGENCY_RESET_PHRASE:
            raise InvalidControlPhraseError(f"Invalid confirmation phrase '{confirmation_phrase}'. Expected '{EMERGENCY_RESET_PHRASE}'.")

        with UnitOfWork(session_factory=self.session_factory) as uow:
            ctrl = uow.db.get(ControlStateModel, 1)
            old_state = ctrl.automation_state
            ctrl.automation_state = AUTOMATION_PAUSED
            ctrl.updated_at = datetime.now(timezone.utc)

            OutboxPublisher.publish_domain_event(
                db=uow.db,
                event_type=EVENT_EMERGENCY_STOP_RESET,
                aggregate_type="CONTROL",
                aggregate_id="1",
                correlation_id=correlation_id,
                payload={"old_state": old_state, "new_state": AUTOMATION_PAUSED}
            )

            uow.audit.log_event("EMERGENCY_STOP_RESET", {"old_state": old_state})
            return {"status": "success", "automation_state": AUTOMATION_PAUSED}

    def enable_demo_trading(self, confirmation_phrase: str, correlation_id: str = "ctrl-enable-demo") -> Dict[str, Any]:
        if confirmation_phrase != DEMO_TRADING_ENABLE_PHRASE:
            raise InvalidControlPhraseError(f"Invalid confirmation phrase '{confirmation_phrase}'. Expected '{DEMO_TRADING_ENABLE_PHRASE}'.")

        # Verify Demo Readiness via MT5 Adapter
        if not self.mt5_service.adapter.is_initialized():
            self.mt5_service.adapter.initialize()
        acc = self.mt5_service.adapter.account_info()
        if acc.environment_kind != "DEMO":
            raise ValueError("Trading enable blocked: Connected MT5 account is not a DEMO account.")

        with UnitOfWork(session_factory=self.session_factory) as uow:
            ctrl = uow.db.get(ControlStateModel, 1)
            ctrl.trading_enabled = True
            ctrl.mt5_execution_enabled = True
            ctrl.updated_at = datetime.now(timezone.utc)

            OutboxPublisher.publish_domain_event(
                db=uow.db,
                event_type=EVENT_TRADING_CONTROL_CHANGED,
                aggregate_type="CONTROL",
                aggregate_id="1",
                correlation_id=correlation_id,
                payload={"trading_enabled": True, "mt5_execution_enabled": True, "account_login": acc.login_masked}
            )

            uow.audit.log_event("DEMO_TRADING_ENABLED", {"login_masked": acc.login_masked, "server": acc.server})
            return {"status": "success", "trading_enabled": True, "mt5_execution_enabled": True}

    def disable_trading(self, correlation_id: str = "ctrl-disable-trading") -> Dict[str, Any]:
        with UnitOfWork(session_factory=self.session_factory) as uow:
            ctrl = uow.db.get(ControlStateModel, 1)
            ctrl.trading_enabled = False
            ctrl.mt5_execution_enabled = False
            ctrl.updated_at = datetime.now(timezone.utc)

            OutboxPublisher.publish_domain_event(
                db=uow.db,
                event_type=EVENT_TRADING_CONTROL_CHANGED,
                aggregate_type="CONTROL",
                aggregate_id="1",
                correlation_id=correlation_id,
                payload={"trading_enabled": False, "mt5_execution_enabled": False}
            )

            uow.audit.log_event("TRADING_DISABLED", {})
            return {"status": "success", "trading_enabled": False, "mt5_execution_enabled": False}
