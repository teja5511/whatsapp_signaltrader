from fastapi import FastAPI, HTTPException, Depends, Header, Query, status, Response
from pydantic import BaseModel, Field
import os
import json
import secrets
from typing import Optional, List, Dict, Any
from src.database.engine import engine, Base, SessionLocal
from src.database.repository import SettingsRepository, AuditLogRepository
from src.database.models import WhatsAppMessageModel, MT5ExecutionJobModel, MT5ExecutionBatchModel
from src.parser.service import MessageParsingService
from src.campaigns.service import CampaignService
from src.campaigns.errors import CampaignNotFoundError, ConcurrencyConflictError, InvalidStateTransitionError
from src.planning.service import PlanningService
from src.planning.constants import PLANNER_VERSION, RISK_ENGINE_VERSION
from src.planning.policies import get_production_default_policies, get_test_fixture_policies
from src.planning.errors import RiskValidationError, ReplanNotAllowedError
from src.mt5.execution_service import MT5ExecutionService
from src.mt5.execution_worker import MT5ExecutionWorker
from src.mt5.order_service import MT5OrderService
from src.mt5.position_service import MT5PositionService
from src.mt5.constants import MT5_ADAPTER_VERSION, EXECUTION_WORKER_VERSION
from src.mt5.contracts import (
    Mt5CampaignExecutionRequestDTO, Mt5OrderModificationRequestDTO,
    Mt5PositionModificationRequestDTO, Mt5PositionCloseRequestDTO,
    Mt5EmergencyCloseRequestDTO
)

# Initialize Database Schema
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="WhatsApp-to-MT5 XAUUSD Trading Service",
    version="1.0.0",
    description="Local FastAPI service executing WhatsApp signal parsing, campaign state machine, entry planning, and MT5 demo execution worker."
)

parse_service = MessageParsingService(session_factory=SessionLocal)
campaign_service = CampaignService(session_factory=SessionLocal)
planning_service = PlanningService(session_factory=SessionLocal)
mt5_service = MT5ExecutionService(session_factory=SessionLocal)
mt5_worker = MT5ExecutionWorker(adapter=mt5_service.adapter, session_factory=SessionLocal)
order_service = MT5OrderService(adapter=mt5_service.adapter, session_factory=SessionLocal)
position_service = MT5PositionService(adapter=mt5_service.adapter, session_factory=SessionLocal)

LOCAL_API_TOKEN = os.getenv("LOCAL_API_TOKEN", "dev-local-secret-token")

def verify_local_token(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Bearer authorization header.")
    token = authorization.split("Bearer ", 1)[1].strip()
    if not secrets.compare_digest(token, LOCAL_API_TOKEN):
        raise HTTPException(status_code=401, detail="Unauthorized local API token.")

# Health & System Endpoints
@app.get("/health", status_code=status.HTTP_200_OK)
def get_health():
    return {
        "status": "ok",
        "service": "trading-service",
        "version": "1.0.0",
        "trading_enabled": False,
        "mt5_connected": mt5_service.adapter.is_initialized(),
        "whatsapp_connected": False
    }

@app.get("/api/v1/status", status_code=status.HTTP_200_OK)
def get_status():
    return {
        "status": "ok",
        "service": "trading-service",
        "instrument": "XAUUSD",
        "max_exposure_lots": 2.00,
        "trading_enabled": False
    }

@app.get("/api/v1/audit-logs", status_code=status.HTTP_200_OK)
def get_audit_logs():
    db = SessionLocal()
    try:
        repo = AuditLogRepository(db)
        return [
            {
                "id": log.id,
                "event_type": log.event_type,
                "payload": log.payload_json,
                "created_at": log.created_at.isoformat()
            }
            for log in repo.list_logs()
        ]
    finally:
        db.close()

@app.get("/api/v1/settings")
def get_app_settings():
    db = SessionLocal()
    try:
        repo = SettingsRepository(db)
        s = repo.get_settings()
        return {
            "entry_count": s.entry_count,
            "lot_per_entry": float(s.lot_per_entry),
            "max_exposure_lots": float(s.max_exposure_lots),
            "execution_mode": s.execution_mode.value,
            "target_group_jid": s.target_group_jid,
            "admin_sender_jid": s.admin_sender_jid,
            "trading_enabled": False
        }
    finally:
        db.close()

# Parser Endpoints
class ParseRawMessageRequest(BaseModel):
    messageId: str = "preview-msg"
    groupId: str = "preview-group"
    senderId: str = "preview-sender"
    text: str
    quotedMessageId: Optional[str] = None
    isReply: bool = False

@app.get("/api/v1/parser/version")
def get_parser_version():
    return {"parser_version": "1.0.0", "deterministic": True}

@app.post("/api/v1/parser/preview")
def preview_parser(req: ParseRawMessageRequest):
    return parse_service.parse_stateless(
        text=req.text,
        message_id=req.messageId,
        group_id=req.groupId,
        sender_id=req.senderId,
        quoted_message_id=req.quotedMessageId,
        is_reply=req.isReply
    )

@app.get("/api/v1/parser/messages")
def get_parser_messages():
    db = SessionLocal()
    try:
        messages = db.query(WhatsAppMessageModel).order_by(WhatsAppMessageModel.received_at.desc()).all()
        return [
            {
                "id": m.id,
                "group_id": m.group_id,
                "sender_id": m.sender_id,
                "raw_content": m.raw_content,
                "received_at": m.received_at.isoformat()
            }
            for m in messages
        ]
    finally:
        db.close()

@app.get("/api/v1/parser/messages/{message_id}")
def get_parser_message_detail(message_id: str):
    db = SessionLocal()
    try:
        m = db.get(WhatsAppMessageModel, message_id)
        if not m:
            raise HTTPException(status_code=404, detail="Message not found")
        parsed_res = json.loads(m.parsed_message.parsed_json) if m.parsed_message else {}
        return {
            "id": m.id,
            "raw_message_id": m.id,
            "group_id": m.group_id,
            "sender_id": m.sender_id,
            "raw_content": m.raw_content,
            "parsed_result": parsed_res,
            "received_at": m.received_at.isoformat()
        }
    finally:
        db.close()

@app.post("/api/v1/parser/parse-raw", status_code=status.HTTP_200_OK)
def parse_raw_text(req: ParseRawMessageRequest):
    return parse_service.parse_stateless(
        text=req.text,
        message_id=req.messageId,
        group_id=req.groupId,
        sender_id=req.senderId,
        quoted_message_id=req.quotedMessageId,
        is_reply=req.isReply
    )

@app.post("/api/v1/parser/messages", status_code=status.HTTP_201_CREATED)
def parse_and_persist_message(req: ParseRawMessageRequest):
    parse_res, is_dup = parse_service.parse_and_persist(
        raw_text=req.text,
        message_id=req.messageId,
        group_id=req.groupId,
        sender_id=req.senderId,
        quoted_message_id=req.quotedMessageId,
        is_reply=req.isReply
    )
    category = parse_res.get("category")
    command = parse_res.get("command")
    signal = parse_res.get("signal")
    return {
        "message_id": req.messageId,
        "group_id": req.groupId,
        "category": category,
        "command": command,
        "signal": signal,
        "is_duplicate": is_dup,
        "parse_result": parse_res
    }

# Campaign Endpoints
@app.get("/api/v1/campaigns")
def list_campaigns():
    return campaign_service.list_campaigns()

@app.get("/api/v1/campaigns/state-machine/version")
def get_state_machine_version():
    return {"state_machine_version": "1.0.0"}

@app.get("/api/v1/campaigns/state-machine")
def get_state_machine():
    from src.campaigns.constants import STATE_MACHINE_VERSION, ALLOWED_TRANSITIONS
    return {
        "state_machine_version": STATE_MACHINE_VERSION,
        "allowed_transitions": ALLOWED_TRANSITIONS
    }

@app.get("/api/v1/duplicates/version")
def get_duplicate_version():
    return {"duplicate_strategy_version": "1.0.0", "window_hours": 24}

@app.get("/api/v1/campaigns/{campaign_id}")
def get_campaign_detail(campaign_id: str):
    c = campaign_service.get_campaign(campaign_id)
    if not c:
        raise HTTPException(status_code=404, detail=f"Campaign '{campaign_id}' not found.")
    return c

@app.get("/api/v1/campaigns/{campaign_id}/transitions")
def get_campaign_transitions(campaign_id: str):
    return campaign_service.get_campaign_transitions(campaign_id)

@app.get("/api/v1/campaigns/{campaign_id}/commands")
def get_campaign_commands(campaign_id: str):
    return campaign_service.get_campaign_commands(campaign_id)

@app.post("/api/v1/campaigns/from-message/{raw_message_id}")
def create_campaign_from_message(raw_message_id: str):
    c_dict, is_dup = campaign_service.create_campaign_from_message(raw_message_id)
    if is_dup:
        return {"status": "duplicate", "campaign": c_dict}
    return c_dict

class ActionRequest(BaseModel):
    expected_version: int = 1

@app.post("/api/v1/campaigns/{campaign_id}/approve")
def approve_campaign(campaign_id: str, req: ActionRequest):
    try:
        return campaign_service.approve_campaign(campaign_id, req.expected_version)
    except CampaignNotFoundError:
        raise HTTPException(status_code=404, detail="Campaign not found.")
    except ConcurrencyConflictError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except InvalidStateTransitionError as e:
        raise HTTPException(status_code=422, detail=str(e))

@app.post("/api/v1/campaigns/{campaign_id}/reject")
def reject_campaign(campaign_id: str, req: ActionRequest):
    try:
        return campaign_service.reject_campaign(campaign_id, req.expected_version)
    except CampaignNotFoundError:
        raise HTTPException(status_code=404, detail="Campaign not found.")
    except ConcurrencyConflictError as e:
        raise HTTPException(status_code=409, detail=str(e))

@app.post("/api/v1/campaigns/process-message/{raw_message_id}")
def process_message_for_campaigns(raw_message_id: str):
    return campaign_service.process_message(raw_message_id)

# Planning Endpoints
@app.get("/api/v1/planning/version")
def get_planning_version():
    return {
        "planner_version": PLANNER_VERSION,
        "risk_engine_version": RISK_ENGINE_VERSION
    }

@app.get("/api/v1/planning/policies")
def get_planning_policies():
    return get_production_default_policies().to_dict()

class PlanningPreviewRequest(BaseModel):
    direction: str = "SELL"
    order_intent: str = "LIMIT"
    entry_count: int = 5
    lot_per_entry: float = 0.30
    maximum_total_lots: float = 2.00
    zone_low: float = 3990.00
    zone_high: float = 3998.00
    stop_loss: float = 4008.00
    tp1: Optional[float] = 3960.00
    tp2: Optional[float] = 3950.00

@app.post("/api/v1/planning/preview")
def preview_planning(req: PlanningPreviewRequest):
    return planning_service.preview_plan(
        direction=req.direction,
        order_intent=req.order_intent,
        entry_count=req.entry_count,
        lot_per_entry=req.lot_per_entry,
        maximum_total_lots=req.maximum_total_lots,
        zone_low=req.zone_low,
        zone_high=req.zone_high,
        stop_loss=req.stop_loss,
        tp1=req.tp1,
        tp2=req.tp2,
        policies=get_test_fixture_policies()
    )

@app.post("/api/v1/campaigns/{campaign_id}/plan", status_code=status.HTTP_201_CREATED)
def plan_campaign(campaign_id: str, response: Response):
    try:
        plan_res, is_idempotent = planning_service.plan_campaign(
            campaign_id=campaign_id,
            policies=get_test_fixture_policies()
        )
        if is_idempotent:
            response.status_code = status.HTTP_200_OK
        return plan_res
    except CampaignNotFoundError:
        raise HTTPException(status_code=404, detail="Campaign not found.")
    except RiskValidationError as e:
        raise HTTPException(status_code=422, detail={"message": str(e), "issues": e.issues})

@app.get("/api/v1/campaigns/{campaign_id}/plan")
def get_campaign_plan(campaign_id: str):
    try:
        return planning_service.get_campaign_plan(campaign_id)
    except CampaignNotFoundError:
        raise HTTPException(status_code=404, detail="Campaign not found.")

@app.get("/api/v1/campaigns/{campaign_id}/planned-entries")
def get_planned_entries(campaign_id: str):
    try:
        res = planning_service.get_campaign_plan(campaign_id)
        return res["planned_entries"]
    except CampaignNotFoundError:
        raise HTTPException(status_code=404, detail="Campaign not found.")

# MT5 Endpoints
@app.get("/api/v1/mt5/version")
def get_mt5_version():
    return {
        "mt5_adapter_version": MT5_ADAPTER_VERSION,
        "execution_worker_version": EXECUTION_WORKER_VERSION
    }

@app.get("/api/v1/mt5/status")
def get_mt5_status():
    return mt5_service.adapter.get_status().model_dump(mode="json")

@app.get("/api/v1/mt5/terminal")
def get_mt5_terminal_info():
    return mt5_service.adapter.terminal_info().model_dump(mode="json")

@app.get("/api/v1/mt5/account")
def get_mt5_account_info():
    return mt5_service.adapter.account_info().model_dump(mode="json")

@app.get("/api/v1/mt5/symbol")
def get_mt5_symbol_resolution():
    return mt5_service.adapter.resolve_symbol().model_dump(mode="json")

@app.get("/api/v1/mt5/symbol/specification")
def get_mt5_symbol_spec():
    return mt5_service.adapter.symbol_specification().model_dump(mode="json")

@app.post("/api/v1/mt5/initialize")
def initialize_mt5(auth: None = Depends(verify_local_token)):
    ok = mt5_service.adapter.initialize()
    return {"status": "initialized" if ok else "failed", "health_state": mt5_service.adapter.health_state}

@app.post("/api/v1/mt5/shutdown")
def shutdown_mt5(auth: None = Depends(verify_local_token)):
    mt5_service.adapter.shutdown()
    return {"status": "shutdown"}

@app.post("/api/v1/mt5/synchronize")
def synchronize_mt5(campaign_id: Optional[str] = None, auth: None = Depends(verify_local_token)):
    if campaign_id:
        return mt5_service.synchronize_campaign(campaign_id)
    return {"status": "synced", "orders_count": len(mt5_service.adapter.orders_get()), "positions_count": len(mt5_service.adapter.positions_get())}

@app.post("/api/v1/mt5/execution/preflight/{campaign_id}")
def execution_preflight(campaign_id: str):
    return mt5_service.run_preflight(campaign_id).model_dump(mode="json")

@app.post("/api/v1/mt5/execution/campaigns/{campaign_id}", status_code=status.HTTP_202_ACCEPTED)
def execute_campaign(
    campaign_id: str,
    req: Mt5CampaignExecutionRequestDTO,
    auth: None = Depends(verify_local_token)
):
    try:
        res, is_dup = mt5_service.queue_campaign_execution(
            campaign_id=campaign_id,
            expected_version=req.expected_version,
            planning_fingerprint=req.planning_fingerprint,
            explicit_user_confirm=req.explicit_user_confirm
        )
        return res.model_dump(mode="json")
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

@app.get("/api/v1/mt5/execution/jobs")
def list_execution_jobs():
    db = SessionLocal()
    try:
        jobs = db.query(MT5ExecutionJobModel).order_by(MT5ExecutionJobModel.created_at.desc()).all()
        return [
            {
                "id": j.id,
                "batch_id": j.batch_id,
                "campaign_id": j.campaign_id,
                "planned_entry_id": j.planned_entry_id,
                "operation_type": j.operation_type,
                "status": j.status,
                "created_at": j.created_at.isoformat()
            }
            for j in jobs
        ]
    finally:
        db.close()

@app.get("/api/v1/mt5/execution/jobs/{job_id}")
def get_execution_job(job_id: str):
    db = SessionLocal()
    try:
        j = db.get(MT5ExecutionJobModel, job_id)
        if not j:
            raise HTTPException(status_code=404, detail="Execution job not found.")
        return {
            "id": j.id,
            "batch_id": j.batch_id,
            "campaign_id": j.campaign_id,
            "planned_entry_id": j.planned_entry_id,
            "operation_type": j.operation_type,
            "idempotency_key": j.idempotency_key,
            "status": j.status,
            "attempt_count": j.attempt_count,
            "result_json": json.loads(j.result_json) if j.result_json else None,
            "last_error_code": j.last_error_code,
            "last_error_message": j.last_error_message,
            "created_at": j.created_at.isoformat()
        }
    finally:
        db.close()

@app.get("/api/v1/mt5/execution/batches/{batch_id}")
def get_execution_batch(batch_id: str):
    db = SessionLocal()
    try:
        b = db.get(MT5ExecutionBatchModel, batch_id)
        if not b:
            raise HTTPException(status_code=404, detail="Execution batch not found.")
        return {
            "id": b.id,
            "campaign_id": b.campaign_id,
            "campaign_version": b.campaign_version,
            "planning_fingerprint": b.planning_fingerprint,
            "status": b.status,
            "total_jobs": b.total_jobs,
            "completed_jobs": b.completed_jobs,
            "failed_jobs": b.failed_jobs,
            "created_at": b.created_at.isoformat()
        }
    finally:
        db.close()

@app.post("/api/v1/mt5/execution/jobs/{job_id}/cancel")
def cancel_execution_job(job_id: str, auth: None = Depends(verify_local_token)):
    db = SessionLocal()
    try:
        j = db.get(MT5ExecutionJobModel, job_id)
        if not j:
            raise HTTPException(status_code=404, detail="Job not found.")
        j.status = "CANCELLED"
        db.commit()
        return {"status": "cancelled", "job_id": job_id}
    finally:
        db.close()

@app.post("/api/v1/mt5/orders/{order_ticket}/modify")
def modify_order(order_ticket: int, req: Mt5OrderModificationRequestDTO, auth: None = Depends(verify_local_token)):
    try:
        return order_service.modify_order(order_ticket, price=req.price, stop_loss=req.stop_loss, take_profit=req.take_profit)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

@app.delete("/api/v1/mt5/orders/{order_ticket}")
def delete_order(order_ticket: int, auth: None = Depends(verify_local_token)):
    try:
        return order_service.delete_order(order_ticket)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

@app.post("/api/v1/mt5/campaigns/{campaign_id}/cancel-pending")
def cancel_campaign_pending(campaign_id: str, auth: None = Depends(verify_local_token)):
    try:
        return order_service.cancel_campaign_pending_orders(campaign_id)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

@app.post("/api/v1/mt5/positions/{position_ticket}/modify-sltp")
def modify_position_sltp(position_ticket: int, req: Mt5PositionModificationRequestDTO, auth: None = Depends(verify_local_token)):
    try:
        return position_service.modify_position_sltp(position_ticket, stop_loss=req.stop_loss, take_profit=req.take_profit)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

@app.post("/api/v1/mt5/positions/{position_ticket}/close")
def close_position(position_ticket: int, req: Optional[Mt5PositionCloseRequestDTO] = None, auth: None = Depends(verify_local_token)):
    try:
        vol = req.volume if req else None
        return position_service.close_position(position_ticket, volume=vol)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

@app.post("/api/v1/mt5/campaigns/{campaign_id}/close")
def close_campaign(campaign_id: str, auth: None = Depends(verify_local_token)):
    try:
        return position_service.close_campaign_positions(campaign_id)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

@app.post("/api/v1/mt5/emergency/close-all-xauusd")
def emergency_close_all(req: Mt5EmergencyCloseRequestDTO, auth: None = Depends(verify_local_token)):
    try:
        return mt5_service.emergency_close_all_xauusd(confirmation_phrase=req.confirmation_phrase, scope=req.scope)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
