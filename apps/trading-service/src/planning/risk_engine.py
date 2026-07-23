from decimal import Decimal
from typing import List, Dict, Any, Optional
from src.planning.decimal_math import to_decimal
from src.planning.symbol_spec import SymbolSpecification
from src.planning.policies import PlanningPolicySnapshot
from src.planning.constants import (
    ENTRY_COUNT_BELOW_MINIMUM, ENTRY_COUNT_ABOVE_MAXIMUM, STOP_LOSS_MISSING,
    STOP_LOSS_DIRECTION_INVALID, ORDER_INTENT_UNRESOLVED, CAMPAIGN_STATE_NOT_PLANNABLE,
    TRADING_ENABLED_UNEXPECTEDLY
)

def validate_campaign_risk(
    campaign_state: str,
    direction: str,
    order_intent: str,
    entry_count: int,
    stop_loss: Optional[Decimal],
    price_levels: List[Decimal],
    trading_enabled: bool,
    policies: PlanningPolicySnapshot
) -> List[Dict[str, Any]]:
    """
    Executes full risk validation rules against a campaign and policies.
    Returns list of issue dictionaries.
    """
    issues = []

    # 1. State Guard
    if campaign_state != "PLANNED":
        issues.append({
            "code": CAMPAIGN_STATE_NOT_PLANNABLE,
            "severity": "ERROR",
            "message": f"Campaign state '{campaign_state}' is not plannable (must be in 'PLANNED' state after confirmation approval)"
        })

    # 2. Trading Enabled Guard
    if trading_enabled:
        issues.append({
            "code": TRADING_ENABLED_UNEXPECTEDLY,
            "severity": "ERROR",
            "message": "Trading is unexpectedly enabled in Prompt 6 (must remain false)"
        })

    # 3. Entry Count Guard
    if entry_count < 3:
        issues.append({
            "code": ENTRY_COUNT_BELOW_MINIMUM,
            "severity": "ERROR",
            "message": f"Entry count ({entry_count}) is below minimum allowable limit (3)"
        })
    elif entry_count > 8:
        issues.append({
            "code": ENTRY_COUNT_ABOVE_MAXIMUM,
            "severity": "ERROR",
            "message": f"Entry count ({entry_count}) exceeds maximum allowable limit (8)"
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

    return issues
