"""add expired booking status

Revision ID: a1b2c3d4e5f6
Revises: dbd0dc11056d
Create Date: 2026-03-24 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "dbd0dc11056d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# The `status` column is VARCHAR(20) with no CHECK constraint, so no DDL change
# is needed to store the new value.  This migration exists to document the
# introduction of the EXPIRED terminal state and to provide a down() path that
# converts any expired rows back to CANCELLED for rollback compatibility.


def upgrade() -> None:
    """No DDL change required — status column is VARCHAR(20) without CHECK constraint."""
    pass


def downgrade() -> None:
    """Revert EXPIRED rows to CANCELLED so the previous code can still run."""
    op.execute(
        "UPDATE bookings SET status = 'cancelled' WHERE status = 'expired'"
    )
