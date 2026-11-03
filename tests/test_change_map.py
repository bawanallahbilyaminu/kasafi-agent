"""The change map (3 Nov): a list of measures (only those whose data check passes: flood, crops/greenness, drought;
land cover and tree loss stay out, said so), then a list of areas, then one map; an area that needs a place asks for
the location and draws the map when it comes."""

import asyncio
from datetime import date

import pytest

from app.geo.location import Spot, memory
from app.place import change
from app.whatsapp import conversation as C
from app.whatsapp import menu as M
from app.whatsapp.messages import COMING
from tests.test_location_waiting import _facilities, _locate, _user
from tests.test_menu import SENDER, _none, _ok, _row
from tests.test_place_planner import conn  # noqa: F401 - the dev database fixture


def _run(msg, s, store):
    return asyncio.run(C.handle(msg, None, store=store, settings=s, answer_fn=None, guard_fn=_ok, place_fn=_none,
                                locate_fn=_locate, facility_fn=_facilities))


@pytest.fixture
def drawn(monkeypatch):
    calls = []
    monkeypatch.setattr(C, "_change_checks", lambda settings: ["flood", "green", "drought"])

    async def draw(measure, area, place, lang, settings):
        calls.append((measure, area, place))
        return [C.Out(f"MAP {measure} {area}", lang=lang, image=b"jpeg")]
    monkeypatch.setattr(C, "_change_draw", draw)
    return calls


def _has_db(monkeypatch, s):
    monkeypatch.setattr(s.__class__, "has_database", property(lambda self: True))


@pytest.mark.parametrize("lang", ["en", "ha"])
def test_the_measure_list_offers_only_the_three_and_says_why_two_are_out(lang, drawn, monkeypatch) -> None:
    s, store, key = _user(lang)
    _has_db(monkeypatch, s)
    out = _run(_row("menu_change"), s, store)[0]
    rows = [r["id"] for r in out.menu["sections"][0]["rows"]]
    assert rows == ["chg_m_flood", "chg_m_green", "chg_m_drought"]
    assert M.change_words(lang)["not_offered"] in out.text


def test_a_measure_that_fails_its_check_is_not_offered(monkeypatch) -> None:
    s, store, key = _user("en")
    _has_db(monkeypatch, s)
    monkeypatch.setattr(C, "_change_checks", lambda settings: ["flood"])
    out = _run(_row("menu_change"), s, store)[0]
    assert [r["id"] for r in out.menu["sections"][0]["rows"]] == ["chg_m_flood"]
    monkeypatch.setattr(C, "_change_checks", lambda settings: [])
    assert _run(_row("menu_change"), s, store)[0].text == M.change_words("en")["none"]


@pytest.mark.parametrize("lang", ["en", "ha"])
@pytest.mark.parametrize("measure", change.MEASURES)
def test_every_list_is_within_whatsapps_limits(lang, measure) -> None:
    for p in (M.change_measures(lang, list(change.MEASURES)), M.change_areas(lang, measure, list(change.OFFER[measure]))):
        rows = p["sections"][0]["rows"]
        assert len(rows) <= 10 and len(p["button"]) <= M.BUTTON and len(p["body"]) <= 1024
        assert all(len(r["title"]) <= M.ROW_TITLE and len(r["description"]) <= M.ROW_DESC for r in rows)


def test_the_areas_follow_the_measure_and_the_place_on_file() -> None:
    assert change.areas_for("drought", {}) == ["lga", "state"]
    assert change.areas_for("green", {}) == ["ward", "lga", "state"]
    assert change.areas_for("flood", {"lat": 13.0, "lon": 5.2, "lga_pcode": "NG034021"}) == ["spot", "5km", "lga", "state"]
    assert change.areas_for("flood", {"lat": 13.0, "lon": 5.2, "lga_pcode": "NG034021", "wardcode": "62102"}) == \
        list(change.AREAS)


def test_the_state_map_needs_no_location(drawn) -> None:
    s, store, key = _user("en")
    outs = _run(_row("chg_a_drought_state"), s, store)
    assert outs[0].image and drawn == [("drought", "state", {})]


@pytest.mark.parametrize("lang", ["en", "ha"])
def test_an_area_that_needs_a_place_asks_then_the_pin_draws_the_map_without_asking_anything(lang, drawn) -> None:
    s, store, key = _user(lang)
    out = _run(_row("chg_a_flood_spot"), s, store)[0]
    assert out.location_request and out.text == M.change_words(lang)["need_place"]
    assert memory.peek_question(key) == f"{C.CHANGE_WAIT}flood:spot"
    pin = {"from": SENDER, "id": f"w-chg-pin-{lang}", "type": "location", "location": {"latitude": 13.045, "longitude": 5.155}}
    outs = _run(pin, s, store)
    ack = next(o.text for o in outs if o.text.startswith("📍"))
    assert COMING[lang]["map"] in ack and "What would you like" not in ack and "Me kuke so" not in ack
    assert outs[-1].image and drawn[-1][:2] == ("flood", "spot") and drawn[-1][2]["lat"] is not None


def test_with_a_recent_pin_the_map_comes_at_once(drawn) -> None:
    s, store, key = _user("en")
    memory.remember(key, Spot(13.045, 5.155, "NG034021", "Wamakko", ward="Bado", how="pin", wardcode="62102"))
    outs = _run(_row("chg_a_green_ward"), s, store)
    assert outs[0].image and drawn[-1][2]["wardcode"] == "62102"


def test_an_unknown_row_id_goes_back_to_the_measures(drawn, monkeypatch) -> None:
    s, store, key = _user("en")
    _has_db(monkeypatch, s)
    out = _run(_row("chg_a_trees_state"), s, store)[0]
    assert out.menu and [r["id"] for r in out.menu["sections"][0]["rows"]][0] == "chg_m_flood"


# --- the maps, against the dev database (skipped without it) -----------------------------------------------------

def test_the_change_rows_and_maps(conn) -> None:
    if not conn.execute("SELECT 1 FROM ward_history WHERE measure = 'gfm_seasons_flooded' LIMIT 1").fetchone():
        pytest.skip("no change rows (scripts/precompute_area.py --layers change)")
    from app.maps.render import draw
    assert change.checks(conn) == {"flood": True, "green": True, "drought": True}
    seasons = dict(conn.execute("SELECT unit, value FROM ward_history WHERE measure = 'gfm_seasons_flooded' AND "
                                "level = 'lga'").fetchall())
    assert len(seasons) == 23 and len(set(seasons.values())) > 3          # the 0.1 % rule spreads the LGAs out
    for measure, area in (("flood", "state"), ("green", "lga"), ("drought", "state")):
        img = draw(conn, change.spec_for(conn, measure, area, {"lga_pcode": "NG034021"}), "en", date(2026, 11, 3))
        assert img is not None and img.jpeg[:2] == b"\xff\xd8"
    green = draw(conn, change.spec_for(conn, "green", "state", {}), "en")
    assert "brown = less green than usual, green = greener" in green.caption and "darkest" not in green.caption


def test_the_draw_step_itself_runs(monkeypatch) -> None:
    """3 Nov smoke: _change_draw failed with a NameError the mocked tests above couldn't see."""
    from types import SimpleNamespace
    s, store, key = _user("en")
    seen = []

    class Conn:
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False
    monkeypatch.setattr("psycopg.connect", lambda *a, **k: Conn())
    monkeypatch.setattr(change, "spec_for", lambda conn, m, a, p: {"kind": "area_map", "m": m, "a": a})

    def render(settings, specs, lang, today):
        seen.append((specs, today))
        return [SimpleNamespace(caption="CAPTION", jpeg=b"jpeg")]
    monkeypatch.setattr(C, "render_specs", render)
    outs = asyncio.run(C._change_draw("drought", "state", {}, "en", s))
    assert outs[0].image == b"jpeg" and outs[0].text == "CAPTION" and seen[0][0][0]["a"] == "state"
