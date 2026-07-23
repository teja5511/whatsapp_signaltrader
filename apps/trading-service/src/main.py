"""
FastAPI Python Core Service — Prompt 4 Implementation
"""
from fastapi import FastAPI, Depends, HTTPException, status, Response
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from sqlalchemy.orm import Session
from src.database.engine import get_db, engine, Base
from src.database.repository import SettingsRepository, CampaignRepository, AuditLogRepository, WhatsAppMessageRepository
from src.database.models import WhatsAppMessageModel, ParsedMessageModel
from src.domain.schemas import AppSettingsDTO
from src.parser.classification import parse_raw_text
from src.parser.service import MessageParsingService
from src.parser.constants import PARSER_VERSION, CONTRACT_VERSION

# Auto-create tables on startup if not present
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="WhatsApp MT5 XAUUSD Trading Service",
    version="1.0.0",
    description="Python core orchestration service for trade signals, deterministic parser, database persistence, and MT5 adapter."
)

class ParserPreviewRequest(BaseModel):
    text: str
    messageId: Optional[str] = "msg-preview"
    groupId: Optional[str] = "group-preview"
    senderId: Optional[str] = "admin-preview"
    quotedMessageId: Optional[str] = None
    isReply: Optional[bool] = False

class ParserMessageRequest(BaseModel):
    messageId: str
    groupId: str
    senderId: str
    text: str
    isAdmin: Optional[bool] = True
    quotedMessageId: Optional[str] = None
    isReply: Optional[bool] = False

@app.get("/health")
async def health_check():
    return {
        "service": "trading-service",
        "status": "ok",
        "version": "development",
        "trading_enabled": False,
        "mt5_connected": False,
        "database_connected": True,
        "database_schema_current": True
    }

@app.get("/ready")
async def readiness_check(db: Session = Depends(get_db)):
    try:
        repo = SettingsRepository(db)
        settings = repo.get_settings()
        return {"status": "ready", "settings_valid": True}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service not ready: {str(e)}")

@app.get("/version")
async def get_version():
    return {
        "service_version": "1.0.0",
        "parser_version": PARSER_VERSION,
        "contract_version": CONTRACT_VERSION
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

# Parser API Endpoints
@app.get("/api/v1/parser/version")
async def get_parser_version():
    return {
        "parser_version": PARSER_VERSION,
        "contract_version": CONTRACT_VERSION,
        "deterministic": True,
        "ai_enabled": False,
        "trading_enabled": False
    }

@app.post("/api/v1/parser/preview")
async def preview_parser(req: ParserPreviewRequest):
    result = parse_raw_text(
        raw_text=req.text,
        message_id=req.messageId,
        group_id=req.groupId,
        sender_id=req.senderId,
        quoted_message_id=req.quotedMessageId,
        is_reply=req.isReply
    )
    return result.to_dict()

@app.post("/api/v1/parser/messages")
async def parse_and_persist_message(req: ParserMessageRequest, response: Response):
    service = MessageParsingService()
    result_dict, is_duplicate = service.parse_and_persist(
        raw_text=req.text,
        message_id=req.messageId,
        group_id=req.groupId,
        sender_id=req.senderId,
        is_admin=req.isAdmin,
        quoted_message_id=req.quotedMessageId,
        is_reply=req.isReply
    )
    response.status_code = status.HTTP_200_OK if is_duplicate else status.HTTP_201_CREATED
    return result_dict

@app.get("/api/v1/parser/messages/{raw_message_id}")
async def get_parsed_message(raw_message_id: str, db: Session = Depends(get_db)):
    raw_msg = db.get(WhatsAppMessageModel, raw_message_id)
    if not raw_msg or not raw_msg.parsed_message:
        raise HTTPException(status_code=404, detail="Parsed message not found")
    
    import json
    return {
        "raw_message_id": raw_msg.id,
        "group_id": raw_msg.group_id,
        "sender_id": raw_msg.sender_id,
        "raw_content": raw_msg.raw_content,
        "received_at": raw_msg.received_at.isoformat(),
        "parsed_result": json.loads(raw_msg.parsed_message.parsed_json)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="127.0.0.1", port=8000, reload=True)
