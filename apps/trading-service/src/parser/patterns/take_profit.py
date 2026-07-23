import re
from decimal import Decimal
from typing import Optional, List, Tuple

def parse_decimal_price(val_str: str) -> Decimal:
    cleaned = val_str.replace(",", "")
    return Decimal(cleaned)

def extract_take_profits(lines: List[str]) -> Tuple[Optional[Decimal], Optional[Decimal], bool, List[str]]:
    """
    Returns (tp1, tp2, tp_open_present, warnings)
    """
    tp_numeric = []
    tp_open_present = False
    warnings = []

    tp_regex = re.compile(
        r"(?:TAKE\s*PROFIT|TAKEPROFIT|\bTP\b|\bTP1\b|\bTP2\b|\bTP\s*1\b|\bTP\s*2\b)\s*[:-]?\s*(OPEN|\d{3,5}(?:,\d{3})?(?:\.\d+)?)",
        re.IGNORECASE
    )

    for line in lines:
        for match in tp_regex.finditer(line):
            val_str = match.group(1).upper()
            if val_str == "OPEN":
                tp_open_present = True
            else:
                try:
                    num_val = parse_decimal_price(val_str)
                    tp_numeric.append(num_val)
                except Exception:
                    continue

    tp1 = tp_numeric[0] if len(tp_numeric) >= 1 else None
    tp2 = tp_numeric[1] if len(tp_numeric) >= 2 else None

    if len(tp_numeric) > 2:
        extra_tps = [str(x) for x in tp_numeric[2:]]
        warnings.append(f"Additional Take Profit targets beyond TP2 detected and preserved in metadata: {', '.join(extra_tps)}")

    return tp1, tp2, tp_open_present, warnings
