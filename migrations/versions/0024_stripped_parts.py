"""Office documents: the inert embedded parts stripped before conversion (chart workbooks), with the reason.

Revision ID: 0024
Revises: 0023
"""

from alembic import op

revision = "0024"
down_revision = "0023"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE documents ADD COLUMN IF NOT EXISTS stripped_parts JSONB")   # [{part, why}] or NULL


def downgrade() -> None:
    op.execute("ALTER TABLE documents DROP COLUMN IF EXISTS stripped_parts")
