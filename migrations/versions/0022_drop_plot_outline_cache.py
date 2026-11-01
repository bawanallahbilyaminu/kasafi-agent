"""Drop plot_outline_cache: plot geometry is never persisted (external review, findings 04 and 05). Outlines live
in the process's memory for 30 minutes (app/place/outline.py); the per-cell satellite statistics stay in sat_cache.

Revision ID: 0022
Revises: 0021
"""

from alembic import op

revision = "0022"
down_revision = "0021"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("DROP TABLE IF EXISTS plot_outline_cache")


def downgrade() -> None:
    op.execute("""
        CREATE TABLE IF NOT EXISTS plot_outline_cache (
            cell        TEXT PRIMARY KEY,
            geometry    JSONB NOT NULL,
            method      TEXT NOT NULL,
            area_ha     DOUBLE PRECISION NOT NULL,
            scene       TEXT,
            note        TEXT,
            computed_at DATE NOT NULL
        )
    """)
