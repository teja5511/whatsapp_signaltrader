import pytest
from src.parser.classification import parse_raw_text

def test_parse_full_gold_sell_signal():
    raw = "Gold Sell\n4120-4128\n\nsl - 4136\n\ntp - 4112\ntp - 4104\ntp - Open"
    res = parse_raw_text(raw)

    assert res.category == "NEW_SIGNAL"
    assert res.executionEligibility == "ELIGIBLE_AFTER_VALIDATION"
    assert res.requiresConfirmation is True
    assert res.signal["instrument"] == "XAUUSD"
    assert res.signal["direction"] == "SELL"
    assert res.signal["orderIntent"] == "UNSPECIFIED"
    assert res.signal["zoneLow"] == "4120.00000000"
    assert res.signal["zoneHigh"] == "4128.00000000"
    assert res.signal["stopLoss"] == "4136.00000000"
    assert res.signal["tp1"] == "4112.00000000"
    assert res.signal["tp2"] == "4104.00000000"
    assert res.signal["tpOpenPresent"] is True
    assert res.signal["completeness"] == "COMPLETE"

def test_parse_incomplete_gold_sell_limit_signal():
    raw = "Gold Sell Limit\n3990-3998\n\nSl - 4008"
    res = parse_raw_text(raw)

    assert res.category == "NEW_SIGNAL"
    assert res.signal["direction"] == "SELL"
    assert res.signal["orderIntent"] == "LIMIT"
    assert res.signal["zoneLow"] == "3990.00000000"
    assert res.signal["zoneHigh"] == "3998.00000000"
    assert res.signal["stopLoss"] == "4008.00000000"
    assert res.signal["tp1"] is None
    assert res.signal["tp2"] is None
    assert res.signal["completeness"] == "INCOMPLETE"

def test_parse_reversed_zone_order():
    raw = "Gold Buy\n4128-4120\nSL 4100\nTP1 4140"
    res = parse_raw_text(raw)

    assert res.category == "NEW_SIGNAL"
    assert res.signal["direction"] == "BUY"
    assert res.signal["zoneLow"] == "4120.00000000"
    assert res.signal["zoneHigh"] == "4128.00000000"
    assert len(res.warnings) > 0
    assert "auto-sorted into low/high" in res.warnings[0]
