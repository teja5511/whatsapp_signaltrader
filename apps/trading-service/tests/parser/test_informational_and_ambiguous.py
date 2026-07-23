import pytest
from src.parser.classification import parse_raw_text

def test_informational_messages():
    info_examples = [
        "We barely survived the SL.",
        "Wait for update.",
        "100 Pips Almost.",
        "50+ Pips.",
        "It will come to Zone again."
    ]
    for text in info_examples:
        res = parse_raw_text(text)
        assert res.category == "INFORMATIONAL", f"Failed for: {text}"
        assert res.isExecutable is False
        assert res.executionEligibility == "NEVER"

def test_ambiguous_messages():
    ambiguous_examples = [
        "Secure Profits.",
        "Exit this trade on your comfort.",
        "Hold it.",
        "Skip this for now.",
        "Just touched our SL and reversed, if you haven't closed like mine, Hold it."
    ]
    for text in ambiguous_examples:
        res = parse_raw_text(text)
        assert res.category == "AMBIGUOUS", f"Failed for: {text}"
        assert res.isExecutable is False
        assert res.requiresConfirmation is True
        assert res.executionEligibility == "REQUIRES_CONFIRMATION"

def test_unsupported_instrument_rejection():
    raw = "BTCUSD Buy 65000-66000 SL 64000"
    res = parse_raw_text(raw)
    assert res.category == "UNSUPPORTED"
    assert res.isExecutable is False
    assert res.validationIssues[0]["code"] == "UNSUPPORTED_INSTRUMENT"
