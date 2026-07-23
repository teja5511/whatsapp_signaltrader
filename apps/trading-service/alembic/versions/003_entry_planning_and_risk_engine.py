"""003 entry planning and risk engine

Revision ID: 003_entry_planning
Revises: 002_campaign_lifecycle
Create Date: 2026-07-23 18:54:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '003_entry_planning'
down_revision: Union[str, None] = '002_campaign_lifecycle'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Add indexes for planning performance
    try:
        op.create_index('ix_planned_entries_campaign_id', 'planned_entries', ['campaign_id'], unique=False)
    except Exception:
        pass

def downgrade() -> None:
    try:
        op.drop_index('ix_planned_entries_campaign_id', table_name='planned_entries')
    except Exception:
        pass
