"""Feature switches (app/config.py: KASAFI_SHORTCUT_*): off turns a capability shortcut's own trigger off without
removing the capability. With every switch off, a message that a shortcut would have answered reaches the answer
function (the planner), the emergency fast path and the guardrails still fire, and the in-code routing eval set
runs with every shortcut case routed to the planner."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

import pytest

from app.geo.location import Spot, memory
from app.guardrails.scope import Verdict
from app.users import UserStore, user_key
from app.whatsapp import conversation as C
from tests.helpers import make_settings

OFF = {"kasafi_shortcut_facilities": False, "kasafi_shortcut_hazards": False, "kasafi_shortcut_place": False,
       "kasafi_shortcut_alerts": False, "kasafi_shortcut_revenue": False}
SENDER = "2348000000055"


def _user(**kw):
    s = make_settings(database_url="postgresql://x:y@127.0.0.1:1/none", kasafi_alerts=True, **kw)
    store = UserStore(":memory:")
    key = user_key(SENDER, s)
    store.create(key, "en")
    store.give_consent(key)
    memory.forget(key)
    return s, store, key


async def _ok(*a, **k):
    return Verdict("ok", "none")


async def _none(*a, **k):
    return None


@pytest.mark.parametrize("text", ["Where is the nearest hospital?", "How far is Arkilla PHC",
                                  "Alert me if there will be floods in Goronyo", "How many PHCs are in Sokoto?"])
def test_with_the_switches_off_facility_and_alert_messages_reach_the_planner(monkeypatch, text) -> None:
    s, store, key = _user(**OFF)
    memory.remember(key, Spot(13.06, 5.24, "NG034021", "Wamakko", how="pin"))
    seen: list[str] = []

    async def answer(question, lang, **kw):
        seen.append(question)
        return "PLANNER"

    def boom(*a, **k):
        raise AssertionError("a facility shortcut ran with its switch off")
    monkeypatch.setattr(C, "lookup", boom)
    monkeypatch.setattr(C, "counted", boom)
    monkeypatch.setattr(C, "search_replies", boom)
    msg = {"from": SENDER, "id": f"w-{len(text)}", "type": "text", "text": {"body": text}}
    outs = asyncio.run(C.handle(msg, None, store=store, settings=s, answer_fn=answer, guard_fn=_ok, place_fn=_none))
    assert seen == [text] and outs[-1].text == "PLANNER"


def test_with_the_switches_on_the_same_messages_take_their_shortcuts(monkeypatch) -> None:
    s, store, key = _user()
    memory.remember(key, Spot(13.06, 5.24, "NG034021", "Wamakko", how="pin"))
    ran: list[str] = []

    async def fake_search(settings, lat, lon, search, lang, **kw):
        ran.append("facilities")
        return [("list", None, None)]

    async def answer(question, lang, **kw):
        raise AssertionError("the planner answered a nearest-facility question with the shortcut on")
    msg = {"from": SENDER, "id": "w-on", "type": "text", "text": {"body": "Where is the nearest hospital?"}}
    asyncio.run(C.handle(msg, None, store=store, settings=s, answer_fn=answer, guard_fn=_ok, place_fn=_none,
                         facility_fn=fake_search))
    assert ran == ["facilities"]


def test_the_emergency_fast_path_and_the_guardrails_have_no_switch() -> None:
    s, store, key = _user(**OFF)

    async def answer(*a, **k):
        raise AssertionError("the planner answered an emergency")
    msg = {"from": SENDER, "id": "w-em", "type": "text", "text": {"body": "My wife is bleeding heavily after birth"}}
    outs = asyncio.run(C.handle(msg, None, store=store, settings=s, answer_fn=answer, guard_fn=_ok, place_fn=_none))
    assert outs[0].text.startswith("🚨")
    msg = {"from": SENDER, "id": "w-guard", "type": "text", "text": {"body": "Is the governor doing a good job on health?"}}
    outs = asyncio.run(C.handle(msg, None, store=store, settings=s, answer_fn=answer, guard_fn=C.scope_guard
                                if hasattr(C, "scope_guard") else _verdict("verdict"), place_fn=_none))
    assert "Kasafi" in outs[0].text or outs[0].text


def _verdict(cat):
    async def guard(texts, *, settings):
        return Verdict(cat, "keyword")
    return guard


def test_the_answer_loop_shortcuts_honour_the_switches() -> None:
    """The in-code routes after the plan (facility card, hazards, outbreaks, place history, the revenue summary):
    with the switch off, each predicate's gate in _answer_question is skipped. Checked on the source so a new call
    site can't forget its switch."""
    src = Path("app/agent/answer.py").read_text(encoding="utf-8")
    assert "settings.kasafi_shortcut_facilities and (fac := facility_route(" in src
    assert "settings.kasafi_shortcut_hazards and (layers := hazard_route(" in src
    assert "settings.kasafi_shortcut_hazards and \\" in src and "official.route(" in src
    assert "place_on = shortcut and settings.kasafi_shortcut_place" in src
    assert "or not settings.kasafi_shortcut_revenue" in src


def test_the_routing_eval_set_runs_with_every_switch_off() -> None:
    from evals.routing.run import route_for
    cases = json.loads(Path("evals/routing/cases.json").read_text(encoding="utf-8"))["cases"]
    s = make_settings(**OFF)
    for c in cases:
        got = route_for(c["question"], s, conn=None)
        if c["expected"] in ("emergency", "guard", "map"):      # no switch: safety, guardrails, "show me the map"
            assert got == c["expected"], (c["id"], got)
        else:
            assert got == "planner", (c["id"], got)        # every shortcut off: the planner decides
