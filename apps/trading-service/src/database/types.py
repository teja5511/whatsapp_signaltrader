"""SQLite-safe exact-decimal column type.

SQLite has no true DECIMAL affinity: a ``Float``/``Numeric`` column round-trips
through a C double and silently loses exactness on prices, lots and stop levels.
Every financial column in this schema therefore stores a canonical, zero-padded
decimal *string* and hands back a ``Decimal`` on read.
"""

from decimal import Decimal
from typing import Optional, Union

from sqlalchemy import String
from sqlalchemy.types import TypeDecorator

DECIMAL_TEXT_LENGTH = 48

Numberish = Union[Decimal, int, float, str, None]


def coerce_decimal(value: Numberish) -> Optional[Decimal]:
    """Convert any supported numeric representation to Decimal without float drift."""
    if value is None:
        return None
    if isinstance(value, Decimal):
        return value
    # str() on a float gives the shortest repr that round-trips, which is the
    # closest thing to the author's intent that we can recover at this point.
    return Decimal(str(value))


class DecimalText(TypeDecorator):
    """Stores an exact decimal as text, returns a ``Decimal``."""

    impl = String(DECIMAL_TEXT_LENGTH)
    cache_ok = True

    def __init__(self, scale: int = 8, **kwargs):
        self.scale = scale
        self._quantum = Decimal(1).scaleb(-scale)
        super().__init__(length=DECIMAL_TEXT_LENGTH, **kwargs)

    def process_bind_param(self, value: Numberish, dialect) -> Optional[str]:
        dec = coerce_decimal(value)
        if dec is None:
            return None
        return format(dec.quantize(self._quantum), "f")

    def process_result_value(self, value, dialect) -> Optional[Decimal]:
        if value is None:
            return None
        if isinstance(value, Decimal):
            return value
        # Legacy rows written while the column was REAL come back as float/int.
        return Decimal(str(value))

    def copy(self, **kwargs):
        return DecimalText(scale=self.scale)


#: Prices, stop losses and take profits (XAUUSD needs 2, we keep 8 for headroom).
PriceDecimal = DecimalText(scale=8)
#: Lot sizes and volume caps.
VolumeDecimal = DecimalText(scale=4)
#: Account money fields.
MoneyDecimal = DecimalText(scale=2)
