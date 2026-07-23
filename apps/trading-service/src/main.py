"""
FastAPI Python Core Service — Prompts 4 & 5 Implementation
"""
from fastapi import FastAPI, Depends, HTTPException, status, Response
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from sqlalchemy.orm import Session
from src.database.engine import get_db, engine, Base
from src.database.repository import SettingsRepository, CampaignRepository, AuditLogRepository, WhatsAppMessageRepository
from src.database.models import WhatsAppMessageModel, ParsedMessageModel, CampaignModel, CampaignStateTransitionModel, CommandModel, DuplicateKeyModel
from src.domain.schemas import AppSettingsDTO
from src.parser.classification import parse_raw_text
from src.parser.service import MessageParsingService
from src.parser.constants import PARSER_VERSION, CONTRACT_VERSION
from src.campaigns.service import CampaignService
from src.campaigns.constants import STATE_MACHINE_VERSION, DUPLICATE_STRATEGY_VERSION, ALLOWED_TRANSITIONS
from src.campaigns.errors import CampaignNotFoundError, InvalidStateTransitionError, ConcurrencyConflictError, DuplicateCampaignError

# Auto-create tables on startup if not present
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="WhatsApp MT5 XAUUSD Trading Service",
    version="1.0.0",
    description="Python core orchestration service for trade signals, deterministic parser, campaign state machine, database persistence, and MT5 adapter."
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

class ApproveCampaignRequest(BaseModel):
    expected_version: Optional[int] = 1

class RejectCampaignRequest(BaseModel):
    reason: Optional[str] = "User rejected campaign"
    expected_version: Optional[int] = 1

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
        "state_machine_version": STATE_MACHINE_VERSION,
        "duplicate_strategy_version": DUPLICATE_STRATEGY_VERSION,
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

# Campaign API Endpoints
@app.get("/api/v1/campaigns/state-machine/version")
async def get_state_machine_version():
    return {
        "state_machine_version": STATE_MACHINE_VERSION,
        "contract_version": CONTRACT_VERSION
    }

@app.get("/api/v1/campaigns/state-machine")
async def get_state_machine_rules():
    return {
        "state_machine_version": STATE_MACHINE_VERSION,
        "allowed_transitions": {k: list(v) for k, v in ALLOWED_TRANSITIONS.items()}
    }

@app.get("/api/v1/duplicates/version")
async def get_duplicates_version():
    return {
        "duplicate_strategy_version": DUPLICATE_STRATEGY_VERSION,
        "window_hours": 24
    }

@app.get("/api/v1/campaigns")
async def list_campaigns(limit: int = 50, state: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(CampaignModel)
    if state:
        query = query.filter(CampaignModel.current_state == state)
    campaigns = query.order_by(CampaignModel.created_at.desc()).limit(limit).all()
    
    service = CampaignService()
    return [service._to_campaign_dict(c) for c in campaigns]

@app.get("/api/v1/campaigns/{campaign_id}")
async def get_campaign(campaign_id: str, db: Session = Depends(get_db)):
    campaign = db.get(CampaignModel, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    service = CampaignService()
    return service._to_campaign_dict(campaign)

@app.get("/api/v1/campaigns/{campaign_id}/transitions")
async def get_campaign_transitions(campaign_id: str, db: Session = Depends(get_db)):
    transitions = (
        db.query(CampaignStateTransitionModel)
        .filter(CampaignStateTransitionModel.campaign_id == campaign_id)
        .order_by(CampaignStateTransitionModel.transitioned_at.asc())
        .all()
    )
    return [
        {
            "id": t.id,
            "campaign_id": t.campaign_id,
            "from_state": t.from_state,
            "to_state": t.to_state,
            "reason_code": t.reason_code,
            "reason": t.reason,
            "trigger_type": t.trigger_type,
            "trigger_reference_id": t.trigger_reference_id,
            "correlation_id": t.correlation_id,
            "transitioned_at": t.transitioned_at.isoformat()
        }
        for t in transitions
    ]

@app.get("/api/v1/campaigns/{campaign_id}/commands")
async def get_campaign_commands(campaign_id: str, db: Session = Depends(get_db)):
    cmds = (
        db.query(CommandModel)
        .filter(CommandModel.campaign_id == campaign_id)
        .order_by(CommandModel.executed_at.asc())
        .all()
    )
    import json
    return [
        {
            "id": c.id,
            "campaign_id": c.campaign_id,
            "raw_message_id": c.raw_message_id,
            "command_type": c.command_type,
            "parameters": json.loads(c.parameters_json),
            "executed_at": c.executed_at.isoformat()
        }
        for c in cmds
    ]

@app.get("/api/v1/campaigns/{campaign_id}/duplicate-records")
async def get_campaign_duplicate_records(campaign_id: str, db: Session = Depends(get_db)):
    keys = db.query(DuplicateKeyModel).all()
    return [
        {
            "dedup_key": k.dedup_key,
            "duplicate_type": k.duplicate_type,
            "message_id": k.message_id,
            "created_at": k.created_at.isoformat()
        }
        for k in keys
    ]

@app.post("/api/v1/campaigns/from-message/{raw_message_id}")
async def create_campaign_from_message_endpoint(raw_message_id: str, response: Response):
    service = CampaignService()
    try:
        campaign_dict, is_dup = service.create_campaign_from_message(raw_message_id)
        response.status_code = status.HTTP_200_OK if is_dup else status.HTTP_201_CREATED
        return campaign_dict
    except ValueError as ve:
        raise HTTPException(status_code=422, detail=str(ve))

@app.post("/api/v1/campaigns/{campaign_id}/approve")
async def approve_campaign_endpoint(campaign_id: str, req: ApproveCampaignRequest):
    service = CampaignService()
    try:
        return service.approve_campaign(campaign_id, expected_version=req.expected_version or 1)
    except CampaignNotFoundError:
        raise HTTPException(status_code=404, detail="Campaign not found")
    except ConcurrencyConflictError as cce:
        raise HTTPException(status_code=409, detail=str(cce))
    except InvalidStateTransitionError as iste:
        raise HTTPException(status_code=409, detail=str(iste))

@app.post("/api/v1/campaigns/{campaign_id}/reject")
async def reject_campaign_endpoint(campaign_id: str, req: RejectCampaignRequest):
    service = CampaignService()
    try:
        return service.reject_campaign(campaign_id, reason=req.reason or "User rejected campaign", expected_version=req.expected_version or 1)
    except CampaignNotFoundError:
        raise HTTPException(status_code=404, detail="Campaign not found")
    except ConcurrencyConflictError as cce:
        raise HTTPException(status_code=409, detail=str(cce))
    except InvalidStateTransitionError as iste:
        raise HTTPException(status_code=409, detail=str(iste))

@app.post("/api/v1/campaigns/process-message/{raw_message_id}")
async def process_message_endpoint(raw_message_id: str):
    service = CampaignService()
    try:
        return service.process_message(raw_message_id)
    except ValueError as ve:
        raise HTTPException(status_code=422, detail=str(ve))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="127.0.0.1", port=8000, reload=True)
