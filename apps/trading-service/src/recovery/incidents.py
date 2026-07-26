import json
from uuid import uuid4
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from src.database.engine import SessionLocal
from src.database.unit_of_work import UnitOfWork
from src.database.models import HealthIncidentModel

class HealthIncidentDTO(BaseModel):
    id: str
    incident_kind: str
    severity: str = "WARNING"
    status: str = "OPEN"
    title: str
    detail: Dict[str, Any] = Field(default_factory=dict)
    occurrence_count: int = 1
    first_seen_at: datetime
    last_seen_at: datetime
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None
    resolved_at: Optional[datetime] = None

class HealthIncidentManager:
    def __init__(self, session_factory=SessionLocal):
        self.session_factory = session_factory

    def record_incident(
        self,
        incident_kind: str,
        title: str,
        severity: str = "WARNING",
        detail: Optional[Dict[str, Any]] = None,
        session: Optional[Session] = None
    ) -> HealthIncidentDTO:
        now_utc = datetime.now(timezone.utc)
        det_json = json.dumps(detail or {})

        with UnitOfWork(session_factory=self.session_factory, session=session) as uow:
            existing = uow.db.query(HealthIncidentModel).filter(
                HealthIncidentModel.incident_kind == incident_kind,
                HealthIncidentModel.status.in_(["OPEN", "ACKNOWLEDGED"])
            ).first()

            if existing:
                existing.occurrence_count += 1
                existing.last_seen_at = now_utc
                existing.detail_json = det_json
                inc = existing
            else:
                inc = HealthIncidentModel(
                    id=str(uuid4()),
                    incident_kind=incident_kind,
                    severity=severity,
                    status="OPEN",
                    title=title,
                    detail_json=det_json,
                    occurrence_count=1,
                    first_seen_at=now_utc,
                    last_seen_at=now_utc
                )
                uow.db.add(inc)

            uow.audit.log_event("HEALTH_INCIDENT_RECORDED", {
                "incident_kind": incident_kind,
                "severity": severity,
                "title": title
            })

            return HealthIncidentDTO(
                id=inc.id,
                incident_kind=inc.incident_kind,
                severity=inc.severity,
                status=inc.status,
                title=inc.title,
                detail=json.loads(inc.detail_json),
                occurrence_count=inc.occurrence_count,
                first_seen_at=inc.first_seen_at,
                last_seen_at=inc.last_seen_at,
                acknowledged_at=inc.acknowledged_at,
                acknowledged_by=inc.acknowledged_by,
                resolved_at=inc.resolved_at
            )

    def acknowledge_incident(
        self,
        incident_id: str,
        actor: str = "OPERATOR",
        session: Optional[Session] = None
    ) -> HealthIncidentDTO:
        now_utc = datetime.now(timezone.utc)
        with UnitOfWork(session_factory=self.session_factory, session=session) as uow:
            inc = uow.db.get(HealthIncidentModel, incident_id)
            if not inc:
                raise ValueError(f"Health incident '{incident_id}' not found.")

            inc.status = "ACKNOWLEDGED"
            inc.acknowledged_at = now_utc
            inc.acknowledged_by = actor

            uow.audit.log_event("HEALTH_INCIDENT_ACKNOWLEDGED", {"incident_id": incident_id, "actor": actor})

            return HealthIncidentDTO(
                id=inc.id,
                incident_kind=inc.incident_kind,
                severity=inc.severity,
                status=inc.status,
                title=inc.title,
                detail=json.loads(inc.detail_json),
                occurrence_count=inc.occurrence_count,
                first_seen_at=inc.first_seen_at,
                last_seen_at=inc.last_seen_at,
                acknowledged_at=inc.acknowledged_at,
                acknowledged_by=inc.acknowledged_by,
                resolved_at=inc.resolved_at
            )

    def resolve_incident(
        self,
        incident_id: str,
        session: Optional[Session] = None
    ) -> HealthIncidentDTO:
        now_utc = datetime.now(timezone.utc)
        with UnitOfWork(session_factory=self.session_factory, session=session) as uow:
            inc = uow.db.get(HealthIncidentModel, incident_id)
            if not inc:
                raise ValueError(f"Health incident '{incident_id}' not found.")

            inc.status = "RESOLVED"
            inc.resolved_at = now_utc

            uow.audit.log_event("HEALTH_INCIDENT_RESOLVED", {"incident_id": incident_id})

            return HealthIncidentDTO(
                id=inc.id,
                incident_kind=inc.incident_kind,
                severity=inc.severity,
                status=inc.status,
                title=inc.title,
                detail=json.loads(inc.detail_json),
                occurrence_count=inc.occurrence_count,
                first_seen_at=inc.first_seen_at,
                last_seen_at=inc.last_seen_at,
                acknowledged_at=inc.acknowledged_at,
                acknowledged_by=inc.acknowledged_by,
                resolved_at=inc.resolved_at
            )

    def list_incidents(
        self,
        status: Optional[str] = None,
        limit: int = 50,
        session: Optional[Session] = None
    ) -> List[HealthIncidentDTO]:
        with UnitOfWork(session_factory=self.session_factory, session=session) as uow:
            query = uow.db.query(HealthIncidentModel)
            if status:
                query = query.filter(HealthIncidentModel.status == status)
            incidents = query.order_by(HealthIncidentModel.last_seen_at.desc()).limit(limit).all()

            return [
                HealthIncidentDTO(
                    id=inc.id,
                    incident_kind=inc.incident_kind,
                    severity=inc.severity,
                    status=inc.status,
                    title=inc.title,
                    detail=json.loads(inc.detail_json) if inc.detail_json else {},
                    occurrence_count=inc.occurrence_count,
                    first_seen_at=inc.first_seen_at,
                    last_seen_at=inc.last_seen_at,
                    acknowledged_at=inc.acknowledged_at,
                    acknowledged_by=inc.acknowledged_by,
                    resolved_at=inc.resolved_at
                )
                for inc in incidents
            ]
