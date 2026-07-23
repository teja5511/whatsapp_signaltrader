import hashlib
import json

def generate_orchestration_run_idempotency_key(
    source_type: str,
    source_id: str,
    orchestrator_version: str = "1.0.0"
) -> str:
    """
    Generates deterministic SHA-256 idempotency key for an orchestration run.
    """
    raw = f"ORCH:{source_type.strip().upper()}:{source_id.strip()}:{orchestrator_version.strip()}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()
