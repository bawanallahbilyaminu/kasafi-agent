"""Place history step 2: the route, the farmer summary written in code, the outline rule, the guardrails and the
two images (no network: histories are built by hand)."""

from __future__ import annotations

import io
import json
from datetime import date

import numpy as np
import pytest
from PIL import Image

from app.guardrails.scope import keyword_check
from app.place import answer as A
from app.place.fit import rain_fit
from app.place.history import History, YearRow, cell_id

TODAY = date(2026, 10, 31)


def _history(kind=None, landcover="cropland", water_months=None, nearest=None, years=range(2016, 2027), thin=()):
    rows = {}
    rain = {2016: 572, 2017: 408, 2018: 373, 2019: 344, 2020: 451, 2021: 172, 2022: 540, 2023: 341, 2024: 575,
            2025: 435, 2026: 297}
    ndvi = {2016: 0.49, 2017: 0.505, 2018: 0.498, 2019: 0.535, 2020: 0.638, 2021: 0.532, 2022: 0.529, 2023: 0.495,
            2024: 0.561, 2025: 0.531, 2026: 0.488}
    for y in years:
        rows[y] = YearRow(y, season_obs=5 if y in thin else 12, ndvi_p90=ndvi[y], water_obs=4, water_share=0.0,
                          water_months=(water_months or {}).get(y, []), dry_obs=10, bsi_dry=0.25,
                          rain_season_mm=float(rain[y]), rain_year_mm=float(rain[y]) + 40, rain_days=153)
    h = History(cell_id(13.1095, 5.2115), 13.1095, 5.2115, rows, landcover=landcover, kind=kind,
                jrc={"occurrence": 0.0, "recurrence": 0.0, "seasonality": 0.0}, nearest_water=nearest)
    usable = h.usable_years()
    if h.vegetated:
        h.fit = rain_fit({y: (rows[y].ndvi_p90, rows[y].rain_season_mm) for y in usable})
        h.trends["greenness"] = ("no clear change", 0.007)
        h.trends["bare_soil"] = ("no clear change", 0.002)
    return h


# --- the route and the guardrails ------------------------------------------------------------------------------

@pytest.mark.parametrize("q", [
    "How green was my farm in 2024?", "Yaya koriyar gonata ta kasance a 2024?", "Has my plot been flooded in past years?",
    "Shin ruwa ya taɓa rufe gonata a shekarun baya?", "tarihin wuri", "Is bare soil spreading on my land since 2019?",
    "What does the satellite show for this pond over the years?",
])
def test_place_questions_take_the_place_path(q) -> None:
    assert A.place_route(q) == "place"
    assert keyword_check([q]) is None                      # must-answer: no guardrail fires


@pytest.mark.parametrize("q", [
    "How much was budgeted for farms in Wamakko in 2026?", "Will it rain on my farm tomorrow?",
    "Nawa aka ware wa noma a 2026?", "Nearest hospital to my farm", "How many IDPs farm in Goronyo?",
])
def test_budget_weather_and_facility_questions_stay_on_their_paths(q) -> None:
    assert A.place_route(q) == ""


@pytest.mark.parametrize("q,cat", [
    ("Prove that this land is mine", "land"), ("Whose farm is this plot?", "land"),
    ("Give me a certificate for my farm", "land"), ("Where is the boundary between my farm and my neighbour's?", "land"),
    ("Ba ni takardar shaidar mallakar gonata", "land"), ("Gonar nan ta wane ne?", "land"),
    ("Which is the safe grazing route for my cattle?", "security"), ("Hanyar kiwo mafi aminci", "security"),
    ("Which villages were abandoned in Sabon Birni?", "security"), ("Waɗanne ƙauyuka ne aka yi watsi da su?", "security"),
])
def test_ownership_certificates_grazing_routes_and_abandonment_are_refused(q, cat) -> None:
    assert keyword_check([q]) == cat


def test_a_budget_line_about_land_or_boundaries_is_still_a_figure() -> None:
    assert keyword_check(["How much was allocated to the boundary commission for land in 2026?"]) is None


# --- the summary -------------------------------------------------------------------------------------------------

def test_the_summary_states_the_year_against_the_plots_own_history_and_the_rain() -> None:
    h = _history()
    s = A.summary(h, "en", TODAY)
    assert "In the 2026 rainy season this plot's peak greenness was 0.49" in s
    assert "11 years with enough clear images (2016–2026)" in s and "297 mm" in s
    assert "normal variation" in s and "shows no clear change" in s
    assert "No open water was seen at this spot" in s and "can be missed" in s
    assert "never" not in s.lower()
    ha = A.summary(h, "ha", TODAY)
    assert "A daminar 2026" in ha and "bambanci ne na yau da kullum" in ha and "Ba a ga ruwa a fili" in ha


def test_a_thin_current_year_is_said_to_have_too_few_images_not_judged() -> None:
    h = _history(thin=(2026,))
    s = A.summary(h, "en", TODAY)
    assert "too few clear satellite images at this spot (5; 8 are needed)" in s
    assert "below" not in s.split("No open water")[0]


def test_no_greenness_claim_about_a_built_up_spot_the_2021_map_is_quoted_not_asserted() -> None:
    h = _history(kind="built-up area", landcover="built-up")
    s = A.summary(h, "en", TODAY)
    assert "The 2021 satellite land-cover map (ESA WorldCover) labels this spot *built-up*" in s
    assert "peak greenness was" not in s and "rising" not in s and "falling" not in s
    assert "wurin gine-gine" in A.summary(h, "ha", TODAY)


def test_water_months_and_the_nearest_water_body_are_reported_honestly() -> None:
    near_h = _history(water_months={y: [2, 3, 4, 9, 10] for y in range(2019, 2027)})
    nearest = {"lat": 13.10293, "lon": 5.20531, "distance_m": 951, "occurrence": 69, "area_ha": 1.4,
               "outline": None, "history": near_h}
    h = _history(water_months={2024: [7]}, nearest=nearest)
    s = A.summary(h, "en", TODAY)
    assert "Open water was seen at this spot in 2024 (July)." in s
    assert "The nearest water body is 1.0 km from your pin (1.4 ha; water in 69%" in s
    assert "February–April and September–October in 2019–2026" in s
    assert "never flooded" not in s
    w = A.details(h, "en")
    assert "muddy water" in w and "Nearest water body (1.0 km, 1.4 ha)" in w and "2026: 12 clear images" in w


def test_too_few_usable_years_means_no_comparison_and_no_trend() -> None:
    h = _history(thin=tuple(range(2016, 2024)))
    s = A.summary(h, "en", TODAY)
    assert "Only 3 of the years since 2016 have enough clear images" in s


def test_the_outline_rule_accepts_a_plot_holding_the_pin_within_0_1_to_50_ha() -> None:
    from rasterio.transform import from_origin
    from app.place.outline import CHIP_PX, Chip, fallback, mask_outline
    lon, lat = 5.4275, 13.2842
    tr = from_origin(lon - 50 * 0.0000923, lat + 50 * 0.0000899, 0.0000923, 0.0000899)     # 100 px of ~10 m
    chip = Chip("S2X", date(2026, 2, 23), np.zeros((CHIP_PX, CHIP_PX, 3), dtype="uint8"), tr,
                (lon - 0.0046, lat - 0.0045, lon + 0.0046, lat + 0.0045))
    mask = np.zeros((800, 800), dtype=bool)
    mask[300:500, 350:550] = True                    # 200 x 200 px at 1.25 m = 250 m square = 6.25 ha, holds the centre
    o = mask_outline(mask, chip, lon, lat)
    assert o.is_plot and 5.5 < o.area_ha < 7.0 and o.geometry["type"] == "Polygon"
    big = np.ones((800, 800), dtype=bool)            # the whole chip: 100 ha
    assert mask_outline(big, chip, lon, lat).note == "too_big"
    small = np.zeros((800, 800), dtype=bool)
    small[398:403, 398:403] = True                    # 25 px: 0.004 ha
    assert mask_outline(small, chip, lon, lat).note == "too_small"
    elsewhere = np.zeros((800, 800), dtype=bool)
    elsewhere[0:200, 0:200] = True
    assert mask_outline(elsewhere, chip, lon, lat).note == "no_pin"
    assert fallback(lon, lat, "no_segment").area_ha == pytest.approx(1.0, abs=0.01)
    assert A.outline_line(fallback(lon, lat, "no_segment"), "en").startswith("No plot outline could be drawn")


def test_sam_masks_cover_their_box_and_are_placed_on_the_frame() -> None:
    from app.providers.sam import Box, Segment
    m = np.ones((3, 2), dtype=bool)
    full = Segment(Box(1, 10, 20, 11, 22), m).on_frame(30, 30)
    assert full.sum() == 6 and full[20, 10] and full[22, 11] and not full[19, 10]


# --- the images --------------------------------------------------------------------------------------------------

def _jpeg_size(b: bytes) -> tuple[int, int]:
    return Image.open(io.BytesIO(b)).size


def test_the_chart_draws_hatched_thin_years_and_stays_under_the_limit() -> None:
    from app.maps.render import MAX_BYTES
    from app.place.images import place_chart
    h = _history(thin=(2016, 2026))
    for lang in ("en", "ha"):
        img = place_chart(h, lang, "Wamakko")
        assert len(img.jpeg) <= MAX_BYTES and _jpeg_size(img.jpeg) == (946, 1034)
        assert "2016–2026" in img.caption


def test_the_map_draws_the_outline_the_water_shading_and_the_nearest_body() -> None:
    from rasterio.transform import from_origin
    from app.maps.render import MAX_BYTES
    from app.place.images import place_map
    from app.place.outline import CHIP_PX, Chip, fallback
    lon, lat = 5.2115, 13.1095
    tr = from_origin(lon - 0.0046, lat + 0.0045, 0.000092, 0.00009)
    rgb = np.full((CHIP_PX, CHIP_PX, 3), 150, dtype="uint8")
    chip = Chip("S2X", date(2026, 2, 23), rgb, tr, (lon - 0.0046, lat - 0.0045, lon + 0.0046, lat + 0.0045))
    occ = np.zeros((34, 34))
    occ[5:10, 25:30] = 70
    ring = [[lon + 0.002, lat + 0.002], [lon + 0.003, lat + 0.002], [lon + 0.003, lat + 0.003], [lon + 0.002, lat + 0.003],
            [lon + 0.002, lat + 0.002]]
    nearest = {"lat": lat + 0.0025, "lon": lon + 0.0025, "distance_m": 380, "occurrence": 70, "area_ha": 1.1,
               "outline": {"type": "Polygon", "coordinates": [ring]}, "history": _history()}
    h = _history(nearest=nearest)
    img = place_map(chip, fallback(lon, lat, "no_segment"), h, "ha", "Wamakko", occ, lat, lon)
    assert len(img.jpeg) <= MAX_BYTES and _jpeg_size(img.jpeg) == (946, 1034)
    assert "da'ira ta kusan hekta 1" in img.caption
    img = place_map(chip, None, h, "en", "Wamakko", None, lat, lon)
    assert "a circle of about 1 ha" in img.caption


def test_the_answer_needs_a_pin_and_asks_for_one(monkeypatch) -> None:
    import asyncio
    pa = asyncio.run(A.place_answer(None, None, "how green was my farm in 2024?", "", "en", None, TODAY))
    assert pa.needs_pin and not pa.found and "send the pin" in pa.text
    pa = asyncio.run(A.place_answer(None, None, "yaya koriyar gonata?", "", "ha", {"lga": "Wamakko"}, TODAY))
    assert pa.needs_pin and "danna maɓallin" in pa.text


def test_catalog_lists_the_place_capabilities() -> None:
    from app.agent.capabilities import catalog
    ids = {c.id for c in catalog()}
    assert {"place_history_point", "plot_outline", "rainfall_history"} <= ids
    assert json.dumps(A.W["ha"]["referral"])              # the Hausa referral line exists
