"""Every long job ends in an answer or an apology, never silence (the 1 Nov live failure: the satellite answer was
computed, then the reply crashed before sending and the maps failed on a missing 'day'); one progress line per
request."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field

from app.geo.location import Spot, memory
from app.place import answer as A
from app.users import UserStore, user_key
from app.whatsapp import conversation as C
from app.whatsapp.conversation import SIZE_WAIT, handle
from tests.helpers import make_settings

LAT, LON = 13.1095, 5.2115
SENDER = "2348000000004"


@dataclass
class FakeAnswer:
    text: str
    found: bool = True
    needs_size: bool = False
    sources: list = field(default_factory=list)
    working: str = ""
    quotes: str = ""


def _text(body):
    return {"from": SENDER, "id": "wamid.t", "type": "text", "text": {"body": body}}


async def located(settings, lat, lon):
    from app.geo import Area
    return Area("NG034021", "Wamakko", "Gumbi", "62109")


async def no_place(settings, text):
    return None


class NoFacilities:
    async def __call__(self, *a, **k):
        return []


def _user(s):
    store = UserStore(":memory:")
    key = user_key(SENDER, s)
    store.create(key, "en")
    store.give_consent(key)
    memory.forget(key)
    memory.remember(key, Spot(LAT, LON, "NG034021", "Wamakko", "Gumbi", how="pin"))
    return store, key


def _run(msg, store, s, answer, notified):
    async def notify(out):
        notified.append(out.text)
    return asyncio.run(handle(msg, None, store=store, settings=s, locate_fn=located, answer_fn=answer, notify=notify,
                              place_fn=no_place, facility_fn=NoFacilities()))


def test_skip_then_the_answer_is_sent_even_when_the_facility_check_runs() -> None:
    """The live crash: with a database configured the facility check's walrus set `outs` to None and the resumed
    answer died on `None + list`; the user got the progress line and then silence."""
    s = make_settings(database_url="postgresql://x:y@127.0.0.1:1/none")      # has_database; never connected
    store, key = _user(s)
    notified: list[str] = []

    async def answer(question, lang, *, settings, notify=None, history=None, place=None):
        if place and place.get("ask_size") and not place.get("shape"):
            return FakeAnswer(A.W["en"]["ask_size"], False, needs_size=True)
        await notify("🛰️ I'm checking about 10 years of satellite images for this spot.")
        return FakeAnswer("ANSWER")
    out = _run(_text("How green was my farm in 2024?"), store, s, answer, notified)
    assert out[0].text.startswith("I couldn't draw this farm's outline") and memory.peek_question(key).startswith(SIZE_WAIT)
    out = _run(_text("Skip"), store, s, answer, notified)
    assert [o.text for o in out] == ["ANSWER"]
    assert notified == ["🛰️ I'm checking about 10 years of satellite images for this spot."]   # one progress line
    memory.forget(key)


def test_a_place_question_sends_no_generic_progress_line_and_others_still_do(monkeypatch) -> None:
    monkeypatch.setattr(C, "PROGRESS_AFTER_S", 0.0)          # every answer counts as slow here
    s = make_settings()
    store, key = _user(s)
    notified: list[str] = []

    async def answer(question, lang, *, settings, notify=None, history=None, place=None):
        await asyncio.sleep(0.05)
        return FakeAnswer("ANSWER")
    _run(_text("How green was my farm in 2024?"), store, s, answer, notified)
    assert notified == []
    _run(_text("What is the 2026 budget for agriculture?"), store, s, answer, notified)
    assert len(notified) == 1 and "document" in notified[0].lower()
    memory.forget(key)


def test_a_job_over_the_limit_gets_the_apology_and_a_failure_note(monkeypatch) -> None:
    s = make_settings(kasafi_answer_timeout_s=0.05)
    store, key = _user(s)
    notified: list[str] = []
    noted: list = []

    async def slow(question, lang, *, settings, notify=None, history=None, place=None):
        await asyncio.sleep(0.5)
        return FakeAnswer("TOO LATE")

    async def note(settings, question, lang, reason, seconds, apology):
        noted.append((question, reason, apology))
    import app.whatsapp.conversation as C
    monkeypatch.setattr(C, "_note_failure", note)
    out = _run(_text("How green was my farm in 2024?"), store, s, slow, notified)
    assert [o.text for o in out] == ["Sorry, I couldn't finish checking the satellite images.\n\nPlease try again in a few minutes."]
    assert noted and noted[0][1].startswith("satellite: timeout after") and noted[0][0] == "How green was my farm in 2024?"
    out = _run(_text("What is the 2026 budget for agriculture?"), store, s, slow, notified)
    assert out[-1].text == "Sorry, I couldn't finish the answer in time.\n\nPlease try again in a few minutes."

    async def boom(question, lang, *, settings, notify=None, history=None, place=None):
        raise RuntimeError("Planetary Computer refused")
    out = _run(_text("Shin ruwa ya taɓa rufe gonata a shekarun baya?"), store, make_settings(), boom, notified)
    assert out[-1].text.startswith("Sorry, I couldn't finish checking the satellite images.")   # the user's language is en
    assert noted[-1][1] == "satellite: RuntimeError: Planetary Computer refused"
    memory.forget(key)


def test_place_specs_are_drawn_without_a_day(monkeypatch) -> None:
    from app.maps import render
    import app.place.images as images
    seen = []
    monkeypatch.setattr(images, "draw_place", lambda conn, s, lang, today: seen.append(s["kind"]) or "IMG")
    monkeypatch.setattr(images, "area_map", lambda conn, s, lang, today: "AREA")
    assert render.draw(None, {"kind": "place_chart", "lat": LAT, "lon": LON, "lga": "Wamakko"}, "ha") == "IMG"
    assert render.draw(None, {"kind": "place_map", "lat": LAT, "lon": LON, "lga": "Wamakko"}, "ha") == "IMG"
    assert render.draw(None, {"kind": "area_map", "measure": "modis_peak", "key": "greenness", "year": 2024,
                              "level": "ward", "unit": "NG034022"}, "en") == "AREA"
    assert seen == ["place_chart", "place_map"]


def test_the_failure_trace_row_is_written_with_the_reason(monkeypatch) -> None:
    from app.agent import trace
    rows = []

    class Conn:
        def execute(self, sql, args=None):
            rows.append(args)
        def commit(self):
            pass
        def __enter__(self):
            return self
        def __exit__(self, *a):
            return False
    import psycopg
    monkeypatch.setattr(psycopg, "connect", lambda *a, **k: Conn())
    trace.save_failure(make_settings(database_url="postgresql://x:y@h/d"), "How green was my farm?", "en",
                       "timeout after 120s", 120.4, "Sorry …")
    assert rows and rows[0][2] == "failed" and '"failure": "timeout after 120s"' in rows[0][5] and rows[0][4] == 120.4


# --- follow-up review (1 Nov), finding 5: the checked text goes first; maps follow under their own deadline -------

def test_the_text_goes_before_a_stalled_map_and_the_map_has_its_own_deadline(monkeypatch) -> None:
    import time as _time

    from app.whatsapp import conversation as C
    from tests.helpers import make_settings
    s = make_settings(database_url="postgresql://x:y@127.0.0.1:1/none", kasafi_answer_timeout_s=5)
    store = UserStore(":memory:")
    key = user_key("2348000000088", s)
    store.create(key, "en")
    store.give_consent(key)
    memory.forget(key)
    sent: list[tuple[float, str]] = []
    t0 = _time.perf_counter()

    class Reply:
        text = "ANSWER"
        maps = [{"kind": "synthetic"}]

    async def answer(*a, **k):
        return Reply()

    async def notify(out):
        sent.append((_time.perf_counter() - t0, out.text))

    def stalled_map(*a, **k):
        _time.sleep(0.6)
        return []

    async def none(*a, **k):
        return None
    monkeypatch.setattr(C, "render_specs", stalled_map)
    monkeypatch.setattr(C, "MAP_DEADLINE_S", 0.1)
    monkeypatch.setattr(C, "_facilities", none)
    msg = {"from": "2348000000088", "id": "w-map", "type": "text", "text": {"body": "What is the agriculture budget in 2026?"}}
    took = {}

    async def run():
        out = await C.handle(msg, None, store=store, settings=s, answer_fn=answer, guard_fn=_ok_guard,
                             place_fn=none, notify=notify)
        took["handle"] = _time.perf_counter() - t0                # the turn's last send is ready here
        return out
    outs = asyncio.run(run())                                     # (asyncio.run then waits for the abandoned thread)
    answered = [at for at, text in sent if text == "ANSWER"]
    assert answered and answered[0] < 0.1                         # the text went before the map was tried
    assert outs[0].text == "ANSWER" and outs[-2].text.startswith("(The map")   # the note, at the map's deadline
    assert outs[-1].text == "Anything else?" and outs[-1].buttons               # the buttons come last
    assert took["handle"] < 0.4                                   # the stalled map (0.6 s) never held the turn


def test_a_timed_out_answer_can_never_send_afterwards(monkeypatch) -> None:
    from app.whatsapp import conversation as C
    from tests.helpers import make_settings
    s = make_settings(kasafi_answer_timeout_s=0.1)
    store = UserStore(":memory:")
    key = user_key("2348000000089", s)
    store.create(key, "en")
    store.give_consent(key)
    memory.forget(key)
    sent: list[str] = []
    late: list = []

    async def answer(question, lang, *, settings, notify=None, history=None, place=None):
        async def finish_later():                 # a task the answer started, outliving its cancellation
            await asyncio.sleep(0.2)
            await notify("FINAL ANSWER (late)")
        late.append(asyncio.create_task(finish_later()))
        await asyncio.sleep(5)

    async def notify(out):
        sent.append(out.text)

    async def run():
        msg = {"from": "2348000000089", "id": "w-late", "type": "text", "text": {"body": "What is the 2026 health budget?"}}
        outs = await C.handle(msg, None, store=store, settings=s, answer_fn=answer, guard_fn=_ok_guard, notify=notify)
        await asyncio.sleep(0.3)                  # the late task runs to the end
        return outs
    outs = asyncio.run(run())
    assert "couldn't" in outs[-1].text.lower() or "sorry" in outs[-1].text.lower() or "yi haƙuri" in outs[-1].text.lower()
    assert "FINAL ANSWER (late)" not in sent and late and late[0].done()


async def _ok_guard(*a, **k):
    from app.guardrails.scope import Verdict
    return Verdict("ok", "none")
