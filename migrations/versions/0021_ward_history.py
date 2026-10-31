"""ward_history: precomputed place-history measures per GRID3 ward, per LGA and for the state
(docs/place-history.md §7, §8): masked to cropland, one row per unit, measure and year.

Revision ID: 0021
Revises: 0020
"""

from alembic import op

revision = "0021"
down_revision = "0020"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS ward_history (
            unit        TEXT NOT NULL,            -- GRID3 wardcode, LGA pcode, or 'NG034' for the state
            level       TEXT NOT NULL,            -- ward | lga | state
            measure     TEXT NOT NULL,            -- modis_peak | jrc_recurrence_share | s1_flood_share | ...
            year        INTEGER NOT NULL,         -- 0 for a measure without a year
            value       DOUBLE PRECISION,
            n_obs       INTEGER,                  -- composites, passes, scenes or cells behind the value
            source      TEXT NOT NULL,
            computed_at DATE NOT NULL DEFAULT CURRENT_DATE,
            PRIMARY KEY (unit, level, measure, year)
        )
        """
    )
    op.execute("CREATE INDEX IF NOT EXISTS ward_history_measure ON ward_history (measure, year, level)")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS ward_history")
