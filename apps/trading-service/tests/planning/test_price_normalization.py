from decimal import Decimal
from src.planning.symbol_spec import SymbolSpecification
from src.planning.price_normalization import normalize_price_levels

def test_price_normalization_success():
    spec = SymbolSpecification(tick_size="0.01000000", digits=2)
    raw = [Decimal("3990.00"), Decimal("3992.003"), Decimal("3994.00"), Decimal("3996.00"), Decimal("3998.00")]
    norm, issues = normalize_price_levels(raw, Decimal("3990.00"), Decimal("3998.00"), spec)
    assert len(issues) == 0
    assert norm[1] == Decimal("3992.00")

def test_price_normalization_collision_detection():
    spec = SymbolSpecification(tick_size="5.00000000", digits=2)
    raw = [Decimal("3990.00"), Decimal("3991.00"), Decimal("3998.00")]
    _, issues = normalize_price_levels(raw, Decimal("3990.00"), Decimal("3998.00"), spec)
    assert any(i["code"] == "PRICE_NORMALIZATION_COLLISION" for i in issues)
