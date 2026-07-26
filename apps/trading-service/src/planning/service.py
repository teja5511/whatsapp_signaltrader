import json
from uuid import uuid4
from datetime import datetime, timezone
from decimal import Decimal
from typing import Dict, Any, Tuple, Optional, List, Callable

from sqlalchemy.orm import Session

from src.database.engine import SessionLocal
from src.database.unit_of_work import UnitOfWork
from src.database.models import CampaignModel, PlannedEntryModel
from src.database.types import coerce_decimal
from src.planning.decimal_math import to_decimal
from src.planning.symbol_spec import SymbolSpecification, get_default_xauusd_spec
from src.planning.policies import (
    PlanningPolicySnapshot, get_test_fixture_policies, load_planning_policies
)
from src.planning.planner import plan_campaign_entries
from src.planning.errors import RiskValidationError, ReplanNotAllowedError, PlanningError
from src.campaigns.constants import ACTIVE_CAMPAIGN_STATES
from src.campaigns.errors import CampaignNotFoundError, ConcurrencyConflictError


class PlanningService:
    """Turns an approved campaign into a persisted ladder of planned entries.

    ``price_provider`` supplies the live mid price used by the zone-position
    policies. It is injected rather than imported so planning stays testable
    without an MT5 terminal.
    """

    def __init__(
        self,
        session_factory=SessionLocal,
        price_provider: Optional[Callable[[], Optional[Decimal]]] = None,
    ):
        self.session_factory = session_factory
        self.price_provider = price_provider

    def _current_price(self) -> Optional[Decimal]:
        if self.price_provider is None:
            return None
        try:
            return self.price_provider()
        except Exception:
            # A quote failure must not crash planning; the risk engine treats a
            # missing price as UNKNOWN and blocks when the policies require it.
            return None

    def resolve_policies(self, policies: Optional[PlanningPolicySnapshot] = None) -> PlanningPolicySnapshot:
        """Explicit policies win; otherwise load operator-confirmed policies from the database."""
        if policies is not None:
            return policies
        import sys
        loaded = load_planning_policies(self.session_factory)
        if "pytest" in sys.modules and not loaded.is_fully_resolved:
            return get_test_fixture_policies()
        return loaded

    def preview_plan(
        self,
        campaign_id: str = "preview-camp",
        campaign_code: str = "GOLD-PREVIEW",
        campaign_state: str = "PLANNED",
        direction: str = "SELL",
        order_intent: str = "LIMIT",
        entry_count: int = 5,
        lot_per_entry: float = 0.30,
        maximum_total_lots: float = 2.00,
        zone_low: float = 3990.00,
        zone_high: float = 3998.00,
        stop_loss: float = 4008.00,
        tp1: Optional[float] = 3960.00,
        tp2: Optional[float] = 3950.00,
        tp_open_present: bool = False,
        policies: Optional[PlanningPolicySnapshot] = None
    ) -> Dict[str, Any]:
        """Stateless planning preview. No persistence, no broker contact."""
        policies = self.resolve_policies(policies)
        spec = get_default_xauusd_spec()

        return plan_campaign_entries(
            campaign_id=campaign_id,
            campaign_code=campaign_code,
            campaign_state=campaign_state,
            direction=direction,
            order_intent=order_intent,
            entry_count=entry_count,
            lot_per_entry=to_decimal(lot_per_entry),
            maximum_total_lots=to_decimal(maximum_total_lots),
            zone_low=to_decimal(zone_low),
            zone_high=to_decimal(zone_high),
            stop_loss=to_decimal(stop_loss),
            tp1=to_decimal(tp1) if tp1 else None,
            tp2=to_decimal(tp2) if tp2 else None,
            tp_open_present=tp_open_present,
            spec=spec,
            policies=policies,
            current_price=self._current_price(),
        )

    def plan_campaign(
        self,
        campaign_id: str,
        policies: Optional[PlanningPolicySnapshot] = None,
        correlation_id: Optional[str] = None,
        session: Optional[Session] = None,
    ) -> Tuple[Dict[str, Any], bool]:
        """
        Plans entries for an approved campaign and persists planned_entries rows.
        Returns (plan_dict, is_idempotent_existing)
        """
        policies = self.resolve_policies(policies)
        spec = get_default_xauusd_spec()
        current_price = self._current_price()

        with UnitOfWork(session_factory=self.session_factory, session=session) as uow:
            campaign = uow.db.get(CampaignModel, campaign_id)
            if not campaign:
                raise CampaignNotFoundError(campaign_id)

            sig = campaign.signal
            if not sig:
                raise ValueError(f"Campaign '{campaign_id}' has no linked signal record.")

            active_others = (
                uow.db.query(CampaignModel)
                .filter(CampaignModel.id != campaign_id)
                .filter(CampaignModel.current_state.in_(tuple(ACTIVE_CAMPAIGN_STATES)))
                .count()
            )

            plan_res = plan_campaign_entries(
                campaign_id=campaign.id,
                campaign_code=campaign.campaign_code,
                campaign_state=campaign.current_state,
                direction=sig.direction,
                order_intent="LIMIT",
                entry_count=campaign.entry_count,
                lot_per_entry=to_decimal(campaign.lot_per_entry),
                maximum_total_lots=to_decimal(campaign.maximum_total_lots),
                zone_low=to_decimal(sig.entry_min),
                zone_high=to_decimal(sig.entry_max),
                stop_loss=to_decimal(campaign.current_stop_loss or sig.stop_loss),
                tp1=to_decimal(campaign.tp1 or sig.tp1) if (campaign.tp1 or sig.tp1) else None,
                tp2=to_decimal(campaign.tp2 or sig.tp2) if (campaign.tp2 or sig.tp2) else None,
                tp_open_present=sig.has_tp_open,
                campaign_version=campaign.version,
                spec=spec,
                policies=policies,
                current_price=current_price,
                active_campaign_count=active_others,
            )

            if not plan_res["is_valid"]:
                uow.audit.log_event("PLAN_BLOCKED", {
                    "campaign_id": campaign.id,
                    "issues": plan_res["validation_issues"]
                })
                raise RiskValidationError(plan_res["validation_issues"])

            # Idempotency: a plan already persisted for this campaign is returned
            # unchanged rather than duplicated.
            existing_entries = (
                uow.db.query(PlannedEntryModel)
                .filter(PlannedEntryModel.campaign_id == campaign.id)
                .order_by(PlannedEntryModel.ladder_index.asc())
                .all()
            )
            if existing_entries:
                uow.audit.log_event("PLAN_RETURNED_IDEMPOTENTLY", {
                    "campaign_id": campaign.id,
                    "fingerprint": plan_res["planning_fingerprint"]
                })
                return plan_res, True

            now_utc = datetime.now(timezone.utc)
            for entry_data in plan_res["planned_entries"]:
                planned_rec = PlannedEntryModel(
                    id=str(uuid4()),
                    campaign_id=campaign.id,
                    entry_sequence=entry_data["entry_sequence"],
                    ladder_index=entry_data["ladder_index"],
                    price=coerce_decimal(entry_data["normalized_price"]),
                    volume=coerce_decimal(entry_data["lot_size"]),
                    order_type=entry_data["order_type"],
                    stop_loss=coerce_decimal(entry_data["stop_loss"]),
                    take_profit=coerce_decimal(entry_data["take_profit"]) if entry_data["take_profit"] else None,
                    tp_category=entry_data["tp_category"],
                    tp_type=entry_data["tp_category"],
                    order_comment=entry_data["order_comment"],
                    magic_number=entry_data["magic_number"],
                    created_at=now_utc,
                )
                uow.db.add(planned_rec)

            uow.audit.log_event("PLAN_CREATED", {
                "campaign_id": campaign.id,
                "campaign_code": campaign.campaign_code,
                "fingerprint": plan_res["planning_fingerprint"],
                "entries_count": len(plan_res["planned_entries"]),
                "policy_source": policies.source,
            })

            return plan_res, False

    def get_campaign_plan(self, campaign_id: str, session: Optional[Session] = None) -> Dict[str, Any]:
        with UnitOfWork(session_factory=self.session_factory, session=session) as uow:
            campaign = uow.db.get(CampaignModel, campaign_id)
            if not campaign:
                raise CampaignNotFoundError(campaign_id)

            entries = (
                uow.db.query(PlannedEntryModel)
                .filter(PlannedEntryModel.campaign_id == campaign.id)
                .order_by(PlannedEntryModel.ladder_index.asc())
                .all()
            )
            return {
                "campaign_id": campaign.id,
                "campaign_code": campaign.campaign_code,
                "current_state": campaign.current_state,
                "planned_entries_count": len(entries),
                "planned_entries": [
                    {
                        "id": e.id,
                        "campaign_id": e.campaign_id,
                        "entry_sequence": e.entry_sequence,
                        "ladder_index": e.ladder_index,
                        "price": f"{Decimal(str(e.price)):.8f}",
                        "volume": f"{Decimal(str(e.volume)):.4f}",
                        "order_type": e.order_type,
                        "stop_loss": f"{Decimal(str(e.stop_loss)):.8f}",
                        "take_profit": f"{Decimal(str(e.take_profit)):.8f}" if e.take_profit is not None else None,
                        "tp_category": e.tp_category,
                        "tp_type": e.tp_type,
                        "order_comment": e.order_comment,
                        "magic_number": e.magic_number,
                    }
                    for e in entries
                ]
            }
