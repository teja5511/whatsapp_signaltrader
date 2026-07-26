import json
import logging
from uuid import uuid4
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.orm import Session

from src.database.engine import SessionLocal
from src.database.unit_of_work import UnitOfWork
from src.database.models import (
    OrchestrationRunModel, OrchestrationStepModel, CampaignModel, SignalModel,
    CommandModel, AmbiguousCommandConfirmationModel, ControlStateModel, PlannedEntryModel
)
from src.parser.service import MessageParsingService
from src.campaigns.service import CampaignService
from src.campaigns.constants import (
    STATE_AWAITING_CONFIRMATION, STATE_PLANNED, STATE_WAITING_FOR_TP,
    REASON_CONFIRMATION_REQUIRED, REASON_AUTOMATIC_PLAN_APPROVED,
    TRIGGER_SYSTEM, TRIGGER_USER_ACTION,
)
from src.campaigns.state_machine import apply_transition
from src.planning.service import PlanningService
from src.planning.errors import RiskValidationError
from src.mt5.execution_service import MT5ExecutionService
from src.policies import PolicyService, COMMAND_BLOCKING_KEYS, POLICY_BY_KEY
from src.events.outbox import OutboxPublisher
from src.events.constants import (
    EVENT_MESSAGE_RECEIVED, EVENT_MESSAGE_PARSED, EVENT_SIGNAL_INCOMPLETE, EVENT_SIGNAL_COMPLETE,
    EVENT_CAMPAIGN_CREATED, EVENT_CAMPAIGN_AWAITING_CONFIRMATION, EVENT_CAMPAIGN_WAITING_FOR_TP,
    EVENT_CAMPAIGN_APPROVED, EVENT_CAMPAIGN_REJECTED, EVENT_CAMPAIGN_PLANNED, EVENT_CAMPAIGN_EXECUTION_QUEUED,
    EVENT_COMMAND_RECEIVED, EVENT_COMMAND_MATCHED, EVENT_COMMAND_MATCH_AMBIGUOUS, EVENT_COMMAND_REQUIRES_CONFIRMATION,
    EVENT_COMMAND_COMPLETED, EVENT_TAKE_PROFIT_UPDATED, EVENT_STOP_LOSS_UPDATED, EVENT_PLAN_INVALIDATED,
    EVENT_REENTRY_CREATED, EVENT_CAMPAIGN_PLAN_BLOCKED,
)
from src.orchestration.constants import (
    ORCHESTRATOR_VERSION, RUN_STATUS_RECEIVED, RUN_STATUS_RUNNING, RUN_STATUS_WAITING, RUN_STATUS_SUCCEEDED,
    RUN_STATUS_BLOCKED, RUN_STATUS_FAILED, STEP_STATUS_RUNNING, STEP_STATUS_SUCCEEDED,
    STEP_STATUS_BLOCKED, STEP_STATUS_FAILED, AUTOMATION_RUNNING, MODE_AUTOMATIC
)
from src.orchestration.idempotency import generate_orchestration_run_idempotency_key

logger = logging.getLogger("orchestration_coordinator")


def uuid4_str() -> str:
    return str(uuid4())


class OrchestrationCoordinator:
    """Drives one WhatsApp message (or one user action) through the pipeline.

    Everything a single run writes - campaign rows, planned entries, execution
    jobs, orchestration steps and outbox events - happens inside one
    transaction on one session, so a failure anywhere rolls the whole run back
    instead of leaving a half-built campaign behind.
    """

    def __init__(self, session_factory=SessionLocal, mt5_service: Optional[MT5ExecutionService] = None):
        self.session_factory = session_factory
        self.parse_service = MessageParsingService(session_factory=session_factory)
        self.campaign_service = CampaignService(session_factory=session_factory)
        self.mt5_service = mt5_service or MT5ExecutionService(session_factory=session_factory)
        self.planning_service = PlanningService(
            session_factory=session_factory,
            price_provider=self.mt5_service.current_mid_price,
        )
        self.policy_service = PolicyService(session_factory=session_factory)

    def process_raw_message_id(self, raw_message_id: str, correlation_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Orchestrates an incoming parsed raw WhatsApp message.
        """
        corr_id = correlation_id or f"corr-{raw_message_id}"

        with UnitOfWork(session_factory=self.session_factory) as uow:
            existing_run = uow.db.query(OrchestrationRunModel).filter(
                OrchestrationRunModel.source_type == "WHATSAPP_MESSAGE",
                OrchestrationRunModel.source_id == raw_message_id
            ).first()

            if existing_run:
                return {
                    "status": "idempotent_existing",
                    "orchestration_run_id": existing_run.id,
                    "run_status": existing_run.status,
                    "campaign_id": existing_run.campaign_id
                }

            now_utc = datetime.now(timezone.utc)
            run = OrchestrationRunModel(
                id=uuid4_str(),
                orchestrator_version=ORCHESTRATOR_VERSION,
                source_type="WHATSAPP_MESSAGE",
                source_id=raw_message_id,
                correlation_id=corr_id,
                status=RUN_STATUS_RUNNING,
                current_step="PARSE_MESSAGE",
                input_payload_json=json.dumps({"raw_message_id": raw_message_id}),
                heartbeat_at=now_utc,
                started_at=now_utc,
                created_at=now_utc,
                updated_at=now_utc
            )
            uow.db.add(run)
            uow.db.flush()

            OutboxPublisher.publish_domain_event(
                db=uow.db,
                event_type=EVENT_MESSAGE_RECEIVED,
                aggregate_type="MESSAGE",
                aggregate_id=raw_message_id,
                correlation_id=corr_id,
                payload={"raw_message_id": raw_message_id}
            )

            try:
                step1 = self._add_step(uow.db, run.id, 1, "PARSE_MESSAGE")
                parse_res, is_dup = self.parse_service.get_parsed_message_by_raw_id(
                    raw_message_id, session=uow.db
                )
                self._complete_step(uow.db, step1, parse_res)

                category = parse_res.get("category")
                OutboxPublisher.publish_domain_event(
                    db=uow.db,
                    event_type=EVENT_MESSAGE_PARSED,
                    aggregate_type="MESSAGE",
                    aggregate_id=raw_message_id,
                    correlation_id=corr_id,
                    payload={"category": category, "is_executable": parse_res.get("is_executable")}
                )

                if category == "NEW_SIGNAL":
                    return self._orchestrate_new_signal(uow, run, parse_res, corr_id)
                elif category == "FOLLOW_UP_COMMAND":
                    return self._orchestrate_command(uow, run, parse_res, corr_id)
                elif category == "AMBIGUOUS":
                    return self._orchestrate_ambiguous(uow, run, parse_res, corr_id)
                else:
                    run.status = RUN_STATUS_SUCCEEDED
                    run.completed_at = datetime.now(timezone.utc)
                    return {"status": "success", "category": category, "orchestration_run_id": run.id}

            except Exception as e:
                # The whole run is rolled back by the enclosing UnitOfWork, so
                # the failure record is written on a fresh session afterwards.
                logger.error("Orchestration run '%s' failed: %s", run.id, e, exc_info=True)
                uow.rollback()
                return self._record_failed_run(raw_message_id, corr_id, str(e))

    def _record_failed_run(self, raw_message_id: str, corr_id: str, error: str) -> Dict[str, Any]:
        with UnitOfWork(session_factory=self.session_factory) as uow:
            now_utc = datetime.now(timezone.utc)
            run = OrchestrationRunModel(
                id=uuid4_str(),
                orchestrator_version=ORCHESTRATOR_VERSION,
                source_type="WHATSAPP_MESSAGE",
                source_id=raw_message_id,
                correlation_id=corr_id,
                status=RUN_STATUS_FAILED,
                current_step="FAILED",
                input_payload_json=json.dumps({"raw_message_id": raw_message_id}),
                error_code="ORCHESTRATION_EXCEPTION",
                error_message=error,
                started_at=now_utc,
                completed_at=now_utc,
                created_at=now_utc,
                updated_at=now_utc,
            )
            uow.db.add(run)
            uow.db.flush()
            return {"status": "failed", "error": error, "orchestration_run_id": run.id}

    def _orchestrate_new_signal(self, uow: UnitOfWork, run: OrchestrationRunModel, parse_res: Dict[str, Any], corr_id: str) -> Dict[str, Any]:
        step2 = self._add_step(uow.db, run.id, 2, "CREATE_CAMPAIGN")
        raw_msg_id = parse_res.get("sourceMetadata", {}).get("messageId", run.source_id)

        camp_dict, is_dup = self.campaign_service.create_campaign_from_message(
            raw_msg_id, correlation_id=corr_id, session=uow.db
        )
        self._complete_step(uow.db, step2, {"campaign_id": camp_dict["id"], "is_duplicate": is_dup})

        campaign_id = camp_dict["id"]
        run.campaign_id = campaign_id

        if is_dup:
            run.status = RUN_STATUS_BLOCKED
            run.error_code = "DUPLICATE_SIGNAL_BLOCKED"
            run.error_message = "Signal identified as duplicate."
            run.completed_at = datetime.now(timezone.utc)

            OutboxPublisher.publish_domain_event(
                db=uow.db,
                event_type="SIGNAL_DUPLICATE_BLOCKED",
                aggregate_type="CAMPAIGN",
                aggregate_id=campaign_id,
                correlation_id=corr_id,
                payload={"campaign_id": campaign_id},
                campaign_id=campaign_id
            )
            return {"status": "blocked_duplicate", "campaign_id": campaign_id, "orchestration_run_id": run.id}

        OutboxPublisher.publish_domain_event(
            db=uow.db,
            event_type=EVENT_CAMPAIGN_CREATED,
            aggregate_type="CAMPAIGN",
            aggregate_id=campaign_id,
            correlation_id=corr_id,
            payload=camp_dict,
            campaign_id=campaign_id
        )

        step3 = self._add_step(uow.db, run.id, 3, "EVALUATE_PIPELINE")
        campaign = uow.campaigns.get_by_id(campaign_id)

        # Gate 1: incomplete exit plan.
        if campaign.current_state == STATE_WAITING_FOR_TP:
            self._complete_step(uow.db, step3, {"result": STATE_WAITING_FOR_TP})
            run.status = RUN_STATUS_WAITING
            run.completed_at = datetime.now(timezone.utc)

            OutboxPublisher.publish_domain_event(
                db=uow.db,
                event_type=EVENT_CAMPAIGN_WAITING_FOR_TP,
                aggregate_type="CAMPAIGN",
                aggregate_id=campaign_id,
                correlation_id=corr_id,
                payload={"campaign_id": campaign_id},
                campaign_id=campaign_id
            )
            return {"status": "waiting_for_tp", "campaign_id": campaign_id, "orchestration_run_id": run.id}

        # Gate 2: automation, execution mode and trading toggles.
        ctrl = uow.db.get(ControlStateModel, 1)
        auto_state = ctrl.automation_state if ctrl else "PAUSED"
        trading_en = ctrl.trading_enabled if ctrl else False
        mt5_en = ctrl.mt5_execution_enabled if ctrl else False
        exec_mode_str = campaign.execution_mode.value if hasattr(campaign.execution_mode, "value") else str(campaign.execution_mode)

        requires_confirmation = (
            exec_mode_str != MODE_AUTOMATIC
            or auto_state != AUTOMATION_RUNNING
            or not trading_en
            or not mt5_en
        )

        if requires_confirmation:
            apply_transition(
                db=uow.db,
                campaign=campaign,
                to_state=STATE_AWAITING_CONFIRMATION,
                reason_code=REASON_CONFIRMATION_REQUIRED,
                reason=f"Mode={exec_mode_str}, automation={auto_state}, trading_enabled={trading_en}.",
                trigger_type=TRIGGER_SYSTEM,
                correlation_id=corr_id,
            )

            self._complete_step(uow.db, step3, {"result": STATE_AWAITING_CONFIRMATION, "reason": "CONFIRMATION_MODE_OR_PAUSED"})
            run.status = RUN_STATUS_WAITING
            run.completed_at = datetime.now(timezone.utc)

            OutboxPublisher.publish_domain_event(
                db=uow.db,
                event_type=EVENT_CAMPAIGN_AWAITING_CONFIRMATION,
                aggregate_type="CAMPAIGN",
                aggregate_id=campaign_id,
                correlation_id=corr_id,
                payload={"campaign_id": campaign_id, "mode": exec_mode_str, "auto_state": auto_state},
                campaign_id=campaign_id
            )
            return {"status": "awaiting_confirmation", "campaign_id": campaign_id, "orchestration_run_id": run.id}

        return self._execute_automatic_demo_pipeline(uow, run, campaign, corr_id)

    def _orchestrate_ambiguous(self, uow: UnitOfWork, run: OrchestrationRunModel, parse_res: Dict[str, Any], corr_id: str) -> Dict[str, Any]:
        """Ambiguous phrasing never executes. It always becomes a confirmation card."""
        step2 = self._add_step(uow.db, run.id, 2, "RECORD_AMBIGUOUS")
        conf_rec = AmbiguousCommandConfirmationModel(
            id=uuid4_str(),
            command_id=uuid4_str(),
            campaign_id=None,
            suggested_action="HUMAN_REVIEW_REQUIRED",
            original_text=parse_res.get("originalText", ""),
            match_type="AMBIGUOUS",
            status="PENDING",
            created_at=datetime.now(timezone.utc)
        )
        uow.db.add(conf_rec)
        uow.db.flush()
        self._complete_step(uow.db, step2, {"confirmation_id": conf_rec.id})

        run.status = RUN_STATUS_WAITING
        run.completed_at = datetime.now(timezone.utc)

        OutboxPublisher.publish_domain_event(
            db=uow.db,
            event_type=EVENT_COMMAND_MATCH_AMBIGUOUS,
            aggregate_type="COMMAND",
            aggregate_id=conf_rec.command_id,
            correlation_id=corr_id,
            payload={"confirmation_id": conf_rec.id, "text": parse_res.get("originalText")},
        )
        return {
            "status": "ambiguous_command_requires_confirmation",
            "confirmation_id": conf_rec.id,
            "orchestration_run_id": run.id,
        }

    def _orchestrate_command(self, uow: UnitOfWork, run: OrchestrationRunModel, parse_res: Dict[str, Any], corr_id: str) -> Dict[str, Any]:
        step2 = self._add_step(uow.db, run.id, 2, "PROCESS_COMMAND")
        raw_msg_id = parse_res.get("sourceMetadata", {}).get("messageId", run.source_id)

        res_dict = self.campaign_service.process_message(raw_msg_id, session=uow.db)
        self._complete_step(uow.db, step2, res_dict)

        c_results = res_dict.get("command_results", [])
        if not c_results:
            run.status = RUN_STATUS_SUCCEEDED
            run.completed_at = datetime.now(timezone.utc)
            return {"status": "no_commands_processed", "orchestration_run_id": run.id, "detail": res_dict}

        first_c = c_results[0]
        cmd_type = first_c.get("command_type")
        campaign_id = first_c.get("campaign_id")

        if campaign_id:
            run.campaign_id = campaign_id

        # A command governed by an unresolved policy is never acted on.
        blocking_key = self._command_policy_key(cmd_type)
        if blocking_key is not None:
            resolution = PolicyService.resolution_from_db(uow.db, blocking_key)
            if not resolution.is_resolved or resolution.selected_option == "REQUIRE_CONFIRMATION":
                return self._raise_command_confirmation(
                    uow, run, corr_id, cmd_type, campaign_id, parse_res,
                    reason="POLICY_UNRESOLVED" if not resolution.is_resolved else "POLICY_REQUIRES_CONFIRMATION",
                    policy_key=blocking_key,
                )

        if cmd_type == "AMBIGUOUS":
            return self._raise_command_confirmation(
                uow, run, corr_id, cmd_type, campaign_id, parse_res, reason="AMBIGUOUS"
            )

        if cmd_type == "ADD_TAKE_PROFIT" and campaign_id:
            campaign = uow.campaigns.get_by_id(campaign_id)
            if campaign and campaign.current_state != STATE_WAITING_FOR_TP:
                OutboxPublisher.publish_domain_event(
                    db=uow.db,
                    event_type=EVENT_TAKE_PROFIT_UPDATED,
                    aggregate_type="CAMPAIGN",
                    aggregate_id=campaign_id,
                    correlation_id=corr_id,
                    payload={
                        "campaign_id": campaign_id,
                        "tp1": str(campaign.tp1) if campaign.tp1 is not None else None,
                        "tp2": str(campaign.tp2) if campaign.tp2 is not None else None,
                    },
                    campaign_id=campaign_id
                )
                return self._orchestrate_new_signal(uow, run, parse_res, corr_id)

        OutboxPublisher.publish_domain_event(
            db=uow.db,
            event_type=EVENT_COMMAND_COMPLETED,
            aggregate_type="COMMAND",
            aggregate_id=first_c.get("command_id", raw_msg_id),
            correlation_id=corr_id,
            payload={"command_type": cmd_type, "campaign_id": campaign_id},
            campaign_id=campaign_id,
        )
        run.status = RUN_STATUS_SUCCEEDED
        run.completed_at = datetime.now(timezone.utc)
        return {"status": "command_orchestrated", "command_type": cmd_type, "orchestration_run_id": run.id}

    @staticmethod
    def _command_policy_key(command_type: Optional[str]) -> Optional[str]:
        if not command_type:
            return None
        for key in COMMAND_BLOCKING_KEYS:
            if command_type in POLICY_BY_KEY[key].applies_to_commands:
                return key
        return None

    def _raise_command_confirmation(
        self,
        uow: UnitOfWork,
        run: OrchestrationRunModel,
        corr_id: str,
        cmd_type: Optional[str],
        campaign_id: Optional[str],
        parse_res: Dict[str, Any],
        reason: str,
        policy_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        conf_rec = AmbiguousCommandConfirmationModel(
            id=uuid4_str(),
            command_id=uuid4_str(),
            campaign_id=campaign_id,
            suggested_action="HUMAN_REVIEW_REQUIRED",
            original_text=parse_res.get("originalText", ""),
            match_type=reason,
            status="PENDING",
            created_at=datetime.now(timezone.utc)
        )
        uow.db.add(conf_rec)
        uow.db.flush()

        run.status = RUN_STATUS_WAITING
        run.completed_at = datetime.now(timezone.utc)

        OutboxPublisher.publish_domain_event(
            db=uow.db,
            event_type=EVENT_COMMAND_REQUIRES_CONFIRMATION,
            aggregate_type="COMMAND",
            aggregate_id=conf_rec.command_id,
            correlation_id=corr_id,
            payload={
                "confirmation_id": conf_rec.id,
                "command_type": cmd_type,
                "reason": reason,
                "policy_key": policy_key,
                "text": parse_res.get("originalText"),
            },
            campaign_id=campaign_id
        )
        return {
            "status": "command_requires_confirmation",
            "reason": reason,
            "policy_key": policy_key,
            "confirmation_id": conf_rec.id,
            "orchestration_run_id": run.id,
        }

    def _execute_automatic_demo_pipeline(self, uow: UnitOfWork, run: OrchestrationRunModel, campaign: CampaignModel, corr_id: str) -> Dict[str, Any]:
        campaign_id = campaign.id

        step4 = self._add_step(uow.db, run.id, 4, "AUTO_PLAN_CAMPAIGN")
        if campaign.current_state == STATE_AWAITING_CONFIRMATION:
            apply_transition(
                db=uow.db,
                campaign=campaign,
                to_state=STATE_PLANNED,
                reason_code=REASON_AUTOMATIC_PLAN_APPROVED,
                reason="Automatic mode with automation running and demo trading enabled.",
                trigger_type=TRIGGER_SYSTEM,
                correlation_id=corr_id,
            )

        try:
            plan_res, _ = self.planning_service.plan_campaign(campaign_id, session=uow.db)
        except RiskValidationError as e:
            self._fail_step(uow.db, step4, "RISK_VALIDATION_BLOCKED", str(e))
            run.status = RUN_STATUS_BLOCKED
            run.error_code = "RISK_VALIDATION_BLOCKED"
            run.error_message = str(e)
            run.completed_at = datetime.now(timezone.utc)

            OutboxPublisher.publish_domain_event(
                db=uow.db,
                event_type=EVENT_CAMPAIGN_PLAN_BLOCKED,
                aggregate_type="CAMPAIGN",
                aggregate_id=campaign_id,
                correlation_id=corr_id,
                payload={"campaign_id": campaign_id, "issues": e.issues},
                campaign_id=campaign_id,
                severity="WARNING",
            )
            return {
                "status": "plan_blocked",
                "campaign_id": campaign_id,
                "issues": e.issues,
                "orchestration_run_id": run.id,
            }

        self._complete_step(uow.db, step4, plan_res)

        OutboxPublisher.publish_domain_event(
            db=uow.db,
            event_type=EVENT_CAMPAIGN_PLANNED,
            aggregate_type="CAMPAIGN",
            aggregate_id=campaign_id,
            correlation_id=corr_id,
            payload=plan_res,
            campaign_id=campaign_id
        )

        step5 = self._add_step(uow.db, run.id, 5, "PREFLIGHT_CHECK")
        preflight = self.mt5_service.run_preflight(campaign_id, session=uow.db)
        self._complete_step(uow.db, step5, preflight.model_dump(mode="json"))

        if not preflight.is_ready:
            run.status = RUN_STATUS_BLOCKED
            run.error_code = "PREFLIGHT_BLOCKED"
            run.error_message = f"Preflight checks failed: {preflight.blocking_reasons}"
            run.completed_at = datetime.now(timezone.utc)
            return {"status": "preflight_blocked", "blocking_reasons": preflight.blocking_reasons, "orchestration_run_id": run.id}

        step6 = self._add_step(uow.db, run.id, 6, "QUEUE_EXECUTION_BATCH")
        exec_res, _ = self.mt5_service.queue_campaign_execution(
            campaign_id=campaign_id,
            expected_version=campaign.version,
            planning_fingerprint=plan_res["planning_fingerprint"],
            explicit_user_confirm=True,
            session=uow.db,
            correlation_id=corr_id,
        )
        self._complete_step(uow.db, step6, exec_res.model_dump(mode="json"))

        OutboxPublisher.publish_domain_event(
            db=uow.db,
            event_type=EVENT_CAMPAIGN_EXECUTION_QUEUED,
            aggregate_type="CAMPAIGN",
            aggregate_id=campaign_id,
            correlation_id=corr_id,
            payload=exec_res.model_dump(mode="json"),
            campaign_id=campaign_id
        )

        run.status = RUN_STATUS_SUCCEEDED
        run.completed_at = datetime.now(timezone.utc)
        return {"status": "automatic_execution_queued", "campaign_id": campaign_id, "batch_id": exec_res.batch_id, "orchestration_run_id": run.id}

    def approve_campaign_and_orchestrate(
        self,
        campaign_id: str,
        expected_version: int,
        auto_execute: bool = True,
        correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        User action approval of a confirmation-gated campaign.
        """
        corr_id = correlation_id or f"corr-approve-{campaign_id}"

        with UnitOfWork(session_factory=self.session_factory) as uow:
            now_utc = datetime.now(timezone.utc)
            source_id = f"approve-{campaign_id}-{expected_version}"

            existing = uow.db.query(OrchestrationRunModel).filter(
                OrchestrationRunModel.source_type == "USER_ACTION",
                OrchestrationRunModel.source_id == source_id,
            ).first()
            if existing:
                return {
                    "status": "idempotent_existing",
                    "orchestration_run_id": existing.id,
                    "run_status": existing.status,
                    "campaign_id": existing.campaign_id,
                }

            run = OrchestrationRunModel(
                id=uuid4_str(),
                orchestrator_version=ORCHESTRATOR_VERSION,
                source_type="USER_ACTION",
                source_id=source_id,
                correlation_id=corr_id,
                campaign_id=campaign_id,
                status=RUN_STATUS_RUNNING,
                current_step="APPROVE_CAMPAIGN",
                input_payload_json=json.dumps({"campaign_id": campaign_id, "expected_version": expected_version}),
                heartbeat_at=now_utc,
                started_at=now_utc,
                created_at=now_utc,
                updated_at=now_utc
            )
            uow.db.add(run)
            uow.db.flush()

            c_dict = self.campaign_service.approve_campaign(
                campaign_id, expected_version, correlation_id=corr_id, session=uow.db
            )

            OutboxPublisher.publish_domain_event(
                db=uow.db,
                event_type=EVENT_CAMPAIGN_APPROVED,
                aggregate_type="CAMPAIGN",
                aggregate_id=campaign_id,
                correlation_id=corr_id,
                payload=c_dict,
                campaign_id=campaign_id
            )

            try:
                plan_res, _ = self.planning_service.plan_campaign(campaign_id, session=uow.db)
            except RiskValidationError as e:
                run.status = RUN_STATUS_BLOCKED
                run.error_code = "RISK_VALIDATION_BLOCKED"
                run.error_message = str(e)
                run.completed_at = datetime.now(timezone.utc)

                OutboxPublisher.publish_domain_event(
                    db=uow.db,
                    event_type=EVENT_CAMPAIGN_PLAN_BLOCKED,
                    aggregate_type="CAMPAIGN",
                    aggregate_id=campaign_id,
                    correlation_id=corr_id,
                    payload={"campaign_id": campaign_id, "issues": e.issues},
                    campaign_id=campaign_id,
                    severity="WARNING",
                )
                return {
                    "status": "plan_blocked",
                    "campaign_id": campaign_id,
                    "issues": e.issues,
                    "orchestration_run_id": run.id,
                }

            OutboxPublisher.publish_domain_event(
                db=uow.db,
                event_type=EVENT_CAMPAIGN_PLANNED,
                aggregate_type="CAMPAIGN",
                aggregate_id=campaign_id,
                correlation_id=corr_id,
                payload=plan_res,
                campaign_id=campaign_id
            )

            if auto_execute:
                campaign = uow.campaigns.get_by_id(campaign_id)
                preflight = self.mt5_service.run_preflight(campaign_id, session=uow.db)
                if not preflight.is_ready:
                    run.status = RUN_STATUS_BLOCKED
                    run.error_code = "PREFLIGHT_BLOCKED"
                    run.error_message = f"Preflight checks failed: {preflight.blocking_reasons}"
                    run.completed_at = datetime.now(timezone.utc)
                    return {
                        "status": "approved_planned_preflight_blocked",
                        "campaign_id": campaign_id,
                        "blocking_reasons": preflight.blocking_reasons,
                        "orchestration_run_id": run.id,
                    }

                exec_res, _ = self.mt5_service.queue_campaign_execution(
                    campaign_id=campaign_id,
                    expected_version=campaign.version,
                    planning_fingerprint=plan_res["planning_fingerprint"],
                    explicit_user_confirm=True,
                    session=uow.db,
                    correlation_id=corr_id,
                )

                OutboxPublisher.publish_domain_event(
                    db=uow.db,
                    event_type=EVENT_CAMPAIGN_EXECUTION_QUEUED,
                    aggregate_type="CAMPAIGN",
                    aggregate_id=campaign_id,
                    correlation_id=corr_id,
                    payload=exec_res.model_dump(mode="json"),
                    campaign_id=campaign_id
                )
                run.status = RUN_STATUS_SUCCEEDED
                run.completed_at = datetime.now(timezone.utc)
                return {"status": "approved_planned_and_queued", "campaign_id": campaign_id, "batch_id": exec_res.batch_id, "orchestration_run_id": run.id}

            run.status = RUN_STATUS_SUCCEEDED
            run.completed_at = datetime.now(timezone.utc)
            return {"status": "approved_and_planned", "campaign_id": campaign_id, "orchestration_run_id": run.id}

    def _add_step(self, db: Session, run_id: str, seq: int, name: str) -> OrchestrationStepModel:
        now_utc = datetime.now(timezone.utc)
        step = OrchestrationStepModel(
            id=uuid4_str(),
            orchestration_run_id=run_id,
            sequence=seq,
            step_name=name,
            status=STEP_STATUS_RUNNING,
            started_at=now_utc,
            created_at=now_utc
        )
        db.add(step)
        db.flush()
        return step

    def _complete_step(self, db: Session, step: OrchestrationStepModel, output_data: Dict[str, Any]) -> None:
        step.status = STEP_STATUS_SUCCEEDED
        step.output_json = json.dumps(output_data, default=str)
        step.completed_at = datetime.now(timezone.utc)
        db.flush()

    def _fail_step(self, db: Session, step: OrchestrationStepModel, error_code: str, error_message: str) -> None:
        step.status = STEP_STATUS_BLOCKED
        step.error_code = error_code
        step.error_message = error_message
        step.completed_at = datetime.now(timezone.utc)
        db.flush()
