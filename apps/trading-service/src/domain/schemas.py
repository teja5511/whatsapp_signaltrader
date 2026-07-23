from decimal import Decimal
from typing import Optional, List, Any, Dict
from datetime import datetime
from pydantic import BaseModel, Field, model_validator
from src.domain.enums import TradeDirection, ExecutionMode, SignalStatus, OrderType

class AppSettingsDTO(BaseModel):
    entry_count: int = Field(default=5, ge=3, le=8, description="Number of grid entries (3-8)")
    lot_per_entry: Decimal = Field(default=Decimal("0.30"), gt=Decimal("0.0"), description="Lot size per individual entry")
    max_exposure_lots: Decimal = Field(default=Decimal("2.00"), le=Decimal("2.00"), description="Maximum campaign exposure cap")
    execution_mode: ExecutionMode = Field(default=ExecutionMode.CONFIRMATION)
    target_group_jid: Optional[str] = None
    admin_sender_jid: Optional[str] = None

    @model_validator(mode="after")
    def validate_total_exposure(self) -> "AppSettingsDTO":
        total_volume = Decimal(str(self.entry_count)) * self.lot_per_entry
        if total_volume > self.max_exposure_lots:
            raise ValueError(
                f"Total volume ({total_volume} lots) exceeds maximum allowable exposure ceiling ({self.max_exposure_lots} lots)"
            )
        return self

class RawMessageDTO(BaseModel):
    id: str
    group_id: str
    sender_id: str
    is_admin: bool
    content: str
    content_hash: str
    received_at: datetime

class ParsedSignalDTO(BaseModel):
    id: str
    raw_message_id: str
    symbol: str = Field(default="XAUUSD")
    direction: TradeDirection
    entry_min: Decimal
    entry_max: Decimal
    stop_loss: Decimal
    tp1: Optional[Decimal] = None
    tp2: Optional[Decimal] = None
    has_tp_open: bool = False
    created_at: datetime

class PlannedEntryDTO(BaseModel):
    id: str
    campaign_id: str
    ladder_index: int
    price: Decimal
    volume: Decimal
    order_type: OrderType
    stop_loss: Decimal
    take_profit: Optional[Decimal] = None
    tp_type: str  # FIXED_100_PIP, TP1, TP2

class CampaignDTO(BaseModel):
    id: str
    signal_id: str
    magic_number: int
    current_state: SignalStatus
    execution_mode: ExecutionMode
    entry_count: int
    lot_per_entry: Decimal
    total_volume: Decimal
    created_at: datetime
    updated_at: datetime
