"""Place history step 3: the ward precompute's arithmetic (label rasters, shares, medians, composite picking)."""

from __future__ import annotations

import numpy as np
import pytest

from app.place import area


def _units():
    grid = area.Grid((5.0, 13.0, 5.02, 13.02), 10, 10)
    wl = np.zeros((10, 10), dtype="int32")
    wl[:5, :] = 1                      # ward 1: the top half
    wl[5:, :5] = 2                     # ward 2: bottom left
    wl[5:, 5:] = 3                     # ward 3: bottom right
    ll = np.where(wl == 1, 1, 2)       # LGA 1 = ward 1; LGA 2 = wards 2 and 3
    return area.Units(grid, wl, ll, {1: ("w1", "One", "L1"), 2: ("w2", "Two", "L2"), 3: ("w3", "Three", "L2")},
                      {1: ("L1", "Lga One"), 2: ("L2", "Lga Two")}, {})


def test_shares_and_medians_are_per_label_over_the_cells_asked_about() -> None:
    u = _units()
    crop = np.zeros((10, 10), dtype=bool)
    crop[:, :8] = True                                   # the right two columns are not cropland
    flag = np.zeros((10, 10), dtype=bool)
    flag[:5, :4] = True                                  # half of ward 1's cropland (40 of 40 cells... 20 of 40)
    s = area.unit_share(flag, u.ward_labels, crop)
    assert s[1] == (pytest.approx(0.5), 40) and s[2] == (0.0, 25) and s[3] == (0.0, 15)
    vals = np.arange(100, dtype=float).reshape(10, 10)
    m = area.unit_median(vals, u.ward_labels, crop)
    assert m[1] == pytest.approx(np.median(vals[:5, :8])) and m[3] == pytest.approx(np.median(vals[5:, 5:8]))
    out = area.per_unit(u, lambda labels: area.unit_share(flag, labels, crop))
    assert out[("ward", "w1")] == (pytest.approx(0.5), 40)
    assert out[("lga", "L2")] == (0.0, 40) and out[("state", area.STATE)][1] == 80
    assert out[("state", area.STATE)][0] == pytest.approx(20 / 80)


def test_the_grid_is_the_state_at_200_m_under_the_api_cap() -> None:
    g = area.Grid((4.118, 11.572, 6.803, 13.904), 1460, 1298)
    assert g.transform.a == pytest.approx((6.803 - 4.118) / 1460) and g.shape == (1298, 1460)
    assert 150 * 150 < g.cell_m2(12.7) < 250 * 250


def test_modis_season_composites_are_june_to_october_on_the_state_tile(monkeypatch) -> None:
    fake = [{"id": f"MOD13Q1.A2024{d:03d}.h18v07.061.x", "properties": {"datetime": "2024-06-01T00:00:00Z"}}
            for d in (129, 145, 161, 289, 305)]
    fake.append({"id": "MOD13Q1.A2024177.h17v07.061.x", "properties": {"datetime": "2024-06-25T00:00:00Z"}})
    monkeypatch.setattr(area, "items", lambda *a, **k: fake)
    got = [it["id"].split(".")[1] for it in area.modis_items(area.Grid((0, 0, 1, 1), 2, 2), 2024)]
    assert got == ["A2024145", "A2024161", "A2024289"]           # not May (129), not November (305), not h17


def test_dry_scenes_take_the_two_clearest_per_tile(monkeypatch) -> None:
    fake = [{"id": f"S2_{t}_{c}", "properties": {"datetime": "2024-02-01T00:00:00Z", "eo:cloud_cover": c,
                                                 "s2:mgrs_tile": t}} for t in ("31PGQ", "31PFQ") for c in (9.0, 1.0, 4.0)]
    monkeypatch.setattr(area, "items", lambda *a, **k: fake)
    got = [it["id"] for it in area.dry_scenes(area.Grid((0, 0, 1, 1), 2, 2), 2024)]
    assert got == ["S2_31PGQ_1.0", "S2_31PGQ_4.0", "S2_31PFQ_1.0", "S2_31PFQ_4.0"]


def test_a_flood_cell_is_normally_dry_and_under_the_threshold_on_its_lowest_pass() -> None:
    from app.place.radar import WATER_DB
    lowest = np.array([[-20.0, -10.0], [np.inf, -16.0]], dtype="float32")
    dry = np.array([[True, True], [True, False]])
    crop = np.ones((2, 2), dtype=bool)
    flooded = np.isfinite(lowest) & (lowest < WATER_DB)
    labels = np.ones((2, 2), dtype="int32")
    s = area.unit_share(flooded, labels, crop & dry)
    assert s[1] == (pytest.approx(1 / 3), 3)           # the wet cell (-16, not normally dry) isn't counted


def test_a_flood_cell_must_be_darker_than_its_dry_season_and_off_the_frame_edge() -> None:
    lowest = np.array([[-20.0, -15.5, -16.0], [-17.0, -10.0, np.inf]], dtype="float32")
    reference = np.array([[-9.0, -15.7, np.nan], [-12.0, -9.0, -9.0]], dtype="float32")
    f = area.flood_cells(lowest, reference)
    # -20 vs -9: flood; -15.5 vs -15.7: sand; -16 with no reference: flood; -17 vs -12: 5 dB darker: flood
    assert f.tolist() == [[True, False, True], [True, False, False]]
    assert area.flood_cells(lowest, None).tolist() == [[True, True, True], [True, False, False]]
    has = np.array([[True, True, True], [True, True, False], [True, True, True]])
    edge = area.swath_edge(has)
    assert edge.tolist() == [[False, False, True], [False, True, False], [False, False, True]]
