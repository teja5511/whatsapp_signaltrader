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
