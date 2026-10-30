"""Nearest health facilities (app/geo/facilities.py): the search against a brute-force distance check, filters, the
LGA wording, routes with and without ORS, and what a message asks."""

import asyncio

import httpx
import psycopg
import pytest
from pydantic import SecretStr

from app.config import get_settings
from app.geo import facilities as fac
from app.geo.facilities import Facility, Filters


def _conn():
    s = get_settings()
    if not s.has_database:
        pytest.skip("no database")
    try:
        conn = psycopg.connect(s.db_url(), connect_timeout=3)
    except psycopg.OperationalError:
        pytest.skip("database not running")
    if not conn.execute("SELECT to_regclass('facility')").fetchone()[0] or \
            not conn.execute("SELECT count(*) FROM facility").fetchone()[0]:
        pytest.skip("facility table empty")
    return conn


def brute_force(conn, lat, lon, k=3, where="TRUE"):
    rows = conn.execute(f"SELECT fid, ST_Y(geom), ST_X(geom) FROM facility f WHERE geom IS NOT NULL AND {where}"
                        ).fetchall()
    return [fid for _, fid in sorted((fac._sphere_km(lat, lon, y, x), fid) for fid, y, x in rows)[:k]]


def test_the_three_nearest_match_a_brute_force_check_in_every_lga() -> None:
    with _conn() as conn:
        pts = conn.execute("SELECT pcode, ST_Y(ST_PointOnSurface(geom)), ST_X(ST_PointOnSurface(geom)) FROM lga"
                           ).fetchall()
        assert len(pts) == 23
        for pcode, lat, lon in pts:
            got = [f.fid for f in fac.nearest_facilities(conn, lat, lon)]
            assert got == brute_force(conn, lat, lon), pcode
            hosp = fac.nearest_facilities(conn, lat, lon, Filters(levels=("Secondary", "Tertiary")))
            assert [f.fid for f in hosp] == brute_force(conn, lat, lon, where="(level IN ('Secondary', 'Tertiary') "
                                                                               "OR level_option ILIKE '%hospital%')")
            nxt = fac.nearest_facilities(conn, lat, lon, skip=3)
            assert [f.fid for f in nxt] == brute_force(conn, lat, lon, k=6)[3:]


def test_filters_reach_the_query() -> None:
    with _conn() as conn:
        near_goronyo = fac.nearest_facilities(conn, 13.44, 5.67, Filters(levels=("Secondary", "Tertiary")), k=1)
        assert near_goronyo[0].name == "Goronyo General Hospital"          # listed 'Primary', typed a hospital
        gov = fac.nearest_facilities(conn, 13.06, 5.245, Filters(ownership="Public"))
        assert gov and all(f.ownership == "Public" for f in gov)
        em = fac.nearest_facilities(conn, 13.06, 5.245, Filters(emonc="cemonc"))
        assert em and all(f.emonc == "cemonc" for f in em)
        none = fac.nearest_facilities(conn, 13.06, 5.245, Filters(emonc="cemonc", confirmed_only=True))
        confirmed = conn.execute("SELECT count(*) FROM facility_capability WHERE confirmed AND capability = 'cemonc'"
                                 ).fetchone()[0]
        assert (len(none) > 0) == (confirmed > 0)          # the fast path uses only confirmed links


def _f(name="Kware General Hospital", lga="Kware", attr="Kware", km=4.2, **kw):
    return Facility("x", name, "Secondary", "General Hospital", "Public", "State Government", 13.2, 5.3, lga, attr,
                    km, **kw)


def test_the_reply_uses_the_points_lga_and_says_when_the_list_differs() -> None:
    a = _f(lga="Sokoto South", attr="Wamakko")
    text = fac.facilities_text("en", [a, _f(emonc="cemonc")], Filters(), routed=False)
    assert "1. *Kware General Hospital*, secondary (General Hospital), in Sokoto South LGA (the facility list says " \
           "Wamakko): about 4.2 km in a straight line" in text
    assert "(General Hospital, comprehensive EmONC), in Kware LGA" in text
    assert "Road distance may be longer." in text
    assert "Kasafi can't confirm opening hours or services; call ahead if you can." in text
    assert "jerin ya ce Wamakko" in fac.facilities_text("ha", [a], Filters(), routed=False)
    assert not _f(lga="Dange Shuni", attr="Dange-Shuni").lga_differs                 # spellings of one LGA


def test_routes_from_ors_and_the_straight_line_fallback() -> None:
    def handler(request):
        body = request.read().decode()
        assert '"sources": [0]' in body or '"sources":[0]' in body
        assert "13.123" in body and "13.1234567" not in body                          # the point, rounded
        return httpx.Response(200, json={"distances": [[5300.0, 12000.0]], "durations": [[420.0, 3900.0]]})
    s = get_settings().model_copy(update={"ors_api_key": SecretStr("k")})
    found = [_f(), _f(name="B")]

    async def go(http):
        return await fac.add_routes(s, 13.1234567, 5.2, found, http=http)
    assert asyncio.run(go(httpx.AsyncClient(transport=httpx.MockTransport(handler))))
    text = fac.facilities_text("en", found, Filters())
    assert "5.3 km by road, about 7 min" in text and "12 km by road, about 1 h 5 min" in text
    assert "Road distance may be longer" not in text
    down = [_f()]
    fail = httpx.AsyncClient(transport=httpx.MockTransport(lambda r: httpx.Response(503)))
    assert not asyncio.run(fac.add_routes(s, 13.1, 5.2, down, http=fail)) and down[0].road_km is None
    nokey = get_settings().model_copy(update={"ors_api_key": None})
    assert not asyncio.run(fac.add_routes(nokey, 13.1, 5.2, [_f()]))


@pytest.mark.parametrize("q, want", [
    ("Where is the nearest hospital?", True), ("Ina asibiti mafi kusa?", True),
    ("nearest clinic to me", True), ("Ina cibiyar lafiya kusa da ni?", True),
    ("How many hospitals are in Wamakko?", False), ("What is the budget for hospitals near Sokoto?", False),
    ("What is the hospital budget?", False),
])
def test_facility_questions(q, want) -> None:
    assert fac.is_facility_query(q) is want


def test_follow_ups_and_filters() -> None:
    assert fac.follow_up("the next one") == "next" and fac.follow_up("na gaba") == "next"
    assert fac.follow_up("route?") == "route" and fac.follow_up("Yaya zan je?") == "route"
    assert fac.follow_up("only government hospitals") == "filter"
    f = fac.filters_from("only government hospitals")
    assert f.ownership == "Public" and f.levels == ("Secondary", "Tertiary")
    assert fac.filters_from("na gwamnati kawai").ownership == "Public"
    assert fac.filters_from("maternity").emonc == "bemonc"
    assert fac.profile_from("on foot") == "foot" and fac.profile_from("da mota", "foot") == "car"
    assert fac.follow_up("What is the 2026 health budget?") == ""


def test_maps_link_and_location_message() -> None:
    f = _f()
    assert fac.maps_link(f) == "https://www.google.com/maps/dir/?api=1&destination=13.200000,5.300000&travelmode=driving"
    assert "travelmode=walking" in fac.maps_link(f, "foot")
    assert fac.location_payload(f, "en") == {"latitude": 13.2, "longitude": 5.3, "name": "Kware General Hospital",
                                             "address": "Kware LGA, Sokoto State"}
