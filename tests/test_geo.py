"""The geo foundation: the LGA crosswalk against the source files, and PostGIS point -> LGA / ward and the
gazetteer on the imported data (skipped without data/geo/ or the database)."""

import json
from pathlib import Path

import pytest

from app.sources.lga_names import CANONICAL, GRID3_CODES, PCODES, canonical, name_of, pcode

GEO = Path(__file__).resolve().parents[1] / "data" / "geo"


def test_every_spelling_of_an_lga_has_one_pcode() -> None:
    assert len(PCODES) == len(GRID3_CODES) == len(CANONICAL) == 23
    for spelling in ("Wamako", "WAMAKKO", "Wamakko LGA", "NG034021"):
        assert pcode(spelling) == "NG034021"
    assert pcode("Dange-Shuni") == pcode("Dange Shuni") == "NG034003" and name_of("NG034003") == "Dange Shuni"
    assert pcode("Kano") == ""


def _features(name: str) -> list[dict]:
    p = GEO / name
    if not p.exists():
        pytest.skip(f"data/geo/{name} not present (not in git)")
    return json.loads(p.read_text(encoding="utf-8"))["features"]


def test_the_crosswalk_matches_the_cod_ab_grid3_and_facility_files() -> None:
    for f in _features("sokoto_lga_codab.geojson"):
        p = f["properties"]
        assert PCODES[canonical(p["admin2Name"])] == p["admin2Pcod"], p["admin2Name"]
    for w in _features("sokoto_wards_grid3.geojson"):
        p = w["properties"]
        assert GRID3_CODES[canonical(p["lganame"])] == p["lgacode"], p["lganame"]


def test_an_emonc_name_matches_only_on_its_own_place_words() -> None:
    import importlib.util
    spec = importlib.util.spec_from_file_location("match_emonc", Path(__file__).resolve().parents[1] / "scripts" /
                                                  "match_emonc.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    assert m.score("Binji Gh", "Binji General Hospital") == 1.0                     # the report's abbreviation
    assert m.score("Margai Health Clinic", "Rara Health Clinic") < m.BAR - 0.2     # 'Health Clinic' alone: no match
    assert m.score("Specialist Hospital", "Shiyar Marina Specialist Hospital") == 0.0   # no place word to match on
    assert m.BAR <= m.score("Maikulki Health Clinic", "Maikulki Health Post") < 1.0     # a kind apart: shown in score


def _conn():
    psycopg = pytest.importorskip("psycopg")
    from app.config import get_settings
    try:
        c = psycopg.connect(get_settings().db_url(), connect_timeout=3)
    except Exception:
        pytest.skip("no database")
    if not c.execute("SELECT to_regclass('lga') IS NOT NULL AND EXISTS (SELECT 1 FROM lga)").fetchone()[0]:
        c.close()
        pytest.skip("geo tables not imported (scripts/import_geo.py)")
    return c


def test_a_pin_inside_each_lga_gives_that_lga_and_outside_sokoto_none() -> None:
    from app.geo import locate
    with _conn() as c:
        pins = c.execute("SELECT pcode, ST_Y(ST_PointOnSurface(geom)), ST_X(ST_PointOnSurface(geom)) FROM lga").fetchall()
        assert len(pins) == 23
        for code, lat, lon in pins:
            assert locate(c, lat, lon).lga_pcode == code
        for lat, lon in ((12.0, 8.5), (13.0, 2.5), (11.5, 4.2), (0.0, 0.0)):      # Kano, Niger Republic, Kebbi, 0/0
            assert locate(c, lat, lon) is None
        # near a border: 200 m inside Sokoto North from its nearest border point, and 200 m beyond it
        bx, by, cx, cy = c.execute(
            "SELECT ST_X(b), ST_Y(b), ST_X(ce), ST_Y(ce) FROM (SELECT ST_ClosestPoint(ST_Boundary(geom), "
            "ST_PointOnSurface(geom)) b, ST_PointOnSurface(geom) ce FROM lga WHERE pcode = 'NG034016') x").fetchone()
        d = ((cx - bx) ** 2 + (cy - by) ** 2) ** 0.5
        step = 0.0018 / d                                        # ~200 m along the line to the inside point
        inside = locate(c, by + (cy - by) * step, bx + (cx - bx) * step)
        beyond = locate(c, by - (cy - by) * step, bx - (cx - bx) * step)
        assert inside.lga_pcode == "NG034016" and (beyond is None or beyond.lga_pcode != "NG034016")


def test_a_typed_place_is_found_in_the_gazetteer() -> None:
    from app.geo import geocode
    with _conn() as c:
        assert geocode(c, "Akwai ambaliya a Goronyo?")[0].lga_pcode == "NG034006"
        assert geocode(c, "zafin rana a Wamako yau")[0].lga == "Wamakko"
        assert geocode(c, "how hot is it in Lagos") == []
        from app.geo.location import area_from_text
        area, spot = area_from_text(c, "Akwai ambaliya a Goronyo?")
        assert area.lga_pcode == "NG034006" and spot.how == "place"
        assert area_from_text(c, "how hot is it here today?", "NG034021")[0].lga == "Wamakko"   # the LGA on file
        assert area_from_text(c, "how hot is it here today?") is None


def test_a_point_near_a_ward_border_says_likely_and_one_inside_does_not() -> None:
    from app.geo import WARD_EDGE_M, locate
    conn = _conn()
    with conn:
        # the middle of a large Wamakko ward, and a point about 60 m inside its border
        far = conn.execute(
            "SELECT ST_Y(c.center), ST_X(c.center), w.name FROM ward w, ST_MaximumInscribedCircle(w.geom) c "
            "WHERE w.lga_pcode = 'NG034021' AND c.radius > 0.01 ORDER BY c.radius DESC LIMIT 1").fetchone()
        near = conn.execute(
            "WITH w AS (SELECT geom, name FROM ward WHERE name = %s AND lga_pcode = 'NG034021'), "
            "e AS (SELECT ST_ClosestPoint(ST_Boundary(w.geom), c.center) AS p, c.center AS m FROM w, "
            "ST_MaximumInscribedCircle(w.geom) c) "
            "SELECT ST_Y(q), ST_X(q) FROM e, ST_Translate(e.p, (ST_X(e.m) - ST_X(e.p)) / "
            "(ST_Distance(e.p, e.m) / 0.00055), (ST_Y(e.m) - ST_Y(e.p)) / (ST_Distance(e.p, e.m) / 0.00055)) q",
            (far[2],)).fetchone()
        inside, edge = locate(conn, far[0], far[1]), locate(conn, near[0], near[1])
    assert WARD_EDGE_M == 300
    assert inside.ward == far[2] and not inside.ward_likely
    assert edge.ward == far[2] and edge.ward_likely
