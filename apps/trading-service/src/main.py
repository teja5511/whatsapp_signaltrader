"""
FastAPI Python Core Service — Prompt 3 Phase Implementation
"""
from fastapi import FastAPI, Depends, HTTPException
from datetime import datetime, timezone
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from src.database.engine import get_db, engine, Base
from src.database.repository import SettingsRepository, CampaignRepository, AuditLogRepository, WhatsAppMessageRepository
from src.domain.schemas import AppSettingsDTO

# Auto-create tables on startup if not present
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="WhatsApp MT5 XAUUSD Trading Service",
    version="1.0.0",
    description="Python core orchestration service for trade signals, database persistence, and MT5 adapter."
)

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "trading-service",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@app.get("/api/v1/status")
async def get_system_status(db: Session = Depends(get_db)):
    repo = SettingsRepository(db)
    settings = repo.get_settings()
    return {
        "execution_mode": settings.execution_mode,
        "default_entry_count": settings.entry_count,
        "lot_per_entry": float(settings.lot_per_entry),
        "max_exposure_lots": float(settings.max_exposure_lots),
        "instrument": "XAUUSD",
        "account_mode": "DEMO"
    }

@app.get("/api/v1/settings", response_model=AppSettingsDTO)
async def get_settings(db: Session = Depends(get_db)):
    repo = SettingsRepository(db)
    return repo.get_settings()

@app.get("/api/v1/campaigns")
async def list_campaigns(limit: int = 50, db: Session = Depends(get_db)):
    repo = CampaignRepository(db)
    campaigns = repo.list_all(limit=limit)
    return [
        {
            "id": c.id,
            "signal_id": c.signal_id,
            "magic_number": c.magic_number,
            "current_state": c.current_state,
            "execution_mode": c.execution_mode,
            "entry_count": c.entry_count,
            "lot_per_entry": c.lot_per_entry,
            "total_volume": c.total_volume,
            "created_at": c.created_at.isoformat(),
            "updated_at": c.updated_at.isoformat()
        }
        for c in campaigns
    ]

@app.get("/api/v1/audit-logs")
async def list_audit_logs(limit: int = 50, db: Session = Depends(get_db)):
    repo = AuditLogRepository(db)
    logs = repo.list_logs(limit=limit)
    return [
        {
            "id": log.id,
            "event_type": log.event_type,
            "payload_json": log.payload_json,
            "created_at": log.created_at.isoformat()
        }
        for log in logs
    ]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="127.0.0.1", port=8000, reload=True)
