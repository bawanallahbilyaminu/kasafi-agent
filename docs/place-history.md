# Place history (Tarihin wuri): satellite history for a pin, a ward or an LGA

Status: design for kasafi-agent, 31 Oct 2026. Put in `docs/place-history.md`.
Builds on `docs/question-planning.md` (capability catalog, plan → act → check), `docs/hazard-and-services.md` (location intake, privacy, maps) and the structured budget core.

## 1. What this adds

Kasafi tells people what years of satellite images show about a place, next to what the public documents say about it.

- **Farmers** send a pin from their farm (or name a village) and get the history of that plot: how green it was each rainy season since 2017 compared with that year's rain, how often it was under water in August–September, and whether bare soil is spreading nearby. With a chart and a map.
- **Planners** (ministries, ADP, partners) ask about a ward or an LGA and get the same measures across all its wards: where vegetation has declined most, where land floods most often, where bare soil is spreading. With a map, a ranking and the related budget lines.

Hausa name: **Tarihin wuri** ("history of a place").

### Principles

1. **Observation, not prescription.** Kasafi says what the images show. It does not diagnose causes ("your soil lacks nitrogen") or prescribe inputs, varieties or dates. For advice it refers to the state's agricultural extension service and quotes NiMet's official forecasts word for word.
2. **Rain first.** Every vegetation comparison is set against that season's rainfall, so a dry year is not mistaken for land decline.
3. **Honest about the sensor.** Every answer states the resolution (10 m, 30 m or 250 m), the years covered, and how many clear images each year had. Years with too few clear images are marked, never filled in.
4. **Every figure has a source and a date**, like the rest of Kasafi.
5. **Same location privacy as hazards.** Coordinates stay in memory for up to 30 minutes; only the LGA is stored with the user. Cached satellite results are keyed by a rounded grid cell, never by user.
6. **Out of scope (refuse politely):** insecurity, farm abandonment or patrol targeting; grazing routes or "safe" movement; land ownership or boundary disputes ("prove this land is mine"); credit or insurance certificates. These touch the security rule, conflict or legal stakes. Credit and insurance verification are a post-hackathon partnership idea (README roadmap only).

## 2. Data

Claude Code verifies current access terms and endpoints before building; nothing below is assumed to need a paid key.

| Layer | Source | Resolution / years | Use |
| --- | --- | --- | --- |
| Optical time series | Sentinel-2 Level-2A (e.g. Microsoft Planetary Computer STAC, or Copernicus Data Space) with its scene classification for clouds | 10 m, 2017→ | Farmer plot: NDVI (greenness), NDWI (surface water), BSI (bare soil) per scene |
| Long water history | JRC Global Surface Water (occurrence, recurrence, yearly history) | 30 m, 1984→2021 | "Under water in X of the years" for plot and ward |
| Vegetation for whole-state views | MODIS vegetation index (16-day) | 250 m, 2001→ | Ward and LGA trends without processing thousands of 10 m scenes |
| Land cover context | ESA WorldCover | 10 m, 2020/2021 | Is this cropland, shrub, built-up or water? Filters ward statistics to cropland |
| Rainfall | Open-Meteo historical weather (already a provider) | daily, 1940→ | Seasonal rain for each year at the point or ward centroid |
| Wards and LGAs | GRID3 wards and COD-AB LGAs (already loaded, PostGIS) | — | Aggregation units, P-codes |
| Official context | NiMet seasonal prediction, NIHSA flood outlook (already in the library) | — | Quoted beside the history |

Radar (Sentinel-1) sees through rainy-season clouds and is the better flood sensor, but it is heavier to process: phase 2, mentioned in the README.

## 3. Measures

For each year (rainy season = June–October unless the data says otherwise):

- **Peak greenness**: the 90th percentile of NDVI over clear observations in the season (robust to one bad scene), plus the count of clear observations.
- **Rain-adjusted change**: peak greenness compared with what that year's rainfall would predict from the plot's own history (a simple fit across years). "Lower than the rain would suggest" is the only decline claim allowed.
- **Wet-season water**: share of August–September clear observations where NDWI says water; JRC yearly history fills 1984–2016.
- **Bare soil**: dry-season (Feb–Apr) median BSI; trend in its share over the plot or ward.
- Trends are stated only when there are at least 5 usable years, with plain words ("rising", "falling", "no clear change") and the numbers in "show working".

## 4. The plot outline (SAM 3.1)

A pin is a point; a farm is a shape. To measure the plot, not just one pixel:

1. Take a Sentinel-2 true-colour chip around the pin (about 1 km square, clearest recent dry-season scene), upsample it for segmentation.
2. Ask SAM 3.1 to segment the object at the pin.
3. Accept the outline only if it contains the pin and its area is plausible (about 0.1 to 50 ha); otherwise fall back to a circle of about 1 ha around the pin, and say so.
4. Answers say "plot outline is approximate (from satellite, 10 m)". The outline is never presented as a boundary.

Same for a pond or fadama patch when the question is about water.

## 5. Answers

### Farmer (pin or village)

1. Progress line first: "I'm checking about 9 years of satellite images for this spot. I'll send it in about a minute." (first request); cached answers come in seconds.
2. Summary (2–3 sentences, user's language): how green the plot was this season compared with its own history and the rain; how often it was under water; bare-soil trend if relevant.
3. Details once: per-year figures in "show working".
4. **Chart image**: bars of peak greenness per year with rainfall as a line, flagged low-data years.
5. **Map image**: the plot outline on the satellite chip, wet-season water recurrence shaded, the LGA name.
6. Context from the library: NiMet's seasonal prediction for the LGA (quoted), the NIHSA outlook class if any, and the state's agriculture, irrigation or erosion budget lines for that LGA (structured core).
7. Referral line: "For advice on what to plant or apply, ask the agricultural extension workers (Sokoto ADP)" with a verified contact if Bilyaminu adds one.

### Planner (ward, LGA or state)

1. Summary: which wards stand out on each measure, with the period and resolution.
2. **Map image**: wards shaded by the chosen measure (vegetation trend, flood recurrence, bare-soil change), category legend, source stamp.
3. Ranking: top and bottom wards with figures; "show working" for all.
4. Budget link: relevant 2026 lines and project status for that LGA (agriculture, irrigation, erosion control, environment), neutral, no performance verdicts.

## 6. Capability catalog entries

`place_history_point` (farmer), `place_history_area` (ward/LGA/state), `plot_outline` (SAM 3.1), `rainfall_history`. Each declares measures, geo levels, years, resolution and freshness. All run through the planning loop.

## 7. Data model

`sat_cache` (grid cell or ward code, layer, year, values, clear_obs, source, computed_at), `ward_history` (ward P-code, measure, year, value), `plot_outline_cache` (grid cell, geometry, method, area). No table stores user coordinates or links a cell to a user.

## 8. Compute

- Point and plot requests run on demand (small windows of cloud-optimised images), with a progress message and a cache per ~100 m cell.
- Ward and LGA measures are **precomputed** once (MODIS for vegetation, JRC for water, WorldCover for cropland masks), as a batch job that can run on Modal (credits available) instead of the VPS, then loaded into `ward_history`.

## 9. Evaluation

- **Known pins**: Goronyo Dam reservoir (water every year), a built-up point in Sokoto city (low greenness, no water), a fadama point on the Sokoto–Rima floodplain (seasonal water), an irrigated plot (dry-season greenness), a northern bare area. Expected values from an independent brute-force script, not the code under test.
- **Rain adjustment**: a synthetic case where greenness falls only in a dry year must not be called a decline.
- **Low-data years** are flagged, never filled.
- **Guardrail cases**: land ownership, "safe route for my cattle", "which villages were abandoned", "give me a certificate" → polite refusal; "how green was my farm in 2024?" → answered.
- **Speed**: first request under ~90 s with a progress message; cached under ~10 s.
- **Privacy**: no coordinates in the database, logs or traces after a place-history conversation.

## 10. Order of work

See the prompts file: (1) data access and point history; (2) plot outline, farmer answer, chart and map; (3) ward and LGA precompute and planner answer; (4) evals, deploy, demo moment.

## 11. Step 1 as built (31 Oct 2026)

Access verified with small calls (`app/place/stac.py`, `app/place/history.py`):

| Source | How it is read | Key |
| --- | --- | --- |
| Sentinel-2 L2A | Planetary Computer STAC search; per scene one request to the data API's `item/bbox` route for the plot's window (the bands that month needs plus SCL, ~10 m grid, WGS84, ~1.6 KB); never a scene | none (optional `PC_SDK_SUBSCRIPTION_KEY=` raises the anonymous rate limit) |
| JRC Global Surface Water v1.3 (1984–2020) | occurrence, recurrence, seasonality from the same route (`jrc-gsw`) | none |
| JRC yearly history (1984–2024) | only published through Google Earth Engine: `scripts/jrc_yearly_ee.py` exports the water class per year clipped to Sokoto + 5 km into `data/place/jrc/yearly_<year>.tif` (outside git, synced like `data/geo`); `jrc_years` reads them when present | a Google account registered for Earth Engine, `uv run earthengine authenticate`, `EE_PROJECT=` |
| ESA WorldCover 2021 | majority class over the plot | none |
| MODIS 13Q1 v061 (step 3) | on Planetary Computer | none |
| Open-Meteo archive | daily rain 2015→ in one call; June–October sums per year | none (non-commercial terms, 10,000 calls/day) |
| Copernicus Data Space | catalogue open; downloads need a free account (`CDSE_CLIENT_ID=`, `CDSE_CLIENT_SECRET=`) — fallback only | account |

Decisions: NDVI and NDWI at 10 m, BSI and the cloud mask at 20 m (said in every answer); years from 2017, with 2015–2016 only where a year has 3+ clear season observations; a scene counts when half the plot's pixels are clear (SCL 4, 5, 6) and its value is the median over them; the baseline-04 reflectance offset is taken off; "below what the rain predicts" only more than 1 SD under the plot's own fit, with 5+ usable years; the cache is keyed by a 0.001° cell (~100 m) with a day-only date, no user or trace link. Water is also noted by month (February–October), since a reservoir or pond is wet in the dry season, not in August–September.

Checked: `scripts/place_check.py LAT LON YEAR --compare` (an independent brute-force implementation reading the signed COGs pixel by pixel) agrees with `app.place` on the Goronyo pin for 2024 (clear observations identical; NDVI p90 within 0.003; BSI within 0.023, the 20 m band on a 10 m grid). A first request for a pin takes about 40 s (12 years, ~470 scenes, 12 threads); a cached one is instant.

Fixes after the first pin run (31 Oct, evening): no greenness trend or rain-adjusted claim where the place isn't vegetation (WorldCover 2021 built-up, bare or water, or peak NDVI under 0.2 in most years: the answer says what the 2021 map labels it, never asserts it); a year enters the fit, the flags and the trends only with **8+** clear season images (2016 had been flagged "below the rain" at 5 of 11 pins on 4–7 images), a figure from 3+ is shown hatched; for a water question on a pin that isn't water, the nearest JRC water body (occurrence ≥ 50 %) within 2 km gets its own history, "X km from your pin"; the Earth Engine export is dropped (its non-commercial terms don't fit a startup product; the JRC yearly history stays on the README roadmap).

## 12. Steps 2 and 2b as built (31 Oct 2026)

**Plot outline** (`app/place/outline.py`, `plot_outline_cache`, migration 0020): a 1 km true-colour chip (B04/B03/B02, 10 m, the chip's own 2nd–98th percentile stretch so field edges show on bright Sahel soils) from the clearest dry-season scene of the last two seasons, upsampled 8× to 800 px, one SAM 3.1 call with a positive point prompt at the pin. SAM's mask covers its box, not the frame (placed at x1, y1; decoded with Meta's `meta-sam-parser`). Accepted when it holds the pin and measures 0.1–50 ha; else the 1 ha circle, and the answer says so. On the 11 pins: 5 outlines accepted (Wurno 5.1 ha, Illela 3.8 ha, Goronyo downstream 0.8 ha, Kware Lake 14.0 ha = the lake itself, Sokoto market 10.2 ha), 6 fell back (a point on featureless sand or dense fadama returns the whole chip → "too big"). One call takes 3–10 s. Samples: `data/samples/place/outline_*.jpg`.

**Farmer answer** (`app/place/answer.py`, catalog `place_history_point`, `plot_outline`, `rainfall_history`): routed in code from the words (a place word with a history word, or "tarihin wuri"; money, forecast and facility words keep their paths), answered from the numbers with no model: the summary (this season against the plot's own years and the rain; trends; water/flood evidence), the outline line, the resolution line, the years and clear-image counts, then NiMet's seasonal prediction and NIHSA's outlook for the LGA and the LGA's agriculture/irrigation/erosion lines from the structured core (quoted, cited), the ADP referral, the sources; the per-year table in "show working". Without a pin the reply is the location-request button and the question waits for it (`needs_pin`, resumed on the pin). Progress line on a first request. Timings: first request 42–48 s (Sentinel-2 history) + 10–17 s radar + 3–10 s outline; cached 0.04 s. Guardrails (`app/guardrails/scope.py`): a new `land` category (ownership, boundaries, certificates; budget lines about land stay figures), grazing routes and abandoned villages under `security`.

**Images** (`app/place/images.py`): the chart is two panels on one time axis (peak greenness bars, hatched for years under 8 clear images, ▼ for "below what the rain predicts"; June–October rain as a line below; the clear-image count under each year), never two scales on one plot; the map is the outline on the chip with JRC water frequency shaded in one blue ramp, the nearest water body (the chip widens to reach it) and a scale bar. Hausa or English, ~100 KB JPEGs, source stamps.

**Floods that see through cloud** (`app/place/radar.py`, `app/place/floods.py`, step 2b): Sentinel-1 RTC on the Planetary Computer is keyless through the same `item/bbox` route (0.6–1.3 s a window). Per July–October pass since 2017 the plot's median VV is read; under **−15 dB** the plot counts as open water. Set against known pixels (July–October 2024 medians): the Goronyo reservoir water pixel −19.4 to −16.6 dB, Sokoto Central Market −2.3 to +0.9 dB, Dundaye floodplain cropland −12.5 to −5.4 dB. Run on the pins: the reservoir reads water on every pass, 96 of 96 in 2017–2026; Kwalkwalawa (191 passes) and Dundaye (121 passes) never (VV −13 to −5 dB): no open water on those fadama plots in any July–October pass, which the answer says as "no flood water seen", with the reason (water under crops reads bright, not dark). Official maps: UNOSAT's VIIRS 375 m water extents over Nigeria on HDX (CC BY-SA; 1–25 Oct 2022, 5–9 Sep 2024, 9–13 Nov 2024; nothing for 2020), clipped to Sokoto + 5 km by `scripts/fetch_floodmaps.py` into `data/place/floodmaps/*.gpkg` (outside git, synced to the server like `data/geo`; unosat.org serves ~17 KB/s). The answer combines radar passes, Sentinel-2 water months and the official maps, and never says "never flooded".
