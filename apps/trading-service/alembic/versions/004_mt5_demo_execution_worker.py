"""004 mt5 demo execution worker

Revision ID: 004_mt5_execution
Revises: 003_entry_planning
Create Date: 2026-07-23 19:10:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '004_mt5_execution'
down_revision: Union[str, None] = '003_entry_planning'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # 1. mt5_execution_batches
    op.create_table(
        'mt5_execution_batches',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('campaign_id', sa.String(36), sa.ForeignKey('campaigns.id'), nullable=False),
        sa.Column('campaign_version', sa.Integer(), nullable=False),
        sa.Column('planning_fingerprint', sa.String(64), nullable=False),
        sa.Column('status', sa.String(32), nullable=False, server_default='QUEUED'),
        sa.Column('total_jobs', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('completed_jobs', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('failed_jobs', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False)
    )
    op.create_index('ix_mt5_batches_campaign_id', 'mt5_execution_batches', ['campaign_id'])

    # 2. mt5_execution_jobs
    op.create_table(
        'mt5_execution_jobs',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('batch_id', sa.String(36), sa.ForeignKey('mt5_execution_batches.id'), nullable=True),
        sa.Column('campaign_id', sa.String(36), sa.ForeignKey('campaigns.id'), nullable=True),
        sa.Column('planned_entry_id', sa.String(36), sa.ForeignKey('planned_entries.id'), nullable=True),
        sa.Column('operation_type', sa.String(64), nullable=False),
        sa.Column('idempotency_key', sa.String(128), nullable=False, unique=True),
        sa.Column('status', sa.String(32), nullable=False, server_default='QUEUED'),
        sa.Column('priority', sa.Integer(), nullable=False, server_default='10'),
        sa.Column('attempt_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('max_attempts', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('payload_json', sa.Text(), nullable=False),
        sa.Column('result_json', sa.Text(), nullable=True),
        sa.Column('last_error_code', sa.String(64), nullable=True),
        sa.Column('last_error_message', sa.Text(), nullable=True),
        sa.Column('available_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('locked_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('locked_by', sa.String(64), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False)
    )
    op.create_index('ix_mt5_jobs_batch_id', 'mt5_execution_jobs', ['batch_id'])
    op.create_index('ix_mt5_jobs_campaign_id', 'mt5_execution_jobs', ['campaign_id'])
    op.create_index('ix_mt5_jobs_status', 'mt5_execution_jobs', ['status'])
    op.create_index('ix_mt5_jobs_idempotency_key', 'mt5_execution_jobs', ['idempotency_key'], unique=True)

    # 3. mt5_account_snapshots
    op.create_table(
        'mt5_account_snapshots',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('login', sa.Integer(), nullable=False),
        sa.Column('login_masked', sa.String(64), nullable=False),
        sa.Column('server', sa.String(128), nullable=False),
        sa.Column('company', sa.String(128), nullable=False),
        sa.Column('environment_kind', sa.String(32), nullable=False),
        sa.Column('margin_mode', sa.String(32), nullable=False),
        sa.Column('currency', sa.String(16), nullable=False, server_default='USD'),
        sa.Column('leverage', sa.Integer(), nullable=False, server_default='100'),
        sa.Column('balance', sa.Float(), nullable=False),
        sa.Column('equity', sa.Float(), nullable=False),
        sa.Column('margin', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('margin_free', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('trade_allowed', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('trade_expert', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('captured_at', sa.DateTime(timezone=True), nullable=False)
    )

    # 4. mt5_symbol_snapshots
    op.create_table(
        'mt5_symbol_snapshots',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('canonical_symbol', sa.String(16), nullable=False, server_default='XAUUSD'),
        sa.Column('broker_symbol', sa.String(32), nullable=False),
        sa.Column('digits', sa.Integer(), nullable=False, server_default='2'),
        sa.Column('point', sa.Float(), nullable=False, server_default='0.01'),
        sa.Column('tick_size', sa.Float(), nullable=False, server_default='0.01'),
        sa.Column('volume_min', sa.Float(), nullable=False, server_default='0.01'),
        sa.Column('volume_max', sa.Float(), nullable=False, server_default='100.0'),
        sa.Column('volume_step', sa.Float(), nullable=False, server_default='0.01'),
        sa.Column('stops_level_points', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('freeze_level_points', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('trade_mode', sa.String(32), nullable=False, server_default='FULL'),
        sa.Column('contract_size', sa.Float(), nullable=False, server_default='100.0'),
        sa.Column('snapshot_json', sa.Text(), nullable=False),
        sa.Column('captured_at', sa.DateTime(timezone=True), nullable=False)
    )

    # 5. mt5_orders
    op.create_table(
        'mt5_orders',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('campaign_id', sa.String(36), sa.ForeignKey('campaigns.id'), nullable=True),
        sa.Column('planned_entry_id', sa.String(36), sa.ForeignKey('planned_entries.id'), nullable=True),
        sa.Column('ticket', sa.Integer(), nullable=False, unique=True),
        sa.Column('magic_number', sa.Integer(), nullable=False),
        sa.Column('symbol', sa.String(32), nullable=False),
        sa.Column('order_type', sa.String(32), nullable=False),
        sa.Column('volume', sa.Float(), nullable=False),
        sa.Column('price', sa.Float(), nullable=False),
        sa.Column('stop_loss', sa.Float(), nullable=False),
        sa.Column('take_profit', sa.Float(), nullable=True),
        sa.Column('comment', sa.String(128), nullable=False),
        sa.Column('state', sa.String(32), nullable=False, server_default='PLACED'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False)
    )
    op.create_index('ix_mt5_orders_ticket', 'mt5_orders', ['ticket'], unique=True)
    op.create_index('ix_mt5_orders_magic', 'mt5_orders', ['magic_number'])

    # 6. mt5_positions
    op.create_table(
        'mt5_positions',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('campaign_id', sa.String(36), sa.ForeignKey('campaigns.id'), nullable=True),
        sa.Column('planned_entry_id', sa.String(36), sa.ForeignKey('planned_entries.id'), nullable=True),
        sa.Column('ticket', sa.Integer(), nullable=False, unique=True),
        sa.Column('magic_number', sa.Integer(), nullable=False),
        sa.Column('symbol', sa.String(32), nullable=False),
        sa.Column('position_type', sa.String(16), nullable=False),
        sa.Column('volume', sa.Float(), nullable=False),
        sa.Column('price_open', sa.Float(), nullable=False),
        sa.Column('stop_loss', sa.Float(), nullable=False),
        sa.Column('take_profit', sa.Float(), nullable=True),
        sa.Column('profit', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('comment', sa.String(128), nullable=False),
        sa.Column('state', sa.String(32), nullable=False, server_default='OPEN'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False)
    )
    op.create_index('ix_mt5_positions_ticket', 'mt5_positions', ['ticket'], unique=True)
    op.create_index('ix_mt5_positions_magic', 'mt5_positions', ['magic_number'])

    # 7. mt5_order_checks
    op.create_table(
        'mt5_order_checks',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('job_id', sa.String(36), sa.ForeignKey('mt5_execution_jobs.id'), nullable=True),
        sa.Column('request_json', sa.Text(), nullable=False),
        sa.Column('retcode', sa.Integer(), nullable=False),
        sa.Column('retcode_name', sa.String(64), nullable=False),
        sa.Column('is_valid', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('comment', sa.String(256), nullable=False, server_default=''),
        sa.Column('margin', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('margin_free', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('checked_at', sa.DateTime(timezone=True), nullable=False)
    )

    # 8. mt5_execution_attempts
    op.create_table(
        'mt5_execution_attempts',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('job_id', sa.String(36), sa.ForeignKey('mt5_execution_jobs.id'), nullable=False),
        sa.Column('attempt_number', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('order_check_id', sa.String(36), sa.ForeignKey('mt5_order_checks.id'), nullable=True),
        sa.Column('retcode', sa.Integer(), nullable=False),
        sa.Column('retcode_name', sa.String(64), nullable=False),
        sa.Column('deal_ticket', sa.Integer(), nullable=True),
        sa.Column('order_ticket', sa.Integer(), nullable=True),
        sa.Column('response_json', sa.Text(), nullable=False),
        sa.Column('is_success', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('executed_at', sa.DateTime(timezone=True), nullable=False)
    )

    # 9. mt5_sync_events
    op.create_table(
        'mt5_sync_events',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('campaign_id', sa.String(36), sa.ForeignKey('campaigns.id'), nullable=True),
        sa.Column('sync_type', sa.String(32), nullable=False, server_default='MANUAL'),
        sa.Column('orders_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('positions_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('payload_json', sa.Text(), nullable=False),
        sa.Column('synced_at', sa.DateTime(timezone=True), nullable=False)
    )

def downgrade() -> None:
    op.drop_table('mt5_sync_events')
    op.drop_table('mt5_execution_attempts')
    op.drop_table('mt5_order_checks')
    op.drop_table('mt5_positions')
    op.drop_table('mt5_orders')
    op.drop_table('mt5_symbol_snapshots')
    op.drop_table('mt5_account_snapshots')
    op.drop_table('mt5_execution_jobs')
    op.drop_table('mt5_execution_batches')
