"""Initial schema setup for WhatsApp MT5 Trading Bot

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-07-23 14:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        'app_settings',
        sa.Column('key', sa.String(length=64), primary_key=True),
        sa.Column('value', sa.Text(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False)
    )

    op.create_table(
        'whatsapp_messages',
        sa.Column('id', sa.String(length=128), primary_key=True),
        sa.Column('group_id', sa.String(length=128), nullable=False, index=True),
        sa.Column('sender_id', sa.String(length=128), nullable=False),
        sa.Column('is_admin', sa.Boolean(), nullable=False),
        sa.Column('raw_content', sa.Text(), nullable=False),
        sa.Column('content_hash', sa.String(length=64), nullable=False, index=True),
        sa.Column('received_at', sa.DateTime(timezone=True), nullable=False)
    )

    op.create_table(
        'duplicate_keys',
        sa.Column('dedup_key', sa.String(length=128), primary_key=True),
        sa.Column('message_id', sa.String(length=128), sa.ForeignKey('whatsapp_messages.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False)
    )

    op.create_table(
        'parsed_messages',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('raw_message_id', sa.String(length=128), sa.ForeignKey('whatsapp_messages.id'), unique=True, nullable=False),
        sa.Column('message_type', sa.String(length=32), nullable=False),
        sa.Column('parsed_json', sa.Text(), nullable=False),
        sa.Column('parsed_at', sa.DateTime(timezone=True), nullable=False)
    )

    op.create_table(
        'signals',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('parsed_message_id', sa.String(length=36), sa.ForeignKey('parsed_messages.id'), nullable=False),
        sa.Column('symbol', sa.String(length=16), nullable=False),
        sa.Column('direction', sa.String(length=8), nullable=False),
        sa.Column('entry_min', sa.Float(), nullable=False),
        sa.Column('entry_max', sa.Float(), nullable=False),
        sa.Column('stop_loss', sa.Float(), nullable=False),
        sa.Column('tp1', sa.Float(), nullable=True),
        sa.Column('tp2', sa.Float(), nullable=True),
        sa.Column('has_tp_open', sa.Boolean(), nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False)
    )

    op.create_table(
        'campaigns',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('signal_id', sa.String(length=36), sa.ForeignKey('signals.id'), unique=True, nullable=False),
        sa.Column('magic_number', sa.Integer(), unique=True, nullable=False),
        sa.Column('current_state', sa.String(length=32), index=True, nullable=False),
        sa.Column('execution_mode', sa.String(length=16), nullable=False),
        sa.Column('entry_count', sa.Integer(), nullable=False),
        sa.Column('lot_per_entry', sa.Float(), nullable=False),
        sa.Column('total_volume', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False)
    )

    op.create_table(
        'campaign_state_transitions',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('campaign_id', sa.String(length=36), sa.ForeignKey('campaigns.id'), index=True, nullable=False),
        sa.Column('from_state', sa.String(length=32), nullable=False),
        sa.Column('to_state', sa.String(length=32), nullable=False),
        sa.Column('reason', sa.Text(), nullable=False),
        sa.Column('transitioned_at', sa.DateTime(timezone=True), nullable=False)
    )

    op.create_table(
        'planned_entries',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('campaign_id', sa.String(length=36), sa.ForeignKey('campaigns.id'), index=True, nullable=False),
        sa.Column('ladder_index', sa.Integer(), nullable=False),
        sa.Column('price', sa.Float(), nullable=False),
        sa.Column('volume', sa.Float(), nullable=False),
        sa.Column('order_type', sa.String(length=16), nullable=False),
        sa.Column('stop_loss', sa.Float(), nullable=False),
        sa.Column('take_profit', sa.Float(), nullable=True),
        sa.Column('tp_type', sa.String(length=16), nullable=False)
    )

    op.create_table(
        'pending_orders',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('campaign_id', sa.String(length=36), sa.ForeignKey('campaigns.id'), nullable=False),
        sa.Column('planned_entry_id', sa.String(length=36), sa.ForeignKey('planned_entries.id'), nullable=False),
        sa.Column('mt5_ticket', sa.Integer(), unique=True, index=True, nullable=True),
        sa.Column('price', sa.Float(), nullable=False),
        sa.Column('volume', sa.Float(), nullable=False),
        sa.Column('status', sa.String(length=16), nullable=False),
        sa.Column('placed_at', sa.DateTime(timezone=True), nullable=False)
    )

    op.create_table(
        'positions',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('campaign_id', sa.String(length=36), sa.ForeignKey('campaigns.id'), nullable=False),
        sa.Column('pending_order_id', sa.String(length=36), sa.ForeignKey('pending_orders.id'), nullable=False),
        sa.Column('mt5_position_ticket', sa.Integer(), unique=True, index=True, nullable=False),
        sa.Column('entry_price', sa.Float(), nullable=False),
        sa.Column('current_sl', sa.Float(), nullable=False),
        sa.Column('current_tp', sa.Float(), nullable=True),
        sa.Column('volume', sa.Float(), nullable=False),
        sa.Column('profit', sa.Float(), nullable=False, default=0.0),
        sa.Column('is_closed', sa.Boolean(), nullable=False, default=False),
        sa.Column('closed_at', sa.DateTime(timezone=True), nullable=True)
    )

    op.create_table(
        'commands',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('campaign_id', sa.String(length=36), sa.ForeignKey('campaigns.id'), nullable=False),
        sa.Column('raw_message_id', sa.String(length=128), sa.ForeignKey('whatsapp_messages.id'), nullable=False),
        sa.Column('command_type', sa.String(length=32), nullable=False),
        sa.Column('parameters_json', sa.Text(), nullable=False),
        sa.Column('executed_at', sa.DateTime(timezone=True), nullable=False)
    )

    op.create_table(
        'confirmations',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('campaign_id', sa.String(length=36), sa.ForeignKey('campaigns.id'), nullable=False),
        sa.Column('status', sa.String(length=16), nullable=False, default='PENDING'),
        sa.Column('user_action_at', sa.DateTime(timezone=True), nullable=True)
    )

    op.create_table(
        'system_audit_events',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('event_type', sa.String(length=64), index=True, nullable=False),
        sa.Column('payload_json', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False)
    )

    op.create_table(
        'system_errors',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('error_code', sa.String(length=64), index=True, nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('traceback_text', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False)
    )

def downgrade() -> None:
    op.drop_table('system_errors')
    op.drop_table('system_audit_events')
    op.drop_table('confirmations')
    op.drop_table('commands')
    op.drop_table('positions')
    op.drop_table('pending_orders')
    op.drop_table('planned_entries')
    op.drop_table('campaign_state_transitions')
    op.drop_table('campaigns')
    op.drop_table('signals')
    op.drop_table('parsed_messages')
    op.drop_table('duplicate_keys')
    op.drop_table('whatsapp_messages')
    op.drop_table('app_settings')
