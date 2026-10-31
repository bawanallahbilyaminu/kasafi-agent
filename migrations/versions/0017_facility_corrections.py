"""Verified fixes to the facility registry (data/geo/facility_corrections.yaml, applied by scripts/import_geo.py):
which fields a person corrected, who and when. Answers say when a location came from a correction.

Revision ID: 0017
Revises: 0016
Create Date: 2026-10-31
"""

from alembic import op

revision = "0017"
down_revision = "0016"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE facility ADD COLUMN correction JSONB;   -- {fields, verified_by, verified_on, note}")


def downgrade() -> None:
    op.execute("ALTER TABLE facility DROP COLUMN correction;")
