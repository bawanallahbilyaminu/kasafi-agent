"""Conversation understanding (app/agent/understand.py), part of the deploy gate. Free: the model's readings of the
45 conversations in evals/understanding/cases.json are replayed from evals/understanding/recorded.json (recorded
with `uv run python evals/understanding/run.py`; re-record after a prompt change)."""

import asyncio
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from app.agent import understand as U
from app.geo.facilities import Facility, FacilitySearch, Filters
from app.geo.location import Spot, memory
from app.guardrails.scope import Verdict
from app.users import UserStore, user_key
from app.whatsapp import conversation as C
from evals.understanding.run import score
from tests.helpers import make_settings

HERE = Path("evals/understanding")
CASES = json.loads((HERE / "cases.json").read_text(encoding="utf-8"))["cases"]
RECORDED = json.loads((HERE / "recorded.json").read_text(encoding="utf-8"))
SENDER = "2348000000077"
PIN = Spot(13.045, 5.155, "NG034021", "Wamakko", ward="Kalambaina", how="pin")


def reading(cid: str) -> U.Understanding:
    d = dict(RECORDED[cid])
    d.pop("seconds", None)
    return U.Understanding(**d)


@pytest.mark.parametrize("case", CASES, ids=[c["id"] for c in CASES])
def test_the_recorded_reading_is_right(case) -> None:
    """Capability, and level, time and kind where the case gives them (the live run is report.md)."""
    assert score(RECORDED[case["id"]], case["expect"]) == []


def test_a_reply_that_isnt_the_json_asked_for_is_no_reading() -> None:
    assert U.parse({"kind": "new"}) is None                           # no restatement
    u = U.parse({"kind": "odd", "capability": "x", "subject": {"level": "planet"}, "time": "now",
                 "restatement": "Has my ward ever flooded?"})
    assert (u.kind, u.capability, u.level, u.time) == ("new", "other", "none", "none")


class _Client:
    """A model client that fails (an exception) or answers with a reading's JSON."""
    replies: dict = {}
    default_model = "fake-model"

    def __init__(self, settings, *a, **k):
        self.name = type(self).__name__

    async def aclose(self):
        return None

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return None

    async def chat(self, messages, **kw):
        r = self.replies[self.name]
        if isinstance(r, Exception):
            raise r
        return SimpleNamespace(content=r)


class Meta(_Client):
    pass


class Open(_Client):
    pass


GOOD = json.dumps({"kind": "new", "capability": "place_history", "subject": {"level": "pin", "name": ""},
                   "time": {"kind": "past", "years": []}, "measure": "flooded",
                   "restatement": "Has my farm (the pin) ever flooded?"})


def test_when_muse_spark_fails_muse_spark_open_reads_it_and_when_both_fail_the_fallback_is_recorded(monkeypatch):
    import app.providers.fireworks as F
    import app.providers.meta as M
    monkeypatch.setattr(M, "MetaClient", Meta)
    monkeypatch.setattr(F, "FireworksClient", Open)          # the Muse Spark Open host (KASAFI_OPEN_HOSTS)
    s = make_settings(fireworks_api_key="f")
    _Client.replies = {"Meta": TimeoutError(), "Open": GOOD}
    fallbacks: list = []
    u = asyncio.run(U.understand_message("Has this land ever flooded?", [], None, s, fallbacks=fallbacks))
    assert u is not None and u.capability == "place_history" and fallbacks == []
    _Client.replies = {"Meta": TimeoutError(), "Open": "not json at all"}
    u = asyncio.run(U.understand_message("Has this land ever flooded?", [], None, s, fallbacks=fallbacks))
    assert u is None and fallbacks[0].startswith("meta: TimeoutError") and \
        any(f.startswith("open: not JSON") for f in fallbacks)


def test_kasafis_reply_is_summed_up_with_what_it_listed() -> None:
    s = U.summary("Nearest hospitals to you (by road):\n1. Specialist Hospital Sokoto: 6.2 km\n2. Women and "
                  "Children Welfare Clinic: 7.0 km")
    assert "listed: 1. Specialist Hospital Sokoto: 6.2 km; 2. Women and Children Welfare Clinic: 7.0 km" in s


# --- the 45 conversations through the conversation handler ---------------------------------------------------------

async def _ok(*a, **k):
    return Verdict("ok", "none")


async def _none(*a, **k):
    return None


async def _quiet_classifier(*a, **k):
    """The emergency classifier saying no: the understanding step's 'urgent' is then the only net."""
    return False


def _setup(case):
    s = make_settings(database_url="postgresql://x:y@127.0.0.1:1/none", kasafi_understanding=True)
    store = UserStore(":memory:")
    key = user_key(SENDER, s)
    store.create(key, case.get("lang") or ("ha" if case["id"] in ("u09", "u10", "u11", "u12", "u27", "u28", "f08",
                                                                  "f09", "f10", "f14", "f15") else "en"))
    store.give_consent(key)
    memory.forget(key)
    from app.privacy import names
    names.forget(key)                         # a name a case gave (p01-p08) never reaches the next case
    if case["place"] == "pin":
        memory.remember(key, PIN)
    elif case["place"] == "lga":
        store.set_last_lga(key, "NG034021")
    for t in case["turns"]:
        store.add_turn(key, "en", t["user"], t["kasafi"], [], "", "")
    return s, store, key


@pytest.mark.parametrize("case", CASES, ids=[c["id"] for c in CASES])
def test_each_conversation_reaches_the_capability_and_subject_it_means(case, monkeypatch) -> None:
    """The handler with the recorded reading: the answer function gets that reading (capability, subject level,
    time) and the restatement; a facility correction is checked by its own handler, never answered as another
    question. Keyword shortcuts don't pre-empt it (no database here: the PostGIS shortcuts are off)."""
    s, store, key = _setup(case)
    seen: dict = {}

    async def understand_fn(text, history, place, settings, fallbacks=None):
        seen["history"], seen["place"] = history, place
        return reading(case["id"])

    async def answer(question, lang, **kw):
        seen["understanding"] = kw.get("understanding")
        seen.setdefault("answered", []).append(question)
        return "ANSWER"

    async def conversational(message, lang, history, place, settings, client_cls=None, name=""):
        seen["conversational"], seen["name"] = (message, lang), name
        return "HELLO", "model"
    import app.agent.conversational as CV
    monkeypatch.setattr(CV, "reply", conversational)
    monkeypatch.setattr(s.__class__, "has_database", property(lambda self: False))
    msg = {"from": SENDER, "id": f"w-{case['id']}", "type": "text", "text": {"body": case["message"]}}
    async def no_facilities(*a, **k):
        return []
    outs = asyncio.run(C.handle(msg, None, store=store, settings=s, answer_fn=answer, guard_fn=_ok, place_fn=_none,
                                understand_fn=understand_fn, emergency_fn=no_facilities,
                                classify_fn=_quiet_classifier))
    assert len(seen.get("history") or []) == len(case["turns"])            # the conversation reached the step
    if reading(case["id"]).urgent:                          # an emergency now: the fast path, never an answer
        assert case["expect"].get("urgent") and "understanding" not in seen
        assert outs[0].text.startswith("🚨")
        return
    if reading(case["id"]).kind == "menu":                  # 'menu' / 'zaɓi': the interactive list, nothing else
        assert case["expect"].get("kind") == "menu" and outs[0].menu and "understanding" not in seen
        return
    if reading(case["id"]).capability == "conversation":    # about Kasafi or the conversation: never the documents
        assert "understanding" not in seen and seen["conversational"][0] == case["message"]
        assert outs and outs[-1].text == "HELLO"
        assert case["expect"]["capability"] == "conversation"
        assert seen["name"] == case["expect"].get("user_name", "")      # the name the message gave, else none
        return
    got = seen.get("understanding")
    if "parts" in case["expect"]:                           # a multi-part message: each part answered, one reply
        assert score(reading(case["id"]).to_record(), case["expect"]) == []
        assert len(seen["answered"]) == len(case["expect"]["parts"]) and outs[0].text.startswith("*1. ")
        assert outs[0].text.count("ANSWER") == len(case["expect"]["parts"])
        return
    assert got is not None and outs and outs[-1].text.startswith("ANSWER")    # with its closing offer, if any
    assert score(got.to_record(), case["expect"]) == []
    if case["place"] == "pin":
        assert seen["place"] and seen["place"].get("lat") is not None


def test_a_correction_about_a_listed_facility_is_checked_against_the_list(monkeypatch) -> None:
    """2 Nov 17:10: 'But Uduth is closer to me' after a nearest-hospital list got the statewide capital budget.
    Now: UDUTH's road distance from the pin against the list's first, and why it wasn't listed."""
    key = "k-correction"
    memory.remember(key, PIN)
    listed = Facility("f1", "Specialist Hospital Sokoto", "Secondary", "General Hospital", "Public", "", 13.06, 5.24,
                      "Sokoto North", "", 6.5)
    memory.remember_search(key, FacilitySearch(Filters(levels=("Secondary", "Tertiary")), shown=[listed]))
    uduth = SimpleNamespace(fid="f9", name="Usman Danfodio University Teaching Hospital", level="Tertiary",
                            kind="Teaching Hospital", ownership="Public", lat=13.0266, lon=5.22, lga="Wamakko",
                            lga_attr="Wamakko", emonc="", checked="")
    asked = []
    monkeypatch.setattr(C, "lookup", lambda settings, text: asked.append(text) or [uduth])

    async def routes(settings, lat, lon, facilities, profile="car", **kw):
        for f, (km, mins) in zip(facilities, [(8.1, 15), (11.0, 22)]):
            f.road_km, f.minutes = km, mins
        return True
    monkeypatch.setattr(C, "add_routes", routes)
    u = U.Understanding(kind="correction", capability="facility", level="facility", name="UDUTH",
                        restatement="UDUTH is closer to my farm (the pin) than the hospitals listed")
    outs = asyncio.run(C._facility_correction(u, key, "en", make_settings(), None))
    text = outs[0].text
    assert asked == ["Usman Danfodio University Teaching Hospital"]          # the abbreviation, spelled out
    assert "You're right: Usman Danfodio University Teaching Hospital is closer" in text
    assert "Specialist Hospital Sokoto" in text and "nearest in a straight line" in text
    assert memory.last_search(key).shown[0].name.startswith("Usman Danfodio")   # 'route?' now means UDUTH


# --- the answer loop obeys the reading -----------------------------------------------------------------------------

@pytest.fixture(scope="module")
def conn():
    psycopg = pytest.importorskip("psycopg")
    from app.config import get_settings
    st = get_settings()
    if not st.has_database:
        pytest.skip("no database configured")
    try:
        c = psycopg.connect(st.db_url(), connect_timeout=3)
        c.execute("SELECT 1 FROM documents LIMIT 1")
    except Exception as e:  # noqa: BLE001
        pytest.skip(f"no dev database: {e}")
    yield c
    c.close()


def test_a_past_flood_question_goes_to_place_history_never_the_forecast(conn, monkeypatch) -> None:
    """2 Nov 17:20: 'Has this area ever flooded' after a pin got the 2026 official forecast. With the reading
    (place_history, ward, past) the ward's satellite record answers; the outlook and hazard routes may not."""
    from app.agent import answer as A
    from app.agent.answer import Plan

    async def plan_question(q, *a, **k):
        return Plan(english_question=q, search_queries=[q], doc_ids=[])

    async def settle(*a, **k):
        return None
    called = []
    monkeypatch.setattr(A, "plan_question", plan_question)
    monkeypatch.setattr(A, "settle_by_words", settle)
    monkeypatch.setattr(A, "area_answer", lambda *a, **k: called.append("area") or
                        SimpleNamespace(text="WARD RECORD", found=True, working="", partial=False, specs=[],
                                        needs_pin=False))
    monkeypatch.setattr(A.official, "route", lambda *a, **k: called.append("official") or "outlook_flood")
    place = {"lat": 13.045, "lon": 5.155, "lga_pcode": "NG034021", "lga": "Wamakko", "ward": "Kalambaina",
             "wardcode": "x"}
    a = asyncio.run(A.answer_question("Has this area ever flooded", "en", conn, settings=make_settings(),
                                      place=place, understanding=reading("u02")))
    assert called == ["area"] and a.text == "WARD RECORD"


# --- 2 Nov evening, live: 'Who are you?' and a cold 'But uduth is closer to me' went to the document search ----------

UDUTH = SimpleNamespace(fid="f9", name="Usman Danfodio University Teaching Hospital", level="Tertiary",
                        kind="Teaching Hospital", ownership="Public", lat=13.0266, lon=5.22, lga="Wamakko",
                        lga_attr="Wamakko", emonc="", checked="", score=1.0)


def _near(*a, **k):
    return [Facility("f1", "Specialist Hospital Sokoto", "Secondary", "General Hospital", "Public", "", 13.06, 5.24,
                     "Sokoto North", "", 6.5),
            Facility("f9", UDUTH.name, "Tertiary", "Teaching Hospital", "Public", "", 13.0266, 5.22, "Wamakko", "", 4.0)]


async def _routes(settings, lat, lon, facilities, profile="car", **kw):
    for f in facilities:
        f.road_km, f.minutes = (5.0, 9) if f.fid == "f9" else (9.0, 17)
    return True


def test_a_cold_claim_with_only_the_lga_on_file_is_checked_from_the_lgas_centre_and_says_so(monkeypatch) -> None:
    """Trace #123: no list, no pin, Wamakko on file. The claim is checked by road against the nearest other
    hospital, from the LGA's centre, and the reply says it measured from there."""
    import app.geo.facilities as G
    key = "k-cold-lga"
    memory.forget(key)
    store = UserStore(":memory:")
    store.create(key, "en")
    store.set_last_lga(key, "NG034021")
    monkeypatch.setattr(C, "lookup", lambda settings, text: [UDUTH])
    monkeypatch.setattr(C, "_lga_centre", lambda settings, pcode: (13.05, 5.17))
    monkeypatch.setattr(G, "_query", _near)
    monkeypatch.setattr(C, "add_routes", _routes)
    u = U.Understanding(kind="correction", capability="facility", level="facility", name="Usmanu Danfodiyo "
                        "University Teaching Hospital", restatement="UDUTH is closer to me in my LGA")
    text = asyncio.run(C._facility_correction(u, key, "en", make_settings(), None, store=store))[0].text
    assert "centre of Wamakko LGA (your LGA on file)" in text
    assert "The nearest other hospital, Specialist Hospital Sokoto" in text
    assert "You're right: Usman Danfodio University Teaching Hospital is the closest hospital to the centre of " \
           "Wamakko LGA." in text


def test_a_cold_claim_with_no_location_asks_for_it_and_checks_when_the_pin_comes(monkeypatch) -> None:
    import app.geo.facilities as G
    key = "k-cold-none"
    memory.forget(key)
    store = UserStore(":memory:")
    store.create(key, "en")
    monkeypatch.setattr(C, "lookup", lambda settings, text: [UDUTH])
    monkeypatch.setattr(G, "_query", _near)
    monkeypatch.setattr(C, "add_routes", _routes)
    u = U.Understanding(kind="correction", capability="facility", level="facility", name="UDUTH",
                        restatement="UDUTH is closer to me")
    out = asyncio.run(C._facility_correction(u, key, "en", make_settings(), None, store=store))[0]
    assert out.location_request and "I need your location" in out.text
    waiting = memory.waiting_question(key)
    assert waiting == C.CLAIM_WAIT + UDUTH.name
    outs = asyncio.run(C._after_location(waiting, key, "en", make_settings(), None, PIN))
    assert "from your pin" in outs[0].text and "is the closest hospital to you" in outs[0].text


def test_couldnt_find_never_answers_a_message_that_isnt_a_document_question(monkeypatch) -> None:
    """A reading of 'other' that the documents can't answer, and with no reading a short non-question: what Kasafi
    can help with and what they're looking for, never 'I couldn't find the answer…'."""
    from app.agent.answer import NOT_FOUND
    case = {"id": "x-other", "place": "pin", "turns": []}
    s, store, key = _setup(case)
    monkeypatch.setattr(s.__class__, "has_database", property(lambda self: False))

    async def answer(question, lang, **kw):
        return SimpleNamespace(text=NOT_FOUND["en"], found=False, sources=[], working="", quotes="")

    async def other(*a, **k):
        return U.Understanding(kind="new", capability="other", restatement="Tell me something interesting")
    msg = {"from": SENDER, "id": "w-x-other", "type": "text", "text": {"body": "Tell me something interesting about this"}}
    outs = asyncio.run(C.handle(msg, None, store=store, settings=s, answer_fn=answer, guard_fn=_ok, place_fn=_none,
                                understand_fn=other))
    assert NOT_FOUND["en"] not in outs[-1].text and "What are you looking for?" in outs[-1].text
    assert "Has my farm ever flooded?" in outs[-1].text              # examples that fit a user with a pin

    async def failed(*a, **k):
        return None
    msg = {"from": SENDER, "id": "w-x-ok", "type": "text", "text": {"body": "ok then"}}
    outs = asyncio.run(C.handle(msg, None, store=store, settings=s, answer_fn=answer, guard_fn=_ok, place_fn=_none,
                                understand_fn=failed))
    assert NOT_FOUND["en"] not in outs[-1].text and "What are you looking for?" in outs[-1].text


def test_who_are_you_with_no_reading_still_gets_the_conversational_reply(monkeypatch) -> None:
    case = {"id": "x-who", "place": "none", "turns": []}
    s, store, key = _setup(case)
    import app.agent.conversational as CV

    async def conversational(message, lang, history, place, settings, client_cls=None):
        return "I'm Kasafi", "model"
    monkeypatch.setattr(CV, "reply", conversational)
    monkeypatch.setattr(s.__class__, "has_database", property(lambda self: False))

    async def failed(*a, **k):
        return None

    async def answer(*a, **k):
        raise AssertionError("no document search for 'Who are you?'")
    msg = {"from": SENDER, "id": "w-x-who", "type": "text", "text": {"body": "Who are you?"}}
    outs = asyncio.run(C.handle(msg, None, store=store, settings=s, answer_fn=answer, guard_fn=_ok, place_fn=_none,
                                understand_fn=failed))
    assert outs[-1].text == "I'm Kasafi"


def test_the_conversational_reply_falls_back_to_the_fixed_words_in_the_users_language() -> None:
    from app.agent import conversational as CV

    class Down(_Client):
        replies = {"Down": TimeoutError()}
    text, how = asyncio.run(CV.reply("Kai wanene?", "ha", [], None, make_settings(), client_cls=Down))
    assert how == "fixed" and text.startswith("Ni ne Kasafi") and "ku aiko da wurinku" in text
    _Client.replies = {"Meta": "# Hello\nI'm Kasafi."}
    text, how = asyncio.run(CV.reply("Hello", "en", [], None, make_settings(), client_cls=Meta))
    assert how == "model" and text == "Hello\nI'm Kasafi."


def test_the_trace_carries_the_reading_first() -> None:
    from app.agent import trace
    from app.agent.answer import Answer
    a = Answer("x", True, True)
    a.understanding = reading("c20")
    t = trace.record(a)
    assert list(t)[0] == "understanding" and t["understanding"]["capability"] == "facility"


def test_a_dash_said_to_mean_no_figure_is_the_rule_followed_not_a_misread() -> None:
    """Trace #123: the retry said 'a dash in the table means no figure is printed' and was refused for it."""
    from app.agent.answer import dash_misread
    assert dash_misread("A dash in the table means no figure was printed for Wamakko.") == ""
    assert dash_misread("In the table a dash means no data.") == ""
    assert dash_misread("The dash is zero") and dash_misread("Dange Shuni shows no enrolment (- in the table)")


# --- the two audit gaps: place_budget and facility readings decide their routes whatever the wording ---------------

def test_a_place_budget_reading_gives_the_lga_tool_whatever_the_wording() -> None:
    from app.agent.answer import Plan, reading_lga_route
    plan = Plan(english_question="x", search_queries=[], doc_ids=[])
    pin = {"lat": 13.045, "lon": 5.155, "lga_pcode": "NG034021", "lga": "Wamakko", "ward": "Kalambaina"}
    farmers = U.Understanding(kind="follow_up", capability="place_budget", level="lga", measure="projects",
                              restatement="Is there anything for farmers in my LGA's budget?")
    spec = reading_lga_route(farmers, farmers.restatement, plan, pin)
    assert spec["tool"] == "lga_projects" and spec["lga"] == "Wamakko" and spec["ward"] == "Kalambaina"
    named = U.Understanding(capability="place_budget", level="lga", name="Tambuwal",
                            restatement="What projects is the government doing in Tambuwal?")
    spec = reading_lga_route(named, named.restatement, plan, pin)
    assert spec["lga"] == "Tambuwal" and spec["ward"] == ""                # a named LGA beats the one on file
    saved = reading_lga_route(farmers, farmers.restatement, plan, {"lga_pcode": "NG034021"})
    assert saved["lga"] == "Wamakko"                                         # the LGA on file alone (no pin)
    assert reading_lga_route(farmers, farmers.restatement, plan, None) == {"tool": "need_place"}
    span = U.Understanding(capability="place_budget", level="lga", time="span", years=[2024, 2025, 2026],
                           restatement="What did my LGA get each year?")
    assert reading_lga_route(span, span.restatement, plan, pin)["tool"] == "lga_years"
    assert reading_lga_route(U.Understanding(capability="budget", restatement="x"), "x", plan, pin) is None


def test_a_place_budget_reading_with_no_place_asks_for_it_and_resumes_with_the_reading(monkeypatch) -> None:
    case = {"id": "x-pb", "place": "none", "turns": []}
    s, store, key = _setup(case)
    monkeypatch.setattr(s.__class__, "has_database", property(lambda self: False))
    reading_pb = U.Understanding(kind="new", capability="place_budget", level="lga", measure="projects",
                                 restatement="Is there anything for farmers in my LGA's budget?")
    seen = []

    async def answer(question, lang, **kw):
        seen.append((question, kw.get("understanding"), kw.get("place")))
        if len(seen) == 1:
            return SimpleNamespace(text="Which area do you mean?", found=False, needs_pin=True, sources=[],
                                   working="", quotes="")
        return "PLACE BUDGET"

    async def understand_fn(*a, **k):
        return reading_pb

    async def typed(settings, text):
        return Spot(12.9, 4.6, "NG034019", "Tambuwal", how="place") if text == "Tambuwal" else None
    msg = {"from": SENDER, "id": "w-pb1", "type": "text", "text": {"body": "Anything for farmers?"}}
    outs = asyncio.run(C.handle(msg, None, store=store, settings=s, answer_fn=answer, guard_fn=_ok, place_fn=typed,
                                understand_fn=understand_fn))
    assert outs[-1].location_request
    assert memory.peek_question(key) == C.PLACE_BUDGET_WAIT + reading_pb.restatement
    msg = {"from": SENDER, "id": "w-pb2", "type": "text", "text": {"body": "Tambuwal"}}
    outs = asyncio.run(C.handle(msg, None, store=store, settings=s, answer_fn=answer, guard_fn=_ok, place_fn=typed,
                                understand_fn=understand_fn))
    assert outs[-1].text.startswith("PLACE BUDGET")             # with its closing offer
    q, u, place = seen[-1]
    assert q == reading_pb.restatement and u.capability == "place_budget" and place["lga_pcode"] == "NG034019"


def test_a_facility_reading_without_name_count_or_nearest_goes_to_the_facilities(monkeypatch) -> None:
    """'Is there anywhere I can deliver a baby?' read as facility: the nearest search of that kind (maternal care),
    the location asked for first when there is none; never the documents."""
    key = "k-fac-reading"
    memory.forget(key)
    u = U.Understanding(kind="new", capability="facility", level="none", measure="nearest", care="maternal",
                        facility_level="any", ownership="any",
                        restatement="Is there a health facility where I can deliver a baby near me?")
    out = asyncio.run(C._facility_reading("Is there anywhere I can deliver a baby?", u, key, "en", make_settings(),
                                          None))[0]
    assert out.location_request and memory.peek_question(key).startswith(C.FACILITY_WAIT)
    searched = []

    async def facility_fn(settings, lat, lon, search, lang, mode="list"):
        searched.append(search.filters)
        return []

    async def run():
        return await C._after_location(memory.waiting_question(key), key, "en", make_settings(), facility_fn, PIN)
    asyncio.run(run())
    assert searched and searched[0].emonc                         # 'deliver a baby' -> maternal (EmONC) care


def test_a_facility_reading_naming_one_gives_its_registry_card(monkeypatch) -> None:
    key = "k-fac-named"
    memory.forget(key)
    monkeypatch.setattr(C, "lookup", lambda settings, text: [UDUTH])
    monkeypatch.setattr(C, "card", lambda f, lang, others: f"CARD {f.name}")
    u = U.Understanding(kind="new", capability="facility", level="facility", name="UDUTH",
                        restatement="Does UDUTH have an emergency unit?")
    outs = asyncio.run(C._facility_reading("Does uduth have emergency?", u, key, "en", make_settings(), None))
    assert outs[0].text == f"CARD {UDUTH.name}"


def test_the_reading_chooses_the_facilities_and_the_words_only_without_one() -> None:
    """2 Nov: 'where can my wife deliver a baby' matched no maternal keyword. The reading's care, level and ownership
    decide; the keyword filters are the fallback when the understanding step gave no reading."""
    from app.geo.facilities import Filters
    words = "Where can my wife deliver a baby?"
    maternal = U.parse({"kind": "new", "capability": "facility", "subject": {"level": "none"}, "time": {"kind": "now"},
                        "facility": {"care": "maternal", "level": "any", "ownership": "public"},
                        "restatement": "Where is the nearest government facility where my wife can deliver?"})
    f = C.reading_filters(maternal, words)
    assert f.emonc == "bemonc" and f.ownership == "Public" and f.levels == ()
    general = U.parse({"kind": "new", "capability": "facility", "subject": {"level": "none"},
                       "facility": {"care": "general", "level": "hospital", "ownership": "any"},
                       "restatement": "Where is the nearest maternity hospital?"})
    assert C.reading_filters(general, "maternity").emonc == ""        # the reading, not the word, decides
    assert C.reading_filters(general, "x").levels == ("Secondary", "Tertiary")
    assert C.reading_filters(None, "nearest maternity").emonc == "bemonc"   # no reading: the keywords
    follow = U.parse({"kind": "follow_up", "capability": "facility", "subject": {"level": "none"},
                      "facility": {"care": "general", "level": "any", "ownership": "public"},
                      "restatement": "Only government ones"})
    kept = C.reading_filters(follow, "only government ones", Filters(emonc="bemonc"))
    assert kept.emonc == "bemonc" and kept.ownership == "Public"       # a follow-up keeps the list's care
    budget = U.parse({"kind": "new", "capability": "budget", "facility": {"care": "maternal"},
                      "restatement": "Maternal health budget 2026"})
    assert budget.care == ""                                           # facility filters only for facility readings


# --- 2 Nov night: 'matata na naƙuda' reached neither the phrase list nor the classifier -----------------------------

def test_a_message_about_someones_body_asks_the_classifier_even_with_no_phrase() -> None:
    from app.guardrails import emergency as em
    for text in ("Matata na naƙuda", "My wife's water broke and the pains are coming fast",
                 "Yaro na yana ta zazzaɓi baya farkawa", "My husband cut his leg with a cutlass and it won't stop"):
        d = em.detect(text)
        assert not d.hit and d.health, text                       # off the phrase list, but the model is asked
    for text in ("How many maternity centres are in Sokoto?", "Nawa aka ware wa lafiyar mata masu ciki a 2026?"):
        assert not em.detect(text).health, text                   # a data question: no call


def test_layer_one_records_what_each_check_said() -> None:
    from app.guardrails import emergency as em

    async def yes(*a, **k):
        return True
    why: dict = {}
    d = asyncio.run(em.decide("Matata na naƙuda", make_settings(), True, yes, why=why))
    assert d is not None and d.by == "classifier" and d.maternal and why == {"phrase": False, "classifier": True}


def test_an_urgent_reading_fires_the_maternal_fast_path_when_both_checks_missed(monkeypatch) -> None:
    """Layer 2: the classifier said no (or wasn't asked); the understanding step reads labour happening now."""
    case = {"id": "x-urgent", "place": "pin", "turns": []}
    s, store, key = _setup(case)
    monkeypatch.setattr(s.__class__, "has_database", property(lambda self: False))
    picked = []

    async def facilities(settings, lat, lon, maternal, lga_pcode=""):
        picked.append(maternal)
        return []

    async def urgent(*a, **k):
        return U.Understanding(kind="new", capability="facility", care="maternal", urgent=True,
                               urgent_reason="woman in labour now", restatement="My wife is in labour now")

    async def answer(*a, **k):
        raise AssertionError("an emergency never goes to an answer")
    msg = {"from": SENDER, "id": "w-x-urgent", "type": "text", "text": {"body": "Matata na naƙuda"}}
    real = C._emergency

    async def emergency(key, lang, d, *a, **k):
        picked.append((d.maternal, d.by))
        return await real(key, lang, d, *a, **k)
    monkeypatch.setattr(C, "_emergency", emergency)
    outs = asyncio.run(C.handle(msg, None, store=store, settings=s, answer_fn=answer, guard_fn=_ok, place_fn=_none,
                                understand_fn=urgent, emergency_fn=facilities, classify_fn=_quiet_classifier))
    assert outs[0].text.startswith("🚨") and picked == [(True, "understanding")]     # maternal: EmONC picks first


def test_the_reading_carries_urgent_and_its_reason() -> None:
    u = U.parse({"kind": "new", "capability": "facility", "subject": {"level": "pin"}, "time": {"kind": "now"},
                 "facility": {"care": "maternal", "level": "any", "ownership": "any"}, "urgent": True,
                 "urgent_reason": "labour now", "restatement": "My wife is in labour now"})
    assert u.urgent and u.urgent_reason == "labour now" and u.care == "maternal"
    assert U.parse({"kind": "new", "capability": "budget", "urgent": "yes", "restatement": "x"}).urgent is False


def test_a_sam_outline_over_20_ha_is_not_one_farm_and_the_size_is_asked_saying_why(monkeypatch) -> None:
    from app.place import answer as PA
    from app.place.outline import fallback
    big = fallback(5.155, 13.045, "too_big")
    big.drawn_ha = 46.9

    async def outline(*a, **k):
        return big
    monkeypatch.setattr(PA, "plot_outline", outline)
    monkeypatch.setattr(PA, "first_request", lambda *a, **k: False)
    place = {"lat": 13.045, "lon": 5.155, "lga": "Wamakko", "lga_pcode": "NG034021"}
    from datetime import date
    a = asyncio.run(PA.place_answer(None, make_settings(), "Has my farm ever flooded?", "", "en", place,
                                    date(2026, 11, 2), ask_size=True))
    assert a.needs_size and "about 47 ha, more than one farm usually is" in a.text
