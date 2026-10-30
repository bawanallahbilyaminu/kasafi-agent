"""Geo foundation (docs/hazard-and-services.md section 2): PostGIS, LGAs, wards, a place gazetteer, health facilities.

- lga: OCHA COD-AB boundaries; the P-code (NG034001 ...) is the LGA's identity and the join key for DTM / HDX data.
  The crosswalk lives on the row: GRID3's code and name, the facility file's name, and every other spelling.
- ward: GRID3 operational wards (INEC, 2019), for wording only; lga_pcode from the crosswalk.
- place: the gazetteer (LGA and ward names, GRID3 settlements, OSM places) that turns a typed place into a point.
- facility: GRID3 + NHFR 2024 health facilities in Sokoto, with the LGA and ward the point falls in.
- facility_capability: EmONC capability from the UNFPA assessment, only on confident name matches, each one listed
  for a person to confirm.
No table stores a user's coordinates.

Revision ID: 0011
Revises: 0010
Create Date: 2026-10-30
"""

from alembic import op

revision = "0011"
down_revision = "0010"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis;")
    op.execute("""
    CREATE TABLE lga (
        pcode           TEXT PRIMARY KEY,                -- COD-AB admin2Pcod, NG034001 ...
        name            TEXT NOT NULL,                   -- COD-AB admin2Name
        grid3_code      TEXT,                            -- GRID3 lgacode (601 ...)
        grid3_name      TEXT,
        facility_name   TEXT,                            -- the facility file's lga spelling
        aliases         TEXT[] NOT NULL DEFAULT '{}',    -- every other spelling (budgets, DTM, typed): Wamako ...
        geom            geometry(MultiPolygon, 4326) NOT NULL,
        source          TEXT NOT NULL,
        valid_on        DATE,
        imported_at     TIMESTAMPTZ NOT NULL DEFAULT now()
    );
    CREATE INDEX lga_geom ON lga USING gist (geom);

    CREATE TABLE ward (
        wardcode        TEXT PRIMARY KEY,                -- GRID3 wardcode
        name            TEXT NOT NULL,
        grid3_lga_code  TEXT NOT NULL,
        grid3_lga_name  TEXT NOT NULL,
        lga_pcode       TEXT REFERENCES lga (pcode),     -- by the crosswalk
        urban           BOOLEAN,
        geom            geometry(MultiPolygon, 4326) NOT NULL,
        source          TEXT NOT NULL,
        imported_at     TIMESTAMPTZ NOT NULL DEFAULT now()
    );
    CREATE INDEX ward_geom ON ward USING gist (geom);

    CREATE TABLE place (
        id              SERIAL PRIMARY KEY,
        name            TEXT NOT NULL,
        name_key        TEXT NOT NULL,                   -- lower-cased, no punctuation: the lookup key
        kind            TEXT NOT NULL,                   -- lga | ward | settlement | town | village | landmark
        lga_pcode       TEXT REFERENCES lga (pcode),
        geom            geometry(Point, 4326) NOT NULL,
        source          TEXT NOT NULL
    );
    CREATE INDEX place_key ON place (name_key);
    CREATE INDEX place_geom ON place USING gist (geom);

    CREATE TABLE facility (
        nhfr_uid        BIGINT PRIMARY KEY,
        nhfr_code       TEXT,
        name            TEXT NOT NULL,
        lga_attr        TEXT,                            -- the file's own lga / ward
        ward_attr       TEXT,
        lga_flag        INT,                             -- the file's lga_name_disagreement / ward_name_disagreement
        ward_flag       INT,
        ownership       TEXT,
        ownership_type  TEXT,
        level           TEXT,                            -- Primary / Secondary / Tertiary
        level_option    TEXT,
        geom            geometry(Point, 4326),
        coord_source    TEXT,                            -- NHFR_2024 / GRID3_EHEALTH
        last_updated    DATE,
        lga_pcode       TEXT REFERENCES lga (pcode),     -- from the point (COD-AB decides)
        ward_code       TEXT REFERENCES ward (wardcode), -- from the point, when its LGA agrees
        source          TEXT NOT NULL,
        imported_at     TIMESTAMPTZ NOT NULL DEFAULT now()
    );
    CREATE INDEX facility_geom ON facility USING gist (geom);

    CREATE TABLE facility_capability (
        nhfr_uid        BIGINT NOT NULL REFERENCES facility (nhfr_uid) ON DELETE CASCADE,
        capability      TEXT NOT NULL,                   -- bemonc | cemonc
        doc_id          TEXT NOT NULL,
        page            INT,
        matched_name    TEXT NOT NULL,                   -- the name as the report prints it
        score           REAL NOT NULL,
        confirmed       BOOLEAN NOT NULL DEFAULT false,  -- a person confirmed the match
        PRIMARY KEY (nhfr_uid, capability)
    );
    """)


def downgrade() -> None:
    op.execute("DROP TABLE facility_capability, facility, place, ward, lga;")
