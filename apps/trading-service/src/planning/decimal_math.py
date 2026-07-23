from decimal import Decimal, ROUND_HALF_UP
from typing import List, Tuple

def to_decimal(val: float | str | Decimal) -> Decimal:
    if isinstance(val, Decimal):
        return val
    return Decimal(str(val))

def round_to_tick(price: Decimal, tick_size: Decimal) -> Decimal:
    """
    Rounds price to nearest tick_size boundary using ROUND_HALF_UP.
    e.g., price = 4120.003, tick_size = 0.01 -> 4120.00
    """
    steps = (price / tick_size).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    return steps * tick_size

def quantize_price(price: Decimal, digits: int = 2) -> Decimal:
    fmt = "0." + "0" * digits if digits > 0 else "0"
    return price.quantize(Decimal(fmt), rounding=ROUND_HALF_UP)

def is_volume_aligned(volume: Decimal, volume_step: Decimal) -> bool:
    remainder = (volume / volume_step) % Decimal("1")
    return remainder == Decimal("0")
