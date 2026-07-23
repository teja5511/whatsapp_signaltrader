import re
from typing import Optional, Tuple
from src.parser.constants import SUPPORTED_INSTRUMENTS, UNSUPPORTED_INSTRUMENTS

def extract_instrument(text: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Returns (detected_symbol, unsupported_symbol_if_any)
    """
    upper_text = text.upper()

    # Check for unsupported explicit instruments first
    for unsup in UNSUPPORTED_INSTRUMENTS:
        pattern = r"\b" + re.escape(unsup) + r"\b"
        if re.search(pattern, upper_text):
            return None, unsup

    # Check for supported instruments
    for sup in ["XAUUSD", "XAU/USD", "XAU USD", "GOLD"]:
        pattern = r"\b" + re.escape(sup) + r"\b"
        if re.search(pattern, upper_text):
            return "XAUUSD", None

    return None, None
