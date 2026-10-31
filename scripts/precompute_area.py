"""The ward / LGA / state precompute (app/place/area.py) into ward_history. Resumable: a layer-year already in
the table is skipped unless --force. Logs the time per layer.

Usage: uv run python scripts/precompute_area.py [--layers cropland,jrc,unosat,rain,modis,s1,bsi]
                                                [--years 2001-2026] [--force] [--workers 6]
"""

from __future__ import annotations

import argparse
import logging
import sys
import time
from datetime import date
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.stdout.reconfigure(encoding="utf-8")

import psycopg  # noqa: E402

from app.config import get_settings  # noqa: E402
from app.place import area  # noqa: E402

LAYERS = ["cropland", "jrc", "unosat", "rain", "modis", "s1", "bsi"]
FIRST = {"modis": 2001, "s1": 2017, "bsi": 2017, "rain": 2001}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--layers", default=",".join(LAYERS))
    ap.add_argument("--years", default="")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--workers", type=int, default=area.WORKERS)
    a = ap.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s: %(message)s")
    for noisy in ("httpx", "httpcore", "rasterio"):
        logging.getLogger(noisy).setLevel(logging.WARNING)
    layers = [x.strip() for x in a.layers.split(",") if x.strip()]
    today = date.today()
    yr = None
    if a.years:
        lo, _, hi = a.years.partition("-")
        yr = (int(lo), int(hi or lo))
    t_all = time.perf_counter()
    with psycopg.connect(get_settings().db_url()) as conn:
        grid = area.state_grid(conn)
        units = area.load_units(conn, grid)
        logging.info("grid %dx%d at %.0f m; %d wards, %d LGAs", grid.width, grid.height, area.GRID_M, len(units.wards),
                     len(units.lgas))
        t0 = time.perf_counter()
        crop = area.cropland(grid)
        shares = area.per_unit(units, lambda labels: area.unit_share(crop, labels, labels > 0))
        if "cropland" in layers and (a.force or not area.have(conn, "cropland_share")):
            area.save(conn, [(u, lvl, "cropland_share", 0, s, n, area.SOURCES["cropland"]) for (lvl, u), (s, n) in shares.items()]
                      + [(u, lvl, "cropland_cells", 0, float(round(s * n)), n, area.SOURCES["cropland"])
                         for (lvl, u), (s, n) in shares.items()], today)
        logging.info("cropland: %.0fs", time.perf_counter() - t0)
        dry = None
        if "jrc" in layers or "s1" in layers:
            t0 = time.perf_counter()
            got = area.jrc(grid)
            if got is None:
                logging.warning("JRC unavailable; the Sentinel-1 layer needs it")
            else:
                occ, rec = got
                dry = ~(np.isfinite(rec) & (rec >= area.NORMALLY_DRY))
                if "jrc" in layers and (a.force or not area.have(conn, "jrc_recurrence_share")):
                    wet = np.isfinite(rec) & (rec >= area.NORMALLY_DRY)
                    s1 = area.per_unit(units, lambda labels: area.unit_share(wet, labels, crop))
                    s2 = area.per_unit(units, lambda labels: area.unit_median(occ, labels, crop & np.isfinite(occ)))
                    rows = [(u, lvl, "jrc_recurrence_share", 0, s, n, area.SOURCES["jrc"]) for (lvl, u), (s, n) in s1.items()]
                    rows += [(u, lvl, "jrc_occurrence_median", 0, v, None, area.SOURCES["jrc"]) for (lvl, u), v in s2.items()]
                    area.save(conn, rows, today)
            logging.info("jrc: %.0fs", time.perf_counter() - t0)
        if "unosat" in layers and (a.force or not area.have(conn, "unosat_share")):
            t0 = time.perf_counter()
            for year, shares_y in area.unosat_shares(grid, units, crop).items():
                area.save(conn, [(u, lvl, "unosat_share", year, s, n, area.SOURCES["unosat"]) for (lvl, u), (s, n) in shares_y.items()], today)
            logging.info("unosat: %.0fs", time.perf_counter() - t0)
        if "rain" in layers and (a.force or not area.have(conn, "rain_season_mm")):
            t0 = time.perf_counter()
            rows = []
            for (lvl, u), vals in area.rain_years(units, FIRST["rain"], today).items():
                rows += [(u, lvl, "rain_season_mm", y, v, None, area.SOURCES["rain"]) for y, v in vals.items()]
            area.save(conn, rows, today)
            logging.info("rain: %.0fs (%d rows)", time.perf_counter() - t0, len(rows))
        for layer, fn, measures in (("modis", area.modis_year, ("modis_peak",)), ("s1", None, ("s1_flood_share",)),
                                    ("bsi", area.bsi_year, ("bsi_share", "bsi_median"))):
            if layer not in layers:
                continue
            lo = max(FIRST[layer], yr[0]) if yr else FIRST[layer]
            hi = min(today.year, yr[1]) if yr else today.year
            t_layer = time.perf_counter()
            for year in range(lo, hi + 1):
                if not a.force and area.have(conn, measures[0], year):
                    continue
                t0 = time.perf_counter()
                if layer == "modis":
                    res = fn(grid, units, crop, year, a.workers)
                    rows = [(u, lvl, "modis_peak", year, v, n, area.SOURCES["modis"]) for (lvl, u), (v, n) in res.items()]
                elif layer == "s1":
                    if dry is None:
                        break
                    res = area.s1_year(grid, units, crop, dry, year, a.workers)
                    rows = [(u, lvl, "s1_flood_share", year, v, n, area.SOURCES["s1"]) for (lvl, u), (v, n) in res.items()]
                else:
                    res = fn(grid, units, crop, year, a.workers)
                    rows = [(u, lvl, "bsi_share", year, s, n, area.SOURCES["bsi"]) for (lvl, u), (s, m, n) in res.items()]
                    rows += [(u, lvl, "bsi_median", year, m, n, area.SOURCES["bsi"]) for (lvl, u), (s, m, n) in res.items()]
                area.save(conn, rows, today)
                logging.info("%s %d: %.0fs (%d rows)", layer, year, time.perf_counter() - t0, len(rows))
            logging.info("%s total: %.0f min", layer, (time.perf_counter() - t_layer) / 60)
    logging.info("all done in %.0f min", (time.perf_counter() - t_all) / 60)


if __name__ == "__main__":
    main()
