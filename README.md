# Kasafi

**Kasafi** is a Hausa, voice-first WhatsApp agent for public budget and policy documents in Sokoto State, Nigeria.

Citizens, civil servants and development partners send a voice note or text in Hausa (or English) and ask about state budgets, budget performance reports, policies, development plans and development partner reports. Kasafi plans which documents it needs, finds and indexes any that are missing from trusted sites, pulls out the evidence, verifies every claim and replies with:

- a short, plain answer in the user's language
- citations (document and page) for every claim
- a cropped image of the source table or row

Kasafi gives neutral, cited facts only. It does not give opinions on politics, does not cover conflict or security topics, and does not give medical or nutrition advice.

> Entry by Halal Numeriq Limited (Startups track) in the **Meta Global AI Developer Hackathon** (Oct 26 – Nov 4, 2026). Problem statement: *Build for Your World*.

## Meta models used

- **Muse Spark** (Meta Model API): planning, tool use, answering, verification
- **Muse Spark Open** (open weights, served via Baseten): the second, independent reading of every budget-line answer (below)
- **Muse Voice Transcribe**: Hausa voice notes to text
- **SAM 3.1**: crops of the source tables used as evidence

### Where Muse Spark Open runs

For a budget-line question, line search finds the 40 most relevant printed budget rows. Two models then read them **independently and at the same time**, and each picks the rows that answer the question:

| Reading | Model | Where in the code |
|---|---|---|
| 1 | Muse Spark (`muse-spark-1.3`, Meta Model API) | `read_lines` → `_read_once` in [`app/agent/line_answer.py`](app/agent/line_answer.py) |
| 2 | **Muse Spark Open** (`meta-models/muse-spark-open-1026`, Baseten) | `read_lines` → `_second_reading` in [`app/agent/line_answer.py`](app/agent/line_answer.py); the client comes from `open_reader` in [`app/agent/answer.py`](app/agent/answer.py) |

Code then compares the two picks (`reconcile`). Rows both models chose are answered and added up. Rows only one model chose are shown as "possibly relevant, not counted". If the two picks share nothing, Kasafi asks the user which reading they meant. A second opinion from a different model, with open weights, catches rows that one model misreads, and code does all the arithmetic either way.

- **Reasoning:** Muse Spark Open always reasons, and `max_tokens` covers reasoning plus answer. Its reasoning comes back in `reasoning_content` and is kept apart from the answer ([`app/providers/chat.py`](app/providers/chat.py)). Only the JSON answer is parsed. Kasafi asks for `reasoning_effort="low"` and leaves 8,000 tokens of room.
- **Fallback:** if Muse Spark Open errors, or takes longer than `KASAFI_OPEN_READ_TIMEOUT_S` (default 20 s), Muse Spark does the second reading instead. The log line is `Muse Spark Open reading fell back to Muse Spark`. Baseten slowness never blocks an answer.
- **Trace:** each answer records which model did each reading (`LineResult.readers`). The admin trace page shows this.
- **Switch:** `KASAFI_OPEN_READER=false` turns it off. Without `BASETEN_API_KEY` it's off too.

**Measured on Oct 29.** Same code and questions, run one after the other: our 39 mid-tier test questions ([`evals/complex`](evals/complex)), then the 10-case main suite twice.

| | Reading 2 on Muse Spark Open | Both readings on Muse Spark |
|---|---|---|
| 39 questions: answered / partial / not found / clarify | **18 / 13 / 6 / 2** | 16 / 17 / 6 / 0 |
| Median time per question | 14.0 s | 13.8 s |
| Muse Spark Open reading time (35 readings) | median 3.4 s, max 6.7 s | – |
| Fallbacks to Muse Spark / provider retries | 0 / 0 | – / 0 |
| Main suite | 20/20 passed, median 10.2 s | – |

Reports: [`mid_tier_report_step13_open.md`](evals/complex/mid_tier_report_step13_open.md) and [`mid_tier_report_step13_meta.md`](evals/complex/mid_tier_report_step13_meta.md). Single runs vary by a few questions either way. Muse Spark Open adds no noticeable time, because the two readings run at the same time.

## Structured budget core and analysis tools

At indexing, the extracted tables become three entity tables, with one column per year and measure as printed. Code builds them in [`app/retrieval/entities.py`](app/retrieval/entities.py) (migration 0009):

- `budget_items`: one row per budget line. Each row has its classification, kind of spending, code and name, and the ministry or agency it belongs to. Lines in a per-agency table belong to the agency section they're printed under.
- `projects`: one row per capital project in a budget's statewide project list. Each row has the MDA, economic, function and location codes and names, the amounts and the page. Rows are parsed from the page text by their code anchors. Where a row leaves empty cells blank, its numbers are placed by where they're printed in the PDF.
- `perf_items`: one row per implementation-report line. Each row has the original, revised and final budget, the quarter's spending and the spending so far this year.

**Reconciliation checks** run at every build. Their counts and failures are stored in `entity_builds`, and `scripts/build_entities.py --examples` prints them.

| Check | 2026 budget | 2025 budget |
|---|---|---|
| Projects | 1,709 add up to ₦553.14 bn of the printed ₦553.34 bn | 1,693 add up to ₦347.40 bn of ₦347.48 bn |
| Projects = each MDA's capital | 633 / 636 | 614 / 624 |
| Agencies → ministry → sector → total | 1,740 / 1,752 | 1,500 / 1,530 |
| Personnel + overhead + debt + capital = total, per MDA | 1,038 / 1,038 | 1,020 / 1,020 |
| Functional total = administrative total | 18 / 18 | 18 / 18 |

- **Known gaps.** On the location pages, table titles are carried over and rows from different tables are interleaved, so the location checks fail. That's why LGA answers use the project list, not the location table.
- **One unplaced row.** One 2026 project row (₦200 m) can't be placed.

The implementation reports (Q4 2024 to Q2 2026) reconcile 100% on functions and programmes, and 97–99% on the administrative hierarchy.

**Analysis tools** ([`app/agent/analysis.py`](app/agent/analysis.py)). The planner chooses one, and every count and sum is a SQL query:

- **`project_status`:** which projects are continuing, started, idle, new or dropped. It uses one budget's own previous-year columns. For example, the 2026 budget prints each project's 2025 revised budget and its January–September 2025 spending.
- **`lga_projects`:** only lines whose location is that LGA. Statewide projects are counted separately, and the reply says so.
- **`ranking`:** projects, LGAs or agencies.
- **`mda_profile`:** one ministry or agency (with the latest report's spending).
- **`function_profile`:** one function of government across all ministries.
- **`revenue`:** where the money comes from.

Search plus model reading stays the fallback for everything else. Profiles are only for a breakdown or overview: "how much for <a sector or ministry>" stays on normal search, from the sector or ministry line.

**Measured on Oct 29, after this step:**

| Run | Result |
|---|---|
| Complex suite, including the 3 new cases (s01 project status, s02 Tambuwal, s03 IDPs now) | 8/8 |
| Main suite | 9/10: the parked debt case 06 passes in 2 of 4 runs |
| 39 mid-tier questions ([`mid_tier_report_step16.md`](evals/complex/mid_tier_report_step16.md)) | 18 answered / 17 partial / 4 not found, median 17.1 s |

After that 39-question run, four questions were re-routed and re-run, and all four were answered. The analysis tools answer in about 3–5 s.

**Replies.**
- 2–5 short, everyday sentences: the total first, then what was spent, saying plainly which figures are allocated and which are spent.
- Then the top 3–5 rows (added by code), then one *Madogara / Sources* line.
- The rows and arithmetic are sent when the user writes *nuna lissafi* / *show working*, with no model call, and are kept in the admin trace.
- For the analysis tools, code writes every figure in the reply.
- Elsewhere the number check still runs on the model's exact wording.

## Topic questions from several sources

Some questions have no single document that answers them, such as "the current state of IDPs in Sokoto" or "employment statistics". These answers come from several sources side by side ([`app/agent/topics.py`](app/agent/topics.py)).

**Source registry.** [`data/source_registry.yaml`](data/source_registry.yaml) records, for each topic:
- who publishes figures for Sokoto, on which domains, and at what level and tier;
- how often each publisher publishes, and its newest known edition;
- how to find their documents.

The registry drives three things:
- **The fetch allowlist.** Verified publisher domains are added to the base list. Unverified domains stay off until a probe (`scripts/probe_registry.py`) and a person confirm them.
- **Topic detection.** English and Hausa synonyms first, with the planner as the fallback.
- **The global excludes.** Attack and incident flash reports, news articles as a source of figures, and BudgIT State of States are never used.

**How an answer is built.**
1. Kasafi picks 3–5 publishers: state and LGA level and tier 1 first.
2. For each, it finds the newest document. It uses the library copy only if that copy is new enough. Otherwise it tries the registry's own links, then the publisher's own listing (Sokoto State Bureau of Statistics API, NBS e-library, UNHCR's Nigeria page), then web search limited to that publisher's domains.
3. These are fetched in parallel within about 90 s, with progress messages.
4. The model copies the figures as fact cards (value, unit, definition, date, area, page). Code keeps a card only if its value is printed on that page.
5. Code, not the model, writes the reply:
   - the newest figure first, then one dated line per source;
   - a "why they differ" line when sources disagree, for example the same count repeated under a later date, or different areas or definitions;
   - scope and definition notes ("covers Sokoto town only"; NBS labour definitions);
   - related context last, labelled as related;
   - the sources it couldn't get.

A question that names a publisher ("according to IOM") is answered from that publisher alone. A short dashboard whose text layer doesn't name Sokoto is read with OCR, because UNHCR prints its state figures only in a map. The Sokoto State Bureau of Statistics is a crawled library: its listing is read weekly.

## Place history (experimental)

**Experimental**, and labelled so in every answer. A farmer sends a pin (or the corners of the plot) and asks "how green was my farm in 2024?", "has it flooded?",
"is bare soil spreading?"; a planner asks the same of a ward, an LGA or the state. Kasafi answers from the
satellite record, in code, with no model in the loop (`app/place/`, design and findings in
[`docs/place-history.md`](docs/place-history.md)).

- **Sources** (all free, read through Microsoft's Planetary Computer unless noted): Copernicus Sentinel-2 L2A
  (greenness NDVI and water NDWI at 10 m, bare soil BSI and the cloud mask at 20 m, 2017→), Sentinel-1 RTC radar
  (open water under −15 dB VV and 3 dB under the plot's own dry-season reading; July–October passes, 2017→), JRC
  Global Surface Water v1.3 (water occurrence 1984–2020, 30 m; also the water-body layer, named from
  OpenStreetMap), ESA WorldCover 2021 (land cover; cropland mask), MODIS 13Q1 (250 m greenness since 2001 for
  wards and LGAs), UNOSAT's satellite flood maps on HDX (VIIRS 375 m; October 2022, September and November 2024;
  CC BY-SA), Open-Meteo's archive (rain, ~9 km), SAM 3.1 on the Meta Model API (the plot outline from a
  Sentinel-2 chip), and the budget core for the LGA's agriculture, irrigation and erosion lines.
- **Resolution is stated in every answer**, and so is what each source misses: radar sees only smooth open water
  (floods under crops read bright), optical images miss water under cloud, the UN maps are generous at 375 m,
  a year with too few clear images is said to be that and never filled. Flood answers lead with the official UN
  map and give radar as a lower bound. Nothing is ever "never flooded": only "no flood water seen", with the
  reason.
- **Observation, not advice.** Kasafi reports what the images show against the plot's own years and that season's
  rain; it names no cause, no input, no variety and no date, and refers farmers to the ADP extension service. It
  refuses land ownership, boundaries, certificates, grazing routes and anything about leaving a place. Outlines
  and ward figures are approximate and never a boundary.
- **Privacy.** Coordinates, plot shapes and corner pins stay in the server's memory for at most 30 minutes; the
  database caches satellite values per ~100 m cell and year, never per user; only the LGA is stored on the user
  record. Precomputed ward and LGA figures carry no personal data at all.

## Status

Work in progress. See [`docs/architecture.md`](docs/architecture.md) for the design and build plan.

**Roadmap (after the hackathon):** place history adds the JRC yearly water history (1984–2024, published only
through Google Earth Engine, whose non-commercial terms don't fit a startup product: a commercial Earth Engine
licence or a self-hosted copy); Sentinel-1 flooded-vegetation detection (VV/VH and the temporal change under
crops, so floods under standing rice stop being a blind spot) at plot and ward level; credit and insurance
verification with partners (a lender or insurer checks a farmer's plot history with the farmer's consent, as a
signed report, never a score); and the weather and rainfall layers move from Open-Meteo's free non-commercial
tier to a paid key (the hazard answers and the place history use its forecast and archive APIs under those terms
today).

## Built during the hackathon

Everything in this repository was written during the hackathon (Oct 26 – Nov 4, 2026). The git history is the record of that work.

- _Filled in as features land._

## Pre-existing assets

Assets created before the hackathon and reused here. No code is reused.

- _Public Sokoto State budget, policy and partner documents (listed in `data/manifest.json` with their source URLs)._
- _Hausa glossary of budget terms (TBD)._
- _Test questions (TBD)._

An earlier, separate Kasafi prototype was built for a different competition. No code from it is used in this repository.

**Design lessons from a previous project.** On Oct 30 we read that prototype's public technical notes for ideas only. Its code and its SQLite database are not used. These ideas were re-implemented here, on the hackathon's own extraction and Postgres:

- Turn budget tables into entities, one column per year and measure, and reconcile them at extraction time.
- Get a project's status from one budget's own previous-year columns.
- Show only projects tagged to an LGA, and say that statewide ones aren't split.
- Keep counts apart from money.
- Label every figure as allocated or spent.
- Keep the plain answer short and the working separate.

## Data sources and use

Kasafi answers only from **public documents**: Sokoto State budgets, implementation reports, plans and policies, and
reports from development partners. Seed documents are listed in `data/manifest.json` with their source URLs; documents
Kasafi finds and fetches by itself are recorded in the database with their URL, SHA-256 hash and fetch date, as
`auto-indexed` until a person verifies them.

- **Fetching rules.** Only https links on an allowlist of government and partner domains
  (`app/acquisition/policy.py`), with a size limit, parsed in a separate resource-limited subprocess (time and
  memory limits; it is not an isolation sandbox). Text in documents is treated as
  data, never as instructions.
- **robots.txt.** Every request identifies itself honestly as `KasafiBot/1.0 (+https://halalnumeriq.com.ng/kasafi)`
  and is checked against the site's robots.txt for that agent. A site that disallows us (or whose robots.txt can't be
  read) is "local only": Kasafi never fetches from it, and a person adds its documents by hand.
- **Content-Signals.** Some sites publish Cloudflare Content-Signals in robots.txt. sokotostate.gov.ng, for example,
  says `search=yes, ai-train=no, use=reference`. Kasafi uses documents for reference only: it cites the page, it does
  not train or fine-tune any model, and it refuses a site that says `ai-input=no`.
- **Minimal excerpts.** Model calls get only what a step needs, never a whole document: the answer step gets at most
  6 page excerpts of up to 4,500 characters each (the matching table rows and their neighbours); checking a fetched
  document reads its first 3 pages (up to 4,000 characters); OCR sends one page image at a time; an evidence crop
  sends SAM 3.1 only the band of the page around the cited row (or, for a scanned page, that one page).
- **Open question (Oct 28).** Meta's hackathon free-credit API usage "may be used to improve Meta's products". We have
  asked Meta whether that includes training on API inputs, and whether it can be turned off, because of sites that
  say `ai-train=no`. After the hackathon we plan to move to paid usage if that avoids it.

## Setup

Requires Python 3.12, [uv](https://docs.astral.sh/uv/), Docker and FFmpeg.

```bash
cp .env.example .env              # fill in values; never commit .env
uv sync                           # install dependencies into .venv
docker compose up -d db           # local Postgres 17 + pgvector
uv run uvicorn app.main:app --reload
uv run pytest
python scripts/fetch_seed_docs.py # download seed documents into data/
```

## License

[MIT](LICENSE)
