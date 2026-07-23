from decimal import Decimal
from typing import List, Dict, Any, Tuple
from src.planning.decimal_math import to_decimal, is_volume_aligned
from src.planning.symbol_spec import SymbolSpecification

def validate_and_normalize_volume(
    entry_count: int,
    lot_per_entry: Decimal,
    maximum_total_lots: Decimal,
    spec: SymbolSpecification
) -> Tuple[Decimal, List[Dict[str, Any]]]:
    """
    Validates per-entry volume and total campaign volume exposure.
    Returns (requested_total_lots, list_of_issue_dicts).
    """
    issues = []
    v_min = spec.volume_min_decimal()
    v_max = spec.volume_max_decimal()
    v_step = spec.volume_step_decimal()

    if lot_per_entry <= Decimal("0"):
        issues.append({
            "code": "LOT_SIZE_NON_POSITIVE",
            "severity": "ERROR",
            "message": f"Lot size per entry ({lot_per_entry}) must be strictly positive"
        })

    if lot_per_entry < v_min:
        issues.append({
            "code": "LOT_SIZE_BELOW_SYMBOL_MINIMUM",
            "severity": "ERROR",
            "message": f"Lot size per entry ({lot_per_entry}) is below symbol minimum allowable volume ({v_min})"
        })

    if lot_per_entry > v_max:
        issues.append({
            "code": "LOT_SIZE_ABOVE_SYMBOL_MAXIMUM",
            "severity": "ERROR",
            "message": f"Lot size per entry ({lot_per_entry}) exceeds symbol maximum allowable volume ({v_max})"
        })

    if not is_volume_aligned(lot_per_entry, v_step):
        issues.append({
            "code": "VOLUME_STEP_MISMATCH",
            "severity": "ERROR",
            "message": f"Lot size per entry ({lot_per_entry}) does not align with symbol volume step increment ({v_step})"
        })

    requested_total_lots = Decimal(str(entry_count)) * lot_per_entry
    if requested_total_lots > maximum_total_lots:
        issues.append({
            "code": "TOTAL_VOLUME_EXCEEDED",
            "severity": "ERROR",
            "message": f"Requested total campaign exposure ({requested_total_lots:.4f} lots for {entry_count} entries × {lot_per_entry:.4f} lots) exceeds maximum campaign exposure cap ({maximum_total_lots:.4f} lots)"
        })

    return requested_total_lots, issues
