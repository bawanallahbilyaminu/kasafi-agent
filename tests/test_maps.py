"""Maps (docs/hazard-and-services.md section 8): rendered on our base layer, under WhatsApp's size limit, captions
that repeat the key numbers, Hausa labels, the user's point rounded, hazard maps cached per hour, and the rules for
when an answer sends one."""

import asyncio
import io
from datetime import date, datetime, timezone

import psycopg
import pytest
from PIL import Image

from app.agent.answer import maps_for
from app.config import get_settings
from app.geo.facilities import Facility
from app.hazards import read
from app.hazards.answer import HazardAnswer
from app.maps import render
from app.whatsapp.conversation import MAP_ONLY

DAY = date(2026, 10, 31)


def _conn():
    s = get_settings()
    try:
        conn = psycopg.connect(s.db_url(), connect_timeout=3)
    except (psycopg.OperationalError, RuntimeError):
        pytest.skip("database not running")
    if not conn.execute("SELECT count(*) FROM lga").fetchone()[0]:
        pytest.skip("no LGAs imported")
    return conn


def _jpeg(b: bytes) -> Image.Image:
    img = Image.open(io.BytesIO(b))
    assert img.format == "JPEG" and len(b) <= render.MAX_BYTES and img.width >= 800
    return img


def test_the_ramps_name_every_category() -> None:
    assert len(render.HEAT) == len(render.HEAT_COLORS) and len(render.AIR) == len(render.AIR_COLORS)
    assert len(render.RAIN) == len(render.RAIN_COLORS) and len(render.RIVER) == len(render.RIVER_COLORS)


def test_a_hazard_map_by_lga_with_its_numbers_in_the_caption(monkeypatch) -> None:
    with _conn() as conn:
        names = [r[0] for r in conn.execute("SELECT name FROM lga").fetchall()]
        values = {n: ("extreme_caution", 36.0, "36 °C") for n in names} | {names[0]: ("danger", 41.0, "41 °C")}
        monkeypatch.setattr(render, "lga_values", lambda conn, layer, day: values)
        render._cache.clear()
        m = render.hazard_map(conn, "heat", DAY, "en", "NG034021", today=DAY)
        _jpeg(m.jpeg)
        assert m.caption.startswith(f"Heat today: highest in {names[0]}, 41 °C (Danger).")
        assert "Danger: 1 LGAs; Extreme caution: 22 LGAs." in m.caption
        assert render.hazard_map(conn, "heat", DAY, "en", "NG034021", today=DAY) is m       # cached this hour
        ha = render.hazard_map(conn, "heat", DAY, "ha", "", today=DAY)
        assert ha is not m and "Haɗari" in ha.caption and "ƙananan hukumomi" in ha.caption
        monkeypatch.setattr(render, "lga_values", lambda conn, layer, day: {})
        render._cache.clear()
        assert render.hazard_map(conn, "rain", DAY, "en") is None                       # no data: no map


def test_the_near_you_map_rounds_the_point_and_is_never_cached() -> None:
    assert render.approx(13.0589127, 5.1673341) == (13.06, 5.17)
    f = Facility("x", "Kware General Hospital", "Secondary", "General Hospital", "Public", "", 13.2, 5.27, "Kware",
                 "Kware", 4.2)
    with _conn() as conn:
        render._cache.clear()
        m = render.near_you_map(conn, 13.0589127, 5.1673341, "Wamakko", [f], [(5.17, 13.06), (5.27, 13.2)], "ha",
                                "1. Kware General Hospital")
        _jpeg(m.jpeg)
        assert m.caption == "1. Kware General Hospital" and not render._cache


def test_river_labels_never_overlap() -> None:
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(8.6, 9.4))
    ax.set_xlim(4.5, 6.0)
    ax.set_ylim(12.9, 13.6)
    render._place_labels(ax, [(4.725, 13.075, "Sokoto-Rima toward the Kebbi border\n7.7 m³/s, low"),
                              (5.175, 13.075, "Sokoto River at Sokoto city\n5.2 m³/s, low"),
                              (5.425, 13.325, "Rima near Wurno\n2.4 m³/s, low")])
    fig.canvas.draw()
    boxes = [t.get_window_extent() for t in ax.texts]
    assert len(boxes) == 3
    assert not any(a.overlaps(b) for i, a in enumerate(boxes) for b in boxes[i + 1:])
    plt.close(fig)


def _ha(kind, layers, pcode=""):
    return HazardAnswer("t", layers, read.Where(kind, pcode, "Goronyo" if pcode else ""), True)


def test_when_an_answer_sends_a_map() -> None:
    today = DAY
    assert maps_for("How hot is it in Sokoto today?", _ha("state", ["heat"]), today) == \
        [{"kind": "hazard", "layer": "heat", "day": "2026-10-31", "highlight": ""}]
    assert maps_for("How hot is it in Goronyo today?", _ha("lga", ["heat"], "NG034006"), today) == []
    assert maps_for("Show me a map of the heat in Goronyo", _ha("lga", ["heat"], "NG034006"), today) == \
        [{"kind": "hazard", "layer": "heat", "day": "2026-10-31", "highlight": "NG034006"}]
    assert maps_for("Is the river high near Goronyo?", _ha("lga", ["flood"], "NG034006"), today) == \
        [{"kind": "river", "day": "2026-10-31"}]
    assert maps_for("What should we watch out for?", _ha("state", ["air", "fires", "heat", "flood", "rain"]),
                    today) == [{"kind": "hazard", "layer": "air", "day": "2026-10-31", "highlight": ""}]
    assert maps_for("Will it rain tomorrow?", _ha("state", ["rain"]), today)[0]["day"] == "2026-11-01"


@pytest.mark.parametrize("text, want", [("show me a map", True), ("Map?", True), ("nuna min taswira", True),
                                        ("taswira", True), ("Show me the map of Goronyo budget", False),
                                        ("How hot is it?", False)])
def test_show_me_a_map(text, want) -> None:
    assert bool(MAP_ONLY.match(text)) is want


def test_an_answers_maps_follow_its_text_unless_images_are_off(monkeypatch) -> None:
    from app.agent.answer import Answer
    from app.users import UserStore, user_key
    from app.whatsapp import conversation as conv
    from tests.helpers import make_settings
    s = make_settings(database_url="postgresql://x:y@127.0.0.1:1/none")
    store = UserStore(":memory:")
    key = user_key("2348000000077", s)
    store.create(key, "en")
    store.give_consent(key)
    drawn = []

    def fake_render(settings, specs, lang, today=None):
        drawn.append(specs)
        return [render.MapImage(b"\xff\xd8jpeg", "Heat today: highest in Illela, 38 °C (Extreme caution).")]
    monkeypatch.setattr(conv, "render_specs", fake_render)

    async def answer(question, lang, **kw):
        return Answer("text", True, True, maps=[{"kind": "hazard", "layer": "heat", "day": "2026-10-31"}])
    msg = {"from": "2348000000077", "id": "w", "type": "text", "text": {"body": "How hot is it in Sokoto today?"}}

    async def guard(texts, settings=None):
        from app.guardrails.scope import Verdict
        return Verdict("ok", "none")
    outs = asyncio.run(conv.handle(msg, None, store=store, settings=s, answer_fn=answer, guard_fn=guard))
    assert outs[-1].image == b"\xff\xd8jpeg" and outs[-1].text.startswith("Heat today") and drawn
    store.set_images(key, False)
    outs = asyncio.run(conv.handle(msg, None, store=store, settings=s, answer_fn=answer, guard_fn=guard))
    assert not any(o.image for o in outs)
