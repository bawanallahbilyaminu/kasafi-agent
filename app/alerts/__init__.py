"""Hazard alerts people sign up for (docs/hazard-and-services.md section 9, hazard step 6).

- `signup`: "Sanar da ni game da ambaliya a Goronyo" / "alert me about heat in Wamakko", or the ALERTS menu; an
  explicit OK before anything is stored; STOP / DAINA deletes the subscription; MORE asks about the last alert.
  No model: these are pattern and button replies, inside the 24-hour window.
- `triggers`: what fires, per hazard and LGA, from the hazard tables (official advisories, heat Danger, dust
  Hazardous or high for the season, rivers above the seasonal 95th percentile, a new NCDC report for Sokoto).
- `dispatch`: the limits (one per hazard per LGA per day, quiet hours 22:00-06:00 except official warnings, the
  global daily cap), the kasafi_hazard_alert template's values, and the dry run (on by default: alerts go to
  /admin/alerts, never to users).

A subscription is the user key (HMAC of the number), LGAs, hazards, language and created_at; nothing else.
"""
