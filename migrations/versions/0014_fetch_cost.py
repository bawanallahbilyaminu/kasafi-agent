"""What each scheduled fetch cost in model calls (the advisories crawl's monthly cap reads it).

Revision ID: 0014
Revises: 0013
Create Date: 2026-10-31
"""

from alembic import op

revision = "0014"
down_revision = "0013"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE hazard_fetch ADD COLUMN usd NUMERIC(10, 4) NOT NULL DEFAULT 0")


def downgrade() -> None:
    op.execute("ALTER TABLE hazard_fetch DROP COLUMN usd")
