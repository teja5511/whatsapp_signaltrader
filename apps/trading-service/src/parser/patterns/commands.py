import re
from decimal import Decimal
from typing import Optional, Dict, Any, List, Tuple

def parse_decimal_price(val_str: str) -> Decimal:
    cleaned = val_str.replace(",", "")
    return Decimal(cleaned)

def classify_command_or_commentary(text: str, lines: List[str]) -> Tuple[Optional[str], Optional[Dict[str, Any]], bool, bool]:
    """
    Returns (command_type_or_category, extracted_payload, is_ambiguous, is_informational)
    """
    upper_text = text.upper()

    # 1. AMBIGUOUS phrases requiring confirmation (Check ambiguous phrases first so commentary like 'Exit this trade on your comfort' is preserved as ambiguous)
    ambiguous_patterns = [
        r"\bSECURE\s+PROFITS\b",
        r"\bEXIT\s+THIS\s+TRADE\s+ON\s+YOUR\s+COMFORT\b",
        r"\bHOLD\s+IT\b",
        r"\bSKIP\s+THIS\s+FOR\s+NOW\b",
        r"\bJUST\s+TOUCHED\s+OUR\s+SL\b"
    ]
    for amb in ambiguous_patterns:
        if re.search(amb, upper_text):
            return "AMBIGUOUS", {
                "phrase": text,
                "requiresConfirmation": True,
                "executionEligibility": "REQUIRES_CONFIRMATION"
            }, True, False

    # 2. Check explicit MODIFY_STOP_LOSS embedded in commentary or standalone
    sl_cmd_match = re.search(
        r"(?:MOVE\s+(?:SL|STOP\s*LOSS)\s+TO|HARD\s+SL|SL)\s*[:-]?\s*(\d{3,5}(?:,\d{3})?(?:\.\d+)?)",
        upper_text
    )
    if sl_cmd_match:
        try:
            sl_val = parse_decimal_price(sl_cmd_match.group(1))
            is_hard = "HARD" in upper_text
            return "MODIFY_STOP_LOSS", {
                "commandType": "MODIFY_STOP_LOSS",
                "classification": "EXPLICIT",
                "value": f"{sl_val:.8f}",
                "valueKind": "PRICE",
                "hardStop": is_hard,
                "targetTpSlot": None
            }, False, False
        except Exception:
            pass

    # 3. Check explicit standalone ADD_TAKE_PROFIT
    tp_cmd_match = re.search(
        r"^\s*(?:TP1|TP2|TP|TAKE\s*PROFIT)\s*[:-]?\s*(\d{3,5}(?:,\d{3})?(?:\.\d+)?)\s*$",
        upper_text
    )
    if tp_cmd_match:
        try:
            tp_val = parse_decimal_price(tp_cmd_match.group(1))
            slot = "UNSPECIFIED"
            if "TP1" in upper_text:
                slot = "TP1"
            elif "TP2" in upper_text:
                slot = "TP2"
            return "ADD_TAKE_PROFIT", {
                "commandType": "ADD_TAKE_PROFIT",
                "classification": "EXPLICIT",
                "value": f"{tp_val:.8f}",
                "valueKind": "PRICE",
                "hardStop": False,
                "targetTpSlot": slot
            }, False, False
        except Exception:
            pass

    # 4. Explicit CLOSE_CAMPAIGN commands
    if re.search(r"\b(CLOSE\s+(?:TRADE|THIS\s+TRADE|THE\s+TRADE|ALL\s+POSITIONS)|EXIT\s+(?:TRADE|THIS\s+TRADE))\b", upper_text):
        return "CLOSE_CAMPAIGN", {
            "commandType": "CLOSE_CAMPAIGN",
            "classification": "EXPLICIT",
            "value": None,
            "valueKind": "NONE",
            "hardStop": False,
            "targetTpSlot": None
        }, False, False

    # 5. Explicit ZONE_VALID
    if re.search(r"\bZONE\s+VALID\b", upper_text):
        return "ZONE_VALID", {
            "commandType": "ZONE_VALID",
            "classification": "EXPLICIT",
            "value": None,
            "valueKind": "NONE",
            "hardStop": False,
            "targetTpSlot": None
        }, False, False

    # 6. Explicit REENTRY
    if re.search(r"\b(SAME\s+ZONE\s+(?:FOR\s+)?RE-?ENTRY|RE-?ENTER\s+SAME\s+ZONE)\b", upper_text):
        return "REENTRY", {
            "commandType": "REENTRY",
            "classification": "EXPLICIT",
            "value": None,
            "valueKind": "NONE",
            "hardStop": False,
            "targetTpSlot": None
        }, False, False

    # 7. Explicit CANCEL_SIGNAL
    if re.search(r"\b(CANCEL\s+SIGNAL|CANCEL\b)", upper_text):
        return "CANCEL_SIGNAL", {
            "commandType": "CANCEL_SIGNAL",
            "classification": "EXPLICIT",
            "value": None,
            "valueKind": "NONE",
            "hardStop": False,
            "targetTpSlot": None
        }, False, False

    # 8. INFORMATIONAL phrases
    info_patterns = [
        r"\bWE\s+BARELY\s+SURVIVED\b",
        r"\bWAIT\s+FOR\s+UPDATE\b",
        r"\b100\s+PIPS\s+ALMOST\b",
        r"\b50\+\s+PIPS\b",
        r"\bIT\s+WILL\s+COME\s+TO\s+ZONE\s+AGAIN\b",
        r"\bMARKET\s+IS\s+VERY\s+SHAKY\b"
    ]
    for inf in info_patterns:
        if re.search(inf, upper_text):
            return "INFORMATIONAL", {
                "commentary": text,
                "isExecutable": False,
                "executionEligibility": "NEVER"
            }, False, True

    return None, None, False, False
