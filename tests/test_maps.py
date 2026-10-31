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


# --- Oct 31 review: values on the map, shading within a category, AQI colours, a readable near-you map --------

@pytest.mark.parametrize("layer,order,colors", [("heat", render.HEAT, render.HEAT_COLORS),
                                                ("air", render.AIR, render.AIR_COLORS),
                                                ("rain", render.RAIN, render.RAIN_COLORS)])
def test_every_fill_is_exactly_a_legend_colour(layer, order, colors) -> None:
    values = {f"L{i}": (order[i % len(order)], 30.0 + i * 0.7, "") for i in range(23)}
    fill = render.fills(layer, values)
    assert set(fill.values()) <= set(colors)                               # no shades the legend doesn't have
    assert fill["L0"] == colors[0] and fill["L1"] == colors[1]
    one = render.fills(layer, {f"L{i}": (order[1], 30.0 + i, "") for i in range(23)})
    assert set(one.values()) == {colors[1]}                                # one category: one colour, numbers differ


def test_air_uses_the_standard_aqi_colours_green_to_maroon() -> None:
    assert dict(zip(render.AIR, render.AIR_COLORS)) == {
        "good": "#00e400", "moderate": "#ffff00", "unhealthy_sensitive": "#ff7e00", "unhealthy": "#ff0000",
        "very_unhealthy": "#8f3f97", "hazardous": "#7e0023"}
    usg, unhealthy = render._rgb("#ff7e00"), render._rgb("#ff0000")
    assert abs(usg[1] - unhealthy[1]) > 0.4                                # clearly distinct neighbours


def test_values_print_short_on_the_map() -> None:
    assert render.short_value("heat", 37.4) == "37°" and render.short_value("air", 181.6) == "182"
    assert render.short_value("rain", 2.36) == "2.4"


def test_text_is_readable_on_a_phone() -> None:
    px = lambda p: p * render.DPI / 72                                     # noqa: E731
    assert px(render.TITLE) >= 28 and px(render.LABEL) >= 20 and px(render.LEGEND) >= 20


def test_the_near_you_frame_fits_the_circle_and_facilities_at_least_2_km_across() -> None:
    f = Facility("x", "A", "Primary", "", "Public", "", 13.0605, 5.1705, "Wamakko", "Wamakko", 0.1)
    cx, cy, side = render.frame((13.06, 5.17), [f])
    assert render.MIN_SIDE <= side < 0.03 and abs(cx - 5.17) < 0.01        # the ~1 km circle with padding
    far = Facility("y", "B", "Primary", "", "Public", "", 13.2, 5.4, "Kware", "Kware", 25.0)
    cx, cy, side = render.frame((13.06, 5.17), [f, far])
    assert cx - side / 2 < 5.17 - render.YOU_RADIUS and cx + side / 2 > 5.4 and cy + side / 2 > 13.2


def test_markers_never_overlap_each_other_or_the_users_circle() -> None:
    import math
    pts = [(5.17, 13.06), (5.1702, 13.0601), (5.1704, 13.0599)]
    out = render.spread_markers(pts, 0.004, [(5.169, 13.059, 0.005)])
    assert all(math.hypot(a[0] - b[0], a[1] - b[1]) >= 0.004 for i, a in enumerate(out) for b in out[i + 1:])
    assert all(math.hypot(x - 5.169, y - 13.059) >= 0.005 for x, y in out)
    assert render.spread_markers([(5.0, 13.0), (5.5, 13.5)], 0.01) == [(5.0, 13.0), (5.5, 13.5)]   # apart: unmoved


@pytest.mark.parametrize("name,vague", [("Bone Centre", True), ("General Hospital", True),
                                        ("Goronyo General Hospital", False), ("Arkilla Primary Health Center", False),
                                        ("Specialist Hospital", True)])
def test_vague_names_get_their_town(name, vague) -> None:
    assert render.vague(name) is vague


def test_the_legend_gives_road_distance_and_time() -> None:
    f = Facility("x", "Goronyo General Hospital", "Secondary", "", "Public", "", 13.44, 5.67, "Goronyo", "Goronyo",
                 0.8, road_km=10.9, minutes=15)
    assert render.distance_words(f, "en") == "10.9 km, about 15 min"
    assert render.distance_words(f, "ha") == "kilomita 10.9, kusan minti 15"
    f.road_km = f.minutes = None
    assert render.distance_words(f, "en") == "about 0.8 km (straight line)"


def test_the_river_title_names_the_time_of_year() -> None:
    assert render.river_title("en", date(2026, 10, 31), date(2026, 10, 31)) == \
        "River levels today vs. normal for late October"
    assert render.river_title("ha", date(2026, 11, 5), date(2026, 11, 5)).endswith("a farkon Nuwamba")


def test_an_old_fetch_is_marked_on_the_map(monkeypatch) -> None:
    at = datetime(2026, 10, 30, 18, 35, tzinfo=timezone.utc)
    monkeypatch.setattr(read, "freshness", lambda conn, layer, now=None: read.Freshness(layer, at, True, 17.0))
    assert render._fetched(None, "forecast", at, "en") == " · fetched 30 Oct 19:35 (older than usual)"
    monkeypatch.setattr(read, "freshness", lambda conn, layer, now=None: read.Freshness(layer, at, False, 1.0))
    assert render._fetched(None, "forecast", at, "en") == " · fetched 30 Oct 19:35"


def test_the_near_you_map_renders_with_towns_scale_and_legend() -> None:
    fs = [Facility("x", "Kware General Hospital", "Secondary", "General Hospital", "Public", "", 13.2, 5.27, "Kware",
                   "Kware", 4.2, road_km=18.2, minutes=24),
          Facility("y", "Bone Centre", "Secondary", "", "Public", "", 13.2005, 5.2702, "Kware", "Kware", 4.3)]
    with _conn() as conn:
        m = render.near_you_map(conn, 13.0589127, 5.1673341, "Wamakko", fs, None, "en", "x")
        _jpeg(m.jpeg)


def test_one_map_per_answer_and_not_the_same_one_twice() -> None:
    from app.whatsapp import conversation as conv
    conv._maps_sent.clear()
    outs = [conv.Out("list"), conv.Out("", image=b"map-a"), conv.Out("", image=b"map-b"), conv.Out("", location={})]
    first = conv.one_map("u1", outs)
    assert [o.image for o in first if o.image] == [b"map-a"] and len(first) == 3
    again = conv.one_map("u1", [conv.Out("list"), conv.Out("", image=b"map-a")])
    assert not any(o.image for o in again)                                 # the same map again: text only
    assert any(o.image for o in conv.one_map("u2", [conv.Out("", image=b"map-a")]))   # another user: sent


def test_far_facilities_are_in_the_legend_only() -> None:
    near = Facility("a", "Goronyo General Hospital", "Secondary", "", "Public", "", 13.44, 5.67, "Goronyo", "Goronyo",
                    0.9)
    far1 = Facility("b", "Wurno General Hospital", "Secondary", "", "Public", "", 13.29, 5.42, "Wurno", "Wurno", 30.2)
    mid = Facility("c", "Kagara PHC", "Primary", "", "Public", "", 13.5, 5.7, "Goronyo", "Goronyo", 7.0)
    assert render.on_map([near, far1, mid]) == [True, False, True]
    assert render.on_map([far1, near]) == [True, True]                     # the first is always drawn
    cx, cy, side = render.frame((13.44, 5.67), [near])
    assert side < 0.03                                                    # zoomed to the user and the nearest


def test_towns_use_the_official_lga_spelling() -> None:
    from app.sources.lga_names import canonical
    assert canonical("Salame") == "Silame" and canonical("Tambawal") == "Tambuwal" and canonical("Achida") == ""


def test_the_near_you_map_with_a_far_facility_renders() -> None:
    fs = [Facility("x", "Goronyo General Hospital", "Secondary", "", "Public", "", 13.441, 5.672, "Goronyo",
                   "Goronyo", 0.9, road_km=1.2, minutes=3),
          Facility("y", "Wurno General Hospital", "Secondary", "", "Public", "", 13.29, 5.42, "Wurno", "Wurno", 30.2)]
    with _conn() as conn:
        _jpeg(render.near_you_map(conn, 13.44, 5.67, "Goronyo", fs, None, "ha", "x").jpeg)
