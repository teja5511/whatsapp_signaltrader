"""Idempotency Key Generation for MT5 Execution Worker."""

import hashlib
import json
from typing import Optional

def generate_execution_idempotency_key(
    campaign_id: str,
    planning_fingerprint: str,
    planned_entry_id: str,
    campaign_version: int,
    account_login: int,
    account_server: str,
    broker_symbol: str,
    operation_type: str = "PLACE_PENDING_ORDER"
) -> str:
    """
    Generates a deterministic 64-character SHA-256 idempotency key for MT5 trade operations.
    """
    login_hash = hashlib.sha256(str(account_login).encode("utf-8")).hexdigest()[:16]
    payload = {
        "campaign_id": campaign_id,
        "planning_fingerprint": planning_fingerprint,
        "planned_entry_id": planned_entry_id,
        "campaign_version": campaign_version,
        "login_hash": login_hash,
        "server": account_server.strip().upper(),
        "broker_symbol": broker_symbol.strip().upper(),
        "operation_type": operation_type.strip().upper()
    }
    canonical_json = json.dumps(payload, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()
