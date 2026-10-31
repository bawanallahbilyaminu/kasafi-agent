"""Place history step 2b: the radar water threshold, the per-year pass counts, the official flood-map lookup and
the combined flood wording (no network)."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import numpy as np
import pytest

from app.place import floods, radar


def test_the_vv_threshold_separates_the_reservoir_from_the_city_and_the_floodplain() -> None:
    # medians measured 31 Oct 2026 over July–October 2024 (see app/place/radar.py)
    water = [-19.1, -19.4, -17.3, -16.6, -18.1, -18.9]
    city = [-1.8, 0.0, -0.7, -0.4, -2.3, 0.9]
    cropland = [-12.5, -8.0, -5.9, -8.7, -6.6, -5.4]
    assert all(radar.is_water(v) for v in water)
    assert not any(radar.is_water(v) for v in city + cropland)
    assert radar.is_water(None) is False
    assert max(water) < radar.WATER_DB - 1.5 and min(cropland) > radar.WATER_DB + 2.0


def test_plot_db_is_the_median_over_the_plot_and_needs_half_its_pixels() -> None:
    vv = np.array([[0.01, 0.02, 0.0], [0.0, 0.0, 0.0]])          # 0 = no data: 2 of 6 valid, under half
    inside = np.array([[True, True, True], [True, True, True]])
    assert radar.plot_db(vv, inside) is None
    vv2 = np.array([[0.01, 0.02, 0.01], [0.5, 0.0, 0.0]])        # 4 of 6: the median of the valid pixels
    db = radar.plot_db(vv2, inside)
    assert db == pytest.approx(10 * np.log10(0.015), abs=0.3)
    assert radar.plot_db(np.zeros((2, 2)), np.ones((2, 2), dtype=bool)) is None


def test_radar_years_count_passes_and_list_the_dates_under_water(monkeypatch) -> None:
    items = [{"id": f"s1_{d}", "properties": {"datetime": f"{d}T17:47:00Z"}} for d in
             ("2024-07-10", "2024-07-22", "2024-08-03", "2024-08-15", "2023-09-01", "2024-11-02", "2024-06-28")]
    monkeypatch.setattr(radar.stac, "search", lambda *a, **k: items)
    values = {"s1_2024-07-10": -17.0, "s1_2024-07-22": -8.0, "s1_2024-08-03": -16.1, "s1_2024-08-15": None,
              "s1_2023-09-01": -3.0}
    monkeypatch.setattr(radar, "read_pass", lambda client, item_id, geom, bbox, shape: values.get(item_id))
    from app.place.raster import circle
    rows = radar.radar_years(13.128, 5.235, circle(5.235, 13.128), [2023, 2024], workers=2)
    assert rows[2024].passes == 3 and rows[2024].water == ["2024-07-10", "2024-08-03"]     # the None pass isn't counted
    assert rows[2023].passes == 1 and rows[2023].water == [] and rows[2023].vv_db == {"2023-09-01": -3.0}
    # June and November passes are outside the flood months
    assert "s1_2024-11-02" not in rows[2024].vv_db and "s1_2024-06-28" not in rows[2024].vv_db


def test_official_maps_report_the_maps_whose_water_touches_the_plot(tmp_path: Path) -> None:
    gpd = pytest.importorskip("geopandas")
    from shapely.geometry import box
    from app.place.raster import circle
    g = gpd.GeoDataFrame({"layer": ["w", "w"], "source": ["UNOSAT", "UNOSAT"], "code": ["FL2022", "FL2024"],
                          "period_start": ["2022-10-01", "2024-09-05"], "period_end": ["2022-10-25", "2024-09-09"],
                          "dataset": ["d", "d"], "licence": ["CC BY-SA", "CC BY-SA"],
                          "geometry": [box(5.20, 13.10, 5.22, 13.12), box(5.30, 13.30, 5.31, 13.31)]}, crs="EPSG:4326")
    g.to_file(tmp_path / "test.gpkg", driver="GPKG")
    floods._maps_cache.clear()
    hits = floods.official_maps_at(circle(5.21, 13.11), tmp_path)
    assert [m["code"] for m in hits] == ["FL2022"] and hits[0]["period_end"] == "2022-10-25"
    assert floods.official_maps_at(circle(5.50, 13.50), tmp_path) == []
    assert floods.official_maps_at(circle(5.50, 13.50), tmp_path / "none") == []


def _dry_history(water_months=None, jrc=0.0, landcover="cropland"):
    from app.place.history import History, YearRow, cell_id
    rows = {y: YearRow(y, season_obs=12, ndvi_p90=0.5, dry_obs=8, water_months=(water_months or {}).get(y, []))
            for y in range(2017, 2027)}
    return History(cell_id(13.128, 5.235), 13.128, 5.235, rows, landcover=landcover,
                   jrc={"occurrence": jrc, "recurrence": 0.0, "seasonality": 0.0})


def test_only_a_normally_dry_cell_with_wet_season_water_is_a_flood() -> None:
    from app.place import answer as A
    h = _dry_history(water_months={2022: [8]})
    ev = floods.FloodEvidence(radar={y: radar.RadarYear(y, 12, ["2024-09-02", "2024-09-14"] if y == 2024 else [])
                                     for y in range(2017, 2027)},
                              official=[{"source": "UNOSAT", "code": "FL20240902NGA_sep", "period_start": "2024-09-05",
                                         "period_end": "2024-09-09", "licence": "CC BY-SA"}])
    assert floods.classify_water(h, ev) == "flood" and floods.flood_years(h, ev) == [2022, 2024]
    h.floods = ev
    s = A.flood_sentence(h, "en")
    assert s.startswith("This spot is normally dry; flood water was seen in 2022, 2024:")
    assert "flood water seen on 2 of 12 radar passes in 2024 (2 Sep, 14 Sep)" in s
    assert "inside the UN satellite flood map of 5–9 September 2024" in s
    assert "Sentinel-2 saw water in 2022 (August)" in s and "never" not in s.lower()
    ha = A.flood_sentence(h, "ha")
    assert "a kullum bushe yake" in ha and "2 cikin 12" in ha and "taswirar ambaliya ta tauraron ɗan adam ta MDD" in ha


def test_no_flood_water_seen_is_said_with_the_reason_never_never_flooded() -> None:
    from app.place import answer as A
    h = _dry_history()
    h.floods = floods.FloodEvidence(radar={y: radar.RadarYear(y, 10, []) for y in range(2017, 2027)})
    assert floods.classify_water(h, h.floods) is None
    s = A.flood_sentence(h, "en")
    assert s.startswith("No flood water was seen at this spot") and "under crops" in s and "never" not in s.lower()
    assert "none of the 100 July–October radar passes" in s and "2017–2026" in s
    assert "no official satellite flood map for Sokoto is loaded yet" in s     # the clipped maps aren't on this machine
    assert "covering Sokoto" not in s
    h.floods.maps_loaded = True
    assert "UNOSAT, October 2022" in A.flood_sentence(h, "en")
    # inside a UN map's water extent yet never seen as water here: said as the map's extent, not a flood
    h.floods.official = [{"source": "UNOSAT", "code": "x", "period_start": "2022-10-01", "period_end": "2022-10-25"}]
    s = A.flood_sentence(h, "en")
    assert s.startswith("No flood water was seen") and "inside the UN flood map's water extent of 1–25 October 2022" in s


def test_permanent_and_seasonal_water_are_never_called_floods() -> None:
    from app.place import answer as A
    wet_all = {y: [2, 3, 8, 9, 10] for y in range(2019, 2027)}
    h = _dry_history(water_months=wet_all, jrc=88.0)
    ev = floods.FloodEvidence(radar={y: radar.RadarYear(y, 10, [f"{y}-07-{d:02d}" for d in range(1, 11)])
                                     for y in range(2017, 2027)},
                              official=[{"source": "UNOSAT", "code": "x", "period_start": "2022-10-01",
                                         "period_end": "2022-10-25"}])
    assert floods.classify_water(h, ev) == "permanent" and floods.flood_years(h, ev) == []
    h.floods, h.water_type, h.water_name = ev, "permanent", "Goronyo Dam reservoir"
    s = A.flood_sentence(h, "en")
    assert s.startswith("This spot is permanent open water (Goronyo Dam reservoir): water in the dry season and the "
                        "rainy season in most years; JRC saw water in 88% of the months it observed (1984–2020)")
    assert "radar saw water on 100 of 100 July–October passes in 2017–2026" in s
    assert "inside the UN flood map's water extent of 1–25 October 2022" in s
    assert "flood water" not in s and "1 Jul" not in s
    assert "ruwa ne na dindindin a fili" in A.flood_sentence(h, "ha")
    # seasonal: wet most years, dry in the dry season
    h2 = _dry_history(water_months={y: [8, 9] for y in range(2019, 2027)})
    ev2 = floods.FloodEvidence(radar={y: radar.RadarYear(y, 10, [f"{y}-08-0{d}" for d in (1, 5)] if y >= 2019 else [])
                                      for y in range(2017, 2027)})
    assert floods.classify_water(h2, ev2) == "seasonal"
    h2.floods = ev2
    s2 = A.flood_sentence(h2, "en")
    assert s2.startswith("This spot is seasonal water: under water in most rainy seasons (2019, 2020") and "flood" not in s2


def test_radar_text_lists_at_most_four_dates() -> None:
    from app.place import answer as A
    rows = {2024: radar.RadarYear(2024, 12, [f"2024-08-{d:02d}" for d in (3, 9, 15, 21, 27)])}
    assert "5 of 12 radar passes in 2024 (3 Aug – 27 Aug)" in A.radar_text(rows, "en")
    rows = {y: radar.RadarYear(y, 10, [f"{y}-07-{d:02d}" for d in range(1, 11)]) for y in range(2017, 2027)}
    assert A.radar_text(rows, "en") == "water on every July–October radar pass in 2017–2026 (100 of 100)"


def test_the_outlook_block_marks_statewide_lines_as_statewide() -> None:
    from app.place import answer as A
    text = ("🌦️ *Official seasonal prediction* — Wurno LGA\n*NiMet, 2026 SCP* (issued February 2026)\n"
            "• the 2026 rainy season, page 106: “Wurno: Onset date: 10-Jul; Season end: 17-Sept”\n"
            "• the 2026 rainy season (onset), page 12: “most of the northern states 18th–23rd June”\n"
            "📄 NiMet, 2026 SCP p. 12, 106")
    out = A.outlook_block(text, "Wurno", "en", 5)
    assert out.splitlines()[0] == "🌦️ *Official seasonal prediction* — Wurno LGA"
    assert "Wurno: Onset" in out and "northern states" not in out and out.endswith("📄 NiMet, 2026 SCP p. 12, 106")
    out = A.outlook_block(text, "Gada", "en", 5)
    assert "for Sokoto State (the document gives no line for Gada LGA)" in out and "northern states" in out
    assert "Wurno: Onset" in out                     # the statewide block keeps the document's items as they are
    out = A.outlook_block(text.replace("Wurno:", "Wamako:"), "Wamakko", "ha", 5)
    assert "Ƙaramar Hukumar Wamakko" in out and "Wamako: Onset" in out
