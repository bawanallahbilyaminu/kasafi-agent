"""What hazard answers read: a day's summary per layer for an LGA (its centroid), a point (the nearest fetch point)
or the state (every LGA, the highest named), and how old the data is.

Freshness: a layer's data is current when its last successful fetch is within twice its interval; older, the
answer says how old ("data from 9 hours ago"); none, or no value for the day asked, the answer says it isn't
available now. Old data is never passed off as current.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone

from app.hazards.categories import aqi_category, heat_category, heat_index_c, percentile_rank, rain_class
from app.hazards.fetch import INTERVALS, SOURCES

LAGOS = timezone(timedelta(hours=1))


@dataclass
class Freshness:
    layer: str
    fetched_at: datetime | None          # the last successful fetch
    stale: bool                          # older than twice the layer's interval
    hours_old: float | None

    @property
    def available(self) -> bool:
        return self.fetched_at is not None


def freshness(conn, layer: str, now: datetime | None = None) -> Freshness:
    now = now or datetime.now(timezone.utc)
    row = conn.execute("SELECT max(started_at) FROM hazard_fetch WHERE layer = %s AND ok", (layer,)).fetchone()
    at = row[0] if row else None
    if at is None:
        return Freshness(layer, None, True, None)
    age = now - at
    return Freshness(layer, at, age > 2 * INTERVALS[layer], round(age.total_seconds() / 3600, 1))


@dataclass
class Where:
    """An LGA (its centroid point), a point (the nearest fetch point), or the state (every LGA's centroid)."""
    kind: str                           # lga | point | state
    lga_pcode: str = ""
    lga: str = ""
    lat: float | None = field(default=None, repr=False)
    lon: float | None = field(default=None, repr=False)


def point_ids(conn, where: Where) -> list[tuple[int, str]]:
    """(point id, LGA name) the summary reads: the LGA's centroid, the nearest point, or every LGA's centroid."""
    if where.kind == "lga":
        return conn.execute("SELECT p.id, l.name FROM hazard_point p JOIN lga l ON l.pcode = p.lga_pcode WHERE "
                            "p.kind = 'lga' AND p.lga_pcode = %s", (where.lga_pcode,)).fetchall()
    if where.kind == "point":
        return conn.execute("SELECT p.id, l.name FROM hazard_point p JOIN lga l ON l.pcode = p.lga_pcode WHERE "
                            "p.kind IN ('lga', 'grid') ORDER BY p.geom <-> ST_SetSRID(ST_MakePoint(%s, %s), 4326) "
                            "LIMIT 1", (where.lon, where.lat)).fetchall()
    return conn.execute("SELECT p.id, l.name FROM hazard_point p JOIN lga l ON l.pcode = p.lga_pcode WHERE "
                        "p.kind = 'lga' ORDER BY l.name").fetchall()


def _day_bounds(day: date) -> tuple[datetime, datetime]:
    start = datetime(day.year, day.month, day.day, tzinfo=LAGOS)
    return start, start + timedelta(days=1)


def _hourly(conn, layer: str, pid: int, day: date, variables: tuple) -> dict[str, list[tuple[datetime, float]]]:
    a, b = _day_bounds(day)
    out: dict[str, list] = {v: [] for v in variables}
    for vt, var, val in conn.execute("SELECT valid_time, variable, value FROM hazard_values WHERE layer = %s AND "
                                     "point_id = %s AND variable = ANY(%s) AND valid_time >= %s AND valid_time < %s "
                                     "ORDER BY valid_time", (layer, pid, list(variables), a, b)):
        if val is not None:
            out[var].append((vt, float(val)))
    return out


@dataclass
class HeatDay:
    lga: str
    day: date
    temp_max: float
    feels_max: float                 # apparent temperature (Open-Meteo)
    heat_index_max: float            # NWS heat index from temperature and humidity, computed here
    category: str                    # from max(air temperature, heat index): the index understates dry heat
    uv_max: float
    wind_max: float
    gust_max: float
    rain_mm: float
    rain_peak_mm_h: float
    rain_class: str
    rain_prob_max: float
    fetched_at: datetime | None
    basis: str = "heat_index"        # which the category used: "heat_index" or "air_temperature" (dry heat)

    @property
    def category_value(self) -> float:
        return max(self.temp_max, self.heat_index_max)


def heat_day(conn, pid: int, lga: str, day: date) -> HeatDay | None:
    h = _hourly(conn, "forecast", pid, day, ("temperature_2m", "apparent_temperature", "relative_humidity_2m",
                                             "uv_index", "wind_speed_10m", "wind_gusts_10m", "precipitation",
                                             "precipitation_probability"))
    if not h["temperature_2m"]:
        return None
    rh = dict(h["relative_humidity_2m"])
    his = [heat_index_c(t, rh[vt]) for vt, t in h["temperature_2m"] if vt in rh]
    hi = max(his) if his else max(t for _, t in h["temperature_2m"])
    peak = max((v for _, v in h["precipitation"]), default=0.0)
    fetched = conn.execute("SELECT max(fetched_at) FROM hazard_values WHERE layer = 'forecast' AND point_id = %s",
                           (pid,)).fetchone()[0]
    mx = lambda k: max((v for _, v in h[k]), default=0.0)      # noqa: E731
    # in dry heat the NWS index falls below the air temperature (37 C at low humidity: index 34 C): the category
    # is taken from the higher of the two, and the answer says which
    temp = mx("temperature_2m")
    basis = "air_temperature" if temp > hi else "heat_index"
    return HeatDay(lga, day, temp, mx("apparent_temperature"), hi, heat_category(max(temp, hi)), mx("uv_index"),
                   mx("wind_speed_10m"), mx("wind_gusts_10m"), round(sum(v for _, v in h["precipitation"]), 1),
                   peak, rain_class(peak), mx("precipitation_probability"), fetched, basis)


@dataclass
class AirDay:
    lga: str
    day: date
    pm10_mean: float
    pm2_5_mean: float
    dust_mean: float
    aod_mean: float
    aqi_max: float                   # the higher of US AQI for PM10 and PM2.5, the day's maximum
    category: str
    fetched_at: datetime | None
    aqi_by: str = "PM10"             # the pollutant that sets aqi_max (PM10 or PM2.5)


def air_day(conn, pid: int, lga: str, day: date) -> AirDay | None:
    h = _hourly(conn, "air", pid, day, ("pm10", "pm2_5", "dust", "aerosol_optical_depth", "us_aqi_pm10",
                                        "us_aqi_pm2_5"))
    if not h["pm10"]:
        return None
    mean = lambda k: round(sum(v for _, v in h[k]) / len(h[k]), 1) if h[k] else 0.0     # noqa: E731
    by_pm10 = max([v for _, v in h["us_aqi_pm10"]], default=0.0)
    by_pm25 = max([v for _, v in h["us_aqi_pm2_5"]], default=0.0)
    aqi = max(by_pm10, by_pm25)
    fetched = conn.execute("SELECT max(fetched_at) FROM hazard_values WHERE layer = 'air' AND point_id = %s",
                           (pid,)).fetchone()[0]
    return AirDay(lga, day, mean("pm10"), mean("pm2_5"), mean("dust"), round(mean("aerosol_optical_depth"), 2), aqi,
                  aqi_category(aqi), fetched, "PM2.5" if by_pm25 > by_pm10 else "PM10")


@dataclass
class RiverDay:
    point: str
    lga: str
    day: date
    discharge: float                 # m3/s, forecast (GloFAS)
    rank: float                      # % of the same time of year's days (+-15 days, every year) with less discharge
    since: date                      # the history's first day
    fetched_at: datetime | None
    level: str = "normal"            # low | normal | high | very_high, for the time of year (river_level)

    @property
    def period(self) -> tuple[str, int]:
        """('late', 10) for 30 October: early (1-10), mid (11-20), late (21-) and the month."""
        return ("early" if self.day.day <= 10 else "mid" if self.day.day <= 20 else "late"), self.day.month


SEASON_WINDOW = 15                   # days either side of the date, in every year of the history


def same_time_of_year(history: list[tuple[float, date]], day: date, window: int = SEASON_WINDOW) -> list[float]:
    """The history's discharges within +-window days of the date's day of year (wrapping round the year end)."""
    doy = day.timetuple().tm_yday
    return [q for q, d in history if min(abs(d.timetuple().tm_yday - doy), 366 - abs(d.timetuple().tm_yday - doy))
            <= window]


def river_level(rank: float) -> str:
    """Plain words for a seasonal percentile: below the 25th low, to the 75th normal, to the 95th high, above
    very high. Alert triggers (step 6) use the same seasonal percentile."""
    return "low" if rank < 25 else "normal" if rank < 75 else "high" if rank < 95 else "very_high"


def river_days(conn, day: date, lga_pcode: str = "") -> list[RiverDay]:
    """Each river point (in the LGA, or all): the day's forecast discharge against the same time of year in its own
    history (a river in late October is compared with late Octobers, not with the whole year)."""
    rows = conn.execute(
        "SELECT p.id, p.name, l.name, v.value, v.fetched_at FROM hazard_point p JOIN lga l ON l.pcode = p.lga_pcode "
        "JOIN hazard_values v ON v.point_id = p.id AND v.layer = 'flood' AND v.variable = 'river_discharge' "
        "AND v.valid_time::date = %s WHERE p.kind = 'river' AND (%s = '' OR p.lga_pcode = %s) ORDER BY p.id",
        (day, lga_pcode, lga_pcode)).fetchall()
    out = []
    for pid, name, lga, q, fetched in rows:
        hist = conn.execute("SELECT discharge, day FROM river_history WHERE point_id = %s", (pid,)).fetchall()
        season = same_time_of_year(hist, day)
        if not season:
            continue
        rank = percentile_rank(float(q), season)
        out.append(RiverDay(name, lga, day, round(float(q), 1), rank, min(h[1] for h in hist), fetched,
                            river_level(rank)))
    return out


@dataclass
class FireCount:
    lga: str
    count: int
    since: datetime
    fetched_at: datetime | None


def fire_counts(conn, hours: int = 24, lga_pcode: str = "", now: datetime | None = None) -> list[FireCount]:
    since = (now or datetime.now(timezone.utc)) - timedelta(hours=hours)
    rows = conn.execute("SELECT l.name, count(*), max(f.fetched_at) FROM fire_detection f JOIN lga l ON "
                        "l.pcode = f.lga_pcode WHERE f.detected_at >= %s AND (%s = '' OR f.lga_pcode = %s) GROUP BY 1 "
                        "ORDER BY 2 DESC", (since, lga_pcode, lga_pcode)).fetchall()
    return [FireCount(lga, n, since, fetched) for lga, n, fetched in rows]


def source_of(layer: str) -> str:
    return SOURCES[layer]
