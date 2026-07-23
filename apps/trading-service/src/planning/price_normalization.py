from decimal import Decimal
from typing import List, Tuple, Dict, Any, Optional
from src.planning.decimal_math import round_to_tick, to_decimal
from src.planning.symbol_spec import SymbolSpecification

def normalize_price_levels(
    raw_levels: List[Decimal],
    zone_low: Decimal,
    zone_high: Decimal,
    spec: SymbolSpecification
) -> Tuple[List[Decimal], List[Dict[str, Any]]]:
    """
    Normalizes price levels to symbol tick size.
    Returns (normalized_levels, list_of_issue_dicts).
    """
    tick = spec.tick_size_decimal()
    digits = spec.digits
    issues = []
    normalized_levels = []

    for idx, raw in enumerate(raw_levels):
        norm = round_to_tick(raw, tick)
        normalized_levels.append(norm)

        # Check outside zone
        if norm < zone_low or norm > zone_high:
            issues.append({
                "code": "PRICE_OUTSIDE_ZONE",
                "severity": "ERROR",
                "message": f"Normalized price level {norm} at index {idx} falls outside entry zone [{zone_low}, {zone_high}]",
                "index": idx
            })

    # Check collisions (duplicate rounded prices)
    seen = set()
    for idx, norm in enumerate(normalized_levels):
        if norm in seen:
            issues.append({
                "code": "PRICE_NORMALIZATION_COLLISION",
                "severity": "ERROR",
                "message": f"Price normalization collision: level {norm} appears multiple times after tick size rounding ({tick})",
                "index": idx
            })
        seen.add(norm)

    # Check monotonic strictly ascending order
    for i in range(len(normalized_levels) - 1):
        if normalized_levels[i] >= normalized_levels[i + 1]:
            issues.append({
                "code": "PRICE_ORDER_NON_MONOTONIC",
                "severity": "ERROR",
                "message": f"Normalized price order non-monotonic at index {i}: {normalized_levels[i]} >= {normalized_levels[i+1]}",
                "index": i
            })

    return normalized_levels, issues
