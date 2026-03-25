"""add_space_business_rules_and_user_max_bookings

Revision ID: dbd0dc11056d
Revises: 74c0950b6977
Create Date: 2026-03-24 15:09:16.674183

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dbd0dc11056d'
down_revision: Union[str, Sequence[str], None] = '74c0950b6977'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add business rule columns to spaces and max_active_bookings to users."""
    op.add_column('spaces', sa.Column('min_duration_minutes', sa.Integer(), nullable=False, server_default='30'))
    op.add_column('spaces', sa.Column('max_duration_minutes', sa.Integer(), nullable=False, server_default='480'))
    op.add_column('spaces', sa.Column('min_advance_minutes', sa.Integer(), nullable=False, server_default='60'))
    op.add_column('spaces', sa.Column('cancellation_deadline_hours', sa.Integer(), nullable=False, server_default='24'))
    op.add_column('spaces', sa.Column('opening_time', sa.Time(), nullable=False, server_default='08:00:00'))
    op.add_column('spaces', sa.Column('closing_time', sa.Time(), nullable=False, server_default='20:00:00'))

    op.add_column('users', sa.Column('max_active_bookings', sa.Integer(), nullable=False, server_default='5'))

    # Remove server defaults — constraints are now enforced at the application layer
    op.alter_column('spaces', 'min_duration_minutes', server_default=None)
    op.alter_column('spaces', 'max_duration_minutes', server_default=None)
    op.alter_column('spaces', 'min_advance_minutes', server_default=None)
    op.alter_column('spaces', 'cancellation_deadline_hours', server_default=None)
    op.alter_column('spaces', 'opening_time', server_default=None)
    op.alter_column('spaces', 'closing_time', server_default=None)
    op.alter_column('users', 'max_active_bookings', server_default=None)


def downgrade() -> None:
    """Remove business rule columns from spaces and max_active_bookings from users."""
    op.drop_column('spaces', 'min_duration_minutes')
    op.drop_column('spaces', 'max_duration_minutes')
    op.drop_column('spaces', 'min_advance_minutes')
    op.drop_column('spaces', 'cancellation_deadline_hours')
    op.drop_column('spaces', 'opening_time')
    op.drop_column('spaces', 'closing_time')
    op.drop_column('users', 'max_active_bookings')
