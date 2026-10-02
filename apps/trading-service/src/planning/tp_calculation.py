from decimal import Decimal
from typing import Optional, Tuple, Dict, Any, List
from src.planning.decimal_math import round_to_tick, to_decimal
from src.planning.symbol_spec import SymbolSpecification
from src.planning.policies import HundredPipDistancePolicy

def calculate_entry_tp(
    direction: str,
    entry_price: Decimal,
    tp_category: str,
    signal_tp1: Optional[Decimal],
    signal_tp2: Optional[Decimal],
    pip_policy: HundredPipDistancePolicy,
    spec: SymbolSpecification
) -> Tuple[Optional[Decimal], List[Dict[str, Any]]]:
    """
    Computes exact TP price for individual entry.
    Returns (calculated_tp_decimal, list_of_issue_dicts).
    """
    issues = []
    tick = spec.tick_size_decimal()
    direction_upper = direction.upper()

    if tp_category == "TP_1" and signal_tp1 is None:
        return calculate_entry_tp(
            direction, entry_price, "TP_100", None, None, pip_policy, spec
        )

    if tp_category == "TP_1":

        # Validate directional alignment
        if direction_upper == "BUY" and signal_tp1 <= entry_price:
            issues.append({
                "code": "SIGNAL_TP_DIRECTION_INVALID",
                "severity": "ERROR",
                "message": f"BUY signal TP1 ({signal_tp1}) must be strictly greater than entry price ({entry_price})"
            })
        elif direction_upper == "SELL" and signal_tp1 >= entry_price:
            issues.append({
                "code": "SIGNAL_TP_DIRECTION_INVALID",
                "severity": "ERROR",
                "message": f"SELL signal TP1 ({signal_tp1}) must be strictly less than entry price ({entry_price})"
            })

        return round_to_tick(signal_tp1, tick), issues

    elif tp_category == "TP_2" and signal_tp2 is None:
        return calculate_entry_tp(
            direction, entry_price, "TP_100", signal_tp1, None, pip_policy, spec
        )

    elif tp_category == "TP_2":

        if direction_upper == "BUY" and signal_tp2 <= entry_price:
            issues.append({
                "code": "SIGNAL_TP_DIRECTION_INVALID",
                "severity": "ERROR",
                "message": f"BUY signal TP2 ({signal_tp2}) must be strictly greater than entry price ({entry_price})"
            })
        elif direction_upper == "SELL" and signal_tp2 >= entry_price:
            issues.append({
                "code": "SIGNAL_TP_DIRECTION_INVALID",
                "severity": "ERROR",
                "message": f"SELL signal TP2 ({signal_tp2}) must be strictly less than entry price ({entry_price})"
            })

        return round_to_tick(signal_tp2, tick), issues

    elif tp_category == "TP_100":
        distance = pip_policy.distance_decimal()
        if distance is None:
            issues.append({
                "code": "HUNDRED_PIP_POLICY_MISSING",
                "severity": "ERROR",
                "message": "HundredPipDistancePolicy is unresolved (price_distance is None). Distance policy required to compute 100-pip TP."
            })
            return None, issues

        if direction_upper == "BUY":
            raw_tp = entry_price + distance
        else:
            raw_tp = entry_price - distance

        return round_to_tick(raw_tp, tick), issues

    return None, issues
