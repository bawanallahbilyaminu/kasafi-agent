"""Place history: the plot shape a farmer gives when SAM 3.1 can't draw one (app/place/shape.py): a size, or 3–6
corner pins; the WhatsApp flow that asks for it; the answer and map wording. No network."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import date

import pytest

from app.geo.location import Spot, memory
from app.place import answer as A
from app.place import shape as S
from app.place.outline import Outline, fallback
from app.users import UserStore, user_key
from app.whatsapp.conversation import SIZE_WAIT, handle
from tests.helpers import make_settings
from tests.test_place_answer import TODAY, _history

LAT, LON = 13.1095, 5.2115


@pytest.mark.parametrize("text,asked,want", [
    ("3 acres", False, 1.21), ("2 ha", False, 2.0), ("hekta 2", False, 2.0), ("kadada 3", False, 1.21),
    ("about 2.5 hectares", False, 2.5), ("1/2 acre", False, 0.2), ("5", True, 5.0), ("5", False, None),
    ("eka 4", False, 1.62), ("it is big", True, None), ("0 ha", False, None), ("9000 ha", False, None),
])
def test_a_farm_size_in_words_is_read_as_hectares(text, asked, want) -> None:
    assert S.parse_area_ha(text, asked=asked) == want


def test_corner_pins_make_a_plot_in_any_order_and_bad_ones_are_refused() -> None:
    square = [(13.0, 5.0), (13.0, 5.002), (13.002, 5.002), (13.002, 5.0)]
    geom, ha, note = S.corners_polygon(square)
    assert geom and note == "" and 4.7 < ha < 5.0
    shuffled = [square[0], square[2], square[1], square[3]]                 # a bow tie if joined as sent
    geom2, ha2, _ = S.corners_polygon(shuffled)
    assert geom2 == geom and ha2 == ha
    assert S.corners_polygon(square[:2])[2] == "too_few"
    assert S.corners_polygon(square + [(13.001, 5.001)] * 3)[2] == "too_many"
    assert S.corners_polygon([(13.0, 5.0), (13.0, 5.0001), (13.0001, 5.00005)])[2] == "too_small"
    assert S.corners_polygon([(13.0, 5.0), (13.0, 5.01), (13.01, 5.01), (13.01, 5.0)])[2] == "too_big"
    assert S.corners_polygon([(13.0, 5.0), (13.0, 5.02), (13.0001, 5.02), (13.0001, 5.0)])[2] == "too_thin"
    shape = S.shape_from_corners(square)
    assert shape["method"] == "corners" and shape["corners"] == 4
    lat, lon = S.centroid(shape["geometry"])
    assert abs(lat - 13.001) < 1e-6 and abs(lon - 5.001) < 1e-6


def test_a_size_gives_a_circle_of_that_area() -> None:
    import math
    from shapely.geometry import shape
    s = S.shape_from_size(LAT, LON, 2.0)
    assert s["method"] == "given_circle" and s["area_ha"] == 2.0
    ring = s["geometry"]["coordinates"][0]
    area = shape(s["geometry"]).area * (111_320.0 ** 2) * math.cos(math.radians(LAT)) / 10_000.0
    assert 1.9 < area < 2.1 and len(ring) == 49


def test_the_answer_says_which_shape_was_used() -> None:
    sam = Outline({"type": "Polygon", "coordinates": [[]]}, "sam", 5.1)
    given = Outline.from_shape(S.shape_from_size(LAT, LON, 2.0))
    corners = Outline.from_shape({"geometry": {"type": "Polygon", "coordinates": [[]]}, "method": "corners",
                                  "area_ha": 3.4, "corners": 4})
    assert A.outline_line(sam, "en").startswith("Plot outline: about 5.1 ha, drawn from the satellite image")
    assert A.outline_line(given, "en") == ("Plot shape: the circle of 2 ha you gave, around your pin (no outline could "
                                           "be drawn from the satellite image).")
    assert A.outline_line(corners, "en") == "Plot shape: about 3.4 ha, from your 4 corner pins: approximate, not a boundary."
    assert A.outline_line(fallback(LON, LAT, "too_big"), "en").startswith("No plot outline could be drawn")
    assert "da'irar hekta 2 da ka bayar" in A.outline_line(given, "ha")
    assert "kusurwoyi 4" in A.outline_line(corners, "ha")
    assert given.is_plot and corners.is_plot and not fallback(LON, LAT, "x").is_plot


def test_the_map_legend_names_the_shape() -> None:
    from app.place.images import T, _shape_words
    given = Outline.from_shape(S.shape_from_size(LAT, LON, 1.5))
    assert _shape_words(T["en"], given, "leg") == "Circle of 1.5 ha around your pin (the size you gave)"
    assert _shape_words(T["ha"], given, "how") == "da'irar hekta 1.5 da ka bayar"
    assert _shape_words(T["en"], None, "leg").startswith("Circle of about 1 ha")


def test_place_answer_asks_for_the_size_only_when_told_to_and_uses_a_given_shape(monkeypatch) -> None:
    from app.place.floods import FloodEvidence

    async def no_outline(conn, settings, lat, lon, **kw):
        return fallback(lon, lat, "too_big")
    seen: dict = {}

    def history(conn, lat, lon, *, today, polygon=None, water=False, **kw):
        seen["polygon"] = polygon
        return _history()
    monkeypatch.setattr(A, "plot_outline", no_outline)
    monkeypatch.setattr(A.H, "point_history", history)
    monkeypatch.setattr(A, "flood_evidence", lambda *a, **k: FloodEvidence())
    place = {"lat": LAT, "lon": LON, "lga": "Wamakko", "lga_pcode": "NG034021"}
    pa = asyncio.run(A.place_answer(None, None, "how green was my farm in 2024?", "", "en", place, TODAY, ask_size=True))
    assert pa.needs_size and not pa.found and pa.text.startswith("I couldn't draw this farm's outline")
    pa = asyncio.run(A.place_answer(None, None, "how green was my farm in 2024?", "", "en", place, TODAY))
    assert pa.found and not pa.needs_size and "circle of about 1 ha" in pa.text and seen["polygon"] is None
    place["shape"] = {"declined": True}
    pa = asyncio.run(A.place_answer(None, None, "how green was my farm in 2024?", "", "en", place, TODAY, ask_size=True))
    assert pa.found and "circle of about 1 ha" in pa.text
    place["shape"] = S.shape_from_size(LAT, LON, 3.0)
    pa = asyncio.run(A.place_answer(None, None, "yaya koriyar gonata a 2024?", "", "ha", place, TODAY, ask_size=True))
    assert pa.found and "da'irar hekta 3 da ka bayar" in pa.text and seen["polygon"] == place["shape"]["geometry"]
    assert pa.specs[1]["shape"]["method"] == "given_circle"           # the map draws the same shape


# --- the WhatsApp flow -------------------------------------------------------------------------------------------

@dataclass
class FakeAnswer:
    text: str
    found: bool = True
    needs_size: bool = False
    sources: list = field(default_factory=list)
    working: str = ""
    quotes: str = ""


def _pin(lat, lon, sender="2348000000002"):
    return {"from": sender, "id": "wamid.x", "type": "location", "location": {"latitude": lat, "longitude": lon}}


def _text(body, sender="2348000000002"):
    return {"from": sender, "id": "wamid.t", "type": "text", "text": {"body": body}}


async def located(settings, lat, lon):
    from app.geo import Area
    return Area("NG034021", "Wamakko", "Gumbi", "62109")


def _flow():
    """A consented user with a farm pin in memory, and an answer function that asks for the size when the place
    carries no shape; the calls record the place each answer saw."""
    s, store = make_settings(), UserStore(":memory:")
    key = user_key("2348000000002", s)
    store.create(key, "en")
    store.give_consent(key)
    memory.forget(key)
    memory.remember(key, Spot(LAT, LON, "NG034021", "Wamakko", "Gumbi", how="pin"))
    calls: list[dict | None] = []

    async def answer(question, lang, *, settings, notify=None, history=None, place=None):
        calls.append(place)
        if place and place.get("ask_size") and not place.get("shape"):
            return FakeAnswer(A.W["en"]["ask_size"], False, needs_size=True)
        shape = (place or {}).get("shape") or {}
        return FakeAnswer(f"ANSWER {shape.get('method', 'none')} {shape.get('area_ha', '')}")

    def run(msg):
        return asyncio.run(handle(msg, None, store=store, settings=s, locate_fn=located, answer_fn=answer))
    return key, calls, run


def test_a_size_in_words_answers_the_waiting_question_with_that_circle() -> None:
    key, calls, run = _flow()
    out = run(_text("How green was my farm in 2024?"))
    assert len(out) == 1 and out[0].text.startswith("I couldn't draw this farm's outline") and not out[0].location_request
    assert memory.peek_question(key) == SIZE_WAIT + "How green was my farm in 2024?"
    out = run(_text("3 acres"))
    assert out[0].text == "Got it: a circle of 1.21 ha around your pin." and out[-1].text.startswith("ANSWER given_circle 1.21")
    assert calls[-1]["shape"]["method"] == "given_circle" and memory.peek_question(key) is None
    out = run(_text("Was it flooded in 2022?"))                   # the shape is kept for the next question
    assert out[-1].text.startswith("ANSWER given_circle 1.21")
    memory.forget(key)


def test_corner_pins_after_the_question_make_the_plot_and_move_the_point() -> None:
    key, calls, run = _flow()
    run(_text("Yaya koriyar gonata?"))
    assert memory.peek_question(key).startswith(SIZE_WAIT)
    out = run(_pin(13.0, 5.0))
    assert out == [out[0]] and out[0].text == "📍 Corner pin 1 received. Send the others (3 to 6 in all), then say *done*."
    out = run(_text("done"))
    assert out[0].text.startswith("I have 1 corner pin(s); a plot needs at least 3")
    run(_pin(13.0, 5.002))
    run(_pin(13.002, 5.002))
    out = run(_pin(13.002, 5.0))
    assert out[0].text.startswith("📍 Corner pin 4 received")
    out = run(_text("Done"))
    assert out[0].text == "Got it: a plot of about 4.8 ha from your 4 corner pins." and out[-1].text.startswith("ANSWER corners 4.8")
    assert calls[-1]["shape"]["corners"] == 4 and abs(calls[-1]["lat"] - 13.001) < 1e-6 and calls[-1]["lga"] == "Wamakko"
    assert memory.recent_pins(key) == [] and memory.peek_question(key) is None
    memory.forget(key)


def test_skip_answers_with_the_one_hectare_circle_and_is_not_asked_again() -> None:
    key, calls, run = _flow()
    run(_text("How green was my farm in 2024?"))
    out = run(_text("skip"))
    assert out[-1].text == "ANSWER none " and calls[-1]["shape"] == {"declined": True}
    out = run(_text("How green was my farm in 2023?"))
    assert out[-1].text == "ANSWER none " and len(calls) == 3
    memory.forget(key)


def test_a_bad_shape_is_refused_and_another_message_drops_the_wait() -> None:
    key, calls, run = _flow()
    run(_text("How green was my farm in 2024?"))
    for lat, lon in [(13.0, 5.0), (13.0, 5.0001), (13.0001, 5.00005)]:
        run(_pin(lat, lon))
    out = run(_text("an gama"))
    assert out[0].text.startswith("Those 3 pins don't make a sensible plot (under 0.1 ha)")
    assert memory.peek_question(key).startswith(SIZE_WAIT)        # still waiting: a size can follow
    out = run(_text("2 1/2"))
    assert out[0].text.startswith("I didn't catch a size")
    out = run(_text("What is the budget for roads?"))             # something else: answered normally, wait dropped
    assert memory.peek_question(key) is None and calls[-1]["shape"] == {"declined": True}
    memory.forget(key)


def test_corners_said_without_being_asked_use_the_recent_pins() -> None:
    key, calls, run = _flow()
    memory.forget(key)
    for lat, lon in [(13.0, 5.0), (13.0, 5.002), (13.002, 5.002), (13.002, 5.0)]:
        out = run(_pin(lat, lon))
    assert out[-1].text.startswith("📍 Got it: you're in Wamakko LGA")
    out = run(_text("These are the corners of my farm"))
    assert out[0].text == ("Got it: a plot of about 4.8 ha from your 4 corner pins. Ask me about it, for example "
                           "«How green was my farm in 2024?».")
    out = run(_text("How green was my farm in 2024?"))
    assert out[-1].text.startswith("ANSWER corners 4.8") and calls[-1]["shape"]["corners"] == 4
    memory.forget(key)


def test_no_coordinates_or_shapes_are_persisted_or_logged(tmp_path, caplog) -> None:
    """Privacy: a corner-pin conversation leaves no coordinate in the user store, the logs or the memory's repr."""
    import logging
    import sqlite3
    s = make_settings()
    db = tmp_path / "kasafi.db"
    store = UserStore(str(db))
    key = user_key("2348000000003", s)
    store.create(key, "en")
    store.give_consent(key)
    memory.forget(key)
    calls: list = []

    async def answer(question, lang, *, settings, notify=None, history=None, place=None):
        calls.append(place)
        return FakeAnswer("ANSWER")
    caplog.set_level(logging.DEBUG)
    for lat, lon in [(13.0589127, 5.1673341), (13.0589127, 5.1693341), (13.0609127, 5.1693341), (13.0609127, 5.1673341)]:
        asyncio.run(handle(_pin(lat, lon, "2348000000003"), None, store=store, settings=s, locate_fn=located, answer_fn=answer))
    asyncio.run(handle(_text("these are the corners", "2348000000003"), None, store=store, settings=s, locate_fn=located,
                       answer_fn=answer))
    asyncio.run(handle(_text("How green was my farm in 2024?", "2348000000003"), None, store=store, settings=s,
                       locate_fn=located, answer_fn=answer))
    assert calls and calls[-1]["shape"]["method"] == "corners"
    blob = " ".join(str(v) for row in sqlite3.connect(db).execute("SELECT * FROM users").fetchall() for v in row)
    for needle in ("13.05", "13.06", "5.167", "5.169", "corners", "Polygon"):
        assert needle not in blob and needle not in caplog.text
    assert "13.05" not in repr(memory.recall(key)) and "Wamakko" in repr(memory.recall(key))
    memory.forget(key)


def test_memory_forgets_shapes_and_pins_with_the_rest() -> None:
    from app.geo.location import LocationMemory
    m = LocationMemory(ttl_s=0.01, corner_ttl_s=0.01)
    m.remember_shape("k", {"method": "given_circle"})
    assert m.add_pin("k", 13.0, 5.0) == 1 and m.add_pin("k", 13.0, 5.0) == 1 and m.shape("k")["method"] == "given_circle"
    import time
    time.sleep(0.02)
    assert m.shape("k") is None and m.recent_pins("k") == []
    m.remember_shape("k", {"method": "corners"})
    m.forget("k")
    assert m.shape("k") is None


def test_a_place_question_is_never_turned_into_a_clarifying_question() -> None:
    """The planner once replied 'Where is your farm?' to a pinned question (speed eval, 1 Nov): the place path
    asks for the pin itself, so a planner clarify never pre-empts it."""
    from app.agent.answer import place_question
    assert place_question("How green was my farm in 2024?")
    assert place_question("Which wards of Wurno LGA were greenest in 2024?")
    assert not place_question("What is the 2026 budget for the Ministry of Agriculture?")
    assert not place_question("How many IDPs are in Gada LGA?")
