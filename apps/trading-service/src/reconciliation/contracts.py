from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class ClassificationKind(str, Enum):
    MATCHED = "MATCHED"
    LOCAL_ONLY = "LOCAL_ONLY"
    BROKER_ONLY = "BROKER_ONLY"
    MISMATCHED = "MISMATCHED"
    MISSING_ORDER = "MISSING_ORDER"
    MISSING_POSITION = "MISSING_POSITION"
    UNEXPECTED_ORDER = "UNEXPECTED_ORDER"
    UNEXPECTED_POSITION = "UNEXPECTED_POSITION"
    DUPLICATE_BROKER_ORDER = "DUPLICATE_BROKER_ORDER"
    OUTCOME_UNKNOWN = "OUTCOME_UNKNOWN"

class ReconciliationItemDTO(BaseModel):
    id: str
    reconciliation_run_id: str
    entity_type: str  # ORDER or POSITION
    classification: str
    ticket: Optional[int] = None
    magic_number: Optional[int] = None
    campaign_id: Optional[str] = None
    planned_entry_id: Optional[str] = None
    job_id: Optional[str] = None
    local_snapshot: Optional[Dict[str, Any]] = None
    broker_snapshot: Optional[Dict[str, Any]] = None
    differences: List[Dict[str, Any]] = Field(default_factory=list)
    requires_review: bool = False
    resolution_status: str = "OPEN"
    resolution_action: Optional[str] = None
    resolved_by: Optional[str] = None
    resolved_at: Optional[datetime] = None
    created_at: datetime

class ReconciliationRunDTO(BaseModel):
    id: str
    reconciliation_version: str = "1.0.0"
    trigger_type: str = "MANUAL"
    scope: str = "ALL"
    campaign_id: Optional[str] = None
    correlation_id: str
    actor: str = "SYSTEM"
    status: str = "COMPLETED"
    broker_symbol: Optional[str] = None
    local_order_count: int = 0
    local_position_count: int = 0
    broker_order_count: int = 0
    broker_position_count: int = 0
    matched_count: int = 0
    mismatch_count: int = 0
    requires_review_count: int = 0
    snapshot_summary: Dict[str, Any] = Field(default_factory=dict)
    error_message: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    items: List[ReconciliationItemDTO] = Field(default_factory=list)
