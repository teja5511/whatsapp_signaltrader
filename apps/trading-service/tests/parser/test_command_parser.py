import pytest
from src.parser.classification import parse_raw_text

def test_parse_modify_sl_command():
    raw = "Move SL to 4138 for added safety"
    res = parse_raw_text(raw)

    assert res.category == "FOLLOW_UP_COMMAND"
    assert res.command["commandType"] == "MODIFY_STOP_LOSS"
    assert res.command["value"] == "4138.00000000"
    assert res.requiresConfirmation is False
    assert res.executionEligibility == "ELIGIBLE_AFTER_CAMPAIGN_MATCH"

def test_parse_embedded_sl_in_commentary():
    raw = "Market is very shaky move SL to 4074 for safety"
    res = parse_raw_text(raw)

    assert res.category == "FOLLOW_UP_COMMAND"
    assert res.command["commandType"] == "MODIFY_STOP_LOSS"
    assert res.command["value"] == "4074.00000000"

def test_parse_hard_sl_command():
    raw = "Hard SL 4013"
    res = parse_raw_text(raw)

    assert res.category == "FOLLOW_UP_COMMAND"
    assert res.command["commandType"] == "MODIFY_STOP_LOSS"
    assert res.command["value"] == "4013.00000000"
    assert res.command["hardStop"] is True

def test_parse_standalone_tp_command():
    raw = "TP 3960"
    res = parse_raw_text(raw)

    assert res.category == "FOLLOW_UP_COMMAND"
    assert res.command["commandType"] == "ADD_TAKE_PROFIT"
    assert res.command["value"] == "3960.00000000"

def test_parse_zone_valid_command():
    raw = "Zone Valid"
    res = parse_raw_text(raw)

    assert res.category == "FOLLOW_UP_COMMAND"
    assert res.command["commandType"] == "ZONE_VALID"

def test_parse_reentry_command():
    raw = "Same Zone for Re-entry"
    res = parse_raw_text(raw)

    assert res.category == "FOLLOW_UP_COMMAND"
    assert res.command["commandType"] == "REENTRY"
