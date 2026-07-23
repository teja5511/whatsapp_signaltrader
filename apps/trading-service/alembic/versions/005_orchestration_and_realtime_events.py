"""orchestration and realtime events

Revision ID: 005_orchestration
Revises: 004_mt5_execution
Create Date: 2026-07-23 19:50:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '005_orchestration'
down_revision = '004_mt5_execution'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # 1. Orchestration Runs
    op.create_table(
        'orchestration_runs',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('orchestrator_version', sa.String(length=32), nullable=False, server_default='1.0.0'),
        sa.Column('source_type', sa.String(length=32), nullable=False),
        sa.Column('source_id', sa.String(length=128), nullable=False),
        sa.Column('correlation_id', sa.String(length=64), nullable=False),
        sa.Column('causation_id', sa.String(length=64), nullable=True),
        sa.Column('campaign_id', sa.String(length=36), nullable=True),
        sa.Column('command_id', sa.String(length=36), nullable=True),
        sa.Column('status', sa.String(length=32), nullable=False, server_default='RECEIVED'),
        sa.Column('current_step', sa.String(length=64), nullable=False, server_default='START'),
        sa.Column('input_payload_json', sa.Text(), nullable=False),
        sa.Column('output_payload_json', sa.Text(), nullable=True),
        sa.Column('error_code', sa.String(length=64), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['campaign_id'], ['campaigns.id'], ),
        sa.ForeignKeyConstraint(['command_id'], ['commands.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('source_type', 'source_id', 'orchestrator_version', name='uq_orch_run_source_ver')
    )
    op.create_index('idx_orch_run_source', 'orchestration_runs', ['source_type', 'source_id'])
    op.create_index('idx_orch_run_correlation', 'orchestration_runs', ['correlation_id'])
    op.create_index('idx_orch_run_campaign', 'orchestration_runs', ['campaign_id'])
    op.create_index('idx_orch_run_status', 'orchestration_runs', ['status'])

    # 2. Orchestration Steps
    op.create_table(
        'orchestration_steps',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('orchestration_run_id', sa.String(length=36), nullable=False),
        sa.Column('sequence', sa.Integer(), nullable=False),
        sa.Column('step_name', sa.String(length=64), nullable=False),
        sa.Column('status', sa.String(length=32), nullable=False, server_default='PENDING'),
        sa.Column('input_json', sa.Text(), nullable=True),
        sa.Column('output_json', sa.Text(), nullable=True),
        sa.Column('error_code', sa.String(length=64), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['orchestration_run_id'], ['orchestration_runs.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_orch_step_run_seq', 'orchestration_steps', ['orchestration_run_id', 'sequence'])

    # 3. Domain Events
    op.create_table(
        'domain_events',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('sequence', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('event_id', sa.String(length=64), nullable=False),
        sa.Column('event_type', sa.String(length=64), nullable=False),
        sa.Column('event_version', sa.String(length=16), nullable=False, server_default='1.0'),
        sa.Column('aggregate_type', sa.String(length=32), nullable=False),
        sa.Column('aggregate_id', sa.String(length=64), nullable=False),
        sa.Column('campaign_id', sa.String(length=36), nullable=True),
        sa.Column('correlation_id', sa.String(length=64), nullable=False),
        sa.Column('causation_id', sa.String(length=64), nullable=True),
        sa.Column('actor_type', sa.String(length=32), nullable=False, server_default='SYSTEM'),
        sa.Column('actor_id', sa.String(length=64), nullable=True),
        sa.Column('payload_json', sa.Text(), nullable=False),
        sa.Column('occurred_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['campaign_id'], ['campaigns.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('event_id'),
        sa.UniqueConstraint('sequence')
    )
    op.create_index('idx_domain_event_seq', 'domain_events', ['sequence'])
    op.create_index('idx_domain_event_type', 'domain_events', ['event_type'])
    op.create_index('idx_domain_event_campaign', 'domain_events', ['campaign_id'])
    op.create_index('idx_domain_event_correlation', 'domain_events', ['correlation_id'])

    # 4. Event Outbox
    op.create_table(
        'event_outbox',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('event_id', sa.String(length=64), nullable=False),
        sa.Column('status', sa.String(length=32), nullable=False, server_default='PENDING'),
        sa.Column('attempt_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('max_attempts', sa.Integer(), nullable=False, server_default='5'),
        sa.Column('last_error', sa.Text(), nullable=True),
        sa.Column('available_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('published_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['event_id'], ['domain_events.event_id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('event_id')
    )
    op.create_index('idx_outbox_status_avail', 'event_outbox', ['status', 'available_at'])

    # 5. Ambiguous Command Confirmations
    op.create_table(
        'ambiguous_command_confirmations',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('command_id', sa.String(length=36), nullable=False),
        sa.Column('campaign_id', sa.String(length=36), nullable=True),
        sa.Column('suggested_action', sa.String(length=64), nullable=False),
        sa.Column('original_text', sa.Text(), nullable=False),
        sa.Column('match_type', sa.String(length=32), nullable=False),
        sa.Column('candidate_count', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('status', sa.String(length=32), nullable=False, server_default='PENDING'),
        sa.Column('resolution_action', sa.String(length=64), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['campaign_id'], ['campaigns.id'], ),
        sa.ForeignKeyConstraint(['command_id'], ['commands.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # 6. Control State Table
    op.create_table(
        'control_states',
        sa.Column('id', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('automation_state', sa.String(length=32), nullable=False, server_default='PAUSED'),
        sa.Column('default_execution_mode', sa.String(length=32), nullable=False, server_default='CONFIRMATION'),
        sa.Column('trading_enabled', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('mt5_execution_enabled', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('orchestrator_enabled', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('event_dispatcher_enabled', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade() -> None:
    op.drop_table('control_states')
    op.drop_table('ambiguous_command_confirmations')
    op.drop_table('event_outbox')
    op.drop_table('domain_events')
    op.drop_table('orchestration_steps')
    op.drop_table('orchestration_runs')
