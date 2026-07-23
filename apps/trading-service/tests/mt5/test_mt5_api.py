import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.database.engine import engine, Base

client = TestClient(app)
AUTH_HEADER = {"Authorization": "Bearer dev-local-secret-token"}

def setup_module(module):
    Base.metadata.create_all(bind=engine)

def test_mt5_status_version_and_info_endpoints():
    r_ver = client.get("/api/v1/mt5/version")
    assert r_ver.status_code == 200
    assert r_ver.json()["mt5_adapter_version"] == "1.0.0"

    r_stat = client.get("/api/v1/mt5/status")
    assert r_stat.status_code == 200
    assert r_stat.json()["demo_only"] is True

    r_term = client.get("/api/v1/mt5/terminal")
    assert r_term.status_code == 200

    r_acc = client.get("/api/v1/mt5/account")
    assert r_acc.status_code == 200

    r_sym = client.get("/api/v1/mt5/symbol")
    assert r_sym.status_code == 200
    assert r_sym.json()["canonical_symbol"] == "XAUUSD"

    r_spec = client.get("/api/v1/mt5/symbol/specification")
    assert r_spec.status_code == 200

def test_mt5_mutating_endpoints_require_local_auth():
    # Missing token -> HTTP 401
    r_init_no_auth = client.post("/api/v1/mt5/initialize")
    assert r_init_no_auth.status_code == 401

    # Invalid token -> HTTP 401
    r_init_bad_auth = client.post("/api/v1/mt5/initialize", headers={"Authorization": "Bearer wrong-token"})
    assert r_init_bad_auth.status_code == 401

    # Valid token -> HTTP 200
    r_init_ok = client.post("/api/v1/mt5/initialize", headers=AUTH_HEADER)
    assert r_init_ok.status_code == 200
    assert r_init_ok.json()["status"] == "initialized"

def test_mt5_execution_preflight_and_jobs_endpoints():
    # 1. Post message & approve campaign & plan
    msg_payload = {
        "messageId": "msg-api-mt5-1",
        "groupId": "g-api",
        "senderId": "s-api",
        "text": "Gold Sell\n4120-4128\nsl - 4136\ntp - 4112\ntp - 4104"
    }
    client.post("/api/v1/parser/messages", json=msg_payload)
    r_c = client.post("/api/v1/campaigns/from-message/msg-api-mt5-1")
    c_id = r_c.json()["id"]
    client.post(f"/api/v1/campaigns/{c_id}/approve", json={"expected_version": 1})
    r_plan = client.post(f"/api/v1/campaigns/{c_id}/plan")
    fingerprint = r_plan.json()["planning_fingerprint"]

    # 2. Preflight
    r_pref = client.post(f"/api/v1/mt5/execution/preflight/{c_id}")
    assert r_pref.status_code == 200
    assert r_pref.json()["is_ready"] is True

    # 3. Queue Execution (202 Accepted)
    exec_payload = {
        "expected_version": 2,
        "planning_fingerprint": fingerprint,
        "explicit_user_confirm": True
    }
    r_exec = client.post(f"/api/v1/mt5/execution/campaigns/{c_id}", json=exec_payload, headers=AUTH_HEADER)
    assert r_exec.status_code == 202
    assert r_exec.json()["status"] == "QUEUED"

    # 4. Get Jobs & Batches
    r_jobs = client.get("/api/v1/mt5/execution/jobs")
    assert r_jobs.status_code == 200
    assert len(r_jobs.json()) >= 5
