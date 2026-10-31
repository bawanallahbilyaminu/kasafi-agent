"""Place history step 1: indices and the clear mask, yearly measures, the rain fit, trends, the cache key."""

from __future__ import annotations

import numpy as np
import pytest

from app.place import fit, indices, rain


def test_reflectance_takes_the_baseline_04_offset_off_and_drops_no_data() -> None:
    dn = np.array([[0, 2000], [11000, 1000]], dtype="uint16")
    old = indices.reflectance(dn, "03.01")
    new = indices.reflectance(dn, "05.11")
    assert np.isnan(old[0, 0]) and old[0, 1] == pytest.approx(0.2) and old[1, 0] == pytest.approx(1.1)
    assert new[0, 1] == pytest.approx(0.1) and new[1, 0] == pytest.approx(1.0) and new[1, 1] == pytest.approx(0.0)


def test_indices_are_the_textbook_ratios_and_zero_denominators_are_nan() -> None:
    b04, b08 = np.array([[0.1, 0.0]]), np.array([[0.5, 0.0]])
    assert indices.ndvi(b04, b08)[0, 0] == pytest.approx((0.5 - 0.1) / 0.6)
    assert np.isnan(indices.ndvi(b04, b08)[0, 1])
    assert indices.ndwi(np.array([[0.3]]), np.array([[0.1]]))[0, 0] == pytest.approx(0.5)      # water: > 0
    assert indices.bsi(np.array([[0.1]]), np.array([[0.3]]), np.array([[0.2]]), np.array([[0.4]]))[0, 0] == \
        pytest.approx(((0.4 + 0.3) - (0.2 + 0.1)) / ((0.4 + 0.3) + (0.2 + 0.1)))


def test_a_scene_counts_only_when_most_of_the_plot_is_clear() -> None:
    scl = np.array([[4, 4, 9], [5, 6, 8]])                  # 4 clear, 2 cloud
    inside = np.ones_like(scl, dtype=bool)
    index = np.array([[0.5, 0.6, 0.9], [0.4, 0.3, 0.9]])
    assert indices.clear_fraction(scl, inside) == pytest.approx(4 / 6)
    assert indices.plot_value(index, indices.clear_mask(scl), inside) == pytest.approx(np.median([0.5, 0.6, 0.4, 0.3]))
    assert indices.plot_value(index, indices.clear_mask(scl), inside, min_clear=0.8) is None
    cloudy = np.array([[9, 9, 9], [8, 8, 4]])
    assert indices.plot_value(index, indices.clear_mask(cloudy), inside) is None


def test_the_rain_fit_does_not_call_a_dry_year_a_decline() -> None:
    # greenness tracks rain exactly, so the dry year 2022 sits on the line: normal variation, never "below"
    pts = {2017: (0.60, 600.0), 2018: (0.65, 650.0), 2019: (0.55, 550.0), 2020: (0.70, 700.0), 2021: (0.62, 620.0),
           2022: (0.40, 400.0), 2023: (0.66, 660.0)}
    f = fit.rain_fit(pts)
    assert f is not None and f.flags[2022] == "normal" and all(v == "normal" for v in f.flags.values())
    # 2024 has the rain of a good year but the greenness of a poor one: below what the rain predicts
    pts[2024] = (0.45, 680.0)
    f = fit.rain_fit(pts)
    assert f.flags[2024] == "below" and f.flags[2022] == "normal"
    assert fit.rain_fit({y: pts[y] for y in list(pts)[:4]}) is None          # fewer than five years: no fit


def test_trends_need_five_years_and_a_change_larger_than_the_spread() -> None:
    assert fit.trend({2020: 0.5, 2021: 0.4, 2022: 0.3, 2023: 0.2}) is None
    assert fit.trend({2017: 0.5, 2018: 0.45, 2019: 0.42, 2020: 0.36, 2021: 0.3, 2022: 0.28})[0] == "falling"
    assert fit.trend({2017: 0.3, 2018: 0.36, 2019: 0.42, 2020: 0.45, 2021: 0.5})[0] == "rising"
    assert fit.trend({2017: 0.5, 2018: 0.3, 2019: 0.5, 2020: 0.3, 2021: 0.5, 2022: 0.3})[0] == "no clear change"


def test_rain_by_year_sums_the_june_to_october_season() -> None:
    daily = {"2024-05-31": 10.0, "2024-06-01": 5.0, "2024-10-31": 7.0, "2024-11-01": 3.0, "2025-07-01": 1.5}
    y = rain.by_year(daily)
    assert y[2024]["season_mm"] == 12.0 and y[2024]["year_mm"] == 25.0 and y[2024]["season_days"] == 2
    assert y[2025]["season_mm"] == 1.5
