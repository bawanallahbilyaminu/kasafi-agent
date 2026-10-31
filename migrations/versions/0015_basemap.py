"""Our own base map's lines for the maps (docs/hazard-and-services.md section 8): Sokoto's main roads and rivers
from OpenStreetMap (© OpenStreetMap contributors, ODbL), clipped to the state, filled by scripts/import_geo.py.

Revision ID: 0015
Revises: 0014
Create Date: 2026-10-31
"""

from alembic import op

revision = "0015"
down_revision = "0014"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
    CREATE TABLE basemap (
        id      BIGSERIAL PRIMARY KEY,
        kind    TEXT NOT NULL,                       -- trunk | primary | secondary | river
        name    TEXT,
        geom    geometry(MultiLineString, 4326) NOT NULL
    );
    CREATE INDEX basemap_geom ON basemap USING gist (geom);
    """)


def downgrade() -> None:
    op.execute("DROP TABLE basemap")
