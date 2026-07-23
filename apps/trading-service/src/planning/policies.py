from dataclasses import dataclass, asdict
from decimal import Decimal
from typing import Optional, Dict, Any
from src.planning.decimal_math import to_decimal

@dataclass
class HundredPipDistancePolicy:
    price_distance: Optional[str] = None  # None in production (unresolved); e.g. "1.00000000" in fixture
    source: str = "PRODUCTION_DEFAULT"
    is_user_confirmed: bool = False

    def distance_decimal(self) -> Optional[Decimal]:
        return to_decimal(self.price_distance) if self.price_distance else None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class CurrentPriceZonePolicy:
    value: str = "NO_CURRENT_PRICE_CHECK"  # NO_CURRENT_PRICE_CHECK, BLOCK_IF_INSIDE_ZONE, BLOCK_IF_ZONE_PASSED, SKIP_PASSED_LEVELS, RECALCULATE_REMAINING_LEVELS, CONVERT_PASSED_LEVELS_TO_MARKET

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class TpIndexAllocationPolicy:
    value: str = "UNRESOLVED"  # UNRESOLVED, LOWEST_INDICES_TO_SIGNAL_TPS, HIGHEST_INDICES_TO_SIGNAL_TPS, OUTER_BOUNDARIES_TO_SIGNAL_TPS, CENTER_TO_SIGNAL_TPS, EXPLICIT_INDICES
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
class PlanningPolicySnapshot:
    hundred_pip_policy: HundredPipDistancePolicy
    current_price_policy: CurrentPriceZonePolicy
    tp_index_policy: TpIndexAllocationPolicy
    order_intent_policy: UnspecifiedOrderIntentPolicy

    def to_dict(self) -> Dict[str, Any]:
        return {
            "hundred_pip_policy": self.hundred_pip_policy.to_dict(),
            "current_price_policy": self.current_price_policy.to_dict(),
            "tp_index_policy": self.tp_index_policy.to_dict(),
            "order_intent_policy": self.order_intent_policy.to_dict()
        }

def get_production_default_policies() -> PlanningPolicySnapshot:
    return PlanningPolicySnapshot(
        hundred_pip_policy=HundredPipDistancePolicy(),
        current_price_policy=CurrentPriceZonePolicy(value="NO_CURRENT_PRICE_CHECK"),
        tp_index_policy=TpIndexAllocationPolicy(value="UNRESOLVED"),
        order_intent_policy=UnspecifiedOrderIntentPolicy(value="BLOCK")
    )

def get_test_fixture_policies(
    price_distance: str = "1.00000000",
    tp_index_value: str = "OUTER_BOUNDARIES_TO_SIGNAL_TPS",
    tp1_index: Optional[int] = None,
    tp2_index: Optional[int] = None
) -> PlanningPolicySnapshot:
    return PlanningPolicySnapshot(
        hundred_pip_policy=HundredPipDistancePolicy(
            price_distance=price_distance,
            source="TEST_FIXTURE",
            is_user_confirmed=False
        ),
        current_price_policy=CurrentPriceZonePolicy(value="NO_CURRENT_PRICE_CHECK"),
        tp_index_policy=TpIndexAllocationPolicy(
            value=tp_index_value,
            tp1_index=tp1_index,
            tp2_index=tp2_index
        ),
        order_intent_policy=UnspecifiedOrderIntentPolicy(value="TREAT_AS_LIMIT")
    )
