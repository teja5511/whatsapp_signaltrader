from decimal import Decimal
from typing import List, Dict, Any, Optional
from src.planning.decimal_math import to_decimal
from src.planning.symbol_spec import SymbolSpecification
from src.planning.policies import PlanningPolicySnapshot
from src.planning.constants import (
    ENTRY_COUNT_BELOW_MINIMUM, ENTRY_COUNT_ABOVE_MAXIMUM, STOP_LOSS_MISSING,
    STOP_LOSS_DIRECTION_INVALID, ORDER_INTENT_UNRESOLVED, CAMPAIGN_STATE_NOT_PLANNABLE,
    UNRESOLVED_TRADING_POLICY, PRICE_INSIDE_ZONE_BLOCKED,
    PRICE_PAST_ZONE_BLOCKED, CONCURRENT_CAMPAIGN_BLOCKED, CURRENT_PRICE_UNAVAILABLE,
)

MIN_ENTRY_COUNT = 3
MAX_ENTRY_COUNT = 8


def evaluate_current_price_position(
    direction: str,
    current_price: Optional[Decimal],
    zone_low: Optional[Decimal],
    zone_high: Optional[Decimal],
) -> str:
    """Classify the live market against the entry zone.

    Returns one of UNKNOWN, BEFORE_ZONE, INSIDE_ZONE, PAST_ZONE. ``BEFORE_ZONE``
    means the market has not yet reached the zone in the trade direction, which
    is the ordinary case for a pending limit grid.

    A SELL limit grid sits *above* the market and fills as price rises into it,
    so the market has passed the zone once it trades above ``zone_high``. A BUY
    limit grid sits *below* the market and is passed once price trades below
    ``zone_low``.
    """
    if current_price is None or zone_low is None or zone_high is None:
        return "UNKNOWN"
    if zone_low <= current_price <= zone_high:
        return "INSIDE_ZONE"
    if direction.upper() == "SELL":
        return "PAST_ZONE" if current_price > zone_high else "BEFORE_ZONE"
    return "PAST_ZONE" if current_price < zone_low else "BEFORE_ZONE"


def validate_campaign_risk(
    campaign_state: str,
    direction: str,
    order_intent: str,
    entry_count: int,
    stop_loss: Optional[Decimal],
    price_levels: List[Decimal],
    trading_enabled: bool,
    policies: PlanningPolicySnapshot,
    current_price: Optional[Decimal] = None,
    zone_low: Optional[Decimal] = None,
    zone_high: Optional[Decimal] = None,
    active_campaign_count: int = 0,
) -> List[Dict[str, Any]]:
    """Executes full risk validation rules against a campaign and policies.

    Returns a list of issue dictionaries. Any issue with severity ERROR blocks
    planning; the planner refuses to emit entries in that case.
    """
    issues: List[Dict[str, Any]] = []

    # 1. Unresolved policy guard. Nothing downstream may substitute a default.
    for key in sorted(policies.unresolved_keys):
        issues.append({
            "code": UNRESOLVED_TRADING_POLICY,
            "severity": "ERROR",
            "message": (
                f"Trading policy '{key}' is unresolved. Confirm it in Settings before "
                "this campaign can be planned."
            ),
            "policy_key": key,
        })

    # 2. State Guard
    if campaign_state != "PLANNED":
        issues.append({
            "code": CAMPAIGN_STATE_NOT_PLANNABLE,
            "severity": "ERROR",
            "message": f"Campaign state '{campaign_state}' is not plannable (must be in 'PLANNED' state after confirmation approval)"
        })

    # 3. Entry Count Guard
    if entry_count < MIN_ENTRY_COUNT:
        issues.append({
            "code": ENTRY_COUNT_BELOW_MINIMUM,
            "severity": "ERROR",
            "message": f"Entry count ({entry_count}) is below minimum allowable limit ({MIN_ENTRY_COUNT})"
        })
    elif entry_count > MAX_ENTRY_COUNT:
        issues.append({
            "code": ENTRY_COUNT_ABOVE_MAXIMUM,
            "severity": "ERROR",
            "message": f"Entry count ({entry_count}) exceeds maximum allowable limit ({MAX_ENTRY_COUNT})"
        })

    # 4. Stop Loss Guard
    if stop_loss is None or stop_loss <= Decimal("0"):
        issues.append({
            "code": STOP_LOSS_MISSING,
            "severity": "ERROR",
            "message": "Stop loss is missing or invalid"
        })
    else:
        direction_upper = direction.upper()
        for idx, lvl in enumerate(price_levels):
            if direction_upper == "BUY" and stop_loss >= lvl:
                issues.append({
                    "code": STOP_LOSS_DIRECTION_INVALID,
                    "severity": "ERROR",
                    "message": f"BUY stop loss ({stop_loss}) must be strictly less than entry price ({lvl}) at level {idx}",
                    "index": idx
                })
            elif direction_upper == "SELL" and stop_loss <= lvl:
                issues.append({
                    "code": STOP_LOSS_DIRECTION_INVALID,
                    "severity": "ERROR",
                    "message": f"SELL stop loss ({stop_loss}) must be strictly greater than entry price ({lvl}) at level {idx}",
                    "index": idx
                })

    # 5. Order Intent Guard
    if order_intent.upper() == "UNSPECIFIED" and policies.order_intent_policy.value == "BLOCK":
        issues.append({
            "code": ORDER_INTENT_UNRESOLVED,
            "severity": "ERROR",
            "message": "Unspecified order intent is BLOCKED by policy. Explicit LIMIT intent required."
        })

    # 6. Current-price-vs-zone guard (OPEN_DECISIONS items 2 and 3).
    position = evaluate_current_price_position(direction, current_price, zone_low, zone_high)
    inside_policy = policies.current_price_policy.value
    past_policy = policies.current_price_policy.zone_passed_value
    zone_checks_active = "NO_CURRENT_PRICE_CHECK" not in (inside_policy, past_policy)

    if position == "UNKNOWN" and zone_checks_active:
        # We cannot prove the market is outside the zone, so we must not plan.
        issues.append({
            "code": CURRENT_PRICE_UNAVAILABLE,
            "severity": "ERROR",
            "message": (
                "No live XAUUSD quote is available, so the price-versus-zone policies "
                "cannot be evaluated. Planning is blocked until the terminal supplies a quote."
            ),
        })

    if position == "INSIDE_ZONE":
        if inside_policy in ("BLOCK_IF_INSIDE_ZONE", "UNRESOLVED"):
            issues.append({
                "code": PRICE_INSIDE_ZONE_BLOCKED,
                "severity": "ERROR",
                "message": (
                    f"Live price {current_price} is inside the entry zone "
                    f"[{zone_low}, {zone_high}] and policy '{inside_policy}' blocks planning."
                ),
            })
        elif inside_policy == "REJECT_STALE":
            issues.append({
                "code": PRICE_INSIDE_ZONE_BLOCKED,
                "severity": "ERROR",
                "message": f"Signal rejected as stale: live price {current_price} is already inside the entry zone.",
            })
        elif inside_policy in ("LIMIT_STOP_SPLIT", "SKIP_PASSED_LEVELS"):
            # Both require order-type variation the demo executor does not yet
            # support, so they are reported rather than silently downgraded.
            issues.append({
                "code": PRICE_INSIDE_ZONE_BLOCKED,
                "severity": "ERROR",
                "message": (
                    f"Policy '{inside_policy}' requires stop-order placement, which the "
                    "demo execution worker does not support in this release."
                ),
            })

    if position == "PAST_ZONE":
        if past_policy in ("BLOCK_IF_ZONE_PASSED", "UNRESOLVED"):
            issues.append({
                "code": PRICE_PAST_ZONE_BLOCKED,
                "severity": "ERROR",
                "message": (
                    f"Live price {current_price} has passed the entry zone "
                    f"[{zone_low}, {zone_high}] and policy '{past_policy}' blocks planning."
                ),
            })
        elif past_policy == "CANCEL_AS_MISSED":
            issues.append({
                "code": PRICE_PAST_ZONE_BLOCKED,
                "severity": "ERROR",
                "message": "Signal cancelled as missed: live price has passed the entry zone.",
            })
        # PLACE_LIMITS_ANYWAY is the explicitly confirmed pass-through.

    # 7. Concurrent campaign guard (OPEN_DECISIONS item 9).
    if active_campaign_count > 0:
        concurrent = policies.concurrent_campaign_policy.value
        if concurrent in ("BLOCK_UNTIL_REVIEWED", "UNRESOLVED"):
            issues.append({
                "code": CONCURRENT_CAMPAIGN_BLOCKED,
                "severity": "ERROR",
                "message": (
                    f"{active_campaign_count} other campaign(s) are still active and policy "
                    f"'{concurrent}' blocks concurrent planning."
                ),
            })

    return issues
