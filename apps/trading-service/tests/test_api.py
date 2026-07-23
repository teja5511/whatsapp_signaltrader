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
    assert float(data["lot_per_entry"]) == 0.10
    assert float(data["max_exposure_lots"]) == 2.00

def test_get_campaigns_endpoint():
    response = client.get("/api/v1/campaigns")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_audit_logs_endpoint():
    response = client.get("/api/v1/audit-logs")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
