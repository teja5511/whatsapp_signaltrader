from fastapi.testclient import TestClient
from src.main import app
from src.database.engine import engine, Base

client = TestClient(app)

def setup_module(module):
    Base.metadata.create_all(bind=engine)

def test_campaign_state_machine_and_version_endpoints():
    r1 = client.get("/api/v1/campaigns/state-machine/version")
    assert r1.status_code == 200
    assert r1.json()["state_machine_version"] == "1.0.0"

    r2 = client.get("/api/v1/campaigns/state-machine")
    assert r2.status_code == 200
    assert "allowed_transitions" in r2.json()

    r3 = client.get("/api/v1/duplicates/version")
    assert r3.status_code == 200
    assert r3.json()["window_hours"] == 24

def test_campaign_creation_approve_reject_api():
    # 1. Post Raw & Parsed Message
    msg_payload = {
        "messageId": "msg-api-c1",
        "groupId": "g-api",
        "senderId": "s-api",
        "text": "Gold Sell\n4120-4128\nsl - 4136\ntp - 4112\ntp - 4104"
    }
    r_msg = client.post("/api/v1/parser/messages", json=msg_payload)
    assert r_msg.status_code == 201

    # 2. Create Campaign from Message
    r_camp = client.post("/api/v1/campaigns/from-message/msg-api-c1")
    assert r_camp.status_code == 201
    c_data = r_camp.json()
    c_id = c_data["id"]
    assert c_data["current_state"] == "AWAITING_CONFIRMATION"

    # 3. Get Campaign Transitions
    r_trans = client.get(f"/api/v1/campaigns/{c_id}/transitions")
    assert r_trans.status_code == 200
    assert len(r_trans.json()) >= 2

    # 4. Approve Campaign
    r_app = client.post(f"/api/v1/campaigns/{c_id}/approve", json={"expected_version": 1})
    assert r_app.status_code == 200
    assert r_app.json()["current_state"] == "PLANNED"
    assert r_app.json()["version"] == 2

    # 5. Stale Version Approval Conflict (HTTP 409)
    r_conflict = client.post(f"/api/v1/campaigns/{c_id}/approve", json={"expected_version": 1})
    assert r_conflict.status_code == 409
