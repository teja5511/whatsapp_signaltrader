import re
from decimal import Decimal
from typing import Optional, Tuple, List

def parse_decimal_price(val_str: str) -> Decimal:
    cleaned = val_str.replace(",", "")
    return Decimal(cleaned)

def extract_stop_loss(lines: List[str]) -> Tuple[Optional[Decimal], bool]:
    """
    Returns (stop_loss_decimal, is_hard_sl)
    """
    sl_regex = re.compile(
        r"(?:HARD\s+SL|STOP\s*LOSS|STOPLOSS|\bSL\b)\s*[:-]?\s*(?:TO\s*)?(\d{3,5}(?:,\d{3})?(?:\.\d+)?)",
        re.IGNORECASE
    )

    for line in lines:
        match = sl_regex.search(line)
        if match:
            val_str = match.group(1)
            try:
                sl_val = parse_decimal_price(val_str)
                is_hard = "HARD" in line.upper()
                return sl_val, is_hard
            except Exception:
                continue

    return None, False
