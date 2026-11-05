"""A new pin on a busy evening (live traces 682, 683, 5 Nov 2026). On-demand reading worked, but 3-6% of Planetary
Computer's image requests answered 504 after 15 s, now and then one hung or came back unreadable, and one such request
among ~400 failed the whole job, lost everything fetched and told the user to try again. A 504 was also taken as 'no
data', so a thinner year went into the cache. Now: requests go again, a job waits out a busy service and goes on from what
it has, the turn stays open until the answer is ready, and the reply never says 'try again'."""

from __future__ import annotations

import asyncio
import json
from datetime import date
from types import SimpleNamespace

import httpx
import pytest

from app.geo.location import Spot, memory
from app.place import answer as A
from app.place import floods as F
from app.place import history as H
from app.place import radar as R
from app.place import rain, stac
from app.place.floods import FloodEvidence
from app.place.history import Scene, YearRow
from app.place.outline import fallback
from app.users import UserStore, user_key
from app.whatsapp import conversation as C
from app.whatsapp.messages import TEXTS as MESSAGES
from tests.helpers import make_settings

LAT, LON = 13.1095, 5.2115
SENDER = "2348000000077"
TODAY = date(2026, 11, 5)


@pytest.fixture(autouse=True)
def no_waits(monkeypatch):
    monkeypatch.setattr(stac, "TRY_WAITS_S", (0.0, 0.0, 0.0))
    monkeypatch.setattr(stac, "ROUND_WAITS_S", (0.0, 0.0))
    H.forget_plots()
    yield
    H.forget_plots()


def _response(status: int = 200, body: bytes = b"{}") -> httpx.Response:
    return httpx.Response(status, content=body, request=httpx.Request("GET", "https://example.test/?latitude=13.1&longitude=5.2"))


# --- one request ------------------------------------------------------------------------------------------------------

def test_an_unreadable_reply_is_tried_again_the_failure_in_trace_682() -> None:
    replies = [_response(200, b""), _response(504, b"upstream request timeout"), _response(200, b'{"features": [1]}')]
    assert stac.read_json(lambda: replies.pop(0)) == {"features": [1]}
    assert not replies


def test_a_read_that_hangs_is_tried_again_the_failure_in_trace_683() -> None:
    calls = []

    def send():
        calls.append(1)
        if len(calls) == 1:
            raise httpx.ReadTimeout("The read operation timed out")
        return _response(200, b"[]")
    assert stac.read_json(send) == []


def test_after_three_tries_it_is_busy_and_the_message_never_holds_the_pin() -> None:
    with pytest.raises(stac.Busy) as busy:
        stac.read_json(lambda: _response(200, b"<html>"))
    assert "13.1" not in str(busy.value)
    with pytest.raises(stac.Busy) as busy:
        stac.read_json(lambda: _response(503))
    assert str(busy.value) == "HTTP 503"


def test_a_refusal_is_not_tried_again_and_its_message_never_holds_the_pin() -> None:
    calls = []

    def send():
        calls.append(1)
        return _response(400, b"bad")
    with pytest.raises(stac.Refused) as refused:
        stac.read_json(send)
    assert len(calls) == 1 and str(refused.value) == "HTTP 400"


def test_the_rain_archive_goes_through_the_same_door(monkeypatch) -> None:
    replies = [_response(200, b""), _response(200, json.dumps({"daily": {"time": ["2024-07-01"], "precipitation_sum": [3.0]}}).encode())]

    class Client:
        def __init__(self, *a, **k):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def get(self, *a, **k):
            return replies.pop(0)
    monkeypatch.setattr(rain.httpx, "Client", Client)
    assert rain.daily_rain(LAT, LON, date(2024, 7, 1), date(2024, 7, 1)) == {"2024-07-01": 3.0}


# --- a scene's window -------------------------------------------------------------------------------------------------

class WindowClient:
    def __init__(self, status: int) -> None:
        self.status = status

    def get(self, *a, **k):
        return _response(self.status, b"upstream request timeout")


SCENE = Scene("S2A_X", date(2024, 7, 1), 5.0, "05.00")


def test_a_504_on_a_window_is_busy_not_no_data() -> None:
    for status in (429, 500, 502, 503, 504):
        with pytest.raises(stac.Busy):
            H.fetch_window(WindowClient(status), SCENE, (5.0, 13.0, 5.1, 13.1), (4, 4), ["B04"])
    assert H.fetch_window(WindowClient(404), SCENE, (5.0, 13.0, 5.1, 13.1), (4, 4), ["B04"]) is None   # no data stays no data


def test_what_failed_goes_again_with_fewer_side_by_side() -> None:
    seen: dict[int, int] = {}

    def fn(i: int) -> int:
        seen[i] = seen.get(i, 0) + 1
        if i % 3 == 0 and seen[i] == 1:
            raise httpx.ReadTimeout("slow")
        return i * 10
    got, failed = stac.each(fn, list(range(30)), 6)
    assert failed == [] and got == {i: i * 10 for i in range(30)}
    assert seen[0] == 2 and seen[1] == 1


def test_a_service_that_fails_nearly_everything_is_not_asked_the_rest() -> None:
    asked = []

    def fn(i: int):
        asked.append(i)
        raise stac.Busy("HTTP 504")
    got, failed = stac.each(fn, list(range(400)), 2)
    assert not got and len(failed) == 400 and len(asked) < 60


def test_a_withdrawn_job_stops_asking() -> None:
    asked = []
    until = stac.Until(100.0)
    until.stop()
    token = stac.time_limit.set(until)
    try:
        got, failed = stac.each(lambda i: asked.append(i), [1, 2, 3], 2)
    finally:
        stac.time_limit.reset(token)
    assert not got and failed == [0, 1, 2] and not asked


# --- a year ----------------------------------------------------------------------------------------------------------

def _scenes(n: int, year: int = 2024) -> list[Scene]:
    return [Scene(f"s{i}", date(year, 6, 1 + i % 28), 1.0, "05.00") for i in range(n)]


def _fake_read(monkeypatch, scenes: list[Scene], unread: set[str]) -> list[str]:
    asked: list[str] = []

    def observe(client, s, geom, bbox, shape):
        asked.append(s.id)
        if s.id in unread:
            raise stac.Busy("HTTP 504")
        return H.Observation(s.day, ndvi=0.5, ndwi=-0.2, clear=1.0)
    monkeypatch.setattr(H, "scenes", lambda *a, **k: scenes)
    monkeypatch.setattr(H, "observe", observe)
    return asked


def test_a_few_scenes_unread_mark_the_year_and_a_job_goes_on(monkeypatch) -> None:
    _fake_read(monkeypatch, _scenes(40), {"s3"})
    rows = H.compute_years(LAT, LON, H.cell_circle(LAT, LON), [2024], workers=4)
    assert rows[2024].lost == 1 and rows[2024].season_obs > 0


def test_too_many_scenes_unread_is_busy_so_the_job_waits(monkeypatch) -> None:
    _fake_read(monkeypatch, _scenes(40), {f"s{i}" for i in range(5)})
    with pytest.raises(stac.Busy):
        H.compute_years(LAT, LON, H.cell_circle(LAT, LON), [2024], workers=4)


class Saved:
    """A connection that keeps sat_cache rows."""

    def __init__(self) -> None:
        self.rows: list[tuple] = []

    def execute(self, sql, args=None):
        if sql.lstrip().startswith("INSERT"):
            self.rows.append(args)
        return SimpleNamespace(fetchall=lambda: [])

    def commit(self):
        pass


def _no_context(monkeypatch) -> None:
    monkeypatch.setattr(H.rain, "daily_rain", lambda *a, **k: {})
    monkeypatch.setattr(H, "jrc_summary", lambda *a, **k: {})
    monkeypatch.setattr(H, "landcover", lambda *a, **k: "cropland")


def test_a_year_with_scenes_unread_is_never_cached_but_serves_the_chart_of_this_answer(monkeypatch) -> None:
    """Before, a 504 counted as 'no data': the year went into the cache with fewer images, for good."""
    _no_context(monkeypatch)
    asked = _fake_read(monkeypatch, _scenes(40), {"s3"})
    conn = Saved()
    h = H._point_history(conn, LAT, LON, today=TODAY)
    assert h.timing["scenes_unread"] == 1.0
    saved = {(r[1], r[2]) for r in conn.rows}
    assert ("s2", 2024) not in saved and ("s2", 2023) in saved
    n = len(asked)
    again = H._point_history(conn, LAT, LON, today=TODAY)   # the chart and the map read the same record, not a new one
    assert len(asked) == n and again.years[2024].season_obs == h.years[2024].season_obs


def test_a_radar_year_with_passes_unread_is_not_cached(monkeypatch) -> None:
    items = [{"id": f"p{i}", "properties": {"datetime": f"2024-08-{1 + i:02d}T10:00:00Z"}} for i in range(25)]
    monkeypatch.setattr(R, "passes", lambda *a, **k: items)

    def read_pass(client, item_id, geom, bbox, shape):
        if item_id == "p3":
            raise stac.Busy("HTTP 504")
        return -8.0
    monkeypatch.setattr(R, "read_pass", read_pass)
    monkeypatch.setattr(R, "dry_reference", lambda *a, **k: R.Reference(-8.0, 5, "2025–2026"))
    conn = Saved()
    rows, _ = F.radar_history(conn, LAT, LON, H.cell_circle(LAT, LON), today=TODAY, years=[2024], workers=4)
    assert rows[2024].lost == 1 and rows[2024].passes == 24
    assert not [r for r in conn.rows if r[1] == "s1"]


# --- the job -----------------------------------------------------------------------------------------------------------

def _history() -> H.History:
    return H.History("c", LAT, LON, {2024: YearRow(2024)}, timing={"sentinel2": 90.0, "total": 90.0})


def _place(monkeypatch, history) -> None:
    async def outline(conn, settings, lat, lon, today=None):
        return fallback(lon, lat, "no_segment")
    monkeypatch.setattr(A, "plot_outline", outline)
    monkeypatch.setattr(A.H, "point_history", history)
    monkeypatch.setattr(A, "flood_evidence", lambda *a, **k: FloodEvidence())
    monkeypatch.setattr(A, "first_request", lambda *a, **k: True)
    monkeypatch.setattr(A, "PATIENT_WAITS_S", (0.01, 0.01))


def test_a_busy_service_is_waited_out_the_user_is_told_once_and_the_answer_comes(monkeypatch) -> None:
    tries: list[int] = []

    def history(*a, **k):
        tries.append(1)
        if len(tries) < 3:
            raise stac.Busy("120 of 398 scenes unread")
        return _history()
    _place(monkeypatch, history)
    lines: list[str] = []

    async def notify(text):
        lines.append(text)
    pa = asyncio.run(A.place_answer(None, None, "my farm", "", "en", {"lat": LAT, "lon": LON, "lga": "Wamakko"}, TODAY,
                                    notify=notify))
    assert pa.found and len(tries) == 3
    assert sum("isn't answering" in x for x in lines) == 1 and sum("years of satellite" in x for x in lines) == 1
    assert pa.timing["sentinel2"] == 90.0
    assert not any("try again" in x.lower().replace("trying again", "") for x in lines)


def test_a_service_down_for_the_whole_time_ends_the_job(monkeypatch) -> None:
    def history(*a, **k):
        raise httpx.ReadTimeout("slow")
    _place(monkeypatch, history)
    monkeypatch.setattr(A, "SATELLITE_JOB_S", 0.03)
    with pytest.raises(A.SatelliteUnavailable):
        asyncio.run(A.place_answer(None, None, "my farm", "", "en", {"lat": LAT, "lon": LON, "lga": "Wamakko"}, TODAY))


def test_a_fault_waiting_cannot_cure_is_not_waited_on(monkeypatch) -> None:
    calls: list[int] = []

    def history(*a, **k):
        calls.append(1)
        raise KeyError("a bug")
    _place(monkeypatch, history)
    with pytest.raises(KeyError):
        asyncio.run(A.place_answer(None, None, "my farm", "", "en", {"lat": LAT, "lon": LON}, TODAY))
    assert len(calls) == 1


def test_the_job_never_outlasts_the_time_a_location_may_be_held() -> None:
    from app.geo.location import TTL_S
    assert A.SATELLITE_JOB_S == TTL_S


# --- the loop's budget --------------------------------------------------------------------------------------------------

def test_a_satellite_turn_is_not_held_to_the_165_second_budget(monkeypatch) -> None:
    from app.agent import answer as ANS

    async def slow(question, lang, conn, box=None, **kw):
        await asyncio.sleep(0.15)
        return ANS.Answer("THE RECORD", True, True)
    monkeypatch.setattr(ANS, "_answer_question", slow)
    monkeypatch.setattr(ANS, "LOOP_BUDGET_S", 0.05)
    a = asyncio.run(ANS._answer_finished("How green was my farm in 2024?", "en", None))
    assert a.text == "THE RECORD"
    b = asyncio.run(ANS._answer_finished("What is the 2026 budget for agriculture?", "en", None))
    assert b.text == ANS.TIMED_OUT["en"]                      # other turns keep their limit


def test_past_the_satellite_budget_the_turn_says_unavailable_not_timed_out(monkeypatch) -> None:
    from app.agent import answer as ANS

    async def slow(question, lang, conn, box=None, **kw):
        await asyncio.sleep(1.0)
    monkeypatch.setattr(ANS, "_answer_question", slow)
    monkeypatch.setattr(ANS, "SATELLITE_JOB_S", -119.95)
    with pytest.raises(A.SatelliteUnavailable):
        asyncio.run(ANS._answer_finished("How green was my farm in 2024?", "en", None))


# --- the turn ------------------------------------------------------------------------------------------------------------

def _user(s):
    store = UserStore(":memory:")
    key = user_key(SENDER, s)
    store.create(key, "en")
    store.give_consent(key)
    memory.forget(key)
    memory.remember(key, Spot(LAT, LON, "NG034021", "Wamakko", "Gumbi", how="pin"))
    return store, key


async def _no_place(settings, text):
    return None


class _NoFacilities:
    async def __call__(self, *a, **k):
        return []


def _msg(body: str = "How green was my farm in 2024?", id_: str = "w-sat") -> dict:
    return {"from": SENDER, "id": id_, "type": "text", "text": {"body": body}}


def _turn(answer, s, store, notified):
    async def notify(out):
        notified.append(out.text)
    return C.handle(_msg(), None, store=store, settings=s, answer_fn=answer, notify=notify, place_fn=_no_place,
                    facility_fn=_NoFacilities())


def test_a_slow_job_keeps_the_turn_open_with_progress_lines_and_sends_the_answer(monkeypatch) -> None:
    s = make_settings(kasafi_answer_timeout_s=0.05)
    store, key = _user(s)
    monkeypatch.setattr(C, "SATELLITE_LINES_AT_S", (0.05, 0.1, 10.0, 20.0))
    notified: list[str] = []

    async def answer(question, lang, *, settings, notify=None, history=None, place=None):
        await asyncio.sleep(0.25)
        return SimpleNamespace(text="THE RECORD", found=True, sources=[], working="", quotes="")
    outs = asyncio.run(_turn(answer, s, store, notified))
    assert outs[0].text == "THE RECORD"
    assert notified[:2] == C.SATELLITE_WORDS["en"][:2]
    assert store.recent_turns(key)[-1]["answer"] == "THE RECORD"
    memory.forget(key)


def test_a_job_that_gives_up_says_so_without_try_again_and_is_noted(monkeypatch) -> None:
    s = make_settings()
    store, key = _user(s)
    noted: list[str] = []

    async def note(settings, question, lang, reason, seconds, apology):
        noted.append(reason)
    monkeypatch.setattr(C, "_note_failure", note)

    async def answer(question, lang, *, settings, notify=None, history=None, place=None):
        raise A.SatelliteUnavailable("Busy: HTTP 504")
    outs = asyncio.run(_turn(answer, s, store, []))
    assert outs[0].text == MESSAGES["satellite_gave_up"]["en"] and "try again" not in outs[0].text.lower()
    assert noted[0].startswith("satellite: unavailable after") and "HTTP 504" in noted[0]
    memory.forget(key)


def test_no_satellite_reply_tells_the_user_to_try_again() -> None:
    for name in ("satellite_failed", "satellite_gave_up"):
        assert "try again" not in MESSAGES[name]["en"].lower() and "sake gwadawa" not in MESSAGES[name]["ha"].lower()
    for lang in ("en", "ha"):
        for line in C.SATELLITE_WORDS[lang] + [A.W[lang]["progress"]]:
            assert "try again" not in line.lower() and "sake gwadawa" not in line.lower()
    assert "minutes" in A.W["en"]["progress"] and "1–2" not in A.W["en"]["progress"]


def test_delete_my_data_stops_a_job_holding_the_location(monkeypatch) -> None:
    s = make_settings(kasafi_answer_timeout_s=0.05)
    store, key = _user(s)
    notified: list[str] = []
    cancelled: list[bool] = []

    async def answer(question, lang, *, settings, notify=None, history=None, place=None):
        try:
            await asyncio.sleep(5)
        except asyncio.CancelledError:
            cancelled.append(True)
            raise
        return SimpleNamespace(text="NEVER SENT", found=True, sources=[], working="", quotes="")

    async def scenario():
        turn = asyncio.create_task(_turn(answer, s, store, notified))
        await asyncio.sleep(0.1)
        assert _running(key)
        C.withdraw_satellite(key)
        return await turn
    outs = asyncio.run(scenario())
    assert outs == [] and cancelled and not store.recent_turns(key)
    memory.forget(key)


def _running(key: str) -> bool:
    return bool(C._satellite_jobs.get(key))


def test_delete_my_data_reaches_the_withdrawal(monkeypatch) -> None:
    s = make_settings()
    store, key = _user(s)
    called: list[str] = []
    monkeypatch.setattr(C, "withdraw_satellite", called.append)
    monkeypatch.setattr(C, "delete_user_data", lambda *a, **k: None)
    asyncio.run(C.handle(_msg("DELETE MY DATA", "w-del"), None, store=store, settings=s))
    assert called == [key]
    memory.forget(key)


def test_the_typing_indicator_lasts_as_long_as_the_longest_turn() -> None:
    from app.whatsapp.webhook import TYPING_MOST_S
    assert TYPING_MOST_S > A.SATELLITE_JOB_S + 240.0


def test_a_failure_says_where_in_our_code() -> None:
    try:
        H.bbox_of(None)
    except Exception as e:     # noqa: BLE001
        assert C._failed_at(e).startswith(" (at app/place/history.py:")
    try:
        raise RuntimeError("here")
    except RuntimeError as e:
        assert C._failed_at(e) == ""
