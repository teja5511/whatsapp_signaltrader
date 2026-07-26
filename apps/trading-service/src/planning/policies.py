from dataclasses import dataclass, asdict, field
from decimal import Decimal
from typing import Optional, Dict, Any, List, Tuple

from src.planning.decimal_math import to_decimal

# Canonical price distances for the resolved 100-pip options.
HUNDRED_PIP_DISTANCE_BY_OPTION = {
    "PRICE_DELTA_1_00": "1.00000000",
    "PRICE_DELTA_10_00": "10.00000000",
}


@dataclass
class HundredPipDistancePolicy:
    price_distance: Optional[str] = None  # None means unresolved; never guessed.
    source: str = "PRODUCTION_DEFAULT"
    is_user_confirmed: bool = False

    def distance_decimal(self) -> Optional[Decimal]:
        return to_decimal(self.price_distance) if self.price_distance else None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class CurrentPriceZonePolicy:
    """How planning reacts to the live market relative to the entry zone.

    ``NO_CURRENT_PRICE_CHECK`` is only used by the offline test fixture; production
    resolves to one of the catalog options and blocks until it does.
    """
    value: str = "UNRESOLVED"
    zone_passed_value: str = "UNRESOLVED"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class TpIndexAllocationPolicy:
    value: str = "UNRESOLVED"
    tp1_index: Optional[int] = None
    tp2_index: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class UnspecifiedOrderIntentPolicy:
    value: str = "BLOCK"  # BLOCK, TREAT_AS_LIMIT

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ConcurrentCampaignPolicy:
    value: str = "UNRESOLVED"  # BLOCK_UNTIL_REVIEWED, COEXIST_DISTINCT_MAGIC, CANCEL_PREVIOUS

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class PlanningPolicySnapshot:
    hundred_pip_policy: HundredPipDistancePolicy
    current_price_policy: CurrentPriceZonePolicy
    tp_index_policy: TpIndexAllocationPolicy
    order_intent_policy: UnspecifiedOrderIntentPolicy
    concurrent_campaign_policy: ConcurrentCampaignPolicy = field(default_factory=ConcurrentCampaignPolicy)
    catalog_version: str = "1.0.0"
    source: str = "PRODUCTION"
    #: Policy keys that were still unresolved when this snapshot was built.
    unresolved_keys: List[str] = field(default_factory=list)

    @property
    def is_fully_resolved(self) -> bool:
        return not self.unresolved_keys

    def to_dict(self) -> Dict[str, Any]:
        return {
            "catalog_version": self.catalog_version,
            "source": self.source,
            "unresolved_keys": sorted(self.unresolved_keys),
            "hundred_pip_policy": self.hundred_pip_policy.to_dict(),
            "current_price_policy": self.current_price_policy.to_dict(),
            "tp_index_policy": self.tp_index_policy.to_dict(),
            "order_intent_policy": self.order_intent_policy.to_dict(),
            "concurrent_campaign_policy": self.concurrent_campaign_policy.to_dict(),
        }


def get_production_default_policies() -> PlanningPolicySnapshot:
    """The state of a freshly installed system: nothing confirmed, everything blocked."""
    from src.policies.catalog import PLANNING_BLOCKING_KEYS

    return PlanningPolicySnapshot(
        hundred_pip_policy=HundredPipDistancePolicy(),
        current_price_policy=CurrentPriceZonePolicy(),
        tp_index_policy=TpIndexAllocationPolicy(),
        order_intent_policy=UnspecifiedOrderIntentPolicy(value="BLOCK"),
        concurrent_campaign_policy=ConcurrentCampaignPolicy(),
        source="PRODUCTION_DEFAULT",
        unresolved_keys=list(PLANNING_BLOCKING_KEYS),
    )


def get_test_fixture_policies(
    price_distance: str = "1.00000000",
    tp_index_value: str = "OUTER_BOUNDARIES_TO_SIGNAL_TPS",
    tp1_index: Optional[int] = None,
    tp2_index: Optional[int] = None
) -> PlanningPolicySnapshot:
    """Fully resolved policy set for deterministic offline tests only.

    Never used by a production code path: the API and orchestrator both build
    their snapshot from persisted, operator-confirmed policies.
    """
    return PlanningPolicySnapshot(
        hundred_pip_policy=HundredPipDistancePolicy(
            price_distance=price_distance,
            source="TEST_FIXTURE",
            is_user_confirmed=False
        ),
        current_price_policy=CurrentPriceZonePolicy(
            value="NO_CURRENT_PRICE_CHECK",
            zone_passed_value="NO_CURRENT_PRICE_CHECK",
        ),
        tp_index_policy=TpIndexAllocationPolicy(
            value=tp_index_value,
            tp1_index=tp1_index,
            tp2_index=tp2_index
        ),
        order_intent_policy=UnspecifiedOrderIntentPolicy(value="TREAT_AS_LIMIT"),
        concurrent_campaign_policy=ConcurrentCampaignPolicy(value="COEXIST_DISTINCT_MAGIC"),
        source="TEST_FIXTURE",
        unresolved_keys=[],
    )


def build_snapshot_from_resolutions(resolutions: Dict[str, Any]) -> PlanningPolicySnapshot:
    """Translate persisted policy resolutions into a planning snapshot.

    Anything unconfirmed stays UNRESOLVED and is reported in ``unresolved_keys``
    so the risk engine can block instead of falling back to a default.
    """
    from src.policies.catalog import (
        POLICY_CATALOG_VERSION,
        PLANNING_BLOCKING_KEYS,
        POLICY_HUNDRED_PIP,
        POLICY_TP_INDEX,
        POLICY_PRICE_INSIDE_ZONE,
        POLICY_PRICE_PAST_ZONE,
        POLICY_ORDER_INTENT,
        POLICY_CONCURRENT_CAMPAIGN,
    )

    def resolved(key: str):
        res = resolutions.get(key)
        if res is None or not res.is_resolved:
            return None, {}
        return res.selected_option, dict(res.parameters or {})

    pip_option, pip_params = resolved(POLICY_HUNDRED_PIP)
    if pip_option == "CUSTOM_PRICE_DELTA":
        pip_distance = pip_params.get("price_distance")
    else:
        pip_distance = HUNDRED_PIP_DISTANCE_BY_OPTION.get(pip_option or "")

    tp_option, tp_params = resolved(POLICY_TP_INDEX)
    inside_option, _ = resolved(POLICY_PRICE_INSIDE_ZONE)
    past_option, _ = resolved(POLICY_PRICE_PAST_ZONE)
    intent_option, _ = resolved(POLICY_ORDER_INTENT)
    concurrent_option, _ = resolved(POLICY_CONCURRENT_CAMPAIGN)

    unresolved = [
        key for key in PLANNING_BLOCKING_KEYS
        if key not in resolutions or not resolutions[key].is_resolved
    ]

    return PlanningPolicySnapshot(
        hundred_pip_policy=HundredPipDistancePolicy(
            price_distance=pip_distance,
            source="OPERATOR_CONFIRMED" if pip_option else "UNRESOLVED",
            is_user_confirmed=bool(pip_option),
        ),
        current_price_policy=CurrentPriceZonePolicy(
            value=inside_option or "UNRESOLVED",
            zone_passed_value=past_option or "UNRESOLVED",
        ),
        tp_index_policy=TpIndexAllocationPolicy(
            value=tp_option or "UNRESOLVED",
            tp1_index=tp_params.get("tp1_index"),
            tp2_index=tp_params.get("tp2_index"),
        ),
        order_intent_policy=UnspecifiedOrderIntentPolicy(value=intent_option or "BLOCK"),
        concurrent_campaign_policy=ConcurrentCampaignPolicy(value=concurrent_option or "UNRESOLVED"),
        catalog_version=POLICY_CATALOG_VERSION,
        source="OPERATOR_CONFIRMED" if not unresolved else "PARTIALLY_RESOLVED",
        unresolved_keys=unresolved,
    )


def load_planning_policies(session_factory=None) -> PlanningPolicySnapshot:
    """Build the active planning snapshot from the database."""
    from src.database.engine import SessionLocal
    from src.policies.service import PolicyService

    factory = session_factory or SessionLocal
    db = factory()
    try:
        resolutions = PolicyService.all_resolutions(db)
        db.commit()
        return build_snapshot_from_resolutions(resolutions)
    finally:
        db.close()
