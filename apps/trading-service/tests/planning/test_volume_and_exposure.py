from decimal import Decimal
from src.planning.symbol_spec import SymbolSpecification
from src.planning.volume_normalization import validate_and_normalize_volume

def test_volume_exposure_validation_cases():
    spec = SymbolSpecification()

    # 1. 5 x 0.30 = 1.50 -> allowed
    req1, issues1 = validate_and_normalize_volume(5, Decimal("0.30"), Decimal("2.00"), spec)
    assert req1 == Decimal("1.50")
    assert len(issues1) == 0

    # 2. 6 x 0.30 = 1.80 -> allowed
    req2, issues2 = validate_and_normalize_volume(6, Decimal("0.30"), Decimal("2.00"), spec)
    assert req2 == Decimal("1.80")
    assert len(issues2) == 0

    # 3. 7 x 0.30 = 2.10 -> blocked by exposure cap
    req3, issues3 = validate_and_normalize_volume(7, Decimal("0.30"), Decimal("2.00"), spec)
    assert req3 == Decimal("2.10")
    assert any(i["code"] == "TOTAL_VOLUME_EXCEEDED" for i in issues3)

    # 4. 8 x 0.25 = 2.00 -> allowed
    req4, issues4 = validate_and_normalize_volume(8, Decimal("0.25"), Decimal("2.00"), spec)
    assert req4 == Decimal("2.00")
    assert len(issues4) == 0
