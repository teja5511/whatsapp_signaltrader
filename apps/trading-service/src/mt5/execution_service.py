"""MT5 Execution Service Orchestrator."""

import json
import os
from uuid import uuid4
from typing import Optional, List, Dict, Any, Tuple
from decimal import Decimal
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from src.database.engine import SessionLocal
from src.database.unit_of_work import UnitOfWork
from src.database.models import (
    CampaignModel, PlannedEntryModel, MT5AccountSnapshotModel, MT5SymbolSnapshotModel,
    MT5SyncEventModel, MT5OrderRecordModel, MT5PositionRecordModel, ControlStateModel,
)
from src.database.types import coerce_decimal
from src.mt5.adapter import MT5AdapterInterface
from src.mt5.fake_adapter import FakeMT5Adapter
from src.mt5.dry_run_adapter import DryRunMT5Adapter
from src.mt5.real_adapter import RealMT5Adapter
from src.mt5.execution_queue import MT5ExecutionQueue
from src.mt5.idempotency import generate_execution_idempotency_key
from src.mt5.contracts import Mt5ExecutionPreflightResultDTO, Mt5CampaignExecutionResultDTO
from src.campaigns.constants import (
    STATE_PLANNED, STATE_PLACING_ORDERS, REASON_EXECUTION_QUEUED, TRIGGER_USER_ACTION,
)
from src.campaigns.state_machine import apply_transition
from src.mt5.constants import (
    MODE_FAKE, MODE_DRY_RUN, MODE_REAL, ENV_DEMO, MARGIN_HEDGING, CANONICAL_SYMBOL_XAUUSD
)

MAX_TOTAL_LOTS = Decimal("2.0000")
EMERGENCY_CLOSE_PHRASE = "CLOSE ALL DEMO XAUUSD"
SCOPE_APPLICATION_OWNED = "APPLICATION_OWNED"
SCOPE_ALL_DEMO_XAUUSD = "ALL_XAUUSD_ON_DEMO_ACCOUNT"
VALID_CLOSE_SCOPES = (SCOPE_APPLICATION_OWNED, SCOPE_ALL_DEMO_XAUUSD)


def uuid4_str() -> str:
    return str(uuid4())


def build_adapter_from_env() -> MT5AdapterInterface:
    import sys
    if "PYTEST_CURRENT_TEST" in os.environ or "pytest" in sys.modules:
        return FakeMT5Adapter()
    mode = os.getenv("MT5_ADAPTER_MODE", MODE_FAKE).lower()
    if mode == MODE_DRY_RUN:
        return DryRunMT5Adapter()
    if mode == MODE_REAL or mode == "real":
        allowed_logins = [
            int(x) for x in os.getenv("MT5_ALLOWED_LOGINS", "").split(",") if x.strip().isdigit()
        ] or None
        allowed_servers = [
            x.strip() for x in os.getenv("MT5_ALLOWED_SERVERS", "").split(",") if x.strip()
        ] or None
        return RealMT5Adapter(allowed_logins=allowed_logins, allowed_servers=allowed_servers)
    return FakeMT5Adapter()


class MT5ExecutionService:
    def __init__(self, adapter: Optional[MT5AdapterInterface] = None, session_factory=SessionLocal):
        self.session_factory = session_factory
        self.adapter = adapter or build_adapter_from_env()

    # -- market data --------------------------------------------------------

    def current_mid_price(self) -> Optional[Decimal]:
        """Live mid price, or None when no quote is available."""
        try:
            tick = self.adapter.symbol_tick()
        except Exception:
            return None
        if tick is None:
            return None
        return (tick.bid + tick.ask) / Decimal("2")

    # -- preflight ----------------------------------------------------------

    def run_preflight(self, campaign_id: str, session: Optional[Session] = None) -> Mt5ExecutionPreflightResultDTO:
        with UnitOfWork(session_factory=self.session_factory, session=session) as uow:
            campaign = uow.campaigns.get_by_id(campaign_id)
            if not campaign:
                return Mt5ExecutionPreflightResultDTO(
                    campaign_id=campaign_id,
                    is_ready=False,
                    blocking_reasons=[f"Campaign '{campaign_id}' not found."]
                )

            passed: List[str] = []
            blocked: List[str] = []

            if campaign.current_state != STATE_PLANNED:
                blocked.append(f"Campaign state '{campaign.current_state}' is not PLANNED.")
            else:
                passed.append("CAMPAIGN_STATE_PLANNED")

            if len(campaign.planned_entries) != campaign.entry_count or campaign.entry_count < 3 or campaign.entry_count > 8:
                blocked.append(f"Invalid planned entries count {len(campaign.planned_entries)} (expected {campaign.entry_count}).")
            else:
                passed.append("ENTRY_COUNT_VALID")

            requested = coerce_decimal(campaign.requested_total_lots) or Decimal("0")
            if requested > MAX_TOTAL_LOTS:
                blocked.append(f"Campaign requested total volume {requested} lots exceeds {MAX_TOTAL_LOTS} limit.")
            else:
                passed.append("TOTAL_VOLUME_CAP_VALID")

            # The planned entries must independently respect the cap; a stale
            # requested_total_lots must not be able to smuggle volume through.
            entries_total = sum(
                (coerce_decimal(e.volume) or Decimal("0")) for e in campaign.planned_entries
            )
            if entries_total > MAX_TOTAL_LOTS:
                blocked.append(f"Planned entries total {entries_total} lots exceeds {MAX_TOTAL_LOTS} limit.")
            else:
                passed.append("PLANNED_ENTRY_VOLUME_CAP_VALID")

            # Control-state gates.
            ctrl = uow.db.get(ControlStateModel, 1)
            if ctrl:
                if ctrl.automation_state == "EMERGENCY_STOPPED":
                    blocked.append("Emergency stop is active.")
                else:
                    passed.append("EMERGENCY_STOP_CLEAR")
                if not ctrl.trading_enabled or not ctrl.mt5_execution_enabled:
                    blocked.append("Demo trading is not enabled.")
                else:
                    passed.append("DEMO_TRADING_ENABLED")
            else:
                passed.append("EMERGENCY_STOP_CLEAR")
                passed.append("DEMO_TRADING_ENABLED")

            try:
                if not self.adapter.is_initialized():
                    self.adapter.initialize()
                acc_info = self.adapter.account_info()
                if acc_info.environment_kind != ENV_DEMO:
                    blocked.append(f"Account environment '{acc_info.environment_kind}' is not DEMO.")
                else:
                    passed.append("ACCOUNT_DEMO_ENVIRONMENT")

                if acc_info.margin_mode != MARGIN_HEDGING:
                    blocked.append(f"Account margin mode '{acc_info.margin_mode}' is not HEDGING.")
                else:
                    passed.append("ACCOUNT_MARGIN_HEDGING")

                resolution = self.adapter.resolve_symbol()
                if not resolution.is_resolved:
                    blocked.append(f"XAUUSD symbol unresolved ({resolution.source}).")
                else:
                    passed.append("SYMBOL_RESOLVED")
            except Exception as e:
                blocked.append(f"MT5 adapter preflight error: {str(e)}")

            return Mt5ExecutionPreflightResultDTO(
                campaign_id=campaign_id,
                is_ready=len(blocked) == 0,
                checks_passed=passed,
                blocking_reasons=blocked
            )

    # -- queueing -----------------------------------------------------------

    def queue_campaign_execution(
        self,
        campaign_id: str,
        expected_version: int,
        planning_fingerprint: str,
        explicit_user_confirm: bool = True,
        session: Optional[Session] = None,
        correlation_id: Optional[str] = None,
    ) -> Tuple[Mt5CampaignExecutionResultDTO, bool]:
        if not explicit_user_confirm:
            raise ValueError("Execution requires explicit user confirmation.")

        with UnitOfWork(session_factory=self.session_factory, session=session) as uow:
            campaign = uow.campaigns.get_by_id(campaign_id)
            if not campaign:
                raise ValueError(f"Campaign '{campaign_id}' not found.")

            if campaign.version != expected_version:
                raise ValueError(
                    f"Concurrency conflict on campaign '{campaign_id}': "
                    f"expected version {expected_version}, got {campaign.version}."
                )

            preflight = self.run_preflight(campaign_id, session=uow.db)
            if not preflight.is_ready:
                raise ValueError(f"Execution preflight blocked: {preflight.blocking_reasons}")

            acc_info = self.adapter.account_info()

            now_utc = datetime.now(timezone.utc)
            uow.db.add(MT5AccountSnapshotModel(
                id=uuid4_str(),
                login=acc_info.login,
                login_masked=acc_info.login_masked,
                server=acc_info.server,
                company=acc_info.company,
                environment_kind=acc_info.environment_kind,
                margin_mode=acc_info.margin_mode,
                currency=acc_info.currency,
                leverage=acc_info.leverage,
                balance=acc_info.balance,
                equity=acc_info.equity,
                margin=acc_info.margin,
                margin_free=acc_info.margin_free,
                trade_allowed=acc_info.trade_allowed,
                trade_expert=acc_info.trade_expert,
                captured_at=now_utc
            ))

            jobs_payload = []
            for entry in sorted(campaign.planned_entries, key=lambda x: x.ladder_index):
                idempotency_key = generate_execution_idempotency_key(
                    campaign_id=campaign.id,
                    planning_fingerprint=planning_fingerprint,
                    planned_entry_id=entry.id,
                    campaign_version=expected_version,
                    account_login=acc_info.login,
                    account_server=acc_info.server,
                    broker_symbol=CANONICAL_SYMBOL_XAUUSD,
                    operation_type="PLACE_PENDING_ORDER"
                )
                jobs_payload.append({
                    "planned_entry_id": entry.id,
                    "operation_type": "PLACE_PENDING_ORDER",
                    "idempotency_key": idempotency_key,
                    "priority": 10 + entry.ladder_index,
                    "max_attempts": 1,
                    "payload": {
                        "campaign_id": campaign.id,
                        "planned_entry_id": entry.id,
                        "ladder_index": entry.ladder_index
                    }
                })

            batch, jobs = MT5ExecutionQueue.create_batch_and_jobs(
                db=uow.db,
                campaign_id=campaign.id,
                campaign_version=expected_version,
                planning_fingerprint=planning_fingerprint,
                jobs_data=jobs_payload
            )

            apply_transition(
                db=uow.db,
                campaign=campaign,
                to_state=STATE_PLACING_ORDERS,
                reason_code=REASON_EXECUTION_QUEUED,
                reason=f"Execution batch {batch.id} queued with {len(jobs)} job(s).",
                trigger_type=TRIGGER_USER_ACTION,
                trigger_reference_id=batch.id,
                correlation_id=correlation_id,
            )

            uow.audit.log_event("EXECUTION_BATCH_QUEUED", {
                "campaign_id": campaign.id,
                "batch_id": batch.id,
                "jobs_count": len(jobs)
            })

            res = Mt5CampaignExecutionResultDTO(
                campaign_id=campaign.id,
                batch_id=batch.id,
                status="QUEUED",
                jobs_count=len(jobs),
                message="Execution batch queued cleanly for single-writer execution worker."
            )
            return res, False

    # -- synchronisation ----------------------------------------------------

    def synchronize_campaign(self, campaign_id: str, session: Optional[Session] = None) -> Dict[str, Any]:
        with UnitOfWork(session_factory=self.session_factory, session=session) as uow:
            campaign = uow.campaigns.get_by_id(campaign_id)
            if not campaign:
                return {"status": "not_found", "orders_count": 0, "positions_count": 0}

            active_orders = self.adapter.orders_get(magic_number=campaign.magic_number)
            active_positions = self.adapter.positions_get(magic_number=campaign.magic_number)

            now_utc = datetime.now(timezone.utc)
            uow.db.add(MT5SyncEventModel(
                id=uuid4_str(),
                campaign_id=campaign_id,
                sync_type="MANUAL",
                orders_count=len(active_orders),
                positions_count=len(active_positions),
                payload_json=json.dumps({
                    "orders": len(active_orders),
                    "positions": len(active_positions),
                }),
                synced_at=now_utc
            ))

            return {
                "campaign_id": campaign_id,
                "orders_count": len(active_orders),
                "positions_count": len(active_positions),
                "orders": [o.model_dump(mode="json") for o in active_orders],
                "positions": [p.model_dump(mode="json") for p in active_positions]
            }

    # -- emergency close ----------------------------------------------------

    def preview_emergency_close(self, scope: str = SCOPE_APPLICATION_OWNED) -> Dict[str, Any]:
        """Everything the operator must see before confirming a close-all.

        Read-only: contacts the broker for current state but mutates nothing.
        """
        if scope not in VALID_CLOSE_SCOPES:
            raise ValueError(f"Invalid scope '{scope}'. Allowed: {VALID_CLOSE_SCOPES}")

        if not self.adapter.is_initialized():
            self.adapter.initialize()
        acc = self.adapter.account_info()
        resolution = self.adapter.resolve_symbol()

        db = self.session_factory()
        try:
            owned_magics = {row[0] for row in db.query(CampaignModel.magic_number).all()}
        finally:
            db.close()

        def in_scope(magic: int) -> bool:
            return scope == SCOPE_ALL_DEMO_XAUUSD or magic in owned_magics

        orders = [
            o for o in self.adapter.orders_get()
            if self._is_gold(o.symbol) and in_scope(o.magic_number)
        ]
        positions = [
            p for p in self.adapter.positions_get()
            if self._is_gold(p.symbol) and in_scope(p.magic_number)
        ]
        total_volume = sum((p.volume for p in positions), Decimal("0"))

        return {
            "scope": scope,
            "confirmation_phrase_required": EMERGENCY_CLOSE_PHRASE,
            "account_environment": acc.environment_kind,
            "account_login_masked": acc.login_masked,
            "account_server": acc.server,
            "margin_mode": acc.margin_mode,
            "is_demo": acc.environment_kind == ENV_DEMO,
            "is_hedging": acc.margin_mode == MARGIN_HEDGING,
            "broker_symbol": resolution.broker_symbol,
            "affected_order_count": len(orders),
            "affected_position_count": len(positions),
            "total_position_volume": f"{total_volume:.4f}",
            "orders": [o.model_dump(mode="json") for o in orders],
            "positions": [p.model_dump(mode="json") for p in positions],
        }

    @staticmethod
    def _is_gold(symbol: str) -> bool:
        upper = (symbol or "").upper()
        return upper.startswith("XAUUSD") or upper == "GOLD"

    def emergency_close_all_xauusd(
        self,
        confirmation_phrase: str,
        scope: str = SCOPE_APPLICATION_OWNED,
        actor: str = "OPERATOR",
    ) -> Dict[str, Any]:
        """Close every in-scope XAUUSD position, then report per-ticket outcomes.

        Success is only claimed for tickets the broker confirmed closed. Anything
        unconfirmed is returned as ``outcome_unknown`` for reconciliation.
        """
        if os.getenv("MT5_CLOSE_ALL_ENABLED", "false").lower() != "true":
            raise ValueError("Emergency close-all is disabled by configuration (MT5_CLOSE_ALL_ENABLED=false).")

        if confirmation_phrase != EMERGENCY_CLOSE_PHRASE:
            raise ValueError(f"Invalid confirmation phrase '{confirmation_phrase}'.")

        if scope not in VALID_CLOSE_SCOPES:
            raise ValueError(f"Invalid scope '{scope}'. Allowed: {VALID_CLOSE_SCOPES}")

        if not self.adapter.is_initialized():
            self.adapter.initialize()
        acc_info = self.adapter.account_info()
        if acc_info.environment_kind != ENV_DEMO:
            raise ValueError("Emergency close-all blocked on non-demo account.")

        with UnitOfWork(session_factory=self.session_factory) as uow:
            owned_magics = {row[0] for row in uow.db.query(CampaignModel.magic_number).all()}
            positions = self.adapter.positions_get()

            closed: List[int] = []
            failed: List[Dict[str, Any]] = []
            unknown: List[Dict[str, Any]] = []

            for p in positions:
                if not self._is_gold(p.symbol):
                    continue
                if scope == SCOPE_APPLICATION_OWNED and p.magic_number not in owned_magics:
                    continue

                result = self.adapter.close_position(p.ticket)
                if result.outcome_unknown:
                    unknown.append({"ticket": p.ticket, "comment": result.comment})
                    continue
                if not result.is_success:
                    failed.append({"ticket": p.ticket, "retcode": result.retcode, "comment": result.comment})
                    continue
                closed.append(p.ticket)
                rec = uow.db.query(MT5PositionRecordModel).filter(
                    MT5PositionRecordModel.ticket == p.ticket
                ).first()
                if rec:
                    rec.state = "CLOSED"
                    rec.updated_at = datetime.now(timezone.utc)

            # Verify against the broker rather than trusting the send results.
            remaining = [
                p for p in self.adapter.positions_get()
                if self._is_gold(p.symbol)
                and (scope == SCOPE_ALL_DEMO_XAUUSD or p.magic_number in owned_magics)
            ]

            uow.audit.log_event("EMERGENCY_CLOSE_ALL_EXECUTED", {
                "scope": scope,
                "actor": actor,
                "closed_tickets_count": len(closed),
                "closed_tickets": closed,
                "failed_count": len(failed),
                "unknown_count": len(unknown),
                "remaining_after_close": len(remaining),
            })

            fully_closed = not failed and not unknown and not remaining
            return {
                "status": "success" if fully_closed else "incomplete",
                "scope": scope,
                "closed_count": len(closed),
                "closed_tickets": closed,
                "failed": failed,
                "outcome_unknown": unknown,
                "remaining_position_count": len(remaining),
                "remaining_tickets": [p.ticket for p in remaining],
                "reconciliation_required": bool(unknown or remaining),
            }

    def current_mid_price(self) -> Optional[Decimal]:
        """Returns the current mid price for XAUUSD from the adapter."""
        try:
            if not self.adapter.is_initialized():
                self.adapter.initialize()
            tick = self.adapter.symbol_tick("XAUUSD")
            if tick and tick.bid and tick.ask:
                return (tick.bid + tick.ask) / Decimal("2")
        except Exception:
            pass
        return None
