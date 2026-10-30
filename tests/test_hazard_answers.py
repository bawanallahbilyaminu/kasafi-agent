"""Hazard answers (docs/hazard-and-services.md sections 4 and 10): which questions route here, which day and place
they mean, the named scales in the reply, and old or missing data said plainly."""

import asyncio
from datetime import date, datetime, timedelta, timezone

from app.agent.answer import Plan, hazard_route
from app.agent.need import Entity, Need
from app.hazards import answer as ha
from app.hazards import read
from app.users import UserStore, user_key
from app.whatsapp.conversation import handle
from tests.helpers import make_settings

TODAY = date(2026, 10, 30)


def plan(q: str, measures=None, entities=None) -> Plan:
    p = Plan(q, [q], [])
    p.english_question = q
    p.need = Need(q, measures=measures or [], entities=entities or [])
    return p


def test_hazard_questions_route_here_and_budget_or_idp_questions_do_not() -> None:
    assert hazard_route("Yaya zafin rana yake a Wamakko yau?", plan("How hot is it in Wamakko today?")) == ["heat"]
    assert hazard_route("Akwai ambaliya kusa da ni?", plan("Is there flooding near me?")) == ["flood"]
    assert hazard_route("Is the harmattan dust bad in Sokoto?", plan("q", ["dust"])) == ["air"]
    assert hazard_route("What should we watch out for this week in Goronyo?", plan("q")) == ["overview"]
    assert hazard_route("What is the budget for flood control?", plan("q", ["approved"])) == []
    assert hazard_route("How many IDPs were displaced by floods?", plan("q", ["idp_count"])) == []


def test_the_day_asked() -> None:
    assert ha.days_asked("how hot today", TODAY) == [TODAY]
    assert ha.days_asked("Za a yi ruwan sama gobe?", TODAY) == [TODAY + timedelta(days=1)]
    assert ha.days_asked("the next 3 days in Wamakko", TODAY) == [TODAY + timedelta(days=i) for i in range(3)]


def test_the_place_an_lga_named_then_here_then_the_state() -> None:
    lga = Entity("lga", "Wamako", "Wamakko")
    assert ha.where_for([lga], None).lga_pcode == "NG034021"
    assert ha.where_for([], {"lat": 13.0, "lon": 5.2, "lga_pcode": "NG034017", "lga": "Sokoto South"}).kind == "point"
    assert ha.where_for([], {"lga_pcode": "NG034006"}).lga == "Goronyo"
    assert ha.where_for([], None).kind == "state"


def _fresh(stale=False, available=True):
    at = datetime(2026, 10, 30, 12, tzinfo=timezone.utc) if available else None
    return lambda conn, layer, now=None: read.Freshness(layer, at, stale, 9.0 if stale else 1.0)


def _patch(monkeypatch, fresh, heat=True):
    monkeypatch.setattr(read, "freshness", fresh)
    monkeypatch.setattr(read, "point_ids", lambda conn, where: [(1, "Wamakko")])
    day = read.HeatDay("Wamakko", TODAY, 41.2, 43.0, 44.6, "danger", 11, 18, 35, 0.0, 0.0, "none", 10,
                       datetime(2026, 10, 30, 12, tzinfo=timezone.utc))
    monkeypatch.setattr(read, "heat_day", lambda conn, pid, lga, d: day if heat else None)


def test_a_heat_answer_names_the_scale_its_category_and_its_source(monkeypatch) -> None:
    _patch(monkeypatch, _fresh())
    a = ha.hazard_answer(None, "How hot is it in Wamakko today?", "en", ["heat"],
                         read.Where("lga", "NG034021", "Wamakko"), TODAY)
    assert "heat index up to 45 °C: *Danger* (US National Weather Service heat index categories, by the heat " \
           "index)" in a.text
    assert "Open-Meteo forecast" in a.text and "not official warnings" in a.text and a.found
    a = ha.hazard_answer(None, "Yaya zafin rana yake?", "ha", ["heat"], read.Where("lga", "NG034021", "Wamakko"),
                         TODAY)
    assert "*Haɗari*" in a.text and "Ƙaramar Hukumar Wamakko" in a.text


def test_old_data_says_how_old_and_missing_data_says_so(monkeypatch) -> None:
    _patch(monkeypatch, _fresh(stale=True))
    a = ha.hazard_answer(None, "how hot today", "en", ["heat"], read.Where("lga", "NG034021", "Wamakko"), TODAY)
    assert "⚠️ This is the latest Weather forecast data, from 9 hours ago" in a.text
    _patch(monkeypatch, _fresh(available=False))
    a = ha.hazard_answer(None, "how hot today", "en", ["heat"], read.Where("state"), TODAY)
    assert "Weather forecast data isn't available now." in a.text and not a.found and "Today: up to" not in a.text
    _patch(monkeypatch, _fresh(), heat=False)                  # fetched, but nothing for the day asked
    a = ha.hazard_answer(None, "how hot tomorrow", "en", ["heat"], read.Where("state"), TODAY)
    assert "no forecast for Tomorrow yet" in a.text and not a.found


def test_dry_heat_takes_its_category_from_the_air_temperature_and_says_so(monkeypatch) -> None:
    _patch(monkeypatch, _fresh())
    dry = read.HeatDay("Wamakko", TODAY, 41.0, 39.0, 38.0, "danger", 9, 15, 30, 0.0, 0.0, "none", 0, None,
                       "air_temperature")
    monkeypatch.setattr(read, "heat_day", lambda conn, pid, lga, d: dry)
    a = ha.hazard_answer(None, "how hot", "en", ["heat"], read.Where("lga", "NG034021", "Wamakko"), TODAY)
    assert "*Danger* (US National Weather Service heat index categories, by the air temperature, which in dry " \
           "air is above the heat index)" in a.text
    a = ha.hazard_answer(None, "how hot", "en", ["heat"], read.Where("state"), TODAY)
    assert "1 LGA is at Danger level or above." in a.text
    calm = read.HeatDay("Wamakko", TODAY, 30.0, 30.0, 29.0, "caution", 9, 15, 30, 0.0, 0.0, "none", 0, None)
    monkeypatch.setattr(read, "heat_day", lambda conn, pid, lga, d: calm)
    assert "No LGA is at Danger level or above." in ha.hazard_answer(None, "how hot", "en", ["heat"],
                                                                     read.Where("state"), TODAY).text


def test_the_aqi_names_its_pollutant_and_each_pm_has_its_own_guideline(monkeypatch) -> None:
    _patch(monkeypatch, _fresh())
    air = read.AirDay("Tureta", TODAY, 179.0, 61.0, 120.0, 0.6, 204.0, "very_unhealthy", None, "PM2.5")
    monkeypatch.setattr(read, "air_day", lambda conn, pid, lga, d: air)
    a = ha.hazard_answer(None, "dust", "en", ["air"], read.Where("lga", "NG034020", "Tureta"), TODAY)
    assert "US AQI up to 204, set by PM2.5: *Very unhealthy*. PM10 averaging 179 µg/m³ (WHO 24-hour guideline: " \
           "45), PM2.5 averaging 61 µg/m³ (WHO 24-hour guideline: 15)" in a.text
    a = ha.hazard_answer(None, "dust", "ha", ["air"], read.Where("state"), TODAY)
    assert "US AQI har zuwa 204, saboda PM2.5" in a.text and "iyakar WHO ta awa 24: 15" in a.text


def test_a_pin_without_grid_data_gets_its_lgas_forecast_said_as_such(monkeypatch) -> None:
    _patch(monkeypatch, _fresh())
    monkeypatch.setattr(read, "point_ids", lambda conn, where: [(7 if where.kind == "point" else 1, "Wamakko")])
    day = read.HeatDay("Wamakko", TODAY, 41.2, 43.0, 44.6, "danger", 11, 18, 35, 0.0, 0.0, "none", 10, None)
    monkeypatch.setattr(read, "heat_day", lambda conn, pid, lga, d: day if pid == 1 else None)   # the grid point: none
    pin = read.Where("point", "NG034021", "Wamakko", 13.08, 5.21)
    a = ha.hazard_answer(None, "how hot here", "en", ["heat"], pin, TODAY)
    assert "Forecast for Wamakko LGA (none for your exact spot yet):\nToday: up to 41 °C" in a.text and a.found
    assert "no forecast for" not in a.text


def test_a_river_is_compared_with_the_same_time_of_year() -> None:
    from datetime import date as d
    history = [(100.0, d(y, 8, 30)) for y in range(1997, 2026)] + [(5.0 + y % 3, d(y, 10, 28)) for y in
                                                                     range(1997, 2026)]
    season = read.same_time_of_year(history, d(2026, 10, 30))
    assert len(season) == 29 and max(season) < 10                # August's floods aren't late October
    assert read.same_time_of_year([(1.0, d(2000, 1, 5))], d(2026, 12, 28)) == [1.0]     # across the year end
    assert [read.river_level(x) for x in (10, 50, 80, 97)] == ["low", "normal", "high", "very_high"]
    r = read.RiverDay("Rima near Goronyo", "Goronyo", d(2026, 10, 30), 2.0, 20.0, d(1997, 1, 1), None, "low")
    assert r.period == ("late", 10)


def test_lowest_only_when_below_every_day_and_dam_releases_are_said(monkeypatch) -> None:
    _patch(monkeypatch, _fresh())
    from datetime import date as d
    near = read.RiverDay("Rima near Goronyo", "Goronyo", TODAY, 2.4, 0.2, d(1997, 1, 1), None, "low", 2, 912, 914,
                         "Goronyo Dam")                     # 1997's late October had 2.3: not 'the lowest'
    monkeypatch.setattr(read, "river_days", lambda conn, day, pcode="": [near])
    a = ha.hazard_answer(None, "river", "en", ["flood"], read.Where("lga", "NG034006", "Goronyo"), TODAY)
    assert "Today: 2.4 m³/s, *low* for late October (lower than all but 2 of 914 late October days since 1997). " \
           "Model estimate; releases from Goronyo Dam not included." in a.text and "the lowest" not in a.text
    lowest = read.RiverDay("Rima near Goronyo", "Goronyo", TODAY, 2.2, 0.0, d(1997, 1, 1), None, "low", 0, 914, 914)
    monkeypatch.setattr(read, "river_days", lambda conn, day, pcode="": [lowest])
    a = ha.hazard_answer(None, "river", "en", ["flood"], read.Where("lga", "NG034006", "Goronyo"), TODAY)
    assert "(the lowest for late October since 1997)." in a.text and "Model estimate" not in a.text


def test_what_to_watch_out_for_leads_with_what_is_in_season(monkeypatch) -> None:
    _patch(monkeypatch, _fresh())
    monkeypatch.setattr(read, "air_day", lambda *a: None)
    monkeypatch.setattr(read, "river_days", lambda *a: [])
    monkeypatch.setattr(read, "fire_counts", lambda *a: [])
    a = ha.hazard_answer(None, "what should we watch out for?", "en", ["overview"], read.Where("state"), TODAY)
    assert a.text.splitlines()[1:3] == ["Most severe now first (each on its own scale).",
                                        "In season now: river floods, rain."]          # October
    # heat is at Danger (3); rain (none) and fires (no detections) are 0; rivers and dust have no data: the most
    # severe leads, and the season (October: rivers, rain) breaks ties
    order = [a.text.index(x) for x in ("*Heat*", "*Rain*", "*Fires*", "*Rivers*", "*Dust")]
    assert order == sorted(order)
    jan = ha.hazard_answer(None, "what should we watch out for?", "en", ["overview"], read.Where("state"),
                           date(2027, 1, 10))
    assert "In season now: harmattan dust, heat." in jan.text


def test_the_users_point_reaches_the_answer_but_only_from_memory() -> None:
    from app.geo.location import Spot, memory
    s, store, got = make_settings(), UserStore(":memory:"), []
    key = user_key("2348000000001", s)
    store.create(key, "en")
    store.give_consent(key)

    async def answer(question, lang, *, settings, notify=None, history=None, place=None):
        got.append(place)
        return "ok"
    msg = {"from": "2348000000001", "id": "w", "type": "text", "text": {"body": "how hot is it here?"}}
    run = lambda: asyncio.run(handle(msg, None, store=store, settings=s, answer_fn=answer,       # noqa: E731
                                     guard_fn=lambda *a, **k: _ok()))
    memory.remember(key, Spot(13.06, 5.24, "NG034016", "Sokoto North"))
    run()
    assert got[-1] == {"lat": 13.06, "lon": 5.24, "lga_pcode": "NG034016", "lga": "Sokoto North"}
    memory.forget(key)
    store.set_last_lga(key, "NG034006")
    run()
    assert got[-1] == {"lga_pcode": "NG034006"}


def test_generated_hazard_cases_are_what_the_answer_gives() -> None:
    """Drawn from the local hazard_values (skipped without them): each case's question, answered without the
    planner (layer and LGA from the case), gives the case's expected figures and label."""
    import random

    import pytest
    psycopg = pytest.importorskip("psycopg")
    from app.config import get_settings
    from evals.generated.hazards import generate
    try:
        conn = psycopg.connect(get_settings().db_url(), connect_timeout=3)
    except Exception:
        pytest.skip("no database")
    with conn:
        if not conn.execute("SELECT to_regclass('hazard_values') IS NOT NULL AND EXISTS (SELECT 1 FROM "
                            "hazard_values)").fetchone()[0]:
            pytest.skip("no hazard data fetched")
        from app.agent.answer import lagos_today
        from app.sources.lga_names import CANONICAL, pcode
        layer = {"hazard_heat": "heat", "hazard_rain": "rain", "hazard_air": "air", "hazard_flood": "flood",
                 "hazard_fires": "fires", "hazard_overview": "overview"}
        for c in generate(conn, 4, random.Random(3)):
            lga = max((n for n in CANONICAL if n in c["text"]), key=len)        # 'Sokoto South', 'Sabon Birni'
            a = ha.hazard_answer(conn, c["text"], c["lang"], [layer[c["family"]]],
                                 read.Where("lga", pcode(lga), lga), lagos_today(), get_settings())
            for want in c["numbers"]:
                assert want in a.text, (c["id"], want, a.text[:300])


async def _ok():
    from app.guardrails.scope import Verdict
    return Verdict("ok", "test")
