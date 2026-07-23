import pytest
from src.parser.normalization import normalize_text

def test_normalization_crlf_and_unicode_dashes():
    raw = "Gold Sell\r\n4120–4128\r\n\r\nsl — 4136\r\n\r\ntp - 4112"
    res = normalize_text(raw)
    assert res.original_text == raw
    assert "-" in res.normalized_text
    assert "–" not in res.normalized_text
    assert "—" not in res.normalized_text
    assert len(res.normalized_lines) == 4
    assert res.normalized_lines[0] == "Gold Sell"
    assert res.normalized_lines[1] == "4120-4128"
    assert res.normalized_lines[2] == "sl - 4136"
    assert res.normalized_lines[3] == "tp - 4112"

def test_normalization_empty_text():
    res = normalize_text("   \n\t  ")
    assert res.normalized_text == ""
    assert res.normalized_lines == []
