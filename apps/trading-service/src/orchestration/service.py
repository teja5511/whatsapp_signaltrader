from typing import Optional, List, Dict, Any
from src.database.engine import SessionLocal
from src.database.unit_of_work import UnitOfWork
from src.database.models import OrchestrationRunModel, OrchestrationStepModel, DomainEventModel
from src.orchestration.coordinator import OrchestrationCoordinator
from src.orchestration.status_aggregation import SystemStatusAggregator
from src.orchestration.policies import ControlPolicyManager

class OrchestrationService:
    def __init__(self, session_factory=SessionLocal):
        self.session_factory = session_factory
        self.coordinator = OrchestrationCoordinator(session_factory=session_factory)
        self.status_aggregator = SystemStatusAggregator(session_factory=session_factory)
        self.control_manager = ControlPolicyManager(session_factory=session_factory)

    def list_runs(self, limit: int = 50) -> List[Dict[str, Any]]:
        with UnitOfWork(session_factory=self.session_factory) as uow:
            runs = uow.db.query(OrchestrationRunModel).order_by(OrchestrationRunModel.created_at.desc()).limit(limit).all()
            return [
                {
                    "id": r.id,
                    "orchestrator_version": r.orchestrator_version,
                    "source_type": r.source_type,
                    "source_id": r.source_id,
                    "correlation_id": r.correlation_id,
                    "campaign_id": r.campaign_id,
                    "status": r.status,
                    "current_step": r.current_step,
                    "created_at": r.created_at.isoformat()
                }
                for r in runs
            ]

    def get_run_detail(self, run_id: str) -> Optional[Dict[str, Any]]:
        with UnitOfWork(session_factory=self.session_factory) as uow:
            r = uow.db.get(OrchestrationRunModel, run_id)
            if not r:
                return None
            steps = uow.db.query(OrchestrationStepModel).filter(OrchestrationStepModel.orchestration_run_id == run_id).order_by(OrchestrationStepModel.sequence.asc()).all()
            return {
                "id": r.id,
                "orchestrator_version": r.orchestrator_version,
                "source_type": r.source_type,
                "source_id": r.source_id,
                "correlation_id": r.correlation_id,
                "causation_id": r.causation_id,
                "campaign_id": r.campaign_id,
                "command_id": r.command_id,
                "status": r.status,
                "current_step": r.current_step,
                "started_at": r.started_at.isoformat(),
                "completed_at": r.completed_at.isoformat() if r.completed_at else None,
                "steps": [
                    {
                        "id": s.id,
                        "sequence": s.sequence,
                        "step_name": s.step_name,
                        "status": s.status,
                        "started_at": s.started_at.isoformat(),
                        "completed_at": s.completed_at.isoformat() if s.completed_at else None
                    }
                    for s in steps
                ]
            }
