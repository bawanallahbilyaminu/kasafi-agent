"""Each LGA's highest US AQI per day (hazard step 6): hazard_values keeps only 3 days, and the dust alert's "high for
the time of year" compares today with the last 30 days. Filled by app/alerts/triggers.py; 120 days are kept.

Revision ID: 0016
Revises: 0015
Create Date: 2026-10-31
"""

from alembic import op

revision = "0016"
down_revision = "0015"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
    CREATE TABLE air_daily (
        lga_pcode  TEXT NOT NULL,
        day        DATE NOT NULL,                    -- Lagos day
        aqi_max    REAL NOT NULL,                    -- the higher of US AQI for PM10 and PM2.5, the day's maximum
        PRIMARY KEY (lga_pcode, day)
    );
    """)


def downgrade() -> None:
    op.execute("DROP TABLE air_daily;")
