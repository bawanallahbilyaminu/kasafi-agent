"""A facility held back from answers until someone confirms it (data/geo/facility_corrections.yaml `hide: true`).

Revision ID: 0018
Revises: 0017
Create Date: 2026-10-31
"""

from alembic import op

revision = "0018"
down_revision = "0017"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE facility ADD COLUMN hidden BOOLEAN NOT NULL DEFAULT false;")


def downgrade() -> None:
    op.execute("ALTER TABLE facility DROP COLUMN hidden;")
