"""schema drift and shutdown state

Revision ID: 007_schema_drift
Revises: 006_reconciliation
Create Date: 2026-07-26 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '007_schema_drift'
down_revision = '006_reconciliation'
branch_labels = None
depends_on = None

def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = set(inspector.get_table_names())

    # 1. Create missing trading_policies table if not exists
    if 'trading_policies' not in existing_tables:
        op.create_table(
            'trading_policies',
            sa.Column('key', sa.String(length=64), nullable=False),
            sa.Column('selected_option', sa.String(length=64), nullable=True),
            sa.Column('parameters_json', sa.Text(), nullable=True),
            sa.Column('status', sa.String(length=16), nullable=False, server_default='UNRESOLVED'),
            sa.Column('confirmed_by', sa.String(length=64), nullable=True),
            sa.Column('confirmed_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
            sa.PrimaryKeyConstraint('key')
        )

    def get_existing_cols(table_name: str):
        if table_name in existing_tables:
            return {c['name'] for c in inspector.get_columns(table_name)}
        return set()

    # Safely add missing columns if not present
    ctrl_cols = get_existing_cols('control_states')
    if 'shutdown_state' not in ctrl_cols:
        with op.batch_alter_table('control_states') as batch_op:
            batch_op.add_column(sa.Column('shutdown_state', sa.String(length=32), nullable=False, server_default='RUNNING'))

    outbox_cols = get_existing_cols('event_outbox')
    with op.batch_alter_table('event_outbox') as batch_op:
        if 'locked_by' not in outbox_cols:
            batch_op.add_column(sa.Column('locked_by', sa.String(length=64), nullable=True))
        if 'lease_expires_at' not in outbox_cols:
            batch_op.add_column(sa.Column('lease_expires_at', sa.DateTime(timezone=True), nullable=True))

    event_cols = get_existing_cols('domain_events')
    if 'severity' not in event_cols:
        with op.batch_alter_table('domain_events') as batch_op:
            batch_op.add_column(sa.Column('severity', sa.String(length=16), nullable=True, server_default='INFO'))

    job_cols = get_existing_cols('mt5_execution_jobs')
    with op.batch_alter_table('mt5_execution_jobs') as batch_op:
        if 'lease_expires_at' not in job_cols:
            batch_op.add_column(sa.Column('lease_expires_at', sa.DateTime(timezone=True), nullable=True))
        if 'requires_manual_review' not in job_cols:
            batch_op.add_column(sa.Column('requires_manual_review', sa.Boolean(), nullable=False, server_default='0'))

    run_cols = get_existing_cols('orchestration_runs')
    if 'heartbeat_at' not in run_cols:
        with op.batch_alter_table('orchestration_runs') as batch_op:
            batch_op.add_column(sa.Column('heartbeat_at', sa.DateTime(timezone=True), nullable=True))

    entry_cols = get_existing_cols('planned_entries')
    with op.batch_alter_table('planned_entries') as batch_op:
        if 'entry_sequence' not in entry_cols:
            batch_op.add_column(sa.Column('entry_sequence', sa.Integer(), nullable=True, server_default='1'))
        if 'tp_category' not in entry_cols:
            batch_op.add_column(sa.Column('tp_category', sa.String(length=16), nullable=False, server_default='TP1'))
        if 'order_comment' not in entry_cols:
            batch_op.add_column(sa.Column('order_comment', sa.String(length=128), nullable=True))
        if 'magic_number' not in entry_cols:
            batch_op.add_column(sa.Column('magic_number', sa.Integer(), nullable=True, server_default='0'))
        if 'created_at' not in entry_cols:
            batch_op.add_column(sa.Column('created_at', sa.DateTime(timezone=True), nullable=True))

    trans_cols = get_existing_cols('campaign_state_transitions')
    with op.batch_alter_table('campaign_state_transitions') as batch_op:
        if 'reason_description' not in trans_cols:
            batch_op.add_column(sa.Column('reason_description', sa.Text(), nullable=True))
        if 'triggered_by' not in trans_cols:
            batch_op.add_column(sa.Column('triggered_by', sa.String(length=32), nullable=False, server_default='SYSTEM'))
        if 'message_id' not in trans_cols:
            batch_op.add_column(sa.Column('message_id', sa.String(length=128), nullable=True))
        if 'command_id' not in trans_cols:
            batch_op.add_column(sa.Column('command_id', sa.String(length=36), nullable=True))

    cmd_cols = get_existing_cols('commands')
    with op.batch_alter_table('commands') as batch_op:
        if 'parsed_message_id' not in cmd_cols:
            batch_op.add_column(sa.Column('parsed_message_id', sa.String(length=36), nullable=True))
        if 'message_id' not in cmd_cols:
            batch_op.add_column(sa.Column('message_id', sa.String(length=128), nullable=True))
        if 'classification' not in cmd_cols:
            batch_op.add_column(sa.Column('classification', sa.String(length=32), nullable=False, server_default='ACTION'))
        if 'value' not in cmd_cols:
            batch_op.add_column(sa.Column('value', sa.String(length=64), nullable=True))
        if 'value_kind' not in cmd_cols:
            batch_op.add_column(sa.Column('value_kind', sa.String(length=16), nullable=False, server_default='NONE'))
        if 'payload_json' not in cmd_cols:
            batch_op.add_column(sa.Column('payload_json', sa.Text(), nullable=True))
        if 'status' not in cmd_cols:
            batch_op.add_column(sa.Column('status', sa.String(length=32), nullable=False, server_default='PENDING'))
        if 'created_at' not in cmd_cols:
            batch_op.add_column(sa.Column('created_at', sa.DateTime(timezone=True), nullable=True))

    audit_cols = get_existing_cols('system_audit_events')
    if 'actor' not in audit_cols:
        with op.batch_alter_table('system_audit_events') as batch_op:
            batch_op.add_column(sa.Column('actor', sa.String(length=32), nullable=False, server_default='SYSTEM'))

    err_cols = get_existing_cols('system_errors')
    with op.batch_alter_table('system_errors') as batch_op:
        if 'stack_trace' not in err_cols:
            batch_op.add_column(sa.Column('stack_trace', sa.Text(), nullable=True))
        if 'context_data' not in err_cols:
            batch_op.add_column(sa.Column('context_data', sa.Text(), nullable=True))

def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = set(inspector.get_table_names())

    def get_existing_cols(table_name: str):
        if table_name in existing_tables:
            return {c['name'] for c in inspector.get_columns(table_name)}
        return set()

    err_cols = get_existing_cols('system_errors')
    with op.batch_alter_table('system_errors') as batch_op:
        if 'context_data' in err_cols:
            batch_op.drop_column('context_data')
        if 'stack_trace' in err_cols:
            batch_op.drop_column('stack_trace')

    audit_cols = get_existing_cols('system_audit_events')
    if 'actor' in audit_cols:
        with op.batch_alter_table('system_audit_events') as batch_op:
            batch_op.drop_column('actor')

    cmd_cols = get_existing_cols('commands')
    with op.batch_alter_table('commands') as batch_op:
        for c in ['created_at', 'status', 'payload_json', 'value_kind', 'value', 'classification', 'message_id', 'parsed_message_id']:
            if c in cmd_cols:
                batch_op.drop_column(c)

    trans_cols = get_existing_cols('campaign_state_transitions')
    with op.batch_alter_table('campaign_state_transitions') as batch_op:
        for c in ['command_id', 'message_id', 'triggered_by', 'reason_description']:
            if c in trans_cols:
                batch_op.drop_column(c)

    entry_cols = get_existing_cols('planned_entries')
    with op.batch_alter_table('planned_entries') as batch_op:
        for c in ['created_at', 'magic_number', 'order_comment', 'tp_category', 'entry_sequence']:
            if c in entry_cols:
                batch_op.drop_column(c)

    run_cols = get_existing_cols('orchestration_runs')
    if 'heartbeat_at' in run_cols:
        with op.batch_alter_table('orchestration_runs') as batch_op:
            batch_op.drop_column('heartbeat_at')

    job_cols = get_existing_cols('mt5_execution_jobs')
    with op.batch_alter_table('mt5_execution_jobs') as batch_op:
        for c in ['requires_manual_review', 'lease_expires_at']:
            if c in job_cols:
                batch_op.drop_column(c)

    event_cols = get_existing_cols('domain_events')
    if 'severity' in event_cols:
        with op.batch_alter_table('domain_events') as batch_op:
            batch_op.drop_column('severity')

    outbox_cols = get_existing_cols('event_outbox')
    with op.batch_alter_table('event_outbox') as batch_op:
        for c in ['lease_expires_at', 'locked_by']:
            if c in outbox_cols:
                batch_op.drop_column(c)

    ctrl_cols = get_existing_cols('control_states')
    if 'shutdown_state' in ctrl_cols:
        with op.batch_alter_table('control_states') as batch_op:
            batch_op.drop_column('shutdown_state')

    if 'trading_policies' in existing_tables:
        op.drop_table('trading_policies')
