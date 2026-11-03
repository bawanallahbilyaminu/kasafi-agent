"""A location that arrives for something waiting (3 Nov, live: menu → 'Rain and flood outlook' → pin got 'What would
you like to know about it?' and the outlook only 17 s later): the acknowledgement says the place and what is coming,
then the waiting request is answered with that pin. Only a pin with nothing waiting (or a wait older than 30
minutes) asks what the user would like to know."""

import asyncio
import time
from types import SimpleNamespace

import pytest

from app.geo.location import Spot, memory
from app.users import UserStore, user_key
from app.whatsapp import conversation as C
from app.whatsapp import menu as M
from app.whatsapp.messages import COMING
from tests.helpers import make_settings
from tests.test_menu import SENDER, _ok, _none, _row, _text

PIN = Spot(13.045, 5.155, "NG034021", "Wamakko", ward="Bado", ward_likely=True, how="pin", wardcode="62102")
ASK = {"en": "What would you like to know", "ha": "Me kuke so ku sani"}


def _user(lang):
    s = make_settings(database_url="postgresql://x:y@127.0.0.1:1/none", kasafi_understanding=True)
    store = UserStore(":memory:")
    key = user_key(SENDER, s)
    store.create(key, lang)
    store.give_consent(key)
    memory.forget(key)
    C._last_reading.pop(key, None)
    return s, store, key


async def _locate(settings, lat, lon):
    return PIN


async def _facilities(settings, lat, lon, search, lang, mode="list"):
    return [("FACILITIES NEAR YOU", None)]


def _pin(s, store, answer, n=1):
    msg = {"from": SENDER, "id": f"w-pin-{n}-{time.time()}", "type": "location",
           "location": {"latitude": 13.045, "longitude": 5.155}}
    return asyncio.run(C.handle(msg, None, store=store, settings=s, answer_fn=answer, guard_fn=_ok, place_fn=_none,
                                locate_fn=_locate, facility_fn=_facilities))


def _recorder(seen):
    async def answer(question, lang, **k):
        seen.append((question, k.get("understanding"), k.get("place")))
        if not (k.get("place") or {}).get("lat"):                    # a place question with no pin: the pin first
            return SimpleNamespace(text="Send your location", found=False, sources=[], working="", quotes="",
                                   needs_pin=True)
        return SimpleNamespace(text="THE ANSWER", found=True, sources=[], working="", quotes="")
    return answer


@pytest.mark.parametrize("lang", ["en", "ha"])
@pytest.mark.parametrize("row,coming", [("menu_outlook", "outlook"), ("menu_budget", "budget"),
                                        ("menu_place", "satellite"), ("menu_facility", "facility")])
def test_each_place_row_then_the_pin_says_whats_coming_and_answers_without_asking(row, coming, lang, monkeypatch) -> None:
    s, store, key = _user(lang)
    seen = []
    answer = _recorder(seen)
    if row == "menu_facility":
        async def reading(r, u, key, lang, settings, facility_fn, spot):
            return [C.Out("FACILITIES NEAR YOU")]
        monkeypatch.setattr(C, "_facility_reading", reading)
    asyncio.run(C.handle(_row(row), None, store=store, settings=s, answer_fn=answer, guard_fn=_ok, place_fn=_none))
    outs = _pin(s, store, answer)
    texts = [o.text for o in outs if o.text]
    ack = next(x for x in texts if x.startswith("📍"))
    assert ASK[lang] not in ack and COMING[lang][coming] in ack
    assert ("Bado" in ack and "Wamakko" in ack)
    if lang == "en":
        assert ack == f"📍 Got it: Wamakko LGA (likely Bado ward). {COMING['en'][coming]}"
    assert any(x.startswith(("THE ANSWER", "FACILITIES NEAR YOU")) for x in texts)
    assert texts.index(ack) < next(i for i, x in enumerate(texts) if x.startswith(("THE ANSWER", "FACILITIES")))
    if row != "menu_facility":
        assert seen[-1][0] == M.READINGS[row].restatement and seen[-1][2]["lat"] is not None


def test_a_typed_question_that_needed_a_place_is_answered_when_the_pin_comes() -> None:
    s, store, key = _user("en")
    seen = []
    answer = _recorder(seen)
    first = asyncio.run(C.handle(_text("Has my farm ever flooded?"), None, store=store, settings=s, answer_fn=answer,
                                 guard_fn=_ok, place_fn=_none, understand_fn=_none))
    assert first[-1].location_request
    outs = _pin(s, store, answer, 2)
    texts = [o.text for o in outs if o.text and not o.text.startswith("Kasafi will use your location")]  # the notice
    assert texts[0] == f"📍 Got it: Wamakko LGA (likely Bado ward). {COMING['en']['satellite']}"
    assert any(x.startswith("THE ANSWER") for x in texts) and seen[-1][0] == "Has my farm ever flooded?"


@pytest.mark.parametrize("lang", ["en", "ha"])
def test_a_bare_pin_with_nothing_waiting_asks_what_they_would_like_to_know(lang) -> None:
    s, store, key = _user(lang)
    seen = []
    outs = _pin(s, store, _recorder(seen), 3)
    ack = next(o.text for o in outs if o.text.startswith("📍"))
    assert ASK[lang] in ack and not seen


def test_a_wait_older_than_30_minutes_is_dropped_and_the_pin_asks(monkeypatch) -> None:
    s, store, key = _user("en")
    seen = []
    asyncio.run(C.handle(_row("menu_outlook"), None, store=store, settings=s, answer_fn=_recorder(seen), guard_fn=_ok,
                         place_fn=_none))
    q, at = memory._needs[key]
    memory._needs[key] = (q, at - 31 * 60)                    # the row was tapped 31 minutes ago
    outs = _pin(s, store, _recorder(seen), 4)
    ack = next(o.text for o in outs if o.text.startswith("📍"))
    assert ASK["en"] in ack and not seen


def test_a_slow_resumed_answer_sends_no_second_checking_line(monkeypatch) -> None:
    """The acknowledgement already says 'Checking the rainfall and flood outlook…': no '🌦️ Checking the latest
    forecasts…' after it (3 Nov smoke)."""
    s, store, key = _user("en")
    monkeypatch.setattr(C, "PROGRESS_AFTER_S", 0.2)
    notes = []

    async def notify(out):
        notes.append(out.text)

    async def slow(question, lang, **k):
        await asyncio.sleep(0.5)
        return SimpleNamespace(text="THE ANSWER", found=True, sources=[], working="", quotes="")
    asyncio.run(C.handle(_row("menu_outlook"), None, store=store, settings=s, answer_fn=slow, guard_fn=_ok,
                         place_fn=_none))
    msg = {"from": SENDER, "id": "w-pin-slow", "type": "location", "location": {"latitude": 13.045, "longitude": 5.155}}
    asyncio.run(C.handle(msg, None, store=store, settings=s, answer_fn=slow, guard_fn=_ok, place_fn=_none,
                         locate_fn=_locate, facility_fn=_facilities, notify=notify))
    checking = [n for n in notes if n.startswith(("🌦️", "🔎", "🛰️"))]
    assert checking == [] and any(n.startswith("📍 Got it") for n in notes)
