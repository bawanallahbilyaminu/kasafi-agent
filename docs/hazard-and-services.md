# Hazard information and nearest services

Status: design for kasafi-agent, 30 Oct 2026. Put in `docs/hazard-and-services.md`.
Builds on `docs/question-planning.md` (capability catalog, plan → act → check loop) and `data/source_registry.yaml`.

## 1. What this adds

Kasafi answers, for any place in Sokoto State:

- **Hazards now and next**: heat, harmattan dust, rain, river floods, disease outbreaks, fires.
- **Official warnings and advisories** from NiMet, NIHSA, NEMA/SEMA, NCDC and the State Ministry of Health, quoted word for word.
- **Nearest health facility**, with distance, travel time, a tap-to-navigate location pin and a route map.
- **Maps**: Sokoto shaded by LGA for heat, dust or rain, and a "you and the nearest facilities" map.
- **Alerts people sign up for**: e.g. "tell me about floods in Goronyo".

Name it **hazard information** (Hausa: *Bayanan haɗari da yanayi*), not "emergency response". Kasafi informs and points people to help. It does not coordinate responders.

### Principles

1. **Official first.** An official warning (NiMet, NIHSA, NEMA/SEMA, NCDC) always leads. Model forecasts follow, labelled as forecasts.
2. **No medical advice.** Official public guidance is quoted word for word with its source. Nothing is tailored to a person's symptoms. Anything that sounds like an emergency gets the fast path in section 7.
3. **No security content.** No attacks, incidents, armed groups or "safe routes" (the existing rule 5 and the source registry's global exclusions).
4. **Location is sensitive personal data** under Nigeria's Data Protection Act 2023. It's used for the request only, and only the LGA is kept (section 3).
5. **Every figure carries its source and time**: "Open-Meteo/ECMWF forecast, issued 06:00 today".
6. **Answer when asked; alert only those who sign up.**

## 2. Geo foundation

Enable **PostGIS** in the existing Postgres (same Docker image family, or `CREATE EXTENSION postgis` where available; Azure Flexible Server also supports it).

| Layer | Source | Use |
| --- | --- | --- |
| LGA boundaries (23) | **OCHA COD-AB from HDX** (`data/geo/sokoto_lga_codab.geojson`): `admin2Name`, `admin2Pcod` (NG034001…), `admin1Pcod` NG034, valid from 2017; lon/lat (CRS84) | Point → LGA; "outside Sokoto"; choropleth maps. **P-codes are the join key** for IOM DTM and HDX data |
| Ward boundaries | **GRID3 operational wards** (`data/geo/sokoto_wards_grid3.geojson`): `wardname`, `wardcode`, `lganame`, `lgacode` (GRID3's own codes, e.g. Tureta 620), source INEC, "Operational Validated", 2019 | Point → ward for finer wording |
| LGA crosswalk | Built in step 1: COD-AB name and P-code ↔ GRID3 `lganame`/`lgacode` ↔ facility file `lga` ↔ names used in budgets and DTM (e.g. Wamako/Wamakko, Dange-Shuni/Dange Shuni) | One LGA identity everywhere |
| Settlements / place names | GRID3 settlement names, OSM place nodes | Turn typed places ("Kasuwar Gwadabawa", a village) into a point |
| Health facilities | **GRID3 + federal Health Facility Registry (NHFR) 2024** (`data/geo/health_facilities_nga.geojson`, national file; filter `state == "Sokoto"`): `nhfr_uid`, `nhfr_facility_code`, `facility_name`, `lga`, `ward`, `lga_name_disagreement`, `ward_name_disagreement`, `ownership`, `ownership_type`, `facility_level` (Primary/Secondary/Tertiary), `facility_level_option`, `latitude`, `longitude`, `geocoordinates_source` (NHFR_2024 or GRID3_EHEALTH), `last_updated` (Nov 2024). No functional-status or phone fields. Licence not yet confirmed: keep out of git, credit "GRID3 Nigeria / NHFR" | Nearest facility; the NHFR code links to the official registry |
| Roads | OpenStreetMap extract for Sokoto (Geofabrik Nigeria, clipped with osmium) | Drawing our own base map (no third-party tiles) |
| Rivers and dams | OSM waterways; GloFAS river points | Flood layer and maps |

### Facility import and data quality

On import, produce a report and fix or flag:

- the count after filtering the national file to Sokoto, by level and ownership;
- coordinates outside Sokoto's boundary, or 0/0;
- points whose LGA or ward from the boundaries disagrees with the file's own `lga`/`ward`, alongside the file's `*_name_disagreement` flags;
- border mismatches between the two boundary layers (a point inside ward W of LGA X but inside LGA polygon Y). Rule: the COD-AB LGA polygon decides the LGA; the ward is used for wording only when its `lganame` matches;
- duplicates (same name within ~200 m);
- missing names, types or LGAs; LGA in the attributes vs LGA from the point disagreeing;
- facility level (primary / secondary / tertiary), ownership (public / private / faith-based), and functional status where present.

Store the source, the data's own date and the import date. Every facility answer carries one line: "Facility list: GRID3 Nigeria / NHFR, updated Nov 2024; opening hours and services aren't confirmed. Call ahead if you can." Link facilities to **EmONC capability** (basic / comprehensive emergency obstetric and newborn care) by matching names against the UNFPA EmONC assessment already in the library. A link is used only when the match is confident, and every link is listed in the report for Bilyaminu to confirm.

## 3. Location intake and privacy

Ways a location arrives:

1. **Location pin** (WhatsApp inbound `location` message: latitude, longitude, optional name and address).
2. **Location request button**: when a question needs a place and none is given, send a WhatsApp *location request message* ("Share location" button).
3. **Typed place**: an LGA, ward, town, village or landmark, geocoded against our own gazetteer (no external geocoder needed for Sokoto names).
4. **LGA on file**: if the user chose a home LGA for alerts, use it when they say "here".

Privacy rules:

- **First use**: one short consent line, in both languages: "Kasafi will use your location only to answer this and won't keep it. Only your LGA is remembered for follow-ups."
- Exact coordinates are kept **in memory for up to 30 minutes**, for follow-ups like "route?" or "the next one?". They are never written to the database, logs or traces. Traces show only "location: Wamakko LGA (pin)".
- The LGA may be stored as `last_lga` on the user record (90-day retention, as now).
- Update `docs/site/privacy.md`: location use, what's kept (LGA only) and for how long. Then update the website copy.

## 4. Hazard layers

Each layer is a scheduled fetcher → table `hazard_values` (layer, lga_code or point_id, valid_time, value, unit, source, issued_at, fetched_at) → answer cards and maps. Fetch for each **LGA centroid** plus a **grid of about 0.1°** over the state for maps.

| Layer | Source (all free) | Refresh | Measures | Categories and labels |
| --- | --- | --- | --- | --- |
| Heat | Open-Meteo forecast API | every 3 h | temperature, apparent ("feels like") temperature, relative humidity, UV index, wind | Heat index categories of the US National Weather Service, in °C: Caution 26.7–32.2, Extreme caution 32.2–39.4, Danger 39.4–51.1, Extreme danger ≥51.1. Name the scale in answers. NiMet heat advisories override. |
| Harmattan dust and air quality | Open-Meteo Air Quality API (Copernicus CAMS) | every 6 h | dust, PM10, PM2.5, aerosol optical depth | US AQI categories for PM10/PM2.5; quote the WHO 24-h guideline (PM10 45 µg/m³, PM2.5 15 µg/m³) as reference |
| Rain | Open-Meteo forecast | every 3 h | precipitation (mm), probability, next 24 h / 3 days | Heavy rain thresholds stated with their source |
| River floods | Open-Meteo Flood API (GloFAS river discharge, daily, with history) at chosen river points (Sokoto River near Sokoto city, Rima near Goronyo, Rima toward Kebbi border; confirm points against the GloFAS grid) | daily | forecast discharge (m³/s) for the coming days | Compare with each point's own history: "higher than X% of days since 1984". Never call it an official flood warning. |
| Flood risk (official) | NIHSA Annual Flood Outlook (yearly list of high/moderate-risk LGAs), NEMA/SEMA flood alerts, NIHSA alerts | on publication | LGA risk class, alert text | Quoted verbatim, with issue date |
| Disease outbreaks | NCDC weekly situation reports (cholera, cerebrospinal meningitis, Lassa fever, measles, diphtheria), WHO AFRO; State MoH announcements | weekly | suspected/confirmed cases and deaths for Sokoto, epi week | State level; say the epi week; no advice beyond quoted official guidance |
| Fires | NASA FIRMS active fire detections (VIIRS), free MAP_KEY | every 3 h | hotspots in Sokoto's bounding box | Call them "satellite heat detections (could be bush, farm or other fires)" |

Notes:

- Open-Meteo's free tier is for **non-commercial use** within its daily call limits. That's fine for the pilot; budget a subscription before charging for Kasafi. Cache everything; one fetch serves all users.
- **Seasonality** shapes what's useful: harmattan dust (about Nov–Feb), meningitis season (about Dec–Jun), heat peak (about Mar–May), rains and floods (about Jun–Oct). Answers to "what should I watch out for?" lead with what's in season.
- Use **Muse Spark vision** to read NCDC and NIHSA PDFs whose tables are images (the same pattern as budget pages). Every number still goes through the code check.

## 5. Official advisories

Add to `data/source_registry.yaml` a topic `hazards_and_advisories` with publishers NiMet (nimet.gov.ng: seasonal climate prediction, daily and impact-based forecasts), NIHSA (nihsa.gov.ng: Annual Flood Outlook, alerts), NEMA (nema.gov.ng), Sokoto SEMA, NCDC (ncdc.gov.ng: situation reports, advisories) and the State MoH. Crawl their pages on a schedule like the SBS library.

Table `advisories`: source, title, issued_at, valid_until, hazard, LGAs covered (or "state-wide"), verbatim text, URL, language. Answers quote the **current** advisories (valid now) first, with the issue date. Expired ones are dropped, or mentioned as "the last advisory, issued X, has expired".

**Built (Oct 30–31):**
- Crawl (`app/hazards/advisories.py`, `KASAFI_ADVISORIES_FETCH=true` on the server): text sources daily at 06:00 and NCDC Mondays at 07:00 (Lagos), capped by `KASAFI_ADVISORIES_MONTHLY_USD` ($2).
- Official outlooks (NIHSA AFO 2026, NiMet SCP 2026 and its August update) come from `data/official_outlooks.yaml`. Every quote is verified on its page (`scripts/official_outlooks.py`). An official outlook leads over GloFAS, which is labelled a model estimate.
- **Alert status is definitive** (`official.checked_status`):
  - when the crawl succeeded within 24 h: "No active alert from NEMA, SEMA or the Ministry of Health for {place} as of 06:00 today";
  - otherwise: "Last checked 2 days ago (29 Oct); no alert … then";
  - when no check has ever succeeded, it says so. It never says "none" without a successful check.

## 6. Nearest health facility and routing

`nearest_facilities(point, filters)`: a PostGIS nearest-neighbour query with optional filters for level, ownership, EmONC capability and functional status. Return the top 3 by straight-line distance, then get road distance and time for those 3.

**Routing (in order of preference):**

1. **OpenRouteService** directions API (free key; check its daily limits on the plans page): car and foot profiles; distance, duration and route geometry.
2. If ORS is unavailable: straight-line distance with "about X km in a straight line; road distance may be longer".
3. Later, optional: self-hosted OSRM on a Sokoto + neighbours OSM extract if volumes grow.

**What the user receives:**

1. A short text: the 3 nearest facilities with name, level, distance and estimated travel time by car, and "Kasafi can't confirm opening hours or services; call ahead if you can."
2. A **WhatsApp location message** for the nearest one (name and address filled in). Tapping it opens the phone's maps app, which gives turn-by-turn directions.
3. A **route map image** (section 8) when ORS gave a route.
4. A Google Maps directions link built from the URL scheme (no API key) as a fallback for phones where the pin doesn't open navigation.

**Built (Oct 31): facilities are a planner capability** (catalog entry `facilities`, need measures `facility_count` and `facility_lookup`; `app/geo/facility_info.py`):
- **Counts** come from the GRID3 / NHFR registry, by type, ownership, level, LGA or ward. "How many PHCs" gives the registry's Primary Health Centres and all primary-level facilities, and offers the UNFPA EmONC figure as "the facilities it assessed". A question about building, budgets or a year is a projects question, not a count.
- **A facility by name**, fuzzy-matched ("What about Arkilla PHC"), gives a card: type, level, ownership, ward and LGA from the registry, plus its EmONC status.
- **Routes:** "I want to go to X" or "how far is it from me" gives the road distance and time, the pin, the directions link and the map. With no location on file, Kasafi asks for one and answers when it arrives. This works by voice too.
- **"Hospital" / "asibiti"** means hospital-level facilities (secondary, tertiary). A facility of any kind at under half the distance gets its own line ("Nearer, but not a hospital: …"). With road times known, the list is ordered by time.
- **A facility named in the message wins** over the "route / next / how far" shortcuts to the last list.
- **Verified corrections** (`data/geo/facility_corrections.yaml`, outside git; `app/geo/corrections.py`) override
  the registry's location, name, level or type at import (`scripts/import_geo.py`, or `--corrections` alone). Each
  needs `verified_by` and `verified_on`. Answers say "(location checked 1 Nov 2026)".
- **Ward wording:** within 300 m of a ward border (the 2019 GRID3 wards can be off near their edges), say "Wamakko
  LGA (likely Bado ward)"; otherwise name the ward plainly.
- **Location on every path** (`app/geo/location.py`): "my LGA", "near me" and "from me" carry the LGA on file to the planner, so budget, topic and hazard questions use it. A place named in the question overrides it. The point is kept in memory for 30 minutes, the LGA in the user record.

## 7. Emergency fast path

Detect emergency language in Hausa and English, text or voice. Examples: heavy bleeding, not breathing, unconscious, convulsions/fits, a snakebite, a burn, a child very hot and not waking, labour complications, a drowning or flood trapping, a fire. This is a **classifier plus a phrase list**; err on the side of triggering.

Behaviour (target: reply in under 3 seconds, before any document search):

1. One line: "This sounds like an emergency. Get help now." in the user's language.
2. **Verified emergency numbers** from a table Bilyaminu maintains (`data/emergency_contacts.yaml`: number, service, area, verified_on). 112 is Nigeria's national emergency number, but its rollout is still being finalised, so list only numbers confirmed to work in Sokoto. Never show an unverified number.
3. If a location is known (pin or LGA): the nearest suitable facility (for labour or bleeding in pregnancy, prefer comprehensive EmONC facilities when known), plus the location pin.
4. If no location is known: the location request button, with "or tell me your LGA or town".
5. **No medical instructions.** At most, quote an official first-aid line from an approved source if one is added later. Not now.

Log only that the fast path fired (no message text) for quality review.

**Built (Oct 31):** with a point on file, the picks get ORS road distance and time within 1.5 s ("6 km by road, about 12 min"), plus a Google Maps driving link. If ORS is slow or down, the reply shows the straight line and says so, and the whole reply stays under 3 s (`tests/test_phone_fixes.py`). From an LGA centre only, there is no ORS call. From the dev machine ORS took 1.4–4.3 s, so the fallback is common there; check its rate on the server.

## 8. Maps and images

Render server-side with geopandas and matplotlib, on our own base layer: LGA boundaries, main roads and rivers from the OSM extract. No third-party map tiles, so no tile-policy issues. OSM data is credited ("© OpenStreetMap contributors").

| Map | Contents |
| --- | --- |
| Hazard choropleth | Sokoto by LGA, coloured by the day's max heat index, dust or rain; legend with category names; title, valid time and source stamped on the image; the user's LGA outlined if known |
| Near you | user's point (rounded to ~1 km on the image), the 3 nearest facilities numbered, the route line to number 1, the LGA name |
| River flood | river points with this week's level vs history |

**Built (Oct 31, after review of `data/samples/`; regenerate with `scripts/map_samples.py`):**
- Choropleths print each LGA's value ("37°", "182"). Every fill is exactly a legend colour; the numbers show the
  differences within a category (shading by value within a category was tried and dropped on Oct 31 because it made
  colours that aren't in the legend). A legend line says what colour and numbers mean. The Sokoto city LGAs are
  labelled in a stack to the south-east, with leader lines.
- Air uses the US EPA AQI colours (green, yellow, orange, red, purple, maroon).
- Near-you: framed on the user's circle, the nearest facility and any other within 15 km (at least ~2 km across).
  Farther facilities are in the legend only, marked "(beyond the map)". Town names use the official LGA spelling
  (Silame, not OSM's "Salame"). Text is at least 28 px for titles
  and 20 px for labels. The legend gives "1. Goronyo General Hospital: 10.9 km, about 15 min". There is a scale bar,
  and the town nearest the user is always labelled. Markers are kept apart, and clear of the user's circle, with
  leader lines. Vague names get their town ("Bone Centre, Wurno"). One map per answer, and not the same map again
  within 10 minutes.
- River map: titled "River levels today vs. normal for late October", with each label joined to its point by a
  leader line.
- A map whose data is older than twice the fetch interval says "(older than usual)" next to its fetch time.

**Every hazard answer sends one map (Oct 31, `maps_for` in `app/agent/answer.py`, `app/maps/render.py`)**, right
after the text, with a caption repeating the key number:
- **Layer:** the one asked (several asked: the most severe).
- **View:**
  - about 10 km around the user's point (pin, saved location or a named town);
  - the LGA and its neighbours when only an LGA is known;
  - the whole state when the answer is state-wide or asked for ("Sokoto", "all LGAs", "taswirar jiha").
- **The ~10 km view** labels the value at the user's point in its category's exact colour, with nearby forecast
  points and their own values. Air shows the CAMS ~40 km cell edges dotted and says "model grid ~40 km". Nothing is
  interpolated.
- **Rivers:** the frame reaches the nearest river point. **Fires:** satellite detections on the view.
- **Caching:** state and LGA maps per layer, view and hour; a point's map 30 minutes, keyed by the ~1 km point.
- **If a map can't be drawn,** the reply says so.

Images in Hausa or English to match the user. Colour-blind-safe palette with clear category labels. Cache per layer per hour. Each image's caption repeats the key number in text, for users on slow data.

## 9. Alerts people sign up for

- **Sign up**: "Sanar da ni game da ambaliya a Goronyo" / "Alert me about heat in Wamakko", or a menu: choose LGA(s) and hazards (heat, dust, floods, outbreaks).
- Store: phone hash, LGAs, hazards, language, created_at; stop with "DAINA" / "STOP". Explicit consent text on sign-up.
- **Triggers**: a new official advisory covering the LGA, heat index reaching Danger, dust at "Hazardous" or high for the time of year, river discharge above the point's 95th percentile, or a new NCDC report showing an outbreak in Sokoto.
- **Limits**: at most 1 alert per hazard per LGA per day; quiet hours 22:00–06:00 except official warnings.
- **WhatsApp requirements**: messages sent outside the 24-hour window need **approved utility templates** (Hausa and English) and a payment method on the WhatsApp Business Account, because each delivered alert is charged. Template approval takes time, so submit templates in the first build step.
- Alert text: hazard, LGA, time, source, and "reply MORE for details or a map".

**Built (Oct 31), dry run only, not deployed** (`app/alerts/`, tests in `tests/test_alerts.py`):
- **Sign-up** (`signup.py`, no model): "Sanar da ni game da ambaliya a Goronyo" / "alert me about heat in Wamakko",
  or ALERTS / FAƊAKARWA for the menu (1 Heat, 2 Dust, 3 Floods, 4 Outbreaks, 5 All, then LGAs, in one reply). A
  missing LGA comes from the LGA on file, else is asked for. A confirmation says what is kept and how to stop, with
  three buttons: *Yes, sign me up* / *No* / *Just answer now* (the Hausa wording can also be a question). Language:
  the user's own (HAUSA / ENGLISH changes it). Stored in the SQLite user store (`alert_subs`: user key, LGAs,
  hazards, language, created_at), so DELETE MY DATA removes it. STOP / DAINA (typed or the template's button) deletes
  it. MORE asks "What is the {hazard} situation in {LGA} today?" about the latest alert.
- **Triggers** (`triggers.py`): a new official advisory (issued in the last 3 days, current) for the LGA or
  state-wide; heat Danger today or tomorrow; dust at Hazardous, or at least Very unhealthy (AQI 201+) and above the 95th percentile of
  the LGA's last 30 days (table `air_daily`, migration 0016; needs 20 days of history); a river point above its
  seasonal 95th percentile within 2 days; a new NCDC report whose Sokoto figures rose. Stale layers fire nothing.
- **Limits** (`dispatch.py`): a key is never sent twice; one alert per hazard per LGA per Lagos day; quiet hours
  22:00–06:00 hold everything but official advisories until 06:00; `KASAFI_ALERTS_DAILY_CAP` template messages a
  day for all users (0 = none live). Values are one line with no closing full stop. A language not in
  `KASAFI_ALERT_TEMPLATE_LANGS` (default `ha`; English is in review) is skipped and logged.
- **Dry run** (`KASAFI_ALERTS_DRY_RUN=true`, the default; checks run only with `KASAFI_ALERTS=true`): each decision
  goes to `alert_log` and `/admin/alerts` (template values, recipients by language, status), never to users.
- **Recipients (decided Oct 31):** only for people who sign up, the WhatsApp number is stored encrypted (Fernet,
  `KASAFI_ALERTS_NUMBER_KEY`; `app/alerts/recipients.py`). It is decrypted only to send the template, and never
  logged or shown. It is deleted with the subscription on STOP / DAINA, DELETE MY DATA, or 90 days without a message
  (`last_contact_at`, pruned each alerts round). Everyone else stays hash-only. Sign-ups made before the key was set
  have no number; their sends are logged as not delivered.

## 10. Answer patterns (examples)

- "Yaya zafin rana yake a Wamakko yau?" → today's and tomorrow's max temperature, feels-like and category, any NiMet advisory, plus the heat map.
- Location pin + "Akwai ambaliya kusa da ni?" → LGA from the pin; NIHSA outlook risk class for the LGA; current NEMA/SEMA alerts; nearest river point forecast vs history; "no official warning now" when true.
- "Ina asibiti mafi kusa?" (no location) → location request button → 3 nearest facilities, the pin, the route map.
- "Akwai sankarau a Sokoto yanzu?" (meningitis) → latest NCDC situation report figures for Sokoto with the epi week, plus quoted official guidance.
- "What should we watch out for this week in Goronyo?" → in-season hazards ranked by current values and advisories.

All of these go through the planning loop as capabilities, not a separate bot.

**Answer format (Oct 31, every answer type):**
1. An executive summary: 1–3 plain sentences that answer directly, in the user's language.
   - Facility and emergency summaries are written in code.
   - **Hazard summaries are written in code (Oct 31, `app/hazards/summary.py`)**: 2–3 sentences that synthesise and never repeat the details:
     - the category with its meaning quoted from the scale's owner (US EPA for AQI, the NWS for heat; Hausa marked "fassarar Kasafi");
     - PM2.5 / PM10 as multiples of the WHO daily guideline;
     - what drives it (the pollutant setting the AQI; air temperature vs heat index);
     - tomorrow vs the day asked, and the LGA's place among the 23 when it's near either end;
     - the official warning status as the last sentence.

     The details then leave out the "no active alert" line, and "model forecasts, not official" appears once.
   - Official-outlook and topic summaries are written by Muse Spark (`app/agent/summary.py`) from the answer's own details. Any figure the details don't print drops the summary.
   - Budget answers already lead with their synthesis.
2. The details: figures, bullets, map.
3. One compact sources line, e.g. "📄 NiMet, 2026 Seasonal Climate Prediction p. 12–16; NiMet SCP Update p. 3".

Verbatim quotes are kept back, stored with the turn and sent on "quotes" / "nuna rubutun", with their pages and no model call.

## 11. Capability catalog entries (add to `data/catalog.yaml`)

`weather_forecast`, `air_quality`, `river_flood`, `flood_outlook_official`, `advisories`, `outbreaks_ncdc`, `fire_detections`, `facilities_nearest`, `routing`, `map_render`, `geocode_place`, `emergency_fast_path` (runs before the planner).

Each declares its measures, geo levels (point, LGA, state), time coverage and freshness, as in the planning design.

## 12. Data model (new tables)

`lga`, `ward` (PostGIS geometry), `place` (gazetteer), `facility`, `facility_capability`, `hazard_values`, `advisories`, `river_point`, `alert_subscription`, `alert_sent`, `map_cache`. No table stores user coordinates.

## 13. Evaluation

- **Location fixtures**: one pin inside each LGA, pins near LGA borders, and pins just outside the state (→ "outside Sokoto").
- **Nearest-facility checks** against a brute-force distance calculation.
- **Emergency phrases**: 40+ in Hausa and English (text and transcribed voice) must hit the fast path; 40+ non-emergency health questions must not.
- **Hazard questions**: generated families per layer × LGA × time (today, tomorrow, this week) × language, with expected values taken straight from `hazard_values`.
- **Stale-data cases**: a fetcher that fails must produce "data from X hours ago" or "not available now", never old data passed off as current.
- **Image tests**: maps render, have a legend and source stamp, and stay under WhatsApp's size limit.
- **Privacy test**: after a location conversation, no coordinates are in the database, logs or traces.

## 14. Order of work

See the prompts file: (1) foundations, location, privacy, templates; (2) hazard layers; (3) advisories and outbreaks; (4) facilities, routing and the emergency fast path; (5) maps; (6) alerts; (7) evals, docs, deploy and the demo.
