import pytest
from src.database.engine import SessionLocal
from src.reconciliation.service import MT5ReconciliationService
from src.reconciliation.contracts import ClassificationKind

def test_reconciliation_service_lifecycle():
    recon = MT5ReconciliationService(session_factory=SessionLocal)

    # 1. Run reconciliation
    res = recon.run_reconciliation(trigger_type="MANUAL", scope="ALL")
    assert res.status == "COMPLETED"
    assert res.reconciliation_version == "1.0.0"
    assert res.correlation_id is not None
    assert isinstance(res.items, list)

    # 2. List runs
    runs = recon.get_runs(limit=10)
    assert len(runs) >= 1
    assert runs[0].id == res.id
