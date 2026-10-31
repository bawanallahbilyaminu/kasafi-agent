"""plot_outline_cache: the plot outline drawn around a pin (SAM 3.1 on a Sentinel-2 chip, or the 1 ha circle),
per ~100 m cell (docs/place-history.md §4, §7). No user, trace or exact pin is stored: the cell only.

Revision ID: 0020
Revises: 0019
"""

from alembic import op

revision = "0020"
down_revision = "0019"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS plot_outline_cache (
            cell        TEXT PRIMARY KEY,          -- '13.061,5.224': the 0.001 degree cell
            geometry    JSONB NOT NULL,            -- GeoJSON polygon, WGS84
            method      TEXT NOT NULL,             -- sam | circle
            area_ha     REAL NOT NULL,
            scene       TEXT,                      -- the Sentinel-2 scene the chip came from
            note        TEXT,                      -- why the circle was used (no segment, too small, too big, no pin)
            computed_at DATE NOT NULL DEFAULT CURRENT_DATE
        )
        """
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS plot_outline_cache")
