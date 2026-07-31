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

    # 1. Range Zone (e.g. 4050 - 4055 or 4050 TO 4055)
    range_regex = re.compile(
        r"(?:ZONE|ENTRY|ENTRY ZONE)?\s*:?\s*(\d{3,5}(?:,\d{3})?(?:\.\d+)?)\s*(?:-|\bTO\b)\s*(\d{3,5}(?:,\d{3})?(?:\.\d+)?)",
        re.IGNORECASE
    )

    # 2. Single Entry Price Zone (e.g. @ 4050 or ENTRY 4050 or BUY GOLD 4050)
    single_regex = re.compile(
        r"(?:@|AT|ENTRY|ZONE|PRICE|NOW)?\s*:?\s*(\d{3,5}(?:,\d{3})?(?:\.\d+)?)",
        re.IGNORECASE
    )

    for line in lines:
        match_range = range_regex.search(line)
        if match_range:
            p1_str, p2_str = match_range.group(1), match_range.group(2)
            try:
                p1 = parse_decimal_price(p1_str)
                p2 = parse_decimal_price(p2_str)
                zone_candidates.append((p1, p2))
                continue
            except Exception:
                pass

        # Try single entry price match if not range
        line_without_sl_tp = re.sub(r"(?:SL|STOP\s*LOSS|TP|TP1|TP2|TAKE\s*PROFIT).*", "", line, flags=re.IGNORECASE)
        match_single = single_regex.search(line_without_sl_tp)
        if match_single:
            p_str = match_single.group(1)
            try:
                p = parse_decimal_price(p_str)
                zone_candidates.append((p, p))
            except Exception:
                pass

    if not zone_candidates:
        return None, None, False, []

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
