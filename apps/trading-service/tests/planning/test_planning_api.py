from fastapi.testclient import TestClient
from src.main import app
from src.database.engine import engine, Base

client = TestClient(app)

def setup_module(module):
    Base.metadata.create_all(bind=engine)

def test_planning_version_and_policies_endpoints():
    r1 = client.get("/api/v1/planning/version")
    assert r1.status_code == 200
    assert r1.json()["planner_version"] == "1.0.0"

    r2 = client.get("/api/v1/planning/policies")
    assert r2.status_code == 200
    assert "hundred_pip_policy" in r2.json()

def test_planning_preview_and_plan_endpoints():
    # 1. Preview
    preview_payload = {
        "direction": "SELL",
        "entry_count": 5,
        "lot_per_entry": 0.30,
        "zone_low": 3990.0,
        "zone_high": 3998.0,
        "stop_loss": 4008.0,
        "tp1": 3960.0,
        "tp2": 3950.0
    }
    r_prev = client.post("/api/v1/planning/preview", json=preview_payload)
    assert r_prev.status_code == 200
    assert len(r_prev.json()["planned_entries"]) == 5

    # 2. Parse Raw & Approve Campaign
    msg_payload = {
        "messageId": "msg-plan-api-1",
        "groupId": "g-api",
        "senderId": "s-api",
        "text": "Gold Sell\n4120-4128\nsl - 4136\ntp - 4112\ntp - 4104"
    }
    client.post("/api/v1/parser/messages", json=msg_payload)
    r_c = client.post("/api/v1/campaigns/from-message/msg-plan-api-1")
    c_id = r_c.json()["id"]
    client.post(f"/api/v1/campaigns/{c_id}/approve", json={"expected_version": 1})

    # 3. Plan Campaign
    r_plan = client.post(f"/api/v1/campaigns/{c_id}/plan")
    assert r_plan.status_code == 201
    assert len(r_plan.json()["planned_entries"]) == 5

    # 4. Idempotent Second Call
    r_plan2 = client.post(f"/api/v1/campaigns/{c_id}/plan")
    assert r_plan2.status_code == 200

    # 5. Get Campaign Plan
    r_get = client.get(f"/api/v1/campaigns/{c_id}/plan")
    assert r_get.status_code == 200
    assert r_get.json()["planned_entries_count"] == 5
