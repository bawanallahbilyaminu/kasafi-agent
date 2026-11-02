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

    def __init__(self, settings, *a, **k):
        self.name = type(self).__name__

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
    import app.providers.baseten as B
    import app.providers.meta as M
    monkeypatch.setattr(M, "MetaClient", Meta)
    monkeypatch.setattr(B, "BasetenClient", Open)
    s = make_settings(baseten_api_key="b")
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


def _setup(case):
    s = make_settings(database_url="postgresql://x:y@127.0.0.1:1/none", kasafi_understanding=True)
    store = UserStore(":memory:")
    key = user_key(SENDER, s)
    store.create(key, "ha" if case["id"] in ("u09", "u10", "u11", "u12", "u27", "u28", "f08", "f09", "f10", "f14",
                                             "f15") else "en")
    store.give_consent(key)
    memory.forget(key)
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
        return "ANSWER"
    monkeypatch.setattr(s.__class__, "has_database", property(lambda self: False))
    msg = {"from": SENDER, "id": f"w-{case['id']}", "type": "text", "text": {"body": case["message"]}}
    outs = asyncio.run(C.handle(msg, None, store=store, settings=s, answer_fn=answer, guard_fn=_ok, place_fn=_none,
                                understand_fn=understand_fn))
    assert len(seen.get("history") or []) == len(case["turns"])            # the conversation reached the step
    got = seen.get("understanding")
    assert got is not None and outs and outs[-1].text == "ANSWER"
    assert score(got.to_dict(), case["expect"]) == []
    if case["place"] == "pin":
        assert seen["place"] and seen["place"].get("lat") is not None


def test_a_correction_about_a_listed_facility_is_checked_against_the_list(monkeypatch) -> None:
    """3 Nov 17:10: 'But Uduth is closer to me' after a nearest-hospital list got the statewide capital budget.
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
    """3 Nov 17:20: 'Has this area ever flooded' after a pin got the 2026 official forecast. With the reading
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
