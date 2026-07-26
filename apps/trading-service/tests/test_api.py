from fastapi.testclient import TestClient
from src.main import app
from src.database.engine import engine, Base

client = TestClient(app)

def setup_module(module):
    Base.metadata.create_all(bind=engine)

def test_get_settings_endpoint():
    response = client.get("/api/v1/settings")
    assert response.status_code == 200
    data = response.json()
    assert data["entry_count"] == 5
    assert float(data["lot_per_entry"]) == 0.30
    assert float(data["max_exposure_lots"]) == 2.00
    assert data["trading_enabled"] is False

def test_get_campaigns_endpoint():
    response = client.get("/api/v1/campaigns")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_audit_logs_endpoint():
    response = client.get("/api/v1/audit-logs")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_cors_options_preflight_system_status():
    response = client.options(
        "/api/v1/system/status",
        headers={
            "Origin": "http://localhost:1420",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "authorization,content-type",
        }
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:1420"
    assert "GET" in response.headers.get("access-control-allow-methods", "")

def test_cors_options_preflight_tauri_origin():
    response = client.options(
        "/api/v1/system/status",
        headers={
            "Origin": "tauri://localhost",
            "Access-Control-Request-Method": "GET",
        }
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "tauri://localhost"
