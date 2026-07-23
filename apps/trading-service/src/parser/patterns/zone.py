import re
from decimal import Decimal
from typing import Optional, Tuple, Dict, Any, List

def parse_decimal_price(val_str: str) -> Decimal:
    # Remove thousands separators if present (e.g. 4,120 -> 4120)
    cleaned = val_str.replace(",", "")
    return Decimal(cleaned)

def extract_zone(lines: List[str]) -> Tuple[Optional[Decimal], Optional[Decimal], bool, List[str]]:
    """
    Returns (zone_low, zone_high, values_reversed, warnings)
    """
    zone_candidates = []

    zone_regex = re.compile(
        r"(?:ZONE|ENTRY|ENTRY ZONE)?\s*:?\s*(\d{3,5}(?:,\d{3})?(?:\.\d+)?)\s*(?:-|\bTO\b)\s*(\d{3,5}(?:,\d{3})?(?:\.\d+)?)",
        re.IGNORECASE
    )

    for line in lines:
        match = zone_regex.search(line)
        if match:
            p1_str, p2_str = match.group(1), match.group(2)
            try:
                p1 = parse_decimal_price(p1_str)
                p2 = parse_decimal_price(p2_str)
                zone_candidates.append((p1, p2))
            except Exception:
                continue

    if not zone_candidates:
        return None, None, False, []

    if len(zone_candidates) > 1:
        # Multiple conflicting zones
        return None, None, False, ["Multiple conflicting price zones detected"]

    p1, p2 = zone_candidates[0]
    warnings = []
    values_reversed = False

    if p1 > p2:
        values_reversed = True
        warnings.append(f"Zone values were reversed ({p1} > {p2}) and auto-sorted into low/high")
        zone_low, zone_high = p2, p1
    else:
        zone_low, zone_high = p1, p2

    return zone_low, zone_high, values_reversed, warnings
