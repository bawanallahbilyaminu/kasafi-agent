"""The named scales hazard answers use (docs/hazard-and-services.md section 4). Every category names its scale.

- Heat: the US National Weather Service heat index, computed here from temperature and relative humidity with the
  NWS formula (Rothfusz regression with its adjustments, simple formula below 80 F), shown in degrees C. Categories:
  Caution 26.7-32.2, Extreme caution 32.2-39.4, Danger 39.4-51.1, Extreme danger >= 51.1 (NWS).
- Air: US AQI categories (Open-Meteo gives us_aqi_pm10 / us_aqi_pm2_5); the WHO 24-hour guideline (PM10 45,
  PM2.5 15 ug/m3, WHO 2021) is quoted as the reference.
- Rain: WMO rainfall intensity classes (WMO-No. 8): light < 2.5 mm/h, moderate 2.5-10, heavy 10-50, violent > 50.
- Rivers: a forecast discharge against the point's own daily history since 1984 ("higher than X% of days").
- Fires: "satellite heat detections (could be bush, farm or other fires)".
"""

from __future__ import annotations

HEAT_SCALE = "US National Weather Service heat index"
HEAT_CATEGORIES = ((51.1, "extreme_danger"), (39.4, "danger"), (32.2, "extreme_caution"), (26.7, "caution"))
AQI_SCALE = "US AQI"
AQI_CATEGORIES = ((301, "hazardous"), (201, "very_unhealthy"), (151, "unhealthy"), (101, "unhealthy_sensitive"),
                  (51, "moderate"), (0, "good"))
WHO_24H = {"pm10": 45.0, "pm2_5": 15.0}          # ug/m3, WHO global air quality guidelines 2021
RAIN_SCALE = "WMO rainfall intensity classes"
RAIN_CLASSES = ((50.0, "violent"), (10.0, "heavy"), (2.5, "moderate"), (0.1, "light"))

LABELS = {
    "en": {"caution": "Caution", "extreme_caution": "Extreme caution", "danger": "Danger",
           "extreme_danger": "Extreme danger", "below": "below Caution",
           "good": "Good", "moderate": "Moderate", "unhealthy_sensitive": "Unhealthy for sensitive groups",
           "unhealthy": "Unhealthy", "very_unhealthy": "Very unhealthy", "hazardous": "Hazardous",
           "light": "light", "heavy": "heavy", "violent": "violent", "none": "no rain"},
    "ha": {"caution": "A kula", "extreme_caution": "A kula sosai", "danger": "Haɗari",
           "extreme_danger": "Babban haɗari", "below": "ƙasa da matakin 'A kula'",
           "good": "Mai kyau", "moderate": "Matsakaici", "unhealthy_sensitive": "Mara kyau ga masu rauni",
           "unhealthy": "Mara kyau", "very_unhealthy": "Mara kyau sosai", "hazardous": "Mai haɗari",
           "light": "kaɗan", "heavy": "mai yawa", "violent": "mai tsanani", "none": "babu ruwan sama"},
}


def heat_index_c(temp_c: float, rh: float) -> float:
    """The NWS heat index in degrees C from air temperature (C) and relative humidity (%)."""
    t = temp_c * 9 / 5 + 32
    simple = 0.5 * (t + 61.0 + (t - 68.0) * 1.2 + rh * 0.094)
    if (simple + t) / 2 < 80:
        hi = simple
    else:
        hi = (-42.379 + 2.04901523 * t + 10.14333127 * rh - 0.22475541 * t * rh - 0.00683783 * t * t
              - 0.05481717 * rh * rh + 0.00122874 * t * t * rh + 0.00085282 * t * rh * rh
              - 0.00000199 * t * t * rh * rh)
        if rh < 13 and 80 <= t <= 112:
            hi -= ((13 - rh) / 4) * ((17 - abs(t - 95)) / 17) ** 0.5
        elif rh > 85 and 80 <= t <= 87:
            hi += ((rh - 85) / 10) * ((87 - t) / 5)
    return round((hi - 32) * 5 / 9, 1)


def heat_category(hi_c: float) -> str:
    return next((name for floor, name in HEAT_CATEGORIES if hi_c >= floor), "below")


def aqi_category(aqi: float) -> str:
    return next((name for floor, name in AQI_CATEGORIES if aqi >= floor), "good")


def rain_class(mm_per_h: float) -> str:
    return next((name for floor, name in RAIN_CLASSES if mm_per_h >= floor), "none")


def label(key: str, lang: str) -> str:
    return LABELS.get(lang, LABELS["en"]).get(key, key)


def percentile_rank(value: float, history: list[float]) -> float:
    """The share of the history's days (%) with less discharge than `value`."""
    if not history:
        return float("nan")
    below = sum(1 for x in history if x < value)
    return round(100 * below / len(history), 1)
