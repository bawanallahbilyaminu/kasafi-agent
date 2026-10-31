"""Place history cache: satellite measures per ~100 m grid cell, layer and year (docs/place-history.md §7).

Keyed by the cell (a coordinate rounded to 0.001°, about 100 m), never by a user, with the day it was computed.
No table links a cell to a user or a trace.

Revision ID: 0019
Revises: 0018
Create Date: 2026-10-31
"""

from alembic import op

revision = "0019"
down_revision = "0018"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE sat_cache (
            cell        TEXT NOT NULL,          -- 'lat,lon' rounded to 0.001° (~100 m)
            layer       TEXT NOT NULL,          -- s2 | rain | jrc | jrc_year
            year        INTEGER NOT NULL,       -- 0 for a summary layer
            values      JSONB NOT NULL,
            clear_obs   INTEGER,
            source      TEXT NOT NULL,
            computed_at DATE NOT NULL DEFAULT CURRENT_DATE,
            PRIMARY KEY (cell, layer, year)
        );
    """)


def downgrade() -> None:
    op.execute("DROP TABLE sat_cache;")
