from decimal import Decimal
from typing import List, Tuple
from src.planning.decimal_math import to_decimal

def calculate_entry_ladder(
    zone_low: Decimal | str | float,
    zone_high: Decimal | str | float,
    entry_count: int
) -> Tuple[List[Decimal], Decimal]:
    """
    Calculates entry_count evenly distributed prices between zone_low and zone_high.
    Returns (raw_levels, raw_step).
    """
    z_low = to_decimal(zone_low)
    z_high = to_decimal(zone_high)

    if z_low >= z_high:
        raise ValueError(f"Invalid zone boundaries: zone_low ({z_low}) must be strictly less than zone_high ({z_high})")

    if not (3 <= entry_count <= 8):
        raise ValueError(f"Invalid entry count ({entry_count}): must be between 3 and 8 inclusive")

    raw_step = (z_high - z_low) / Decimal(str(entry_count - 1))
    levels = []

    for i in range(entry_count):
        if i == 0:
            levels.append(z_low)
        elif i == entry_count - 1:
            levels.append(z_high)
        else:
            level = z_low + (raw_step * Decimal(str(i)))
            levels.append(level)

    return levels, raw_step
