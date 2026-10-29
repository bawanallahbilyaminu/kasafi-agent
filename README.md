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

Search plus model reading stays the fallback for everything else.

**Replies.**
- 2–5 short, everyday sentences: the total first, then what was spent, saying plainly which figures are allocated and which are spent.
- Then the top 3–5 rows (added by code), then one *Madogara / Sources* line.
- The rows and arithmetic are sent when the user writes *nuna lissafi* / *show working*, with no model call, and are kept in the admin trace.
- For the analysis tools, code writes every figure in the reply.
- Elsewhere the number check still runs on the model's exact wording.

## Status

Work in progress. See [`docs/architecture.md`](docs/architecture.md) for the design and build plan.

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
  (`app/acquisition/policy.py`), with a size limit, parsed in a sandboxed process. Text in documents is treated as
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
