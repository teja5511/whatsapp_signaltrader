from typing import List, Dict, Any, Tuple
from src.parser.normalization import normalize_text, NormalizationResult
from src.parser.patterns.instrument import extract_instrument
from src.parser.patterns.direction import extract_direction_and_intent
from src.parser.patterns.zone import extract_zone
from src.parser.patterns.stop_loss import extract_stop_loss
from src.parser.patterns.take_profit import extract_take_profits
from src.parser.patterns.commands import classify_command_or_commentary
from src.parser.validation import (
    ValidationIssue, EMPTY_MESSAGE, UNSUPPORTED_INSTRUMENT, INSTRUMENT_MISSING,
    DIRECTION_MISSING, DIRECTION_CONFLICT, ZONE_MISSING, ZONE_MULTIPLE_CONFLICT,
    STOP_LOSS_MISSING, TP1_MISSING, TP2_MISSING
)
from src.parser.result import ParserResult

def parse_raw_text(
    raw_text: str,
    message_id: str = "msg-001",
    group_id: str = "group-001",
    sender_id: str = "admin-001",
    quoted_message_id: str = None,
    is_reply: bool = False
) -> ParserResult:
    norm: NormalizationResult = normalize_text(raw_text)
    
    source_metadata = {
        "messageId": message_id,
        "groupId": group_id,
        "senderId": sender_id,
        "quotedMessageId": quoted_message_id,
        "isReply": is_reply
    }

    result = ParserResult(
        originalText=norm.original_text,
        normalizedText=norm.normalized_text,
        sourceMetadata=source_metadata
    )

    if not norm.normalized_lines:
        result.category = "INVALID"
        result.validationIssues.append(ValidationIssue(
            code=EMPTY_MESSAGE, severity="ERROR", field="text", message="Empty or whitespace-only message payload"
        ).to_dict())
        return result

    # 1. Check Instrument
    instrument, unsupported = extract_instrument(norm.normalized_text)
    if unsupported:
        result.category = "UNSUPPORTED"
        result.validationIssues.append(ValidationIssue(
            code=UNSUPPORTED_INSTRUMENT, severity="ERROR", field="instrument",
            message=f"Unsupported trading instrument '{unsupported}'. Only XAUUSD/Gold is supported."
        ).to_dict())
        return result

    # 2. Check Direction & Zone
    direction, order_intent, direction_conflict = extract_direction_and_intent(norm.normalized_text)
    zone_low, zone_high, values_reversed, zone_warnings = extract_zone(norm.normalized_lines)
    result.warnings.extend(zone_warnings)

    # Candidate check for NEW_SIGNAL:
    # A NEW_SIGNAL candidate requires explicit direction (BUY or SELL) and a valid price zone
    if direction and zone_low is not None and zone_high is not None and not direction_conflict:
        # We have a NEW_SIGNAL candidate!
        instrument_final = instrument or "XAUUSD" # Gold assumed if direction + zone exist explicitly
        stop_loss, is_hard_sl = extract_stop_loss(norm.normalized_lines)
        tp1, tp2, tp_open_present, tp_warnings = extract_take_profits(norm.normalized_lines)
        result.warnings.extend(tp_warnings)

        missing_fields = []
        if stop_loss is None:
            missing_fields.append("stop_loss")
            result.validationIssues.append(ValidationIssue(
                code=STOP_LOSS_MISSING, severity="WARNING", field="stop_loss", message="Signal lacks explicit Stop Loss"
            ).to_dict())

        if tp1 is None:
            missing_fields.append("tp1")
            result.validationIssues.append(ValidationIssue(
                code=TP1_MISSING, severity="WARNING", field="tp1", message="Signal lacks explicit TP1 target"
            ).to_dict())

        if tp2 is None:
            missing_fields.append("tp2")
            result.validationIssues.append(ValidationIssue(
                code=TP2_MISSING, severity="WARNING", field="tp2", message="Signal lacks explicit TP2 target"
            ).to_dict())

        completeness = "COMPLETE" if not missing_fields else "INCOMPLETE"

        result.category = "NEW_SIGNAL"
        result.executionEligibility = "ELIGIBLE_AFTER_VALIDATION"
        result.requiresConfirmation = True
        result.campaignMatchStrategyHint = "NONE"
        result.signal = {
            "instrument": instrument_final,
            "direction": direction,
            "orderIntent": order_intent,
            "zoneLow": f"{zone_low:.8f}",
            "zoneHigh": f"{zone_high:.8f}",
            "stopLoss": f"{stop_loss:.8f}" if stop_loss else None,
            "tp1": f"{tp1:.8f}" if tp1 else None,
            "tp2": f"{tp2:.8f}" if tp2 else None,
            "tpOpenPresent": tp_open_present,
            "completeness": completeness
        }
        return result

    # 3. Check Commands, Informational, or Ambiguous
    cmd_type, payload, is_ambiguous, is_informational = classify_command_or_commentary(norm.normalized_text, norm.normalized_lines)

    strategy_hint = "QUOTED_MESSAGE" if (is_reply and quoted_message_id) else ("LATEST_COMPATIBLE" if cmd_type else "NONE")

    if cmd_type and not is_ambiguous and not is_informational:
        result.category = "FOLLOW_UP_COMMAND"
        result.executionEligibility = "ELIGIBLE_AFTER_CAMPAIGN_MATCH"
        result.requiresConfirmation = False
        result.campaignMatchStrategyHint = strategy_hint
        result.command = payload
        result.commands = [payload]
        return result

    if is_ambiguous:
        result.category = "AMBIGUOUS"
        result.executionEligibility = "REQUIRES_CONFIRMATION"
        result.requiresConfirmation = True
        result.campaignMatchStrategyHint = strategy_hint
        result.ambiguous = payload
        result.validationIssues.append(ValidationIssue(
            code="AMBIGUOUS_COMMAND", severity="WARNING", field="command", message="Ambiguous phrase requires manual user confirmation"
        ).to_dict())
        return result

    if is_informational:
        result.category = "INFORMATIONAL"
        result.executionEligibility = "NEVER"
        result.requiresConfirmation = False
        result.campaignMatchStrategyHint = "NONE"
        result.informational = payload
        return result

    # 4. Fallback Invalid / Unsupported Syntax
    result.category = "INVALID"
    result.executionEligibility = "NEVER"
    result.validationIssues.append(ValidationIssue(
        code="UNSUPPORTED_MESSAGE", severity="ERROR", field="text", message="Message format could not be classified into signal or command"
    ).to_dict())
    return result
