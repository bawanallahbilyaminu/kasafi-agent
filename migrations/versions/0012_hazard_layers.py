"""Hazard layers (docs/hazard-and-services.md section 4): scheduled fetchers write here, answers read from here.

- hazard_point: where values are fetched: each LGA's centroid (a point on its surface), a ~0.1 degree grid inside
  Sokoto (for maps), and the river points (with the GloFAS cell the Flood API actually used).
- hazard_values: one value per layer, point, valid time and variable, with its unit, source, issued_at (the model
  run or report time, when the source gives it) and fetched_at.
- river_history: each river point's daily discharge since 1984 (pulled once), for "higher than X% of days".
- fire_detection: NASA FIRMS VIIRS satellite heat detections in Sokoto (satellite points, not user locations).
- hazard_fetch: one row per fetch attempt, so an answer can say how old its data is, or that it is unavailable.
No table stores a user's location.

Revision ID: 0012
Revises: 0011
Create Date: 2026-10-30
"""

from alembic import op

revision = "0012"
down_revision = "0011"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
    CREATE TABLE hazard_point (
        id          SERIAL PRIMARY KEY,
        kind        TEXT NOT NULL CHECK (kind IN ('lga', 'grid', 'river')),
        name        TEXT NOT NULL,                  -- the LGA, 'grid 13.1 5.2', or the river point's name
        lga_pcode   TEXT REFERENCES lga (pcode),
        geom        geometry(Point, 4326) NOT NULL, -- the point asked for
        cell        geometry(Point, 4326),          -- river points: the GloFAS cell the API used
        UNIQUE (kind, name)
    );
    CREATE INDEX hazard_point_geom ON hazard_point USING gist (geom);

    CREATE TABLE hazard_values (
        layer       TEXT NOT NULL,                  -- forecast | air | flood
        point_id    INT NOT NULL REFERENCES hazard_point (id) ON DELETE CASCADE,
        valid_time  TIMESTAMPTZ NOT NULL,           -- the hour (or day) the value is for
        variable    TEXT NOT NULL,                  -- temperature_2m, pm10, river_discharge ...
        value       REAL,
        unit        TEXT NOT NULL DEFAULT '',
        source      TEXT NOT NULL,
        issued_at   TIMESTAMPTZ,                    -- the forecast run / report time, when the source gives it
        fetched_at  TIMESTAMPTZ NOT NULL,
        PRIMARY KEY (layer, point_id, valid_time, variable)
    );
    CREATE INDEX hazard_values_time ON hazard_values (layer, variable, valid_time);

    CREATE TABLE river_history (
        point_id    INT NOT NULL REFERENCES hazard_point (id) ON DELETE CASCADE,
        day         DATE NOT NULL,
        discharge   REAL NOT NULL,                  -- m3/s, GloFAS reanalysis
        PRIMARY KEY (point_id, day)
    );

    CREATE TABLE fire_detection (
        id          BIGSERIAL PRIMARY KEY,
        geom        geometry(Point, 4326) NOT NULL,
        lga_pcode   TEXT REFERENCES lga (pcode),
        detected_at TIMESTAMPTZ NOT NULL,
        confidence  TEXT,
        frp         REAL,                           -- fire radiative power, MW
        satellite   TEXT,
        source      TEXT NOT NULL,
        fetched_at  TIMESTAMPTZ NOT NULL,
        UNIQUE (geom, detected_at, satellite)
    );
    CREATE INDEX fire_detection_time ON fire_detection (detected_at);

    CREATE TABLE hazard_fetch (
        id          BIGSERIAL PRIMARY KEY,
        layer       TEXT NOT NULL,                  -- forecast | air | flood | flood_history | fires
        started_at  TIMESTAMPTZ NOT NULL,
        ok          BOOLEAN NOT NULL,
        rows        INT NOT NULL DEFAULT 0,
        calls       INT NOT NULL DEFAULT 0,         -- API calls as Open-Meteo counts them (locations, long ranges)
        error       TEXT NOT NULL DEFAULT ''
    );
    CREATE INDEX hazard_fetch_layer ON hazard_fetch (layer, started_at DESC);
    """)


def downgrade() -> None:
    op.execute("DROP TABLE hazard_fetch, fire_detection, river_history, hazard_values, hazard_point;")
