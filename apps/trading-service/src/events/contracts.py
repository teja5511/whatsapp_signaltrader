import json
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class DomainEventDTO(BaseModel):
    event_contract_version: str = "1.0.0"
    event_id: str
    sequence: int
    event_type: str
    event_version: str = "1.0"
    aggregate_type: str
    aggregate_id: str
    campaign_id: Optional[str] = None
    correlation_id: str
    causation_id: Optional[str] = None
    actor_type: str = "SYSTEM"
    actor_id: Optional[str] = None
    occurred_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    payload: Dict[str, Any]

def redact_event_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Redacts sensitive tokens, passwords, session data, and secrets from event payloads."""
    redacted = {}
    for k, v in payload.items():
        k_lower = k.lower()
        if any(term in k_lower for term in ["token", "secret", "password", "cookie", "session_data", "qr_payload", "auth"]):
            redacted[k] = "[REDACTED]"
        elif isinstance(v, dict):
            redacted[k] = redact_event_payload(v)
        else:
            redacted[k] = v
    return redacted
