"""The phone-test gaps of Oct 31 2026, one test group per fix: location on every path, facilities as a capability,
'hospital' means hospitals, the executive summary and quotes on request, definitive alert status (in
test_official.py), and road distances in the emergency reply."""

import asyncio
import time

import psycopg
import pytest

from app.agent.summary import lead, numbers_ok, split_quotes, summarize
from app.config import get_settings
from app.geo import facilities as fac
from app.geo import facility_info as fi
from app.geo.location import LocationMemory, Spot, memory, names_place, with_location
from app.providers.chat import ChatResult
from app.users import UserStore, user_key
from app.whatsapp import conversation as conv
from tests.helpers import make_settings

PIN = {"lat": 13.06, "lon": 5.17, "lga_pcode": "NG034021", "lga": "Wamakko"}


# --- 1. location for every path -------------------------------------------------------------------------------

def test_my_lga_reaches_the_planner_and_a_named_place_wins() -> None:
    assert with_location("Projects in my current LGA", PIN) == \
        "Projects in my current LGA [the user's LGA on file: Wamakko LGA, Sokoto State]"
    assert with_location("Ayyuka a ƙaramar hukumata", {"lga_pcode": "NG034006"}).endswith("Goronyo LGA, Sokoto State]")
    assert with_location("What is the 2026 health budget?", PIN) == "What is the 2026 health budget?"   # not asked
    assert names_place("What did NiMet predict for Sokoto's rainy season?")
    assert with_location("How hot is it here in Sokoto?", PIN) == "How hot is it here in Sokoto?"     # named wins
    assert names_place("IDPs in Kebbe LGA") and not names_place("How hot is it near me?")
    assert names_place("What is the budget of Sokoto North?")                                        # an LGA


def test_the_point_survives_30_minutes_between_messages(monkeypatch) -> None:
    clock = [1000.0]
    monkeypatch.setattr(time, "monotonic", lambda: clock[0])
    m = LocationMemory()
    m.remember("k", Spot(13.06, 5.17, "NG034021", "Wamakko"))
    clock[0] += 15 * 60
    assert m.recall("k") is not None                                 # 15 minutes later: still there
    clock[0] += 16 * 60
    assert m.recall("k") is None                                     # 31 minutes: forgotten


# --- 2. facilities as a capability ----------------------------------------------------------------------------

def _conn():
    try:
        conn = psycopg.connect(get_settings().db_url(), connect_timeout=3)
    except (psycopg.OperationalError, RuntimeError):
        pytest.skip("database not running")
    if not conn.execute("SELECT count(*) FROM facility").fetchone()[0]:
        pytest.skip("no facilities imported")
    return conn


def test_counts_come_from_the_registry_and_offer_the_emonc_figure() -> None:
    with _conn() as conn:
        n = conn.execute("SELECT count(*) FROM facility WHERE level_option = 'Primary Health Center'").fetchone()[0]
        text = fi.count_answer(conn, "How many PHCs are in Sokoto?", "en")
        assert text.startswith(f"Sokoto State has *{n} Primary Health Centres* in the facility registry.")
        assert "facilities it assessed" in text and "GRID3 Nigeria / NHFR" in text
    assert fi.is_count("How many PHCs are in Sokoto?") and fi.is_count("Asibitoci nawa ne a Wamakko?")
    assert not fi.is_count("How many hospitals were built in 2025?")          # a projects question


def test_a_facility_named_fuzzily_gives_its_card() -> None:
    with _conn() as conn:
        hits = fi.find_by_name(conn, "What about Arkilla PHC")
        if not hits:
            pytest.skip("Arkilla not in this registry")
        assert hits[0].name == "Arkilla Primary Health Center" and hits[0].score >= fi.NAMED
        assert fi.find_by_name(conn, "Arkila primary health centre")[0].name == "Arkilla Primary Health Center"
        assert fi.find_by_name(conn, "What is the budget for health?") == []
        text = fi.card(hits[0], "en", hits[1:2])
        assert text.startswith("*Arkilla Primary Health Center*: Primary Health Center, primary level") and \
            "Wamakko LGA" in text and "EmONC" in text


def _db_settings():
    return make_settings(database_url="postgresql://x:y@127.0.0.1:1/none")


ARKILLA = fi.Registered("a1", "Arkilla Primary Health Center", "Primary", "Primary Health Center", "Public",
                        "Arkilla", "Wamakko", "Wamako", 13.07, 5.2, "bemonc", 1.0)


def test_going_to_a_named_facility_asks_for_a_location_then_routes(monkeypatch) -> None:
    s, store = _db_settings(), UserStore(":memory:")
    key = user_key("2348000000055", s)
    store.create(key, "en")
    store.give_consent(key)
    monkeypatch.setattr(conv, "lookup", lambda settings, text: [ARKILLA] if "arkilla" in text.lower() else [])
    routes = []

    async def fake_routes(settings, lat, lon, search, lang, *, mode="list", **kw):
        routes.append((mode, search.shown[0].name))
        return [(f"route to {search.shown[0].name}", None, None)]

    def say(body, kind="text", **kw):
        msg = {"from": "2348000000055", "id": "w", "type": kind, **({"text": {"body": body}} if kind == "text"
                                                                      else kw)}
        return asyncio.run(conv.handle(msg, None, store=store, settings=s, answer_fn=None, facility_fn=fake_routes,
                                       locate_fn=_located))
    out = say("What about Arkilla PHC")
    assert out[0].text.startswith("*Arkilla Primary Health Center*") and not routes
    out = say("How far is it from me?")                             # no point yet: the location request
    assert out[-1].location_request
    say("", kind="location", location={"latitude": 13.06, "longitude": 5.17})
    assert routes == [("route", "Arkilla Primary Health Center")]
    out = say("I want to go to Arkilla PHC")                       # point in memory: straight to the route
    assert out[0].text == "route to Arkilla Primary Health Center"
    memory.forget(key)


async def _located(settings, lat, lon):
    from app.geo import Area
    return Area("NG034021", "Wamakko", "Gumbi", "62109")


# --- 3. 'hospital' means hospitals --------------------------------------------------------------------------

def test_hospital_means_hospital_level_facilities() -> None:
    assert fac.filters_from("Where is the nearest hospital?").levels == ("Secondary", "Tertiary")
    assert fac.filters_from("Ina asibiti mafi kusa?").levels == ("Secondary", "Tertiary")
    assert fac.filters_from("Where is the nearest clinic?").levels == ()
    assert fac.filters_from("nearest health facility or hospital").levels == ()   # any kind asked


def test_a_much_nearer_facility_of_any_kind_gets_its_own_line(monkeypatch) -> None:
    def f(fid, name, level, km):
        return fac.Facility(fid, name, level, "", "Public", "", 13.1, 5.2, "Wamakko", "Wamakko", km)

    def query(settings, lat, lon, filters, skip):
        return [f("h", "Kware General Hospital", "Secondary", 9.0)] if filters.levels else \
            [f("p", "Rinin Tawaye PHC", "Primary", 0.8)]
    monkeypatch.setattr(fac, "_query", query)
    s = make_settings()
    out = asyncio.run(fac.search_replies(s, 13.06, 5.17, fac.FacilitySearch(fac.filters_from("nearest hospital")),
                                         "en", route=False, drawn=False))
    text = out[0][0]
    assert text.startswith("The nearest hospital is Kware General Hospital, about 9.0 km in a straight line.")
    assert "Nearer, but not a hospital: *Rinin Tawaye PHC* (primary), about 0.8 km in a straight line." in text


# --- 4. executive summary first, quotes on request ------------------------------------------------------------

class Client:
    def __init__(self, reply):
        self.reply = reply

    async def chat(self, messages, **kw):
        return ChatResult(content=self.reply, model="m", finish_reason="stop")


def test_the_summary_uses_only_verified_figures() -> None:
    details = "Rima near Goronyo: 2.4 m³/s, low for late October. Sokoto: 1,200 people."
    s = make_settings()
    ok = asyncio.run(summarize("q", details, "en", s, Client("The Rima near Goronyo is low, at 2.4 m³/s.")))
    assert ok == "The Rima near Goronyo is low, at 2.4 m³/s."
    assert asyncio.run(summarize("q", details, "en", s, Client("The river is at 3.1 m³/s."))) == ""     # not printed
    assert numbers_ok("1200 people", details)                                                       # commas aside
    cut = asyncio.run(summarize("q", details, "en", s, Client("The Rima is low. It is 2.4 m³/s and")))
    assert cut == "The Rima is low."                                                                # cut off: trimmed


def test_quotes_are_held_back_and_sent_on_request() -> None:
    full = "• October-November 2026, page 42: “Sokoto remains under High Flood Risk.”\n📄 NIHSA AFO p. 42"
    details, quotes = split_quotes(full)
    assert details == "• October-November 2026, page 42\n📄 NIHSA AFO p. 42"
    assert quotes == "• October-November 2026, page 42: “Sokoto remains under High Flood Risk.”"
    assert lead("Sokoto is at high flood risk this season.", details).startswith("Sokoto is at high flood risk")
    assert split_quotes("NiMet, page 3: “Wetter.”\nNiMet, page 3: “Drier spells.”")[0] == "NiMet, page 3"
    s, store = make_settings(), UserStore(":memory:")
    key = user_key("2348000000066", s)
    store.create(key, "en")
    store.give_consent(key)
    store.add_turn(key, "en", "q", details, quotes=quotes)
    out = asyncio.run(conv.handle({"from": "2348000000066", "id": "w", "type": "text", "text": {"body": "quotes"}},
                                  None, store=store, settings=s, answer_fn=None))
    assert out[0].text == quotes


# --- 6. the emergency reply's road distance ---------------------------------------------------------------------

def _emergency(monkeypatch, routes_fn):
    from app.guardrails import emergency as em
    store = UserStore(":memory:")
    key = user_key("2348000000044", make_settings())
    store.create(key, "en")
    store.give_consent(key)
    memory.remember(key, Spot(13.06, 5.24, "NG034017", "Sokoto South"))
    hosp = fac.Facility("h", "Specialist Hospital", "Tertiary", "", "Public", "", 13.07, 5.23, "Sokoto North",
                        "Sokoto North", 2.1)

    async def lookup(settings, lat, lon, maternal, lga_pcode=""):
        return [("hospital", hosp)]
    monkeypatch.setattr(conv, "add_routes", routes_fn)
    t0 = time.perf_counter()
    out = asyncio.run(conv.handle({"from": "2348000000044", "id": "w", "type": "text",
                                   "text": {"body": "My father collapsed"}}, None, store=store, settings=_db_settings(),
                                  answer_fn=None, emergency_fn=lookup, classify_fn=lambda *a: None))
    memory.forget(key)
    assert em.WORDS["en"]["now"] in out[0].text
    return out[0].text, time.perf_counter() - t0


def test_the_emergency_reply_gives_road_distance_and_directions(monkeypatch) -> None:
    async def routes(settings, lat, lon, found, profile="car", timeout=6.0):
        for f in found:
            f.road_km, f.minutes = 6.0, 12
        return True
    text, took = _emergency(monkeypatch, routes)
    assert "*Specialist Hospital*, 6 km by road, about 12 min" in text and "google.com/maps/dir" in text
    assert "straight-line" not in text and took < 3.0


def test_a_slow_road_service_falls_back_to_the_straight_line_and_says_so(monkeypatch) -> None:
    async def slow(settings, lat, lon, found, profile="car", timeout=6.0):
        await asyncio.sleep(5)
        return True
    text, took = _emergency(monkeypatch, slow)
    assert "about 2.1 km in a straight line" in text and "straight-line distance shown" in text and took < 3.0
