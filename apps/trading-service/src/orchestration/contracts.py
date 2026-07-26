from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from src.orchestration.constants import (
    ORCHESTRATOR_VERSION, EVENT_CONTRACT_VERSION, OUTBOX_VERSION, SYSTEM_STATUS_CONTRACT_VERSION,
    AUTOMATION_PAUSED, MODE_CONFIRMATION
)

class SystemStatusDTO(BaseModel):
    system_status_contract_version: str = SYSTEM_STATUS_CONTRACT_VERSION
    overall_state: str = "HEALTHY"  # HEALTHY, DEGRADED, BLOCKED, ERROR, STARTING, STOPPED
    automation_state: str = AUTOMATION_PAUSED
    default_execution_mode: str = MODE_CONFIRMATION
    execution_mode: str = MODE_CONFIRMATION
    trading_enabled: bool = False
    mt5_execution_enabled: bool = False
    mt5_account_environment: str = "DEMO"
    mt5_margin_mode: str = "HEDGING"
    whatsapp_worker_state: str = "READY"
    whatsapp_spool_pending: int = 0
    active_campaign_count: int = 0
    awaiting_confirmation_count: int = 0
    waiting_for_tp_count: int = 0
    queued_mt5_jobs: int = 0
    outbox_pending: int = 0
    latest_event_sequence: int = 0
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    database: Dict[str, Any] = Field(default_factory=lambda: {"connected": True, "backend": "sqlite", "pending_migrations": False})
    mt5_adapter: Dict[str, Any] = Field(default_factory=lambda: {"initialized": True, "adapter_mode": "DEMO", "health_state": "OK", "account_environment": "DEMO", "login_masked": "*****", "is_live_account": False, "live_blocked": True})
    whatsapp_worker: Dict[str, Any] = Field(default_factory=lambda: {"connected": True, "worker_enabled": True, "group_configured": True, "admin_configured": True})
    outbox_queue: Dict[str, Any] = Field(default_factory=lambda: {"pending_events": 0, "delivered_events": 0, "failed_events": 0})

class ControlStateDTO(BaseModel):
    automation_state: str = AUTOMATION_PAUSED
    default_execution_mode: str = MODE_CONFIRMATION
    trading_enabled: bool = False
    mt5_execution_enabled: bool = False
    orchestrator_enabled: bool = True
    event_dispatcher_enabled: bool = True

class ControlPhraseActionDTO(BaseModel):
    confirmation_phrase: str

class OrchestrationRunDTO(BaseModel):
    id: str
    orchestrator_version: str = ORCHESTRATOR_VERSION
    source_type: str
    source_id: str
    correlation_id: str
    causation_id: Optional[str] = None
    campaign_id: Optional[str] = None
    command_id: Optional[str] = None
    status: str
    current_step: str
    input_payload: Dict[str, Any]
    output_payload: Optional[Dict[str, Any]] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    started_at: str
    completed_at: Optional[str] = None

class OrchestrationStepDTO(BaseModel):
    id: str
    orchestration_run_id: str
    sequence: int
    step_name: str
    status: str
    input_data: Optional[Dict[str, Any]] = None
    output_data: Optional[Dict[str, Any]] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    started_at: str
    completed_at: Optional[str] = None

class AmbiguousCommandConfirmationDTO(BaseModel):
    id: str
    command_id: str
    campaign_id: Optional[str] = None
    suggested_action: str
    original_text: str
    match_type: str
    candidate_count: int = 1
    status: str = "PENDING"
    expires_at: Optional[str] = None
    created_at: str

class CommandResolutionActionDTO(BaseModel):
    action: str  # APPROVE_CLOSE, APPROVE_CANCEL, APPROVE_HOLD_NO_ACTION, APPROVE_SKIP_NO_ACTION, REJECT_COMMAND
