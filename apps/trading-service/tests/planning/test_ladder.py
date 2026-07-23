import pytest
from decimal import Decimal
from src.planning.ladder import calculate_entry_ladder

def test_ladder_calculation_5_entries():
    levels, step = calculate_entry_ladder(3990.0, 3998.0, 5)
    assert len(levels) == 5
    assert levels[0] == Decimal("3990.0")
    assert levels[1] == Decimal("3992.0")
    assert levels[2] == Decimal("3994.0")
    assert levels[3] == Decimal("3996.0")
    assert levels[4] == Decimal("3998.0")
    assert step == Decimal("2.0")

def test_ladder_calculation_3_and_8_entries():
    levels_3, _ = calculate_entry_ladder(3990.0, 3998.0, 3)
    assert len(levels_3) == 3
    assert levels_3[0] == Decimal("3990.0")
    assert levels_3[-1] == Decimal("3998.0")

    levels_8, _ = calculate_entry_ladder(3990.0, 3998.0, 8)
    assert len(levels_8) == 8
    assert levels_8[0] == Decimal("3990.0")
    assert levels_8[-1] == Decimal("3998.0")

def test_ladder_invalid_entry_count_and_boundaries():
    with pytest.raises(ValueError):
        calculate_entry_ladder(3990.0, 3998.0, 2)

    with pytest.raises(ValueError):
        calculate_entry_ladder(3990.0, 3998.0, 9)

    with pytest.raises(ValueError):
        calculate_entry_ladder(3998.0, 3990.0, 5)
