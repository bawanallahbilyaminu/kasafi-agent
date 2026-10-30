"""Hazard information (docs/hazard-and-services.md section 4): scheduled fetchers write each layer into
hazard_values (with source, issued_at and fetched_at); answers and maps read from there, never from a live call.

- categories.py: the named scales (NWS heat index in degrees C, US AQI with the WHO guideline, WMO rain intensity,
  discharge against the point's own history, "satellite heat detections").
- points.py: where values are fetched (LGA centroids, a ~0.1 degree grid, river points).
- fetch.py: the fetchers (Open-Meteo forecast, air quality, flood; NASA FIRMS) and their schedule.
- read.py: what an answer needs (a day's summary for an LGA, a point or the state), and how old the data is.
- answer.py: the planner capabilities' answers (weather_forecast, air_quality, river_flood, fire_detections).
"""
