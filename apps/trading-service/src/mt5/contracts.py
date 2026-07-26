"""Pydantic Contracts & Data Transfer Objects for MT5 Adapter & Worker."""

from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from src.mt5.constants import (
    MODE_FAKE, HEALTH_NOT_INITIALIZED, ENV_DEMO, MARGIN_HEDGING,
    CANONICAL_SYMBOL_XAUUSD, FILLING_RETURN, TIME_GTC, JOB_QUEUED
)

class Mt5TerminalInfoDTO(BaseModel):
    connected: bool = True
    trade_allowed: bool = True
    name: str = "MetaTrader 5 Exness Demo"
    path: str = "C:\\Program Files\\MetaTrader 5\\terminal64.exe"
    company: str = "Exness Technologies Ltd"

class Mt5AccountInfoDTO(BaseModel):
    login: int = 12345678
    login_masked: str = "1234****"
    server: str = "Exness-MT5Trial6"
    company: str = "Exness Technologies Ltd"
    environment_kind: str = ENV_DEMO  # DEMO, CONTEST, REAL, UNKNOWN
    margin_mode: str = MARGIN_HEDGING # HEDGING, NETTING, EXCHANGE, UNKNOWN
    currency: str = "USD"
    leverage: int = 100
    balance: Decimal = Decimal("10000.00")
    equity: Decimal = Decimal("10000.00")
    margin: Decimal = Decimal("0.00")
    margin_free: Decimal = Decimal("10000.00")
    trade_allowed: bool = True
    trade_expert: bool = True

class Mt5SymbolResolutionDTO(BaseModel):
    canonical_symbol: str = CANONICAL_SYMBOL_XAUUSD
    broker_symbol: str = CANONICAL_SYMBOL_XAUUSD
    is_resolved: bool = True
    source: str = "EXACT_MATCH"

class Mt5SymbolSpecificationDTO(BaseModel):
    symbol: str = CANONICAL_SYMBOL_XAUUSD
    digits: int = 2
    point: Decimal = Decimal("0.01")
    tick_size: Decimal = Decimal("0.01")
    volume_min: Decimal = Decimal("0.01")
    volume_max: Decimal = Decimal("100.00")
    volume_step: Decimal = Decimal("0.01")
    stops_level_points: int = 0
    freeze_level_points: int = 0
    trade_mode: str = "FULL"
    contract_size: Decimal = Decimal("100.00")
    filling_mode: str = FILLING_RETURN
    source: str = "TEST_FIXTURE"
    captured_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class Mt5OrderCheckRequestDTO(BaseModel):
    action: int = 5  # TRADE_ACTION_PENDING
    symbol: str = CANONICAL_SYMBOL_XAUUSD
    volume: Decimal
    order_type: str  # BUY_LIMIT, SELL_LIMIT
    price: Decimal
    stop_loss: Decimal
    take_profit: Optional[Decimal] = None
    magic_number: int
    comment: str
    filling_type: str = FILLING_RETURN
    time_type: str = TIME_GTC

class Mt5OrderCheckResultDTO(BaseModel):
    retcode: int = 0
    retcode_name: str = "TRADE_RETCODE_DONE"
    is_valid: bool = True
    comment: str = "Check OK"
    margin: Decimal = Decimal("0.00")
    margin_free: Decimal = Decimal("10000.00")

class Mt5OrderSendRequestDTO(BaseModel):
    action: int = 5
    symbol: str = CANONICAL_SYMBOL_XAUUSD
    volume: Decimal
    order_type: str
    price: Decimal
    stop_loss: Decimal
    take_profit: Optional[Decimal] = None
    magic_number: int
    comment: str
    filling_type: str = FILLING_RETURN
    time_type: str = TIME_GTC
    idempotency_key: str

class Mt5OrderSendResultDTO(BaseModel):
    retcode: int = 10009  # TRADE_RETCODE_DONE
    retcode_name: str = "TRADE_RETCODE_DONE"
    deal_ticket: Optional[int] = None
    order_ticket: Optional[int] = None
    volume: Decimal = Decimal("0.00")
    price: Decimal = Decimal("0.00")
    comment: str = "Order placed successfully"
    is_success: bool = True
    dry_run: bool = False
    execution_performed: bool = True

class Mt5OrderSnapshotDTO(BaseModel):
    ticket: int
    magic_number: int
    symbol: str
    order_type: str
    volume: Decimal
    price: Decimal
    stop_loss: Decimal
    take_profit: Optional[Decimal] = None
    comment: str
    state: str = "PLACED"

class Mt5PositionSnapshotDTO(BaseModel):
    ticket: int
    magic_number: int
    symbol: str
    position_type: str
    volume: Decimal
    price_open: Decimal
    stop_loss: Decimal
    take_profit: Optional[Decimal] = None
    profit: Decimal = Decimal("0.00")
    comment: str
    state: str = "OPEN"

class Mt5TickDTO(BaseModel):
    symbol: str = CANONICAL_SYMBOL_XAUUSD
    bid: Decimal
    ask: Decimal
    captured_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    @property
    def mid(self) -> Decimal:
        return (self.bid + self.ask) / Decimal("2")

class Mt5HistoryOrderDTO(BaseModel):
    ticket: int
    magic_number: int = 0
    symbol: str = CANONICAL_SYMBOL_XAUUSD
    order_type: str = "SELL_LIMIT"
    volume: Decimal = Decimal("0.00")
    price: Decimal = Decimal("0.00")
    state: str = "HISTORY"
    comment: str = ""
    closed_at: Optional[str] = None

class Mt5MutationResultDTO(BaseModel):
    """Outcome of a broker-side mutation (modify / delete / close).

    ``outcome_unknown`` is set when the request was transmitted but the result
    could not be confirmed. Callers must never treat that as success and must
    never blindly resend.
    """
    ticket: int
    operation: str
    retcode: int = 10009
    retcode_name: str = "TRADE_RETCODE_DONE"
    is_success: bool = True
    outcome_unknown: bool = False
    comment: str = ""
    closed_volume: Optional[Decimal] = None

class Mt5StatusDTO(BaseModel):
    adapter_mode: str = MODE_FAKE
    health_state: str = HEALTH_NOT_INITIALIZED
    execution_enabled: bool = False
    demo_only: bool = True
    live_execution_enabled: bool = False
    trading_enabled: bool = False
    account_connected: bool = False
    account_environment: str = ENV_DEMO
    margin_mode: str = MARGIN_HEDGING
    resolved_symbol: Optional[str] = CANONICAL_SYMBOL_XAUUSD

class Mt5ExecutionPreflightResultDTO(BaseModel):
    campaign_id: str
    is_ready: bool = True
    checks_passed: List[str] = Field(default_factory=list)
    blocking_reasons: List[str] = Field(default_factory=list)

class Mt5CampaignExecutionRequestDTO(BaseModel):
    expected_version: int
    planning_fingerprint: str
    explicit_user_confirm: bool = True

class Mt5CampaignExecutionResultDTO(BaseModel):
    campaign_id: str
    batch_id: str
    status: str = "QUEUED"
    jobs_count: int
    message: str = "Execution batch queued successfully."

class Mt5OrderModificationRequestDTO(BaseModel):
    price: Optional[Decimal] = None
    stop_loss: Optional[Decimal] = None
    take_profit: Optional[Decimal] = None

class Mt5PositionModificationRequestDTO(BaseModel):
    stop_loss: Decimal
    take_profit: Optional[Decimal] = None

class Mt5PositionCloseRequestDTO(BaseModel):
    volume: Optional[Decimal] = None

class Mt5EmergencyCloseRequestDTO(BaseModel):
    confirmation_phrase: str
    scope: str = "APPLICATION_OWNED"
