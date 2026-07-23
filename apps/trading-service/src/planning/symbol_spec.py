from dataclasses import dataclass, asdict
from decimal import Decimal
from typing import Dict, Any
from src.planning.decimal_math import to_decimal

@dataclass
class SymbolSpecification:
    symbol: str = "XAUUSD"
    digits: int = 2
    point: str = "0.01000000"
    tick_size: str = "0.01000000"
    volume_min: str = "0.0100"
    volume_max: str = "100.0000"
    volume_step: str = "0.0100"
    stops_level_points: int = 0
    freeze_level_points: int = 0
    trade_mode: str = "FULL"
    contract_size: str = "100.0000"
    source: str = "TEST_FIXTURE"
    captured_at: str = "2026-07-23T10:00:00Z"

    def point_decimal(self) -> Decimal:
        return to_decimal(self.point)

    def tick_size_decimal(self) -> Decimal:
        return to_decimal(self.tick_size)

    def volume_min_decimal(self) -> Decimal:
        return to_decimal(self.volume_min)

    def volume_max_decimal(self) -> Decimal:
        return to_decimal(self.volume_max)

    def volume_step_decimal(self) -> Decimal:
        return to_decimal(self.volume_step)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

def get_default_xauusd_spec() -> SymbolSpecification:
    return SymbolSpecification()
