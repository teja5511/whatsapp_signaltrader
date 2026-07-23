from fastapi.testclient import TestClient
from src.main import app
from src.database.engine import engine, Base

client = TestClient(app)

def setup_module(module):
    Base.metadata.create_all(bind=engine)

def test_get_parser_version_endpoint():
    response = client.get("/api/v1/parser/version")
    assert response.status_code == 200
    data = response.json()
    assert data["parser_version"] == "1.0.0"
    assert data["deterministic"] is True

def test_parser_preview_endpoint():
    payload = {
        "text": "Gold Sell\n4120-4128\nsl - 4136\ntp - 4112",
        "messageId": "msg-preview-1"
    }
    response = client.post("/api/v1/parser/preview", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["category"] == "NEW_SIGNAL"
    assert data["signal"]["direction"] == "SELL"

def test_parser_messages_post_and_get():
    payload = {
        "messageId": "msg-api-001",
        "groupId": "group-api",
        "senderId": "admin-api",
        "text": "Move SL to 4138 for added safety"
    }
    # 1. POST message
    res1 = client.post("/api/v1/parser/messages", json=payload)
    assert res1.status_code == 201
    data1 = res1.json()
    assert data1["category"] == "FOLLOW_UP_COMMAND"
    assert data1["command"]["value"] == "4138.00000000"

    # 2. GET message
    res2 = client.get("/api/v1/parser/messages/msg-api-001")
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["raw_message_id"] == "msg-api-001"
    assert data2["parsed_result"]["category"] == "FOLLOW_UP_COMMAND"
