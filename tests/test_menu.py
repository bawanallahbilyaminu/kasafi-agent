"""The menu (an interactive list), the reply buttons under answers, the closing offer and the typing indicator
(app/whatsapp/menu.py, conversation.py, webhook.py, client.py): shortcuts into the same pipeline."""

import asyncio
import json
from types import SimpleNamespace

import httpx
import pytest

from app.agent import understand as U
from app.geo.location import Spot, memory
from app.guardrails.scope import Verdict
from app.users import UserStore, user_key
from app.whatsapp import conversation as C
from app.whatsapp import menu as M
from app.whatsapp import webhook as W
from app.whatsapp.client import WhatsAppClient
from tests.helpers import make_settings

SENDER = "2348000000088"
PIN = Spot(13.045, 5.155, "NG034021", "Wamakko", ward="Kalambaina", how="pin")


async def _ok(*a, **k):
    return Verdict("ok", "none")


async def _none(*a, **k):
    return None


def _user(lang="en", pin=False):
    s = make_settings(database_url="postgresql://x:y@127.0.0.1:1/none", kasafi_understanding=True)
    store = UserStore(":memory:")
    key = user_key(SENDER, s)
    store.create(key, lang)
    store.give_consent(key)
    memory.forget(key)
    C._last_reading.pop(key, None)
    if pin:
        memory.remember(key, PIN)
    return s, store, key


def _run(msg, s, store, answer=None, understand_fn=_none, **kw):
    async def default_answer(question, lang, **k):
        kw.setdefault("seen", []).append((question, k.get("understanding")))
        return SimpleNamespace(text="ANSWER", found=True, sources=[], working="", quotes="")
    return asyncio.run(C.handle(msg, None, store=store, settings=s, answer_fn=answer or default_answer, guard_fn=_ok,
                                place_fn=_none, understand_fn=understand_fn))


def _text(body):
    return {"from": SENDER, "id": f"w-{body[:10]}", "type": "text", "text": {"body": body}}


def _row(rid):
    return {"from": SENDER, "id": f"w-{rid}", "type": "interactive",
            "interactive": {"type": "list_reply", "list_reply": {"id": rid, "title": rid}}}


def _button(bid):
    return {"from": SENDER, "id": f"w-{bid}", "type": "interactive",
            "interactive": {"type": "button_reply", "button_reply": {"id": bid, "title": bid}}}


# --- payload limits ---------------------------------------------------------------------------------------------

@pytest.mark.parametrize("lang", ["en", "ha"])
def test_the_menu_and_the_buttons_are_within_whatsapps_limits(lang) -> None:
    p = M.menu_payload(lang)
    rows = [r for s in p["sections"] for r in s["rows"]]
    assert 1 <= len(rows) <= 10 and len(p["button"]) <= 20 and len(p["body"]) <= 4096
    assert all(len(r["title"]) <= 24 and len(r["description"]) <= 72 for r in rows)
    assert all(len(s["title"]) <= 24 for s in p["sections"])
    assert not any("alert" in r["id"] for r in rows)                # no alerts row while alerts are in dry run
    w = M.words(lang)
    assert all(len(b) <= 20 for b in w["buttons"].values())
    for combo in [(True, True, True, True), (False, False, False, False)]:
        bs = M.answer_buttons(lang, working=combo[0], brief=combo[1], other_lang=combo[2], needs_location=combo[3])
        assert 1 <= len(bs) <= 3 and all(len(t) <= 20 for _, t in bs)


def test_the_client_refuses_a_list_over_the_limits_and_sends_one_within_them() -> None:
    sent = []

    def handler(request: httpx.Request) -> httpx.Response:
        sent.append(json.loads(request.content))
        return httpx.Response(200, json={"messages": [{"id": "x"}]})
    s = make_settings(whatsapp_token="t", whatsapp_phone_number_id="1")
    client = WhatsAppClient(s, transport=httpx.MockTransport(handler))
    p = M.menu_payload("ha")
    asyncio.run(client.send_list("234", p["body"], p["button"], p["sections"]))
    assert sent[0]["interactive"]["type"] == "list" and len(sent[0]["interactive"]["action"]["sections"][0]["rows"]) == 8
    bad = [{"title": "x", "rows": [{"id": "a", "title": "x" * 25}]}]
    with pytest.raises(ValueError):
        asyncio.run(client.send_list("234", "b", "menu", bad))
    asyncio.run(client.mark_typing("wamid.1"))
    assert sent[-1] == {"messaging_product": "whatsapp", "status": "read", "message_id": "wamid.1",
                        "typing_indicator": {"type": "text"}}


# --- the menu --------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("lang,word", [("en", "menu"), ("ha", "zaɓi")])
def test_menu_read_as_kind_menu_sends_the_list_in_the_users_language(lang, word) -> None:
    s, store, key = _user(lang)

    async def reading(*a, **k):
        return U.Understanding(kind="menu", capability="conversation", restatement="Show me the menu")
    outs = _run(_text(word), s, store, understand_fn=reading)
    assert outs[0].menu and outs[0].text == M.words(lang)["body"]
    assert outs[0].menu["button"] == M.words(lang)["button"]


def test_with_no_reading_the_word_menu_alone_still_opens_it() -> None:
    s, store, key = _user("en")
    assert _run(_text("menu"), s, store)[0].menu


@pytest.mark.parametrize("row,capability", [("menu_budget", "place_budget"), ("menu_place", "place_history"),
                                            ("menu_outlook", "hazard")])
def test_a_place_row_with_a_recent_point_enters_the_pipeline_as_its_reading(row, capability, monkeypatch) -> None:
    s, store, key = _user("en", pin=True)
    monkeypatch.setattr(s.__class__, "has_database", property(lambda self: False))
    seen = []

    async def answer(question, lang, **k):
        seen.append((question, k.get("understanding")))
        return SimpleNamespace(text="ANSWER", found=True, sources=[], working="", quotes="")

    async def never(*a, **k):
        raise AssertionError("a row's reading needs no understanding call")
    outs = _run(_row(row), s, store, answer=answer, understand_fn=never)
    assert seen and seen[0][1].capability == capability and seen[0][0] == M.READINGS[row].restatement
    assert outs[-1].text.startswith("ANSWER")


@pytest.mark.parametrize("row", sorted(M.NEEDS_PLACE))
def test_a_place_row_with_no_recent_point_sends_the_location_request(row) -> None:
    s, store, key = _user("ha")
    outs = _run(_row(row), s, store)
    assert outs[0].location_request and outs[0].text == M.words("ha")["need_place"][row]
    waiting = memory.peek_question(key)
    assert waiting.startswith(C.FACILITY_WAIT if row == "menu_facility" else C.READING_WAIT)


def test_the_budget_row_then_the_pin_answers_with_the_rows_reading(monkeypatch) -> None:
    s, store, key = _user("en")
    seen = []

    async def answer(question, lang, **k):
        seen.append((question, k.get("understanding"), k.get("place")))
        return SimpleNamespace(text="BUDGET FOR WAMAKKO", found=True, sources=[], working="", quotes="")
    _run(_row("menu_budget"), s, store, answer=answer)

    async def locate(settings, lat, lon):
        return PIN
    pin = {"from": SENDER, "id": "w-pin", "type": "location", "location": {"latitude": 13.045, "longitude": 5.155}}
    outs = asyncio.run(C.handle(pin, None, store=store, settings=s, answer_fn=answer, guard_fn=_ok, place_fn=_none,
                                locate_fn=locate))
    assert seen and seen[0][1].capability == "place_budget" and seen[0][2]["lga_pcode"] == "NG034021"
    assert any(o.text.startswith("BUDGET FOR WAMAKKO") for o in outs)


@pytest.mark.parametrize("row", ["menu_docs", "menu_lang", "menu_privacy"])
def test_the_rows_with_replies_of_their_own(row) -> None:
    s, store, key = _user("en")
    out = _run(_row(row), s, store)[0]
    if row == "menu_lang":
        assert [b for b, _ in out.buttons] == ["lang_ha", "lang_en"]
    if row == "menu_privacy":
        assert "DELETE MY DATA" in out.text and "phone number" in out.text
    if row == "menu_docs":
        assert out.text.count("•") == 3


def test_the_about_row_is_the_conversational_reply(monkeypatch) -> None:
    s, store, key = _user("ha")
    import app.agent.conversational as CV

    async def reply(message, lang, history, place, settings, client_cls=None):
        return f"ABOUT {message}", "model"
    monkeypatch.setattr(CV, "reply", reply)
    assert _run(_row("menu_about"), s, store)[0].text == f"ABOUT {M.words('ha')['about']}"


# --- the buttons under answers --------------------------------------------------------------------------------

def test_buttons_under_an_answer_are_the_ones_that_apply(monkeypatch) -> None:
    s, store, key = _user("en")

    async def answer(question, lang, **k):
        return SimpleNamespace(text="ANSWER", found=True, sources=[], working="rows …", quotes="")

    async def reading(*a, **k):
        return U.Understanding(kind="new", capability="budget", restatement="How much is the health budget?")
    out = _run(_text("How much is the health budget?"), s, store, answer=answer, understand_fn=reading)[-1]
    assert [b for b, _ in out.buttons] == [M.BTN_WORKING]
    out = _run(_text("Nawa aka ware wa lafiya a 2026?"), s, store, understand_fn=reading)[-1]
    assert [b for b, _ in out.buttons] == [M.BTN_LANG]                 # asked in Hausa, answered in English
    out = _run(_text("What is the health budget for 2026?"), s, store, understand_fn=reading)[-1]
    assert [b for b, _ in out.buttons] == [M.BTN_MENU]                 # nothing else applies


def test_a_long_answer_is_never_cut_its_buttons_go_on_a_short_last_message() -> None:
    s, store, key = _user("en")
    long = "Figure line. " * 200

    async def answer(question, lang, **k):
        return SimpleNamespace(text=long, found=True, sources=[], working="w", quotes="")

    async def reading(*a, **k):
        return U.Understanding(kind="new", capability="budget", restatement="x")
    outs = _run(_text("How much is the health budget?"), s, store, answer=answer, understand_fn=reading)
    assert long.strip() in outs[0].text and not outs[0].buttons
    assert outs[-1].text == "Anything else?" and outs[-1].buttons


@pytest.mark.parametrize("button,expect", [(M.BTN_WORKING, "working"), (M.BTN_BRIEF, "brief"), (M.BTN_MENU, "menu")])
def test_each_button_runs_its_command(button, expect) -> None:
    s, store, key = _user("en")
    store.add_turn(key, "en", "q", "a", [], "the stored working", "")
    out = _run(_button(button), s, store)[0]
    if expect == "working":
        assert out.text == "the stored working"
    elif expect == "brief":
        assert out.text == C.BRIEF_WORDS["en"]["none"]
    else:
        assert out.menu


def test_the_language_button_switches_and_answers_the_same_question_again() -> None:
    s, store, key = _user("en")
    seen = []

    async def answer(question, lang, **k):
        seen.append((question, lang, k.get("understanding")))
        return SimpleNamespace(text=f"ANSWER {lang}", found=True, sources=[], working="", quotes="")

    async def reading(*a, **k):
        return U.Understanding(kind="new", capability="budget", restatement="How much is the 2026 health budget?")
    _run(_text("health budget 2026?"), s, store, answer=answer, understand_fn=reading)
    outs = _run(_button(M.BTN_LANG), s, store, answer=answer)
    assert store.get(key).lang == "ha" and seen[-1][:2] == ("How much is the 2026 health budget?", "ha")
    assert outs[0].text.startswith("ANSWER ha")


def test_the_location_button_asks_for_it_and_the_pin_answers_the_question_again(monkeypatch) -> None:
    s, store, key = _user("en")
    seen = []

    async def answer(question, lang, **k):
        seen.append((question, k.get("place")))
        return SimpleNamespace(text="ANSWER", found=True, sources=[], working="", quotes="")

    async def reading(*a, **k):
        return U.Understanding(kind="new", capability="hazard", level="lga", time="forecast", measure="rain",
                               restatement="Will it rain this week in my LGA?")
    out = _run(_text("will it rain this week?"), s, store, answer=answer, understand_fn=reading)[-1]
    assert M.BTN_LOCATION in [b for b, _ in out.buttons]
    out = _run(_button(M.BTN_LOCATION), s, store, answer=answer)[0]
    assert out.location_request and memory.peek_question(key).startswith(C.READING_WAIT)

    async def locate(settings, lat, lon):
        return PIN
    pin = {"from": SENDER, "id": "w-pin2", "type": "location", "location": {"latitude": 13.045, "longitude": 5.155}}
    asyncio.run(C.handle(pin, None, store=store, settings=s, answer_fn=answer, guard_fn=_ok, place_fn=_none,
                         locate_fn=locate))
    assert seen[-1][0] == "Will it rain this week in my LGA?" and seen[-1][1]["lat"] is not None


# --- the closing offer ----------------------------------------------------------------------------------------

def test_one_closing_offer_tied_to_the_answer_and_none_on_emergencies_or_refusals(monkeypatch) -> None:
    s, store, key = _user("en")

    async def reading(*a, **k):
        return U.Understanding(kind="new", capability="place_budget", level="lga", restatement="x")
    out = _run(_text("What does the budget give my area?"), s, store, understand_fn=reading)[0]
    assert out.text.endswith("Want the same for another year? Just name it.") and out.text.count("?") == 1
    assert M.closing_offer("en", U.Understanding(capability="budget"), "Shall I?") == ""   # already ends asking

    async def refuse(texts, settings):
        return Verdict("electoral", "keyword")
    outs = asyncio.run(C.handle(_text("Who is the best governor?"), None, store=store, settings=s,
                                guard_fn=refuse, place_fn=_none, understand_fn=reading,
                                answer_fn=lambda *a, **k: None))
    assert not any(o for o in M.words("en")["offers"].values() if o in outs[0].text)

    async def no_facilities(*a, **k):
        return []
    outs = asyncio.run(C.handle(_text("My son is not breathing, please help"), None, store=store, settings=s,
                                guard_fn=_ok, place_fn=_none, understand_fn=reading, emergency_fn=no_facilities))
    assert outs[0].text.startswith("🚨")
    assert not any(o in x.text for x in outs for o in M.words("en")["offers"].values())


# --- the typing indicator and the progress line -----------------------------------------------------------------

def test_a_failing_typing_indicator_never_blocks_or_delays_the_answer(monkeypatch) -> None:
    s, store, key = _user("en")

    class Slow:
        sent: list = []

        async def mark_typing(self, message_id):
            await asyncio.sleep(30)                 # longer than the whole answer
            raise RuntimeError("Graph down")

        async def send_text(self, to, body):
            Slow.sent.append(body)

        async def aclose(self):
            return None

    async def handle(msg, wa, **kw):
        return [C.Out("ANSWER", lang="en")]
    monkeypatch.setattr(W, "get_settings", lambda: s)
    monkeypatch.setattr(W, "get_store", lambda: store)
    monkeypatch.setattr(W, "WhatsAppClient", Slow)
    monkeypatch.setattr(W, "handle", handle)
    import time
    t0 = time.perf_counter()
    asyncio.run(W._reply([{"from": SENDER, "id": "wamid.typing1", "type": "text", "text": {"body": "hi"}}]))
    assert Slow.sent == ["ANSWER"] and time.perf_counter() - t0 < 2.0


def test_the_typing_indicator_is_only_for_consented_users() -> None:
    s, store, key = _user("en")

    class Client:
        async def mark_typing(self, message_id):
            return None

    async def run(msg):
        return W.start_typing(Client(), msg, store, s)
    assert asyncio.run(run({"from": SENDER, "id": "wamid.2"})) is not None
    assert asyncio.run(run({"from": "2348000000099", "id": "wamid.3"})) is None      # no consent yet


def test_a_quick_answer_sends_no_progress_line_and_a_slow_one_does(monkeypatch) -> None:
    s, store, key = _user("en")
    monkeypatch.setattr(C, "PROGRESS_AFTER_S", 0.2)
    notes = []

    async def notify(out):
        notes.append(out.text)

    async def quick(question, lang, **k):
        return SimpleNamespace(text="ANSWER", found=True, sources=[], working="", quotes="")

    async def slow(question, lang, **k):
        await asyncio.sleep(0.5)
        return SimpleNamespace(text="ANSWER", found=True, sources=[], working="", quotes="")
    msg = _text("How much is the 2026 health budget?")
    asyncio.run(C.handle(msg, None, store=store, settings=s, answer_fn=quick, guard_fn=_ok, place_fn=_none,
                         understand_fn=_none, notify=notify))
    assert notes == []
    asyncio.run(C.handle({**msg, "id": "w-slow"}, None, store=store, settings=s, answer_fn=slow, guard_fn=_ok,
                         place_fn=_none, understand_fn=_none, notify=notify))
    assert notes == ["🔎 Checking the documents…"]
