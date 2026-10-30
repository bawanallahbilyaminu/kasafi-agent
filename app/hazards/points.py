"""Where hazard values are fetched: each LGA's centroid (a point on its surface, so inside it), a ~0.1 degree grid
over Sokoto (only the points inside the state, for maps), and the river points.

River points were chosen against the GloFAS v4 grid (0.05 degrees) through the Open-Meteo Flood API, which returns
the largest river within ~5 km and the cell it used: candidates around each place were probed and the cell on the
main channel kept (mean discharge 2020-2024 or 2024). Oct 30 2026.
"""

from __future__ import annotations

import psycopg

GRID_STEP = 0.1
# (name, LGA P-code, the coordinate asked for = the GloFAS cell the API returned for it)
RIVER_POINTS = (
    ("Sokoto River at Sokoto city", "NG034021", 13.075, 5.175),        # above the Rima confluence; mean 36 m3/s
    ("Rima near Goronyo", "NG034006", 13.475, 5.675),                  # mean 79 m3/s, peaks ~2,000
    ("Rima near Wurno", "NG034005", 13.325, 5.425),                    # between Goronyo and Sokoto; mean 80 m3/s
    ("Sokoto-Rima toward the Kebbi border", "NG034015", 13.075, 4.725),  # last main-channel cell in Sokoto; ~287
)


def ensure_points(conn: psycopg.Connection) -> dict[str, int]:
    """Create the points once (idempotent); returns how many of each kind exist."""
    conn.execute("INSERT INTO hazard_point (kind, name, lga_pcode, geom) SELECT 'lga', name, pcode, "
                 "ST_PointOnSurface(geom) FROM lga ON CONFLICT (kind, name) DO NOTHING")
    conn.execute(
        "INSERT INTO hazard_point (kind, name, lga_pcode, geom) "
        "SELECT 'grid', 'grid ' || round(y::numeric, 1) || ' ' || round(x::numeric, 1), l.pcode, "
        "ST_SetSRID(ST_MakePoint(x, y), 4326) FROM (SELECT ST_Extent(geom) e FROM lga) b, "
        "generate_series(floor(ST_XMin(b.e) * 10)::int, ceil(ST_XMax(b.e) * 10)::int) gx(ix), "
        "generate_series(floor(ST_YMin(b.e) * 10)::int, ceil(ST_YMax(b.e) * 10)::int) gy(iy), "
        "LATERAL (SELECT ix / 10.0 AS x, iy / 10.0 AS y) p "
        "JOIN lga l ON ST_Within(ST_SetSRID(ST_MakePoint(p.x, p.y), 4326), l.geom) "
        "ON CONFLICT (kind, name) DO NOTHING")
    for name, pcode, lat, lon in RIVER_POINTS:
        conn.execute("INSERT INTO hazard_point (kind, name, lga_pcode, geom, cell) VALUES ('river', %s, %s, "
                     "ST_SetSRID(ST_MakePoint(%s, %s), 4326), ST_SetSRID(ST_MakePoint(%s, %s), 4326)) "
                     "ON CONFLICT (kind, name) DO NOTHING", (name, pcode, lon, lat, lon, lat))
    return dict(conn.execute("SELECT kind, count(*) FROM hazard_point GROUP BY 1").fetchall())


def points(conn: psycopg.Connection, kinds: tuple[str, ...]) -> list[tuple[int, str, float, float]]:
    """(id, name, lat, lon) of the points of these kinds."""
    return conn.execute("SELECT id, name, ST_Y(geom), ST_X(geom) FROM hazard_point WHERE kind = ANY(%s) ORDER BY id",
                        (list(kinds),)).fetchall()
