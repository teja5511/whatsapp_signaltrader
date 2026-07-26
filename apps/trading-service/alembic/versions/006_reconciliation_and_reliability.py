"""reconciliation and reliability

Revision ID: 006_reconciliation
Revises: 005_orchestration
Create Date: 2026-07-26 08:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '006_reconciliation'
down_revision = '005_orchestration'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # 1. Reconciliation Runs
    op.create_table(
        'reconciliation_runs',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('reconciliation_version', sa.String(length=16), nullable=False, server_default='1.0.0'),
        sa.Column('trigger_type', sa.String(length=32), nullable=False, server_default='MANUAL'),
        sa.Column('scope', sa.String(length=32), nullable=False, server_default='ALL'),
        sa.Column('campaign_id', sa.String(length=36), nullable=True),
        sa.Column('correlation_id', sa.String(length=64), nullable=False),
        sa.Column('actor', sa.String(length=32), nullable=False, server_default='SYSTEM'),
        sa.Column('status', sa.String(length=32), nullable=False, server_default='RUNNING'),
        sa.Column('broker_symbol', sa.String(length=32), nullable=True),
        sa.Column('local_order_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('local_position_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('broker_order_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('broker_position_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('matched_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('mismatch_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('requires_review_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('snapshot_json', sa.Text(), nullable=False, server_default='{}'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['campaign_id'], ['campaigns.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_recon_run_status', 'reconciliation_runs', ['status'], unique=False)
    op.create_index('idx_recon_run_trigger', 'reconciliation_runs', ['trigger_type'], unique=False)

    # 2. Reconciliation Items
    op.create_table(
        'reconciliation_items',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('reconciliation_run_id', sa.String(length=36), nullable=False),
        sa.Column('entity_type', sa.String(length=16), nullable=False),
        sa.Column('classification', sa.String(length=32), nullable=False),
        sa.Column('ticket', sa.Integer(), nullable=True),
        sa.Column('magic_number', sa.Integer(), nullable=True),
        sa.Column('campaign_id', sa.String(length=36), nullable=True),
        sa.Column('planned_entry_id', sa.String(length=36), nullable=True),
        sa.Column('job_id', sa.String(length=36), nullable=True),
        sa.Column('local_snapshot_json', sa.Text(), nullable=True),
        sa.Column('broker_snapshot_json', sa.Text(), nullable=True),
        sa.Column('differences_json', sa.Text(), nullable=False, server_default='[]'),
        sa.Column('requires_review', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('resolution_status', sa.String(length=32), nullable=False, server_default='OPEN'),
        sa.Column('resolution_action', sa.String(length=64), nullable=True),
        sa.Column('resolved_by', sa.String(length=64), nullable=True),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['reconciliation_run_id'], ['reconciliation_runs.id'], ),
        sa.ForeignKeyConstraint(['campaign_id'], ['campaigns.id'], ),
        sa.ForeignKeyConstraint(['planned_entry_id'], ['planned_entries.id'], ),
        sa.ForeignKeyConstraint(['job_id'], ['mt5_execution_jobs.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_recon_item_run', 'reconciliation_items', ['reconciliation_run_id'], unique=False)
    op.create_index('idx_recon_item_class', 'reconciliation_items', ['classification'], unique=False)
    op.create_index('idx_recon_item_ticket', 'reconciliation_items', ['ticket'], unique=False)

    # 3. Recovery Actions
    op.create_table(
        'recovery_actions',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('recovery_version', sa.String(length=16), nullable=False, server_default='1.0.0'),
        sa.Column('action_kind', sa.String(length=48), nullable=False),
        sa.Column('entity_type', sa.String(length=32), nullable=False),
        sa.Column('entity_id', sa.String(length=64), nullable=False),
        sa.Column('previous_state', sa.String(length=32), nullable=True),
        sa.Column('new_state', sa.String(length=32), nullable=True),
        sa.Column('detail_json', sa.Text(), nullable=False, server_default='{}'),
        sa.Column('correlation_id', sa.String(length=64), nullable=False),
        sa.Column('actor', sa.String(length=32), nullable=False, server_default='SYSTEM'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_recovery_kind', 'recovery_actions', ['action_kind'], unique=False)
    op.create_index('idx_recovery_created', 'recovery_actions', ['created_at'], unique=False)

    # 4. System Locks
    op.create_table(
        'system_locks',
        sa.Column('lock_name', sa.String(length=64), nullable=False),
        sa.Column('owner_id', sa.String(length=64), nullable=False),
        sa.Column('acquired_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('heartbeat_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('metadata_json', sa.Text(), nullable=False, server_default='{}'),
        sa.PrimaryKeyConstraint('lock_name')
    )

    # 5. Health Incidents
    op.create_table(
        'health_incidents',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('incident_kind', sa.String(length=48), nullable=False),
        sa.Column('severity', sa.String(length=16), nullable=False, server_default='WARNING'),
        sa.Column('status', sa.String(length=16), nullable=False, server_default='OPEN'),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('detail_json', sa.Text(), nullable=False, server_default='{}'),
        sa.Column('occurrence_count', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('first_seen_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('last_seen_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('acknowledged_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('acknowledged_by', sa.String(length=64), nullable=True),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_incident_status', 'health_incidents', ['status'], unique=False)
    op.create_index('idx_incident_kind', 'health_incidents', ['incident_kind'], unique=False)

    # 6. Worker Heartbeats
    op.create_table(
        'worker_heartbeats',
        sa.Column('worker_id', sa.String(length=64), nullable=False),
        sa.Column('worker_kind', sa.String(length=32), nullable=False),
        sa.Column('status', sa.String(length=32), nullable=False, server_default='IDLE'),
        sa.Column('detail_json', sa.Text(), nullable=False, server_default='{}'),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('heartbeat_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('worker_id')
    )

def downgrade() -> None:
    op.drop_table('worker_heartbeats')
    op.drop_index('idx_incident_kind', table_name='health_incidents')
    op.drop_index('idx_incident_status', table_name='health_incidents')
    op.drop_table('health_incidents')
    op.drop_table('system_locks')
    op.drop_index('idx_recovery_created', table_name='recovery_actions')
    op.drop_index('idx_recovery_kind', table_name='recovery_actions')
    op.drop_table('recovery_actions')
    op.drop_index('idx_recon_item_ticket', table_name='reconciliation_items')
    op.drop_index('idx_recon_item_class', table_name='reconciliation_items')
    op.drop_index('idx_recon_item_run', table_name='reconciliation_items')
    op.drop_table('reconciliation_items')
    op.drop_index('idx_recon_run_trigger', table_name='reconciliation_runs')
    op.drop_index('idx_recon_run_status', table_name='reconciliation_runs')
    op.drop_table('reconciliation_runs')
