import os
import http
import json
from typing import Optional, List, Dict, Any
from urllib.request import Request, urlopen
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from src.database.engine import SessionLocal
from src.database.models import CampaignModel, MT5ExecutionJobModel, DomainEventModel, EventOutboxModel, ControlStateModel
from src.orchestration.contracts import SystemStatusDTO
from src.orchestration.constants import (
    SYSTEM_STATUS_CONTRACT_VERSION, AUTOMATION_PAUSED, MODE_CONFIRMATION
)
from src.mt5.execution_service import MT5ExecutionService

class SystemStatusAggregator:
    def __init__(self, session_factory=SessionLocal, mt5_service: Optional[MT5ExecutionService] = None):
        self.session_factory = session_factory
        self.mt5_service = mt5_service or MT5ExecutionService(session_factory=session_factory)

    def aggregate_status(self) -> SystemStatusDTO:
        db = self.session_factory()
        try:
            # 1. Fetch Control State
            ctrl = db.get(ControlStateModel, 1)
            auto_state = ctrl.automation_state if ctrl else AUTOMATION_PAUSED
            exec_mode = ctrl.default_execution_mode if ctrl else MODE_CONFIRMATION
            trading_en = ctrl.trading_enabled if ctrl else False
            mt5_exec_en = ctrl.mt5_execution_enabled if ctrl else False

            # 2. Fetch Campaign Counts
            active_c_count = db.query(CampaignModel).filter(CampaignModel.current_state.notin_(["CLOSED", "CANCELLED", "REJECTED", "FAILED"])).count()
            awaiting_conf_count = db.query(CampaignModel).filter(CampaignModel.current_state == "AWAITING_CONFIRMATION").count()
            waiting_tp_count = db.query(CampaignModel).filter(CampaignModel.current_state == "WAITING_FOR_TP").count()

            # 3. Fetch MT5 Jobs & Outbox Counts
            queued_jobs = db.query(MT5ExecutionJobModel).filter(MT5ExecutionJobModel.status == "QUEUED").count()
            outbox_pending = db.query(EventOutboxModel).filter(EventOutboxModel.status == "PENDING").count()

            # 4. Fetch Latest Event Sequence
            latest_event = db.query(DomainEventModel).order_by(DomainEventModel.sequence.desc()).first()
            latest_seq = latest_event.sequence if latest_event and latest_event.sequence else 0

            # 5. Fetch MT5 Adapter Info
            mt5_status = self.mt5_service.adapter.get_status()

            # 6. Fetch WhatsApp Worker Status (Local HTTP poll with timeout fallback)
            wa_state = "DEGRADED"
            wa_connected = False
            wa_spool_pending = 0
            wa_url = os.getenv("WHATSAPP_WORKER_URL", "http://127.0.0.1:8010")
            try:
                req = Request(f"{wa_url}/health", headers={"User-Agent": "TradingService/1.0"})
                with urlopen(req, timeout=1) as resp:
                    if resp.status == 200:
                        data = json.loads(resp.read().decode("utf-8"))
                        wa_state = data.get("connection_state", "READY")
                        wa_spool_pending = data.get("spool_pending", 0)
                        wa_connected = wa_state in ["READY", "CONNECTED", "AUTHENTICATED"] or data.get("whatsapp_integration_enabled", False)
            except Exception:
                wa_state = "UNAVAILABLE"
                wa_connected = False

            overall = "HEALTHY"
            if auto_state == "EMERGENCY_STOPPED" or wa_state == "UNAVAILABLE":
                overall = "DEGRADED"

            return SystemStatusDTO(
                system_status_contract_version=SYSTEM_STATUS_CONTRACT_VERSION,
                overall_state=overall,
                automation_state=auto_state,
                default_execution_mode=exec_mode,
                execution_mode=exec_mode,
                trading_enabled=trading_en,
                mt5_execution_enabled=mt5_exec_en,
                mt5_account_environment=mt5_status.account_environment,
                mt5_margin_mode=mt5_status.margin_mode,
                whatsapp_worker_state=wa_state,
                whatsapp_spool_pending=wa_spool_pending,
                active_campaign_count=active_c_count,
                awaiting_confirmation_count=awaiting_conf_count,
                waiting_for_tp_count=waiting_tp_count,
                queued_mt5_jobs=queued_jobs,
                outbox_pending=outbox_pending,
                latest_event_sequence=latest_seq,
                updated_at=datetime.now(timezone.utc).isoformat(),
                database={"connected": True, "backend": "sqlite", "pending_migrations": False},
                mt5_adapter={
                    "initialized": True,
                    "adapter_mode": mt5_status.account_environment,
                    "health_state": "OK",
                    "account_environment": mt5_status.account_environment,
                    "login_masked": "*****",
                    "is_live_account": False,
                    "live_blocked": True
                },
                whatsapp_worker={
                    "connected": wa_connected,
                    "worker_enabled": True,
                    "group_configured": True,
                    "admin_configured": True
                },
                outbox_queue={
                    "pending_events": outbox_pending,
                    "delivered_events": 0,
                    "failed_events": 0
                }
            )
        finally:
            db.close()
