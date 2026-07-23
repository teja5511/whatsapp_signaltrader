import re
from typing import Optional, Tuple
from src.parser.constants import DIRECTION_BUY, DIRECTION_SELL, ORDER_INTENT_LIMIT, ORDER_INTENT_UNSPECIFIED

def extract_direction_and_intent(text: str) -> Tuple[Optional[str], str, bool]:
    """
    Returns (direction, order_intent, conflict_detected)
    """
    upper_text = text.upper()
    has_buy = bool(re.search(r"\bBUY\b", upper_text))
    has_sell = bool(re.search(r"\bSELL\b", upper_text))

    if has_buy and has_sell:
        return None, ORDER_INTENT_UNSPECIFIED, True

    if not has_buy and not has_sell:
        return None, ORDER_INTENT_UNSPECIFIED, False

    direction = DIRECTION_BUY if has_buy else DIRECTION_SELL
    has_limit = bool(re.search(r"\bLIMIT\b", upper_text))
    order_intent = ORDER_INTENT_LIMIT if has_limit else ORDER_INTENT_UNSPECIFIED

    return direction, order_intent, False
