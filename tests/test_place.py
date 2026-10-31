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


def _obs(day, **kw):
    from datetime import date as _d
    from app.place.history import Observation
    return Observation(_d.fromisoformat(day), **kw)


def test_year_rows_need_three_clear_season_observations_and_count_water_by_month() -> None:
    from app.place.history import year_rows
    obs = [_obs("2024-06-10", ndvi=0.2, ndwi=-0.3), _obs("2024-07-15", ndvi=0.5, ndwi=-0.2),
           _obs("2024-08-09", ndvi=0.6, ndwi=0.1), _obs("2024-08-24", ndvi=0.7, ndwi=0.2),
           _obs("2024-09-13", ndvi=0.65, ndwi=-0.1), _obs("2024-03-02", bsi=0.3, ndwi=0.15),
           _obs("2024-03-17", bsi=0.1, ndwi=0.05), _obs("2024-04-01", bsi=0.2, ndwi=-0.2),
           _obs("2023-07-01", ndvi=0.4, ndwi=-0.1), _obs("2023-08-01", ndvi=0.5, ndwi=-0.1)]
    rows = year_rows(obs, [2023, 2024])
    r = rows[2024]
    assert r.season_obs == 5 and r.ndvi_p90 == pytest.approx(np.percentile([0.2, 0.5, 0.6, 0.7, 0.65], 90), abs=1e-3)
    assert r.water_obs == 3 and r.water_share == pytest.approx(2 / 3, abs=0.01)
    assert r.water_months == [3, 8]                       # March (median 0.10) and August (0.15) mostly water
    assert r.dry_obs == 3 and r.bsi_dry == pytest.approx(0.2) and r.usable
    assert rows[2023].season_obs == 2 and rows[2023].ndvi_p90 is None and not rows[2023].usable


def test_the_cache_key_is_a_100_m_cell_and_the_grid_is_about_10_m() -> None:
    from app.place.history import bbox_of, cell_id, grid_shape
    from app.place.raster import circle
    assert cell_id(13.0612345, 5.2398765) == "13.061,5.240"
    g = circle(5.24, 13.06)
    b = bbox_of(g)
    assert (b[2] - b[0]) * 111_320 * 0.974 == pytest.approx(112.8, abs=1.0)        # ~113 m across
    assert grid_shape(b, 13.06) == (12, 12)


@pytest.fixture(scope="module")
def conn():
    psycopg = pytest.importorskip("psycopg")
    from app.config import get_settings
    s = get_settings()
    if not s.has_database:
        pytest.skip("no database configured")
    try:
        c = psycopg.connect(s.db_url(), connect_timeout=3)
        if not c.execute("SELECT to_regclass('sat_cache')").fetchone()[0]:
            pytest.skip("sat_cache not migrated")
    except psycopg.OperationalError:
        pytest.skip("dev database not available")
    yield c
    c.close()


def test_the_cache_serves_past_years_and_recomputes_a_stale_current_year(conn, monkeypatch) -> None:
    from datetime import date as _d
    from app.place import history as H
    cell = "0.000,0.000"
    conn.execute("DELETE FROM sat_cache WHERE cell = %s", (cell,))
    conn.commit()
    today = _d(2026, 10, 31)
    H._save(conn, cell, "s2", 2024, {"year": 2024, "season_obs": 5, "ndvi_p90": 0.5}, "test", 5, _d(2026, 1, 1))
    H._save(conn, cell, "s2", 2026, {"year": 2026, "season_obs": 4, "ndvi_p90": 0.4}, "test", 4, _d(2026, 10, 1))
    cached = H._load(conn, cell)
    assert H._fresh(cached[("s2", 2024)], 2024, today)          # a past year is final
    assert not H._fresh(cached[("s2", 2026)], 2026, today)      # the current year, a month old: recomputed
    assert not H._fresh(None, 2020, today)
    conn.execute("DELETE FROM sat_cache WHERE cell = %s", (cell,))
    conn.commit()
    # no user or coordinate column exists: only the rounded cell
    cols = {r[0] for r in conn.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'sat_cache'")}
    assert cols == {"cell", "layer", "year", "values", "clear_obs", "source", "computed_at"}


@pytest.mark.skipif(not __import__("os").environ.get("PLACE_NETWORK_TESTS"), reason="network: PLACE_NETWORK_TESTS=1")
def test_against_the_brute_force_checker_goronyo_2024() -> None:
    """Expected values from scripts/place_check.py 13.531 5.882 2024 (an independent implementation):
    season_obs 11, ndvi_p90 0.191, water_obs 1, water_share 0.0, dry_obs 12, bsi_dry 0.259."""
    from app.place.history import compute_years
    from app.place.raster import circle
    r = compute_years(13.531, 5.882, circle(5.882, 13.531), [2024])[2024]
    assert r.season_obs == 11 and r.water_obs == 1 and r.dry_obs == 12
    assert r.ndvi_p90 == pytest.approx(0.191, abs=0.02)       # the checker picks pixels by centre, 10 m grid
    assert r.bsi_dry == pytest.approx(0.259, abs=0.05)        # B11 is 20 m: nearest onto the 10 m grid vs 20 m pixels
