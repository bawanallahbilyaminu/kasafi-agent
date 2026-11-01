# Kasafi

Kasafi is a WhatsApp agent for people in Sokoto State, Nigeria. You send it a Hausa voice note or a text message
in Hausa or English, and it answers from public sources: the state's budgets and budget performance reports,
policies and plans, development-partner reports, official weather and flood outlooks, the health facility
registry, and, as an experiment, the satellite record of a farm or a ward. Every figure in an answer comes from a
cited page or table and is checked in code before it is sent. When a document Kasafi needs isn't in its library,
it looks for it on government and partner sites, fetches it, indexes it and then answers. Kasafi gives neutral
facts only: no opinions on politics, nothing about conflict or security operations, and no medical advice.

> Entry by Halal Numeriq Limited (Startups track) in the **Meta Global AI Developer Hackathon** (Oct 26 – Nov 4,
> 2026). Problem statement: *Build for Your World*.

## Three journeys

**A farmer worried about flooding.** Hauwa shares her farm's location and asks by voice, "Shin ruwa ya taɓa rufe
gonata?" (Has my farm ever flooded?). Kasafi tries to draw the plot from a satellite image. If it can't, it asks
how big the farm is, or for its corners. It then answers in Hausa from the satellite record. The UN's satellite
flood maps come first, with their dates. Radar comes next, labelled as a lower bound. If no water was seen, the
answer says so and explains why a flood could still have been missed. It never says "never flooded". A chart and
a map follow. Hauwa then asks "and what's budgeted for irrigation here?" and gets her LGA's budget lines. If no
line names her LGA, she gets the statewide totals that may cover it.

**A citizen checking a service budget by voice.** Musa sends a voice note: "Nawa aka ware wa Ma'aikatar Lafiya a
2026?" (How much was budgeted for the Ministry of Health in 2026?). Kasafi reads back what it heard when it isn't
sure. It answers in a few plain sentences with the source page. It sends a cropped image of the printed row. If
Musa replies *nuna lissafi* (show working), he gets the rows and the arithmetic. He can also ask what had been
spent by the end of the last quarter, against the revised budget.

**A partner assessing an LGA.** A programme officer asks which wards of Wurno LGA were greenest in 2024, which
LGAs the 2022 floods covered most, and which 2026 capital projects are located in Wurno. Kasafi answers with a
ward map and a ranking, then the project lines tagged to the LGA. Statewide lines are counted separately and said
to be so. A question that names a publisher, such as "according to IOM, how many IDPs are in Sokoto?", is answered
from that publisher's own documents.

## What works today (1 Nov 2026)

| Capability | Status |
| --- | --- |
| Budget and budget-performance answers, typed or by Hausa voice note, with citations, evidence crops and *show working* | Live |
| Finding, fetching and indexing a missing document from allowlisted sites | Live |
| Questions that need several publishers (IDPs, poverty, employment), answered side by side | Live |
| Weather, air quality, river and fire answers with a map; official advisories and outlooks (NEMA, NIHSA, NiMet); NCDC outbreak figures | Live |
| Nearest health facility, route and road distance | Live |
| Emergency fast path (verified numbers and the nearest suitable facility, before anything else) | Live |
| Scope guardrails (politics, security, medical advice, land ownership) | Live |
| Hazard alerts people sign up for (one approved WhatsApp template) | Dry run: decisions go to the admin page, not to users |
| Place history for a farm pin, a ward, an LGA or the state (satellite greenness, water, floods, bare soil) | Experimental: live, and labelled so in every answer |
| Spoken (audio) replies | Planned: replies are text and images only |

## How Meta's models are used

| Model | What it does | Where |
| --- | --- | --- |
| **Muse Spark** (Meta Model API) | Plans each question and fills its information need. Reads budget rows (first reading). Writes page-based answers. Reads scanned pages (OCR). Reconciles the two transcripts of a voice note. Classifies borderline guardrail and emergency messages. | [`app/agent/answer.py`](app/agent/answer.py) (`plan_question`, `compose`), [`app/agent/line_answer.py`](app/agent/line_answer.py), [`app/retrieval/ocr.py`](app/retrieval/ocr.py), [`app/providers/stt.py`](app/providers/stt.py), [`app/guardrails/scope.py`](app/guardrails/scope.py), [`app/guardrails/emergency.py`](app/guardrails/emergency.py); client [`app/providers/meta.py`](app/providers/meta.py) |
| **Muse Spark Open** (open weights, Baseten; Fireworks as fallback host) | The second, independent reading of every budget-line answer. The second-opinion plan when the question's own words conflict. | `_second_reading` in [`app/agent/line_answer.py`](app/agent/line_answer.py), `open_reader` and `settle_by_words` in [`app/agent/answer.py`](app/agent/answer.py); clients [`app/providers/baseten.py`](app/providers/baseten.py), [`app/providers/fireworks.py`](app/providers/fireworks.py) |
| **Muse Voice Transcribe** | One of two transcripts of each voice note; Muse Spark's audio reading is the other. | [`app/providers/stt.py`](app/providers/stt.py), [`app/whatsapp/voice.py`](app/whatsapp/voice.py) |
| **SAM 3.1** (Meta Model API) | Crops the cited table row from the source page as evidence. Draws a farm's outline from a satellite image. | [`app/evidence/crops.py`](app/evidence/crops.py), [`app/place/outline.py`](app/place/outline.py); client [`app/providers/sam.py`](app/providers/sam.py) |

## How answers are checked

- **The words settle what they can.** Before the planner's plan is used, code reads the question's own words in
  English, Hausa and code-switched forms: the period (and so the report), spent vs approved vs revised, the splits
  named, the publishers named, and a named budget line. A clear match overrides the plan. When the words conflict,
  a second plan from Muse Spark Open decides. Every override is recorded in the trace
  ([`app/agent/words.py`](app/agent/words.py), [`docs/planner-variance.md`](docs/planner-variance.md)).
- **Two readings.** For a budget-line question, Muse Spark and Muse Spark Open each pick the rows that answer it,
  independently and at the same time. Code answers only from the rows both chose, and shows the others as
  "possibly relevant, not counted".
- **Code does the arithmetic.** Totals, differences, shares, rankings and project status are SQL over the
  structured budget tables built at indexing time, not model arithmetic.
- **Figures are checked against their rows.** On the page-based path, each figure in the answer is looked up in
  the cited rows and checked against the row's entity, the year and quarter period of its own column, its unit and
  its kind (allocation or spending). A contradiction (another entity's or another column's figure) is rewritten
  once and refused if still wrong. *Attribution checked* is given only when the row settles the entity, year and
  period; when the evidence can't settle one of them (a table with two year columns and no label on the cell, or
  one shared word like "Education" with two Education rows), the answer says *figures checked* instead. This is a
  rule-based check of the cited text, not a full semantic verification. The state is shown in *show working* and
  on the admin trace ([`app/agent/attribution.py`](app/agent/attribution.py)).
- **Entity, level and period** of the rows used are compared with what was asked; a mismatch is redone once and
  then said plainly ([`app/agent/consistency.py`](app/agent/consistency.py)).
- **An answer or an apology.** While the server is running, the answer function has a 120-second limit; past it
  the user gets an apology, and nothing from that job can be sent afterwards. The checked text is sent as soon as it
  is ready. Maps follow under their own 30-second limit (or a note says the map couldn't be drawn), and evidence
  crops under a 45-second one. A failure is logged with its reason on the admin page. Incoming messages are not yet
  persisted before processing, so a job lost to a server restart is not recovered (roadmap).

## How we evaluate

- **Generated sets from the data.** Each run draws about 50 fresh budget questions from the extracted tables:
  lookups, splits, quarterly spending, comparisons, rankings, false premises and questions with no answer in the
  data. Each is asked in a template form or a paraphrase: Hausa, informal, code-switched, with typos, or as a
  follow-up. A reply is wrong when an expected figure is missing, a wrong agency is named, or a false premise isn't
  corrected ([`evals/generated/`](evals/generated)).
- **Fixed sets:** multi-publisher topic questions ([`evals/topics/`](evals/topics)), answer patterns found in phone
  tests ([`evals/patterns/`](evals/patterns)), official advisories, the scope guardrails in Hausa and English
  ([`evals/guardrails/`](evals/guardrails)), place history for wards and LGAs with expected values from the
  precomputed table ([`evals/place/`](evals/place)), and the questions that once flipped between runs
  ([`evals/variance/`](evals/variance)).
- **Conversations end to end.** Scripted WhatsApp conversations run through the real webhook handler against a
  test database before every deploy. Each scripted message must get exactly the expected replies, never silence
  and never a duplicate ([`tests/test_e2e_conversation.py`](tests/test_e2e_conversation.py)).
- **A held-out set** of questions is kept outside this repository, so that it can't shape the code. It is run
  before the final submission, with the same checks.

Latest reports before the 1 Nov deploy: fresh draw [`report-predeploy-review2.md`](evals/generated/report-predeploy-review2.md)
(52 cases, 0 wrong), topics [`report-predeploy-review.md`](evals/topics/report-predeploy-review.md) (0 wrong of 12),
guardrails [`report.md`](evals/guardrails/report.md) (104 of 104), place history
[`report-full.md`](evals/place/report-full.md) (89 cases, 0 wrong), flip cases
[`report.md`](evals/variance/report.md) (0 flips). These are results on these test sets, not a general accuracy
figure.

## Safety and privacy

- **Consent first.** No message reaches any model until the user accepts the first-contact notice
  ([`app/whatsapp/conversation.py`](app/whatsapp/conversation.py)). The notice says that Meta's free-credit API
  usage may be used to improve Meta's products. Deleting your data and the emergency path work before consent.
- **No numbers stored.** Users are keyed by a keyed hash of their number. Phone numbers and WhatsApp names never
  reach a model. Alert subscribers' numbers are the one exception: they are stored encrypted, only to send the
  alert, and deleted on STOP or DELETE MY DATA.
- **Locations.** A shared location stays in the server's memory for at most 30 minutes; only the LGA is stored.
  A plot outline, a farm size given as a circle and corner pins also stay in memory only. The database keeps
  satellite statistics for 100 m cells, with no link to any user. Full details are on the
  [privacy page](docs/site/privacy.md).
- **Documents are data.** Fetching is limited to https sites on an allowlist and respects robots.txt and
  Content-Signals. Downloads have a size limit. PDFs are parsed in a separate resource-limited subprocess (time
  and memory limits; not an isolation sandbox). Text inside a document is never followed as an instruction.
- **Scope.** Politics, conflict and security operations, and medical or nutrition advice are declined politely,
  in Hausa or English. Budget figures for security agencies are given as plain cited figures. Place history
  reports what the images show and refers farmers to the state's agricultural extension service. It refuses land
  ownership, boundary and certificate questions.

## Known limitations and roadmap

- Replies are text and images; there are no spoken replies yet.
- Hazard alerts are in dry run until the template and the delivery tracking are ready. A per-recipient outbox
  with delivery callbacks is planned.
- Place history is experimental. It has not been validated in the field. Radar misses water under crops, and the
  UN flood maps are coarse (375 m).
- Weather and rainfall come from Open-Meteo's free non-commercial tier, to be moved to a paid key.
- Backups stay on the server for now. Off-host copies and a restore rehearsal are planned.
- An external review of the code was done on 1 Nov. Each finding and our response (done, planned or not accepted,
  with reasons) is in [the review document](docs/reviews/2026-11-01-external-review.md#response-to-the-external-review-bilyaminu-bawan-allah--kasafi-1-nov-2026).
- Design notes: [`docs/architecture.md`](docs/architecture.md), [`docs/hazard-and-services.md`](docs/hazard-and-services.md),
  [`docs/place-history.md`](docs/place-history.md), and every document-extraction problem fixed so far with its
  regression test, in [`docs/extraction-lessons.md`](docs/extraction-lessons.md).

## Built during the hackathon

Everything in this repository was written during the hackathon, Oct 26 – Nov 4, 2026. The git history is the
record; by day:

- **Oct 26:** the project skeleton, the Meta Model API client, and the Hausa voice-note test harness.
- **Oct 27:** the WhatsApp webhook, the two-transcript voice pipeline with read-back and corrections, consent and
  per-user limits, guardrails, the privacy pages, the deploy with rollback, the PDF indexer, OCR of scanned pages,
  and grounded answers with figure checks.
- **Oct 28:** fetching missing documents safely (allowlist, robots.txt, size limits, provenance), recency-aware
  search, follow-up context, Kasafi's own calculations, evidence crops with SAM 3.1, and budget queries in code.
- **Oct 29:** searchable budget lines and the two independent readings with Muse Spark Open, the structured
  budget core and its analysis tools, the admin trace and review pages, the source registry, and multi-source
  topic answers.
- **Oct 30:** the information need in the plan, the capability catalogue and the plan → act → check loop,
  generated evals, IOM's displacement API, PostGIS boundaries and facilities, location intake, the emergency fast
  path, hazard layers and the official advisories crawl.
- **Oct 31:** server-drawn maps, facility routing and corrections, hazard summaries written in code, hazard alerts
  in dry run, a speed round, and place history steps 1 and 2 (the satellite record of a pin, the SAM 3.1 plot
  outline, and radar and UN flood maps).
- **Nov 1:** place history for wards, LGAs and the state, plot shapes from the farmer, the water-body layer, fixes
  for planner variance, the end-to-end conversation tests, the external review round, and the admin status page.

## Pre-existing assets

Assets created before the hackathon and reused here. No code is reused.

- Public Sokoto State budget, policy and partner documents, listed in [`data/manifest.json`](data/manifest.json)
  with their source URLs.
- No Hausa glossary was reused. The test questions in [`evals/`](evals) were written during the hackathon.

An earlier, separate Kasafi prototype was built for a different competition. No code from it is used here. On
Oct 30 we read that prototype's public technical notes for ideas only, and re-implemented these on this
project's own extraction and database: budget tables as entities with one column per year and measure, reconciled
at extraction time; a project's status from one budget's own previous-year columns; only LGA-tagged projects for
an LGA, with statewide ones counted apart; counts kept apart from money; every figure labelled as allocated or
spent; and a short plain answer with the working sent separately.

## Setup

Requires Python 3.12, [uv](https://docs.astral.sh/uv/), Docker and FFmpeg.

```bash
cp .env.example .env              # fill in values; never commit .env
uv sync                           # install dependencies into .venv
docker compose up -d db           # local Postgres 17 with pgvector and PostGIS
uv run alembic upgrade head
uv run uvicorn app.main:app --reload
uv run pytest
python scripts/fetch_seed_docs.py # download the seed documents into data/
```

Deploying to the server: [`deploy/README.md`](deploy/README.md). WhatsApp setup:
[`docs/whatsapp-setup.md`](docs/whatsapp-setup.md).

## License

[MIT](LICENSE)
