"""campaign lifecycle and duplicates

Revision ID: 002_campaign_lifecycle
Revises: 001_initial_schema
Create Date: 2026-07-23 14:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '002_campaign_lifecycle'
down_revision: Union[str, None] = '001_initial_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Campaign table columns
    with op.batch_alter_table('campaigns', schema=None) as batch_op:
        batch_op.add_column(sa.Column('campaign_code', sa.String(length=64), nullable=True))
        batch_op.add_column(sa.Column('parent_campaign_id', sa.String(length=36), nullable=True))
        batch_op.add_column(sa.Column('reentry_sequence', sa.Integer(), nullable=False, server_default='0'))
        batch_op.add_column(sa.Column('maximum_total_lots', sa.Float(), nullable=False, server_default='2.0'))
        batch_op.add_column(sa.Column('requested_total_lots', sa.Float(), nullable=False, server_default='1.5'))
        batch_op.add_column(sa.Column('current_stop_loss', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('tp1', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('tp2', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('has_tp_open', sa.Boolean(), nullable=False, server_default='0'))
        batch_op.add_column(sa.Column('version', sa.Integer(), nullable=False, server_default='1'))
        batch_op.create_index(batch_op.f('ix_campaigns_campaign_code'), ['campaign_code'], unique=True)
        batch_op.create_index(batch_op.f('ix_campaigns_parent_campaign_id'), ['parent_campaign_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_campaigns_created_at'), ['created_at'], unique=False)
        batch_op.create_foreign_key('fk_campaigns_parent', 'campaigns', ['parent_campaign_id'], ['id'])

    # Duplicate keys table columns
    with op.batch_alter_table('duplicate_keys', schema=None) as batch_op:
        batch_op.add_column(sa.Column('duplicate_type', sa.String(length=32), nullable=False, server_default='EXACT'))
        batch_op.add_column(sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True))
        batch_op.alter_column('message_id', existing_type=sa.String(length=128), nullable=True)

    # Campaign state transitions columns
    with op.batch_alter_table('campaign_state_transitions', schema=None) as batch_op:
        batch_op.add_column(sa.Column('reason_code', sa.String(length=64), nullable=False, server_default='SIGNAL_RECEIVED'))
        batch_op.add_column(sa.Column('trigger_type', sa.String(length=32), nullable=False, server_default='WHATSAPP_MESSAGE'))
        batch_op.add_column(sa.Column('trigger_reference_id', sa.String(length=128), nullable=True))
        batch_op.add_column(sa.Column('correlation_id', sa.String(length=128), nullable=True))

    # Commands table index
    with op.batch_alter_table('commands', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_commands_campaign_id'), ['campaign_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_commands_raw_message_id'), ['raw_message_id'], unique=False)


def downgrade() -> None:
    with op.batch_alter_table('commands', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_commands_raw_message_id'))
        batch_op.drop_index(batch_op.f('ix_commands_campaign_id'))

    with op.batch_alter_table('campaign_state_transitions', schema=None) as batch_op:
        batch_op.drop_column('correlation_id')
        batch_op.drop_column('trigger_reference_id')
        batch_op.drop_column('trigger_type')
        batch_op.drop_column('reason_code')

    with op.batch_alter_table('duplicate_keys', schema=None) as batch_op:
        batch_op.alter_column('message_id', existing_type=sa.String(length=128), nullable=False)
        batch_op.drop_column('expires_at')
        batch_op.drop_column('duplicate_type')

    with op.batch_alter_table('campaigns', schema=None) as batch_op:
        batch_op.drop_constraint('fk_campaigns_parent', type_='foreignkey')
        batch_op.drop_index(batch_op.f('ix_campaigns_created_at'))
        batch_op.drop_index(batch_op.f('ix_campaigns_parent_campaign_id'))
        batch_op.drop_index(batch_op.f('ix_campaigns_campaign_code'))
        batch_op.drop_column('version')
        batch_op.drop_column('has_tp_open')
        batch_op.drop_column('tp2')
        batch_op.drop_column('tp1')
        batch_op.drop_column('current_stop_loss')
        batch_op.drop_column('requested_total_lots')
        batch_op.drop_column('maximum_total_lots')
        batch_op.drop_column('reentry_sequence')
        batch_op.drop_column('parent_campaign_id')
        batch_op.drop_column('campaign_code')
