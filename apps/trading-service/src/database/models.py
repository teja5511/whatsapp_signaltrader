from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import (
    String, Boolean, Integer, Float, DateTime, ForeignKey, Text, UniqueConstraint, Index
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database.engine import Base

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class AppSettingModel(Base):
    __tablename__ = "app_settings"
    __table_args__ = {'extend_existing': True}

    key: Mapped[str] = mapped_column(String(64), primary_key=True)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

class WhatsAppMessageModel(Base):
    __tablename__ = "whatsapp_messages"
    __table_args__ = {'extend_existing': True}

    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    group_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    sender_id: Mapped[str] = mapped_column(String(128), nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    raw_content: Mapped[str] = mapped_column(Text, nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    parsed_message: Mapped[Optional["ParsedMessageModel"]] = relationship("ParsedMessageModel", back_populates="raw_message", uselist=False)

class DuplicateKeyModel(Base):
    __tablename__ = "duplicate_keys"
    __table_args__ = {'extend_existing': True}

    dedup_key: Mapped[str] = mapped_column(String(128), primary_key=True)
    duplicate_type: Mapped[str] = mapped_column(String(32), nullable=False, default="EXACT")
    message_id: Mapped[Optional[str]] = mapped_column(String(128), ForeignKey("whatsapp_messages.id"), nullable=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

class ParsedMessageModel(Base):
    __tablename__ = "parsed_messages"
    __table_args__ = {'extend_existing': True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    raw_message_id: Mapped[str] = mapped_column(String(128), ForeignKey("whatsapp_messages.id"), unique=True, nullable=False)
    message_type: Mapped[str] = mapped_column(String(32), nullable=False)  # NEW_SIGNAL, FOLLOW_UP_COMMAND, etc.
    parsed_json: Mapped[str] = mapped_column(Text, nullable=False)
    parsed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    raw_message: Mapped["WhatsAppMessageModel"] = relationship("WhatsAppMessageModel", back_populates="parsed_message")
    signal: Mapped[Optional["SignalModel"]] = relationship("SignalModel", back_populates="parsed_message", uselist=False)

class SignalModel(Base):
    __tablename__ = "signals"
    __table_args__ = {'extend_existing': True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    parsed_message_id: Mapped[str] = mapped_column(String(36), ForeignKey("parsed_messages.id"), nullable=False)
    symbol: Mapped[str] = mapped_column(String(16), nullable=False, default="XAUUSD")
    direction: Mapped[str] = mapped_column(String(8), nullable=False)  # BUY or SELL
    entry_min: Mapped[float] = mapped_column(Float, nullable=False)
    entry_max: Mapped[float] = mapped_column(Float, nullable=False)
    stop_loss: Mapped[float] = mapped_column(Float, nullable=False)
    tp1: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    tp2: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    has_tp_open: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    parsed_message: Mapped["ParsedMessageModel"] = relationship("ParsedMessageModel", back_populates="signal")
    campaign: Mapped[Optional["CampaignModel"]] = relationship("CampaignModel", back_populates="signal", uselist=False)

class CampaignModel(Base):
    __tablename__ = "campaigns"
    __table_args__ = {'extend_existing': True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    campaign_code: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    signal_id: Mapped[str] = mapped_column(String(36), ForeignKey("signals.id"), index=True, nullable=False)
    parent_campaign_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("campaigns.id"), index=True, nullable=True)
    reentry_sequence: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    magic_number: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    current_state: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    execution_mode: Mapped[str] = mapped_column(String(16), nullable=False)
    entry_count: Mapped[int] = mapped_column(Integer, nullable=False)
    lot_per_entry: Mapped[float] = mapped_column(Float, nullable=False)
    total_volume: Mapped[float] = mapped_column(Float, nullable=False)
    maximum_total_lots: Mapped[float] = mapped_column(Float, nullable=False, default=2.0)
    requested_total_lots: Mapped[float] = mapped_column(Float, nullable=False, default=1.5)
    current_stop_loss: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    tp1: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    tp2: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    has_tp_open: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, index=True, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    signal: Mapped["SignalModel"] = relationship("SignalModel", back_populates="campaign")
    transitions: Mapped[List["CampaignStateTransitionModel"]] = relationship("CampaignStateTransitionModel", back_populates="campaign")
    planned_entries: Mapped[List["PlannedEntryModel"]] = relationship("PlannedEntryModel", back_populates="campaign")
    pending_orders: Mapped[List["PendingOrderModel"]] = relationship("PendingOrderModel", back_populates="campaign")
    positions: Mapped[List["PositionModel"]] = relationship("PositionModel", back_populates="campaign")

class CampaignStateTransitionModel(Base):
    __tablename__ = "campaign_state_transitions"
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    campaign_id: Mapped[str] = mapped_column(String(36), ForeignKey("campaigns.id"), index=True, nullable=False)
    from_state: Mapped[str] = mapped_column(String(32), nullable=False)
    to_state: Mapped[str] = mapped_column(String(32), nullable=False)
    reason_code: Mapped[str] = mapped_column(String(64), nullable=False, default="SIGNAL_RECEIVED")
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    trigger_type: Mapped[str] = mapped_column(String(32), nullable=False, default="WHATSAPP_MESSAGE")
    trigger_reference_id: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    correlation_id: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    transitioned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    campaign: Mapped["CampaignModel"] = relationship("CampaignModel", back_populates="transitions")

class PlannedEntryModel(Base):
    __tablename__ = "planned_entries"
    __table_args__ = {'extend_existing': True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    campaign_id: Mapped[str] = mapped_column(String(36), ForeignKey("campaigns.id"), index=True, nullable=False)
    ladder_index: Mapped[int] = mapped_column(Integer, nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    volume: Mapped[float] = mapped_column(Float, nullable=False)
    order_type: Mapped[str] = mapped_column(String(16), nullable=False)
    stop_loss: Mapped[float] = mapped_column(Float, nullable=False)
    take_profit: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    tp_type: Mapped[str] = mapped_column(String(16), nullable=False)

    campaign: Mapped["CampaignModel"] = relationship("CampaignModel", back_populates="planned_entries")
    pending_order: Mapped[Optional["PendingOrderModel"]] = relationship("PendingOrderModel", back_populates="planned_entry", uselist=False)

class PendingOrderModel(Base):
    __tablename__ = "pending_orders"
    __table_args__ = {'extend_existing': True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    campaign_id: Mapped[str] = mapped_column(String(36), ForeignKey("campaigns.id"), nullable=False)
    planned_entry_id: Mapped[str] = mapped_column(String(36), ForeignKey("planned_entries.id"), nullable=False)
    mt5_ticket: Mapped[Optional[int]] = mapped_column(Integer, unique=True, index=True, nullable=True)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    volume: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False)
    placed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    campaign: Mapped["CampaignModel"] = relationship("CampaignModel", back_populates="pending_orders")
    planned_entry: Mapped["PlannedEntryModel"] = relationship("PlannedEntryModel", back_populates="pending_order")
    position: Mapped[Optional["PositionModel"]] = relationship("PositionModel", back_populates="pending_order", uselist=False)

class PositionModel(Base):
    __tablename__ = "positions"
    __table_args__ = {'extend_existing': True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    campaign_id: Mapped[str] = mapped_column(String(36), ForeignKey("campaigns.id"), nullable=False)
    pending_order_id: Mapped[str] = mapped_column(String(36), ForeignKey("pending_orders.id"), nullable=False)
    mt5_position_ticket: Mapped[int] = mapped_column(Integer, unique=True, index=True, nullable=False)
    entry_price: Mapped[float] = mapped_column(Float, nullable=False)
    current_sl: Mapped[float] = mapped_column(Float, nullable=False)
    current_tp: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    volume: Mapped[float] = mapped_column(Float, nullable=False)
    profit: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    is_closed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    closed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    campaign: Mapped["CampaignModel"] = relationship("CampaignModel", back_populates="positions")
    pending_order: Mapped["PendingOrderModel"] = relationship("PendingOrderModel", back_populates="position")

class CommandModel(Base):
    __tablename__ = "commands"
    __table_args__ = {'extend_existing': True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    campaign_id: Mapped[str] = mapped_column(String(36), ForeignKey("campaigns.id"), index=True, nullable=False)
    raw_message_id: Mapped[str] = mapped_column(String(128), ForeignKey("whatsapp_messages.id"), index=True, nullable=False)
    command_type: Mapped[str] = mapped_column(String(32), nullable=False)
    parameters_json: Mapped[str] = mapped_column(Text, nullable=False)
    executed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

class ConfirmationModel(Base):
    __tablename__ = "confirmations"
    __table_args__ = {'extend_existing': True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    campaign_id: Mapped[str] = mapped_column(String(36), ForeignKey("campaigns.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="PENDING")
    user_action_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

class SystemAuditEventModel(Base):
    __tablename__ = "system_audit_events"
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    event_type: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    payload_json: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

class SystemErrorModel(Base):
    __tablename__ = "system_errors"
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    error_code: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    traceback_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

# MT5 Execution & Adapter Persistence Models

class MT5ExecutionBatchModel(Base):
    __tablename__ = "mt5_execution_batches"
    __table_args__ = {'extend_existing': True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    campaign_id: Mapped[str] = mapped_column(String(36), ForeignKey("campaigns.id"), index=True, nullable=False)
    campaign_version: Mapped[int] = mapped_column(Integer, nullable=False)
    planning_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="QUEUED")
    total_jobs: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    completed_jobs: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    failed_jobs: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

class MT5ExecutionJobModel(Base):
    __tablename__ = "mt5_execution_jobs"
    __table_args__ = (
        UniqueConstraint('idempotency_key', name='uq_mt5_jobs_idempotency_key'),
        {'extend_existing': True}
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    batch_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("mt5_execution_batches.id"), index=True, nullable=True)
    campaign_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("campaigns.id"), index=True, nullable=True)
    planned_entry_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("planned_entries.id"), index=True, nullable=True)
    operation_type: Mapped[str] = mapped_column(String(64), nullable=False)
    idempotency_key: Mapped[str] = mapped_column(String(128), unique=True, index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(32), index=True, nullable=False, default="QUEUED")
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=10)
    attempt_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    max_attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    payload_json: Mapped[str] = mapped_column(Text, nullable=False)
    result_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    last_error_code: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    last_error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    available_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    locked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    locked_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

class MT5AccountSnapshotModel(Base):
    __tablename__ = "mt5_account_snapshots"
    __table_args__ = {'extend_existing': True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    login: Mapped[int] = mapped_column(Integer, nullable=False)
    login_masked: Mapped[str] = mapped_column(String(64), nullable=False)
    server: Mapped[str] = mapped_column(String(128), nullable=False)
    company: Mapped[str] = mapped_column(String(128), nullable=False)
    environment_kind: Mapped[str] = mapped_column(String(32), nullable=False)  # DEMO, CONTEST, REAL, UNKNOWN
    margin_mode: Mapped[str] = mapped_column(String(32), nullable=False)       # HEDGING, NETTING, EXCHANGE, UNKNOWN
    currency: Mapped[str] = mapped_column(String(16), nullable=False, default="USD")
    leverage: Mapped[int] = mapped_column(Integer, nullable=False, default=100)
    balance: Mapped[float] = mapped_column(Float, nullable=False)
    equity: Mapped[float] = mapped_column(Float, nullable=False)
    margin: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    margin_free: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    trade_allowed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    trade_expert: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    captured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

class MT5SymbolSnapshotModel(Base):
    __tablename__ = "mt5_symbol_snapshots"
    __table_args__ = {'extend_existing': True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    canonical_symbol: Mapped[str] = mapped_column(String(16), nullable=False, default="XAUUSD")
    broker_symbol: Mapped[str] = mapped_column(String(32), nullable=False)
    digits: Mapped[int] = mapped_column(Integer, nullable=False, default=2)
    point: Mapped[float] = mapped_column(Float, nullable=False, default=0.01)
    tick_size: Mapped[float] = mapped_column(Float, nullable=False, default=0.01)
    volume_min: Mapped[float] = mapped_column(Float, nullable=False, default=0.01)
    volume_max: Mapped[float] = mapped_column(Float, nullable=False, default=100.0)
    volume_step: Mapped[float] = mapped_column(Float, nullable=False, default=0.01)
    stops_level_points: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    freeze_level_points: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    trade_mode: Mapped[str] = mapped_column(String(32), nullable=False, default="FULL")
    contract_size: Mapped[float] = mapped_column(Float, nullable=False, default=100.0)
    snapshot_json: Mapped[str] = mapped_column(Text, nullable=False)
    captured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

class MT5OrderRecordModel(Base):
    __tablename__ = "mt5_orders"
    __table_args__ = {'extend_existing': True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    campaign_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("campaigns.id"), index=True, nullable=True)
    planned_entry_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("planned_entries.id"), index=True, nullable=True)
    ticket: Mapped[int] = mapped_column(Integer, unique=True, index=True, nullable=False)
    magic_number: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    symbol: Mapped[str] = mapped_column(String(32), nullable=False)
    order_type: Mapped[str] = mapped_column(String(32), nullable=False)
    volume: Mapped[float] = mapped_column(Float, nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    stop_loss: Mapped[float] = mapped_column(Float, nullable=False)
    take_profit: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    comment: Mapped[str] = mapped_column(String(128), nullable=False)
    state: Mapped[str] = mapped_column(String(32), nullable=False, default="PLACED")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

class MT5PositionRecordModel(Base):
    __tablename__ = "mt5_positions"
    __table_args__ = {'extend_existing': True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    campaign_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("campaigns.id"), index=True, nullable=True)
    planned_entry_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("planned_entries.id"), index=True, nullable=True)
    ticket: Mapped[int] = mapped_column(Integer, unique=True, index=True, nullable=False)
    magic_number: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    symbol: Mapped[str] = mapped_column(String(32), nullable=False)
    position_type: Mapped[str] = mapped_column(String(16), nullable=False)  # BUY or SELL
    volume: Mapped[float] = mapped_column(Float, nullable=False)
    price_open: Mapped[float] = mapped_column(Float, nullable=False)
    stop_loss: Mapped[float] = mapped_column(Float, nullable=False)
    take_profit: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    profit: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    comment: Mapped[str] = mapped_column(String(128), nullable=False)
    state: Mapped[str] = mapped_column(String(32), nullable=False, default="OPEN")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

class MT5OrderCheckModel(Base):
    __tablename__ = "mt5_order_checks"
    __table_args__ = {'extend_existing': True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    job_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("mt5_execution_jobs.id"), nullable=True)
    request_json: Mapped[str] = mapped_column(Text, nullable=False)
    retcode: Mapped[int] = mapped_column(Integer, nullable=False)
    retcode_name: Mapped[str] = mapped_column(String(64), nullable=False)
    is_valid: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    comment: Mapped[str] = mapped_column(String(256), nullable=False, default="")
    margin: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    margin_free: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    checked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

class MT5ExecutionAttemptModel(Base):
    __tablename__ = "mt5_execution_attempts"
    __table_args__ = {'extend_existing': True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    job_id: Mapped[str] = mapped_column(String(36), ForeignKey("mt5_execution_jobs.id"), index=True, nullable=False)
    attempt_number: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    order_check_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("mt5_order_checks.id"), nullable=True)
    retcode: Mapped[int] = mapped_column(Integer, nullable=False)
    retcode_name: Mapped[str] = mapped_column(String(64), nullable=False)
    deal_ticket: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    order_ticket: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    response_json: Mapped[str] = mapped_column(Text, nullable=False)
    is_success: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    executed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

class MT5SyncEventModel(Base):
    __tablename__ = "mt5_sync_events"
    __table_args__ = {'extend_existing': True}

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    campaign_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("campaigns.id"), nullable=True)
    sync_type: Mapped[str] = mapped_column(String(32), nullable=False, default="MANUAL")
    orders_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    positions_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    payload_json: Mapped[str] = mapped_column(Text, nullable=False)
    synced_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
