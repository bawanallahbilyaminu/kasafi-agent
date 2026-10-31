"""Seasonal rainfall per year at a point, from Open-Meteo's historical weather archive (ERA5-Land, ~9 km,
daily, from 1940; free, no key, non-commercial terms, 10,000 calls a day). One call covers every year."""

from __future__ import annotations

from datetime import date

import httpx

ARCHIVE = "https://archive-api.open-meteo.com/v1/archive"
TIMEOUT = 40.0
SEASON = (6, 10)          # June–October: the rainy season


def daily_rain(lat: float, lon: float, start: date, end: date) -> dict[str, float]:
    """{'YYYY-MM-DD': mm} for the period (the archive runs about five days behind today)."""
    params = {"latitude": lat, "longitude": lon, "start_date": start.isoformat(), "end_date": end.isoformat(),
              "daily": "precipitation_sum", "timezone": "Africa/Lagos"}
    with httpx.Client(timeout=TIMEOUT) as c:
        r = c.get(ARCHIVE, params=params)
        r.raise_for_status()
        d = r.json()["daily"]
    return {t: (v if v is not None else 0.0) for t, v in zip(d["time"], d["precipitation_sum"])}


def by_year(daily: dict[str, float]) -> dict[int, dict[str, float]]:
    """Per year: the June–October total and the whole year's total, in mm; days counted too (an incomplete
    season, the current year, is shown as such)."""
    out: dict[int, dict[str, float]] = {}
    for day, mm in daily.items():
        y, m = int(day[:4]), int(day[5:7])
        row = out.setdefault(y, {"season_mm": 0.0, "year_mm": 0.0, "season_days": 0})
        row["year_mm"] += mm
        if SEASON[0] <= m <= SEASON[1]:
            row["season_mm"] += mm
            row["season_days"] += 1
    for row in out.values():
        row["season_mm"], row["year_mm"] = round(row["season_mm"], 1), round(row["year_mm"], 1)
    return out
