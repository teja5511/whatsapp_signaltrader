import pytest
from decimal import Decimal
from pydantic import ValidationError
from src.domain.schemas import AppSettingsDTO, ParsedSignalDTO
from src.domain.enums import TradeDirection, ExecutionMode

def test_valid_app_settings():
    settings = AppSettingsDTO(
        entry_count=5,
        lot_per_entry=Decimal("0.30"),
        max_exposure_lots=Decimal("2.00"),
        execution_mode=ExecutionMode.CONFIRMATION
    )
    assert settings.entry_count == 5
    assert settings.lot_per_entry == Decimal("0.30")
    # 5 * 0.30 = 1.50 <= 2.00

def test_exposure_limit_exceeded_raises_validation_error():
    with pytest.raises(ValidationError) as exc_info:
        AppSettingsDTO(
            entry_count=5,
            lot_per_entry=Decimal("0.50"), # 5 * 0.50 = 2.50 > 2.00
            max_exposure_lots=Decimal("2.00")
        )
    assert "exceeds maximum allowable exposure ceiling" in str(exc_info.value)

def test_entry_count_out_of_bounds_raises():
    with pytest.raises(ValidationError):
        AppSettingsDTO(entry_count=2) # Less than 3
    with pytest.raises(ValidationError):
        AppSettingsDTO(entry_count=9) # Greater than 8

def test_parsed_signal_dto():
    from datetime import datetime, timezone
    sig = ParsedSignalDTO(
        id="123e4567-e89b-12d3-a456-426614174000",
        raw_message_id="msg-001",
        symbol="XAUUSD",
        direction=TradeDirection.SELL,
        entry_min=Decimal("4120.00"),
        entry_max=Decimal("4128.00"),
        stop_loss=Decimal("4136.00"),
        tp1=Decimal("4112.00"),
        tp2=Decimal("4104.00"),
        has_tp_open=True,
        created_at=datetime.now(timezone.utc)
    )
    assert sig.symbol == "XAUUSD"
    assert sig.direction == TradeDirection.SELL
