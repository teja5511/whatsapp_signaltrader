import pytest
from src.database.engine import SessionLocal
from src.recovery.incidents import HealthIncidentManager
from src.recovery.startup import StartupRecoveryManager

def test_health_incident_manager_lifecycle():
    mgr = HealthIncidentManager(session_factory=SessionLocal)

    # 1. Record incident
    inc = mgr.record_incident(
        incident_kind="TEST_INCIDENT",
        title="Test Health Incident Title",
        severity="WARNING",
        detail={"info": "test detail"}
    )
    assert inc.status == "OPEN"
    assert inc.occurrence_count == 1

    # Record duplicate kind increases occurrence count
    inc2 = mgr.record_incident(
        incident_kind="TEST_INCIDENT",
        title="Test Health Incident Title",
        severity="WARNING"
    )
    assert inc2.id == inc.id
    assert inc2.occurrence_count == 2

    # 2. Acknowledge
    ack_inc = mgr.acknowledge_incident(inc.id, actor="ADMIN_TEST")
    assert ack_inc.status == "ACKNOWLEDGED"
    assert ack_inc.acknowledged_by == "ADMIN_TEST"

    # 3. Resolve
    res_inc = mgr.resolve_incident(inc.id)
    assert res_inc.status == "RESOLVED"

    # 4. List incidents
    list_inc = mgr.list_incidents(status="RESOLVED")
    assert any(i.id == inc.id for i in list_inc)

def test_startup_recovery_manager():
    rec = StartupRecoveryManager(session_factory=SessionLocal)
    res = rec.run_startup_recovery()
    assert res.database_integrity == "OK"
    assert res.wal_mode == "WAL"
    assert isinstance(res.control_state, dict)
    assert isinstance(res.recovery_actions, list)
