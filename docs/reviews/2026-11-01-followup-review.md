# Kasafi — Follow-up Repository Review

**Prepared for:** Bilyaminu Bawan Allah / Halal Numeriq Limited  
**Review date:** 1 November 2026, Africa/Lagos  
**Repository:** https://github.com/bawanallahbilyaminu/kasafi-agent  
**Previously reviewed:** [645456d034ec1e96e0d3ed2bc800ef198b3b3a0e][BASE]  
**Reviewed now:** [89ea576256c08bf56f0dce9660bfc30623a8ce17][HEAD]  
**Change set:** 41 commits, 79 files changed, 8,067 insertions and 989 deletions.  
**Purpose:** Reassess the changes against the previous 24 recommendations, credit working fixes, reproduce remaining problems, and identify the next work in order.

This is a new audit of a later snapshot. The first report remains a record of what was found at the earlier commit. No application fixes, deployments, live WhatsApp messages or paid model calls were made during this re-review.

## 1. Revised judgment

**Kasafi has materially improved. Several original defects are fixed, the product is easier to understand, and the operational work is more credible. However, three findings marked “done” are only partly resolved: claim attribution, plot identity, and location privacy.**

The strongest improvement is the combination of actual fixes and clearer product presentation. The README now explains three connected journeys, distinguishes live capabilities from experiments and dry runs, and explicitly states that spoken replies are not implemented. That makes the broader feature set much easier to defend. [README][R01]

I would preserve the broad feature vision. Budgets, official information, facilities and environmental observations can serve connected questions from the same Sokoto users. The current problem is whether the system reliably preserves the correct agency, period, place and uncertainty as users move through those features.

The next engineering round should concentrate on those associations. More feature removal is not justified by this review. Nor would a large last-minute rewrite be a sensible response. The most useful immediate changes are small, targeted fixes with meaningful regression cases.

For a carefully presented demonstration, the project is substantially stronger. For an unattended public service, important work remains: durable message processing, recipient-level alert state, an independent factual benchmark, complete privacy enforcement, and recovery verification.

## 2. What was checked

| Check | Result and scope |
| --- | --- |
| Source comparison | Compared the earlier commit with the current snapshot, including the review-response document and the changed application, tests, deployment and documentation files. |
| Branch identity | A final remote-head check still returned the reviewed commit, 89ea576256c08bf56f0dce9660bfc30623a8ce17. |
| Dependency setup | Installed the locked project dependencies with `uv sync --frozen`. Added `socksio` only to the review environment because its proxy setup requires it; no dependency file was changed. |
| Repository tests | `uv run --no-sync pytest -q --disable-warnings -ra`: **1,404 passed, 105 skipped, 9 warnings**, in **20.42 seconds**. |
| Original reproductions | The original wrong-attribution example is rejected; ordinary failed/partial alert sends are retryable; the original two-pin outline-cache example is covered by a passing regression test. |
| Additional local probes | Reproduced three attribution variants, a stale user-provided farm shape, typed-coordinate persistence, duplicate alert sending after interruption, and map work outside the answer timeout. |
| Public liveness | At **13:10:28 Lagos time**, `/health` returned HTTP 200 and `{"status":"ok"}`. |
| Public release identity | At **13:10:31 Lagos time**, `/version` returned **f90ffd9b249bedda50bf608fbdade9f87bac8b21**, an earlier commit than the reviewed branch. |
| Repository integrity | Review work was isolated from the original checkout. No tracked application file was edited. |

The skipped tests matter. They include the database-backed conversation suite, extraction tests requiring source PDFs, geographic tests requiring imported boundaries/facilities, and tests requiring external credentials or explicit network flags. The passing count therefore does **not** independently establish that the complete deployed application, real imagery, real speech recognition or source-document extraction passed.

The new conversation suite is useful integration coverage: it exercises the real reply handler and conversation flow against the development database, while substituting model and satellite responses in several paths. It is not a test of the WhatsApp transport or every live model response. The deployment script correctly makes that suite mandatory when deploying. [Conversation tests][R10] · [Deployment gate][R11]

All newly reproduced failures below used synthetic inputs and controlled substitutes for external calls. They demonstrate reproducible software weaknesses, not a measured frequency of errors among real users.

## 3. Improvements that deserve full credit

### 3.1 The original health-versus-education substitution is now blocked

The earlier example placed Health at ₦100 million and Education at ₦200 million, then supplied an incorrect model sentence giving ₦200 million to Health.

The new code retries the answer and returns an unsupported/refusal result if the substitution remains. I reran that exact case and observed `verified=False`, `verification="unsupported"`, and two composition attempts.

This is a real fix. The problem is that nearby cases still pass, as detailed in finding 1 below. The new verification states and trace visibility are useful foundations. [Attribution tests][R03] · [Page-answer checks][R04]

### 3.2 Normal alert failures now remain retryable

The dispatcher now distinguishes failed, partial, sent and no-recipient outcomes. It records the recipients still owed after an ordinary completed dispatch round, retries only those failures, and prevents dry-run records from consuming a later live send.

The corresponding regression tests passed. The remaining interruption case does not invalidate that improvement; it identifies the boundary between this minimum fix and the planned durable outbox. [Dispatch][R05] · [Review regression tests][R06]

### 3.3 The original outline cache collision and persisted-geometry issue received substantive fixes

A cached outline is now checked to ensure it contains the new pin. Plot histories use a geometry hash and method version. Plot-specific results and outlines are held in memory, and migration 0022 drops the previous database table containing outline geometry.

The original two-pin test and geometry-key tests pass. That closes the exact shared-cell failure from the first review. A separate conversation-state error remains when a user changes a pin after supplying a farm size or corners. [Outline cache][R07] · [History cache][R08] · [Migration][R09]

### 3.4 SQLite backup support is present

The user store now uses SQLite's online backup API, with a daily backup hook and a pre-deploy copy. The deployment also attempts a PostgreSQL backup before proceeding, and refuses that deployment path if the backup command fails.

The local backup tests pass. Off-host copies and a full restore rehearsal are explicitly still planned. There is also a scheduler configuration caveat described later. [User-store backup][R12] · [Backup scheduler][R13] · [Pre-deploy backup][R14]

### 3.5 Conversation failure handling and operational visibility are better

Timeout apologies, exception handling, failure traces and the new admin status page are useful additions. The status page exposes hazard fetch age, advisory information, alert outcomes, emergency-path counts, place requests and failures.

This is meaningful progress on monitoring. It does not replace readiness checks or durable work queues. [Timeout handling][R15] · [Admin status][R16]

### 3.6 Satellite interpretation and scope handling are more careful

The new dry-season radar reference addresses the documented smooth-sand false positives. The area planner distinguishes a user's ward, LGA and statewide questions, and now consults catalogue season completeness when selecting a headline year. The product labels place history as experimental and acknowledges that field validation remains outstanding.

These are appropriate changes. The local tests support implementation behaviour; I did not independently establish their geospatial accuracy or rerun the live data precompute. [Radar method][R17] · [Area planner][R18] · [Area precompute][R19]

### 3.7 The feature presentation is much more coherent

The three journeys explain why the features belong together. The capability-status table, roadmap and demo script also make the project easier for another person to assess.

Keep these improvements. Correct the remaining absolute claims and the two missing report links discussed in finding 6. [README][R01] · [Demo script][R20]

## 4. Remaining findings and suggestions, one by one

### Finding 1 — P1: Wrong entity, year and quarter claims can still receive “attribution checked”

**Status of original recommendation 01: partially resolved.**

The check now blocks the exact original example. It does not yet reliably bind a number to the complete identity and period of a claim.

I reproduced the following through the real `_page_path` function, with only composition and retrieval replaced by controlled fixtures:

| Source evidence | Incorrect supplied answer | Observed result |
| --- | --- | --- |
| Basic Education: ₦100m; Higher Education: ₦200m | Basic Education was allocated ₦200m in 2026 | `verified=True`; `attribution checked`; no retry |
| Health, 2025 approved: ₦100m; 2026 approved: ₦200m | Health was allocated ₦100m in 2026 | `verified=True`; `attribution checked`; no retry |
| Health, Q1 2026 actual: ₦100m; Q1–Q3 2026 actual: ₦200m | Health spent ₦200m in Q1 2026 | `verified=True`; `attribution checked`; no retry |

**Why this happens.** The entity test accepts a row when *any* extracted entity term occurs in it, so “education” is enough to confuse Basic Education and Higher Education. The year test combines years from the whole row, the first 300 characters of the evidence and the document year. Finding 2026 anywhere in that combined context does not establish which amount belongs to its column. Quarter identity is not part of the claim representation. [Attribution implementation][R02]

The separate explicit states are an improvement, but the strongest state currently promises more than these checks establish. A reader should not interpret it as a complete semantic verification.

**Suggested changes, in order:**

1. Add these three failing examples to the regression suite, alongside correct examples with similarly named agencies and multi-year tables.
2. Bind an amount to a structured claim containing the canonical entity, measure, fiscal year, quarter/cumulative period, unit, source row and source column.
3. Resolve Hausa/English aliases to that entity; do not let a single shared word or any name elsewhere in a multi-entity plan establish the binding.
4. Render factual financial sentences from the bound records where possible. Keep free-form explanation separate from the identity and values.
5. When a complete binding is unavailable, expose the weaker state honestly; do not promote it to “attribution checked”.
6. Tighten the README claim that every figure is bound to the same entity, year, unit and kind until the broader criteria pass.

**Acceptance criteria:** All three wrong examples are rejected or corrected. Valid Basic/Higher Education statements still work. A 2026 document containing 2025 and 2026 columns cannot validate a swapped-year claim. Q1 and Q1–Q3 are separately checked.

**Practical importance:** This remains the most important correctness issue because source citations and a strong verification label can make the incorrect answer appear more trustworthy.

### Finding 2 — P1: A new farm pin can inherit the previous farm's shape

**Status of original recommendation 04: the original cache defect is fixed; the wider plot-identity requirement remains partial.**

I replayed this conversation locally:

1. Keep farm A's pin in memory.
2. Ask about its greenness.
3. Answer the size prompt with “3 acres”.
4. Share a new pin roughly three kilometres away.
5. Ask about the farm again.

The current point updated, but the previous circle remained in `LocationMemory._shapes`. The conversation passed both the new point and the old shape into the answer path. The real `place_answer` then forwarded that old polygon to the history calculation without a containment check.

Observed result:

- Point updated: **true**.
- Old shape retained: **true**.
- Polygon passed to the history calculation was the old shape: **true**.
- That polygon contained the new pin: **false**.
- The answer path still returned a found answer: **true**.

The imagery/history response was substituted, so this establishes selection of the wrong analysis geometry, not a measured satellite-reading error.

**Why this happens.** `remember()` updates the point without invalidating its associated shape. Conversation handling fetches the shape by user key, and `place_answer` accepts a supplied geometry directly. The new cache hash faithfully identifies that old geometry; it cannot correct the earlier selection mistake. [Location state][R21] · [Conversation place construction][R15] · [Shape selection][R22]

**Suggested changes, in order:**

1. Give the current farm/plot an explicit identity and bind its point, size/corners, outline and pending request to that identity.
2. When a new ordinary location pin selects another farm, clear or explicitly re-establish its shape and related state.
3. Add a defensive validation before analysis: a retained shape must be appropriate for the active pin and plot.
4. Preserve the intentional corner-collection flow. Avoid a blanket reset that deletes the corners while the user is still supplying them.
5. If the plot centre moves across a ward or LGA, resolve its geography again instead of reusing the previous place labels.

**Acceptance criteria:** Switching between farms cannot silently analyse the first one. Repeat questions about the same farm reuse the correct shape. Size-based and corner-based shapes both pass the switching test, including a move across an administrative boundary.

### Finding 3 — P1: Typed coordinates are still persisted in conversation history

**Status of original recommendation 05: partially resolved.**

Removing the geometry table was the right action. However, the public policy still makes the broader statement that exact locations are never written to the database.

Using the actual conversation handler, a synthetic user sent:

> What is the 2026 agriculture budget near my farm at 13.0589127, 5.1673341?

The `turns.question` column contained that exact coordinate pair afterwards. The answer function was substituted with a simple fixed reply; the database write was the real one.

**Why this happens.** The trace redactor gained a coordinate rule, but the conversation handler sends the original question into `UserStore.add_turn`, and that method stores the text without equivalent redaction. Redacting one storage path is insufficient to support a promise about all databases and logs. [Conversation persistence][R15] · [Turn storage][R23] · [Trace redaction][R24] · [Privacy policy][R25]

There is a second wording mismatch to resolve: failed-recipient tracking now places coded user keys in `alert_log.failed`, while the policy describes alert records as having no ID. Keeping such keys may be operationally justified; the description and deletion/retention handling need to reflect that design. [Alert state storage][R26]

**Suggested changes, in order:**

1. Define the exact policy for coordinates in typed messages and speech transcripts, in addition to native WhatsApp pins.
2. Enforce that policy at a shared persistence boundary for conversation turns, traces, pending questions, failure records and saved working.
3. Review model-bound text and follow-up history as well, because removing a separate structured pin does not remove coordinates embedded in a question.
4. Add tests that inspect SQLite, trace records and logs after typed-coordinate and transcript-based conversations.
5. Align the alert-record description with the coded recipient state now retained.
6. Decide how existing stored text and backups are handled when applying the corrected retention rule.

**Acceptance criteria:** Under a “no exact coordinates persisted” policy, the synthetic coordinate pair does not appear in stored conversation text or the other covered records. Ordinary public budget figures must survive redaction. The written policy describes the remaining coarse caches and recipient identifiers accurately.

This finding is a code-versus-promise mismatch. This review does not make a legal compliance determination.

### Finding 4 — P1 before live alerts: An interrupted dispatch can duplicate an accepted send

**Status of original recommendation 02: the minimum fix works; durable recipient delivery remains open. Original recommendation 03 also remains open.**

The ordinary failure tests pass. I then tested interruption between recipients:

1. Two synthetic recipients subscribe.
2. Recipient u1's send function returns success.
3. The second send raises cancellation, simulating interruption before the dispatch round finishes.
4. Reopen the same SQLite database and rerun dispatch.

There were **zero alert-log rows** after interruption. On retry, the accepted-attempt sequence was **u1, u1, u2**.

**Why this happens.** Dispatch records its result after the recipient loop. A completed first send is not durably recorded before the next one begins. In addition, the current sender treats a successful API call as success; it does not independently prove handset delivery. [Dispatch][R05] · [Live sender][R27]

The README acknowledges that the outbox and delivery callbacks are planned and that alerts are in dry run. That is an appropriate current boundary.

The incoming WhatsApp side also still acknowledges and schedules work without a durable inbox. Message deduplication is in memory. Catching an exception and sending an apology helps while the process remains alive; it does not recover an acknowledged job after process termination. [Webhook][R28]

**Suggested changes, in order:**

1. Persist each intended recipient operation before sending, with a stable alert-plus-recipient identity.
2. Record attempt state, provider message ID and API acceptance separately from delivery confirmation.
3. Support bounded retry/backoff and alert expiry; stop sending obsolete advice.
4. Treat an interrupted or ambiguous provider response as an explicit uncertain outcome. A database outbox alone does not magically guarantee exactly-once transport.
5. Persist incoming message jobs before acknowledging them, and process messages in a defined order per sender.
6. Test interruption before sending, between recipients, after provider acceptance and during local status persistence.

**Acceptance criteria:** The application can identify and recover pending work across a worker restart. The reproduced completed-first-recipient case does not silently restart from the entire subscriber list. Unknown provider outcomes are visible and handled deliberately. Accepted, delivered, failed and expired states are not conflated.

**Recommendation:** Keep alerts in dry run until this lifecycle is validated. The ordinary retry fix is useful progress and should stay.

### Finding 5 — P2: The two-minute answer timeout does not cover the complete reply

**Related original recommendation: 22, complete-turn latency.**

The new timeout surrounds the answer function. Map rendering happens afterwards, before `handle()` returns its text-and-image outputs to the webhook. A slow map can therefore hold back an already-computed text answer beyond the configured answer limit. [Conversation timeout and maps][R15] · [Webhook send order][R28]

I checked this with a deliberately small local limit:

| Controlled setting | Observation |
| --- | --- |
| Answer timeout | 0.05 seconds |
| Substituted map rendering | 0.20 seconds |
| Complete handler time | About 0.20 seconds |
| Result | Normal answer and map-failure note; no timeout apology |

This is a boundary test, not a claim that production takes these timings or currently exceeds two minutes.

**Suggested changes, in order:**

1. Send the checked text when it is ready.
2. Render optional maps/crops under their own bounded deadlines and send them afterwards.
3. Define a complete-turn deadline that accounts for progress messages, model work, maps and provider sends.
4. Distinguish cancellation of an awaiting task from termination of any worker-thread calculation it started.
5. Replace the absolute “never silence” promise with a measured target and a description of retries/fallbacks.

**Acceptance criteria:** A stalled map does not delay the main answer. A timed-out job cannot later send a duplicate final answer. Test timing includes the final user-visible send, not only the answer function.

### Finding 6 — P2: The documentation is better, but two evidence links are missing and deployment identity needs precision

**Status of original recommendation 24: substantially improved, with specific remaining corrections.**

Two README evaluation links point to paths that do not exist in the reviewed checkout:

- `evals/generated/report-predeploy-review2.md`
- `evals/topics/report-predeploy-review.md`

This does not show that those evaluations were never run. It means a reader cannot inspect the linked evidence from this source snapshot.

The review-response table also lags later changes: it still says the admin freshness page is planned and the capability table is planned, although both are now implemented. Other “done” entries need the narrower qualification from findings 1–3. [Review response][R29] · [README][R01]

At the time checked, the public API served `f90ffd9`, while this audit reviewed `89ea576`. The latest catalogue-completeness and facility-pin commits were therefore not independently confirmed live. An older serving commit is not automatically a service fault; it is a reason to distinguish “implemented” from “deployed”.

**Suggested changes, in order:**

1. Commit the intended evaluation reports or link to the reports that are actually published.
2. Update the response table to the implementation now present, using “partial” where a broader acceptance criterion is still unmet.
3. Tie the capability-status table and demo instructions to a checked release commit and date.
4. Confirm the release identity after deployment, then perform phone tests against that exact release.
5. Keep absolute claims about attribution, retention and reply deadlines within what the checks actually establish.

**Acceptance criteria:** Every evidence link resolves, each status corresponds to a reproducible test or a clearly stated deployment observation, and source readiness is distinguished from live availability.

## 5. Additional operational points to retain from the first review

These are not all newly introduced bugs. They are still relevant release conditions that the new passing tests do not close.

### 5.1 Daily SQLite backups depend on the hazard scheduler

The daily backup hook sits inside `start_scheduler()`, which returns immediately unless both hazard fetching and a database are enabled. Thus setting a backup directory alone does not enable daily SQLite backups. This is configuration-dependent; I did not establish that the current server has hazard fetching disabled.

Make maintenance scheduling independent of optional hazard fetching, or explicitly enforce and test that dependency. Monitor backup age and run an off-host restore rehearsal. The online backup implementation itself is sound progress. [Scheduler condition][R13]

### 5.2 Liveness still is not readiness

`/health` returns a static success. The admin status page adds useful detail, but the deployment health check still cannot establish that required data, migrations or dependencies are ready.

Keep a lightweight liveness route and add a bounded readiness check. A working process and a fully usable budget/facility/place capability are different observations. [Health endpoint][R30] · [Deployment health check][R14]

### 5.3 Cost limits remain estimates

Conversation gating still adds configured fixed costs per question/voice request. The changes reviewed do not turn that into a transactionally reserved, provider-reconciled operating budget.

Keep the current controls, but describe them as estimates and enforce provider-side limits where available. Broader access needs accounting for retries, second opinions, OCR, imagery and background jobs. [Conversation spending gate][R15]

### 5.4 Independent evidence remains essential

The new generated and conversation tests help find routing, state and consistency errors. They do not establish independent extraction accuracy, Hausa speech accuracy across speakers, emergency-facility availability or field accuracy of satellite interpretations.

A manually checked factual set, consented speech samples from multiple speakers, current facility verification and independent geospatial references remain high-value work.

### 5.5 Scheduled retention is still needed

Several records expire on access or are pruned on subsequent writes. The move to in-memory geometry improves privacy, but an expiry check when a cache is accessed is not the same as guaranteed removal at a wall-clock deadline.

Use an independent maintenance job and test inactivity as well as normal traffic. Ensure public retention wording matches primary storage and backups. [Location memory][R21] · [User records][R23] · [Trace retention][R24]

### 5.6 Deferring a broad refactor is reasonable

The response declines a large answer-workflow refactor before the freeze. I agree with that sequencing. Fix the specific identity, privacy and delivery errors first, preserve the working capability set, and modularise incrementally afterwards.

Similarly, clearly identifying the parser as a resource-limited subprocess corrects the immediate overstatement. Stronger isolation is still a real future requirement; the wording change does not implement containment.

## 6. Updated status of all 24 original recommendations

“Partial” means some useful work is implemented, while the original broader acceptance criterion is not fully met. “Deferred” means a conscious roadmap choice, not an assertion that the current feature is broken.

| # | Original recommendation | Re-review status | Next concrete action |
| --- | --- | --- | --- |
| 01 | Bind claims to the right evidence | **Partial; original example fixed** | Reject shared-name, wrong-column-year and wrong-quarter substitutions; bind complete claims. |
| 02 | Recipient-level alert delivery/retries | **Partial; normal retry behaviour fixed** | Durable recipient operations, provider IDs, callbacks and interruption recovery before live alerts. |
| 03 | Durable, ordered WhatsApp processing | **Open; apologies added** | Persist the inbox before acknowledgement; process and recover jobs in sender order. |
| 04 | Plot/history cache identity | **Partial; original collision fixed** | Bind user-provided shapes to the active plot and invalidate them when the farm changes. |
| 05 | Location privacy contract | **Partial; geometry table removed** | Apply coordinate handling to stored text, transcripts, failures and follow-up history; align alert-log wording. |
| 06 | Correct source evidence crops | **Deferred** | Use source row/column identity to select the crop and retain unit/period headers. |
| 07 | Hausa audio replies | **Deferred and honestly documented** | Trial comprehensible short Hausa output with a text fallback; retain current feature status. |
| 08 | Broader Hausa speech evaluation | **Open/deferred** | Consent-based held-out recordings across speakers and conditions; score critical factual transcription errors. |
| 09 | Independent factual benchmark | **Open/deferred** | Manually verify source claims independently of the extracted tables used by the application. |
| 10 | Extraction provenance and dataset versions | **Partial** | Keep existing document provenance and regression lessons; add versioned acceptance/rollback and quality reporting. |
| 11 | Financial status versus physical progress | **Partial** | Use explicit financial-proxy wording and avoid implying independently observed completion. |
| 12 | Independent satellite validation | **Partial** | Retain experimental labels and improved radar checks; validate against external references and field observations. |
| 13 | Facility freshness and capability checks | **Partial** | Coordinate/pin handling improved; add dated verification of operational status, services and emergency capability. |
| 14 | Hazard freshness and coverage monitoring | **Partial; admin page now implemented** | Monitor expected sources, stale/failed layers and coverage gaps; test outage behaviour. |
| 15 | Enforceable operating budget | **Open beyond existing estimates** | Persist actual usage/cost attribution and reserve spend atomically before work. |
| 16 | Parser containment | **Wording corrected; stronger isolation deferred** | Add restricted filesystem/network/process permissions before stronger security claims or wider ingestion. |
| 17 | Activity-independent retention | **Open** | Scheduled deletion/pruning plus backup and inactivity tests. |
| 18 | Liveness, readiness and capability status | **Partial** | Admin visibility improved; add readiness checks and capability availability conditions. |
| 19 | Complete backup and recovery | **Partial; local SQLite backups implemented** | Decouple scheduling, add off-host copies and prove a full restore. |
| 20 | Reproducible setup and continuous checks | **Partial** | Migration step and deploy conversation gate improved; add CI and repeatable test-data/bootstrap instructions. |
| 21 | Explicit capability modules | **Reasonably deferred** | Incremental extraction after the release freeze, protected by the existing tests. |
| 22 | Complete-turn latency | **Partial** | Keep cold/cache measurements; include maps, outgoing delivery, cancellation and concurrency in current-release gates. |
| 23 | Connected journeys and user usefulness | **Presentation strongly improved; impact unvalidated** | Run the three journeys on the release and measure completion/usefulness with actual pilot users. |
| 24 | Accurate README/demo/status claims | **Substantially improved** | Repair report links, update response statuses and narrow attribution/privacy/deadline guarantees. |

The project records place-history first requests of roughly 45–50 seconds and cached requests of roughly 4–7 seconds on two pins. Those are repository-reported measurements, not new measurements from this review. Repeat the relevant speed gate after the geometry-cache and conversation changes; a previous passing result should not be treated as a measurement of every later commit. [Speed report][R31]

## 7. Suggested implementation order

### First: close the three reproduced correctness/privacy gaps

1. **Claim attribution:** add and fix the three new mismatches; correct the verification label while a complete binding is unavailable.
2. **Farm switching:** invalidate or rebind user-provided geometry when the active farm changes.
3. **Text-location persistence:** apply the chosen privacy policy consistently before storage, including conversation history.

For each, keep the original passing regression and add the broader case. A narrowly passing example should not be the only evidence for closing a finding.

### Second: make the demonstration evidence match the release

4. Send checked text before optional map work, and give the optional work a bounded timeout.
5. Repair README evaluation links and update the finding-status table.
6. Deploy the intended reviewed release through the existing gate and confirm its `/version`.
7. Phone-test budget → show working; farm A → size → farm B → history; typed coordinates; facility pin and directions; and a controlled failure response.

No live emergency or alert needs to be triggered for a demonstration. Use clearly marked synthetic test phrases and dry-run evidence.

### Third: before wider unattended access

8. Implement durable inbound work and the recipient outbox before enabling live alerts.
9. Add readiness and maintenance monitoring, off-host backup, and a full restore exercise.
10. Add the independently checked factual, speech, facility and geospatial evidence needed for stronger reliability claims.
11. Reconcile real operating costs and make retention independent of subsequent user activity.

## 8. Release decision

| Intended use | Judgment at this snapshot |
| --- | --- |
| Demonstration of the product vision | **Substantially stronger.** The connected journeys and transparent feature states help. Fix the three reproduced gaps and validate the selected release. |
| Small, supervised pilot | **Conditional.** Keep experimental place history explicit, alerts in dry run, and review failures and factual samples closely. |
| Unattended broad public service | **Not yet established.** Durable work, complete privacy enforcement, delivery state, recovery and independent accuracy evidence remain incomplete. |

The project stands out more clearly now. Its next improvement should be making “this figure belongs to this agency and period” and “this observation belongs to this farm” dependable across an entire conversation.

## Appendix A. Reproduction method and limits

The script below was executed against the reviewed commit. It uses repository test fixtures, synthetic people/places and substitutes for external model, imagery and send calls. It does not send a WhatsApp message, invoke a paid model, contact the production database or modify source files.

Run it from an isolated checkout with its dependencies installed, saving the code as a temporary file outside the repository:

```bash
PYTHONPATH=. .venv/bin/python /tmp/kasafi_followup_reproductions.py
```

The script records observed behaviour rather than containing failing assertions. For a regression test, assert the corrected desired behaviour from each finding's acceptance criteria. It imports current test helpers and is therefore pinned to this commit.

The interruption test demonstrates lack of a durable record after one successful send return. The geometry test demonstrates which polygon the application selects; imagery is substituted. The attribution tests supply deliberately wrong model outputs to test the verifier. The timeout test uses a reduced threshold to test scope, not production speed.

### Executed probe code

```python
"""Read-only local regression probes for Kasafi commit 89ea576.
Run from the repository root with PYTHONPATH=. and its Python environment.
Only synthetic inputs and stubbed external services; no live messages or models.
"""
import asyncio
import json
import tempfile
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import AsyncMock, patch

from shapely.geometry import Point, shape
from app.agent import answer as M
from app.agent.answer import Evidence, Plan
from app.alerts.dispatch import dispatch
from app.alerts.triggers import Candidate
from app.config import Settings
from app.geo.location import Spot, memory
from app.guardrails.scope import Verdict
from app.place import answer as PA
from app.place.floods import FloodEvidence
from app.users import UserStore, user_key
from app.whatsapp import conversation as C
from tests.helpers import make_settings
from tests.test_place_answer import _history, TODAY
from tests.test_place_shape import FakeAnswer, located, _pin, _text, LAT, LON


def emit(case, **values):
    print(json.dumps({"case": case, **values}, ensure_ascii=False))


def check_attribution():
    cases = [
        ("original_case_fixed",
         "Health allocation: 100,000,000.00. Education allocation: 200,000,000.00.",
         "Health was allocated 200,000,000.00 in 2026 [1]."),
        ("shared_entity_word",
         "Ministry of Basic Education allocation: 100,000,000.00.\n"
         "Ministry of Higher Education allocation: 200,000,000.00.",
         "The Ministry of Basic Education was allocated 200,000,000.00 in 2026 [1]."),
        ("wrong_year_column",
         "Ministry of Health | 2025 Approved Budget: 100,000,000.00 | "
         "2026 Approved Budget: 200,000,000.00",
         "The Ministry of Health was allocated 100,000,000.00 in 2026 [1]."),
        ("wrong_quarter",
         "Ministry of Health | Actual expenditure Q1 2026: 100,000,000.00 | "
         "Actual expenditure Q1-Q3 2026: 200,000,000.00",
         "The Ministry of Health spent 200,000,000.00 in Q1 2026 [1]."),
    ]
    for label, source, claim in cases:
        evidence = [Evidence(1, "budget-2026-approved", "2026 Approved Budget",
                             2026, 10, "text", source)]
        question = ("How much was allocated to Basic Education in 2026?"
                    if label == "shared_entity_word"
                    else "How much did health spend in Q1 2026?"
                    if label == "wrong_quarter"
                    else "How much was allocated to health in 2026?")
        plan = Plan(question, ["health"], ["budget-2026-approved"])
        compose = AsyncMock(return_value={"summary": claim, "cited": [1], "found": "full"})
        with (
            patch.object(M, "compose", compose),
            patch.object(M.pool, "run", AsyncMock(return_value=evidence)),
            patch.object(M, "scope_notes", return_value=""),
            patch.object(M, "off_topic_note", return_value=""),
        ):
            answer = asyncio.run(M._page_path(
                None, plan, question, "en", None, Settings(_env_file=None), {},
                acq=None, latest=None, prev=None, context="", recheck_note="",
                cache={"evidence": evidence},
            ))
        emit(label, verified=answer.verified, verification=answer.verification,
             compose_calls=compose.call_count, answer=answer.text, problems=answer.attribution)


async def allow(*args, **kwargs):
    return Verdict("ok", "none")


def check_shape_and_coordinates():
    settings, store = make_settings(), UserStore(":memory:")
    key = user_key("2348000000002", settings)  # Synthetic test number from repository fixtures.
    store.create(key, "en")
    store.give_consent(key)
    memory.forget(key)
    memory.remember(key, Spot(LAT, LON, "NG034021", "Wamakko", how="pin"))
    calls = []

    async def answer(question, lang, **kwargs):
        place = kwargs.get("place")
        calls.append(place)
        if place and place.get("ask_size") and not place.get("shape"):
            return FakeAnswer("SIZE?", False, needs_size=True)
        return FakeAnswer("ANSWER")

    def run(message):
        return asyncio.run(C.handle(
            message, None, store=store, settings=settings, locate_fn=located,
            answer_fn=answer, guard_fn=allow,
        ))

    run(_text("How green was my farm in 2024?"))
    run(_text("3 acres"))
    original = calls[-1]["shape"]["geometry"]
    lat2, lon2 = LAT + 0.02, LON + 0.02
    run(_pin(lat2, lon2))
    run(_text("How green was my farm in 2024?"))
    place = calls[-1]
    captured = {}

    def history(conn, lat, lon, **kwargs):
        captured.update(lat=lat, lon=lon, polygon=kwargs.get("polygon"))
        return _history()

    with (
        patch.object(PA.H, "point_history", history),
        patch.object(PA, "flood_evidence", return_value=FloodEvidence()),
    ):
        result = asyncio.run(PA.place_answer(
            None, settings, "How green was my farm in 2024?", "", "en", place,
            TODAY, ask_size=True,
        ))
    emit("new_pin_old_shape",
         point_updated=(place["lat"], place["lon"]) == (lat2, lon2),
         old_shape_retained=place["shape"]["geometry"] == original,
         polygon_sent_to_history_is_old_shape=captured["polygon"] == original,
         analysis_polygon_contains_new_pin=shape(captured["polygon"]).covers(Point(lon2, lat2)),
         answer_found=result.found)

    memory.forget(key)
    question = ("What is the 2026 agriculture budget near my farm at "
                "13.0589127, 5.1673341?")
    run(_text(question))
    stored = store._db.execute(
        "SELECT question FROM turns WHERE user_key=? ORDER BY at DESC LIMIT 1", (key,)
    ).fetchone()[0]
    emit("typed_coordinates_persist", stored_question=stored,
         contains_exact_pair="13.0589127, 5.1673341" in stored)
    store._db.close()


def check_interrupted_alert():
    now = datetime(2026, 11, 1, 12, tzinfo=timezone.utc)
    settings = Settings(_env_file=None, kasafi_alerts_dry_run=False,
                        kasafi_alerts_daily_cap=10, kasafi_alert_template_langs="ha")
    candidate = Candidate("heat", "NG034006", "review-interrupted-send", False,
                          {"ha": "synthetic", "en": "synthetic"},
                          {"ha": "synthetic", "en": "synthetic"})
    with tempfile.TemporaryDirectory() as folder:
        db = Path(folder) / "state.sqlite"
        store = UserStore(str(db))
        for user in ("u1", "u2"):
            store.subscribe(user, ["NG034006"], ["heat"], "ha")
        accepted = []

        async def interrupted(key, lang, values):
            if accepted:
                raise asyncio.CancelledError("simulated interruption")
            accepted.append(key)
            return True

        async def first():
            try:
                await dispatch([candidate], store, settings, now, interrupted)
            except asyncio.CancelledError:
                pass

        asyncio.run(first())
        rows = len(store.alert_log())
        store._db.close()
        store = UserStore(str(db))  # Reopen the persisted state, like a restarted worker.

        async def ok(key, lang, values):
            accepted.append(key)
            return True

        outcome = asyncio.run(dispatch([candidate], store, settings, now, ok))
        emit("alert_interruption", log_rows_after_interruption=rows,
             accepted_attempts=accepted, counts=dict(Counter(accepted)),
             retry_result=dict(outcome))
        store._db.close()


def check_map_deadline():
    # Invalid local database address only enables the relevant branch; all database paths are avoided/stubbed.
    settings = make_settings(database_url="postgresql://x:y@127.0.0.1:1/none",
                             kasafi_answer_timeout_s=0.05)
    store = UserStore(":memory:")
    sender = "2348000000099"  # Synthetic.
    key = user_key(sender, settings)
    memory.forget(key)
    store.create(key, "en")
    store.give_consent(key)

    class Reply:
        text = "ANSWER"
        maps = [{"kind": "synthetic"}]

    async def answer(*args, **kwargs):
        return Reply()

    async def nothing(*args, **kwargs):
        return None

    def maps(*args, **kwargs):
        time.sleep(0.2)
        return []

    message = {"from": sender, "id": "review-map-budget", "type": "text",
               "text": {"body": "What is the agriculture budget in 2026?"}}
    started = time.perf_counter()
    with patch.object(C, "render_specs", maps), patch.object(C, "_facilities", nothing):
        result = asyncio.run(C.handle(
            message, None, store=store, settings=settings, answer_fn=answer,
            guard_fn=allow, place_fn=nothing, notify=nothing,
        ))
    emit("map_outside_timeout", configured_answer_timeout_s=settings.kasafi_answer_timeout_s,
         handle_seconds=round(time.perf_counter() - started, 3),
         outputs=[out.text for out in result])
    store._db.close()


if __name__ == "__main__":
    check_attribution()
    check_shape_and_coordinates()
    check_interrupted_alert()
    check_map_deadline()
```

### Recorded probe output

```jsonl
{"case": "original_case_fixed", "verified": false, "verification": "unsupported", "compose_calls": 2, "answer": "I found documents about your question, but couldn't verify the figures. Please check these sources:\n\n[1] 2026 Approved Budget, page 10", "problems": ["entity: 200,000,000.00 is in the row 'Education allocation: 200,000,000.00.', not in the row of 'health'"]}
{"case": "shared_entity_word", "verified": true, "verification": "attribution checked", "compose_calls": 1, "answer": "The Ministry of Basic Education was allocated ₦200.00 million in 2026.\n\n📄 *Sources:* 2026 Approved Budget, p. 10", "problems": []}
{"case": "wrong_year_column", "verified": true, "verification": "attribution checked", "compose_calls": 1, "answer": "The Ministry of Health was allocated ₦100.00 million in 2026.\n\n📄 *Sources:* 2026 Approved Budget, p. 10", "problems": []}
{"case": "wrong_quarter", "verified": true, "verification": "attribution checked", "compose_calls": 1, "answer": "The Ministry of Health spent ₦200.00 million in Q1 2026.\n\n📄 *Sources:* 2026 Approved Budget, p. 10", "problems": []}
{"case": "new_pin_old_shape", "point_updated": true, "old_shape_retained": true, "polygon_sent_to_history_is_old_shape": true, "analysis_polygon_contains_new_pin": false, "answer_found": true}
{"case": "typed_coordinates_persist", "stored_question": "What is the 2026 agriculture budget near my farm at 13.0589127, 5.1673341?", "contains_exact_pair": true}
{"case": "alert_interruption", "log_rows_after_interruption": 0, "accepted_attempts": ["u1", "u1", "u2"], "counts": {"u1": 2, "u2": 1}, "retry_result": {"sent": 1}}
{"case": "map_outside_timeout", "configured_answer_timeout_s": 0.05, "handle_seconds": 0.202, "outputs": ["ANSWER", "(The map for this answer couldn't be drawn this time.)"]}
```

## Appendix B. Source references

All repository links below are pinned to the reviewed commit, except the explicit baseline and commit links. Public endpoint observations are point-in-time checks and are not continuous monitoring.

[BASE]: https://github.com/bawanallahbilyaminu/kasafi-agent/commit/645456d034ec1e96e0d3ed2bc800ef198b3b3a0e
[HEAD]: https://github.com/bawanallahbilyaminu/kasafi-agent/commit/89ea576256c08bf56f0dce9660bfc30623a8ce17
[R01]: https://github.com/bawanallahbilyaminu/kasafi-agent/blob/89ea576256c08bf56f0dce9660bfc30623a8ce17/README.md#L1
[R02]: https://github.com/bawanallahbilyaminu/kasafi-agent/blob/89ea576256c08bf56f0dce9660bfc30623a8ce17/app/agent/attribution.py#L166
[R03]: https://github.com/bawanallahbilyaminu/kasafi-agent/blob/89ea576256c08bf56f0dce9660bfc30623a8ce17/tests/test_attribution.py#L1
[R04]: https://github.com/bawanallahbilyaminu/kasafi-agent/blob/89ea576256c08bf56f0dce9660bfc30623a8ce17/app/agent/answer.py#L1604
[R05]: https://github.com/bawanallahbilyaminu/kasafi-agent/blob/89ea576256c08bf56f0dce9660bfc30623a8ce17/app/alerts/dispatch.py#L61
[R06]: https://github.com/bawanallahbilyaminu/kasafi-agent/blob/89ea576256c08bf56f0dce9660bfc30623a8ce17/tests/test_review_round.py#L28
[R07]: https://github.com/bawanallahbilyaminu/kasafi-agent/blob/89ea576256c08bf56f0dce9660bfc30623a8ce17/app/place/outline.py#L222
[R08]: https://github.com/bawanallahbilyaminu/kasafi-agent/blob/89ea576256c08bf56f0dce9660bfc30623a8ce17/app/place/history.py#L165
[R09]: https://github.com/bawanallahbilyaminu/kasafi-agent/blob/89ea576256c08bf56f0dce9660bfc30623a8ce17/migrations/versions/0022_drop_plot_outline_cache.py#L1
[R10]: https://github.com/bawanallahbilyaminu/kasafi-agent/blob/89ea576256c08bf56f0dce9660bfc30623a8ce17/tests/test_e2e_conversation.py#L1
[R11]: https://github.com/bawanallahbilyaminu/kasafi-agent/blob/89ea576256c08bf56f0dce9660bfc30623a8ce17/deploy/deploy.sh#L93
[R12]: https://github.com/bawanallahbilyaminu/kasafi-agent/blob/89ea576256c08bf56f0dce9660bfc30623a8ce17/app/users.py#L178
[R13]: https://github.com/bawanallahbilyaminu/kasafi-agent/blob/89ea576256c08bf56f0dce9660bfc30623a8ce17/app/hazards/fetch.py#L291
[R14]: https://github.com/bawanallahbilyaminu/kasafi-agent/blob/89ea576256c08bf56f0dce9660bfc30623a8ce17/deploy/remote.sh#L44
[R15]: https://github.com/bawanallahbilyaminu/kasafi-agent/blob/89ea576256c08bf56f0dce9660bfc30623a8ce17/app/whatsapp/conversation.py#L268
[R16]: https://github.com/bawanallahbilyaminu/kasafi-agent/blob/89ea576256c08bf56f0dce9660bfc30623a8ce17/app/admin/__init__.py#L312
[R17]: https://github.com/bawanallahbilyaminu/kasafi-agent/blob/89ea576256c08bf56f0dce9660bfc30623a8ce17/app/place/radar.py#L94
[R18]: https://github.com/bawanallahbilyaminu/kasafi-agent/blob/89ea576256c08bf56f0dce9660bfc30623a8ce17/app/place/planner.py#L381
[R19]: https://github.com/bawanallahbilyaminu/kasafi-agent/blob/89ea576256c08bf56f0dce9660bfc30623a8ce17/app/place/area.py#L232
[R20]: https://github.com/bawanallahbilyaminu/kasafi-agent/blob/89ea576256c08bf56f0dce9660bfc30623a8ce17/docs/demo-script.md#L1
[R21]: https://github.com/bawanallahbilyaminu/kasafi-agent/blob/89ea576256c08bf56f0dce9660bfc30623a8ce17/app/geo/location.py#L40
[R22]: https://github.com/bawanallahbilyaminu/kasafi-agent/blob/89ea576256c08bf56f0dce9660bfc30623a8ce17/app/place/answer.py#L690
[R23]: https://github.com/bawanallahbilyaminu/kasafi-agent/blob/89ea576256c08bf56f0dce9660bfc30623a8ce17/app/users.py#L453
[R24]: https://github.com/bawanallahbilyaminu/kasafi-agent/blob/89ea576256c08bf56f0dce9660bfc30623a8ce17/app/agent/trace.py#L25
[R25]: https://github.com/bawanallahbilyaminu/kasafi-agent/blob/89ea576256c08bf56f0dce9660bfc30623a8ce17/docs/site/privacy.md#L29
[R26]: https://github.com/bawanallahbilyaminu/kasafi-agent/blob/89ea576256c08bf56f0dce9660bfc30623a8ce17/app/users.py#L380
[R27]: https://github.com/bawanallahbilyaminu/kasafi-agent/blob/89ea576256c08bf56f0dce9660bfc30623a8ce17/app/alerts/recipients.py#L55
[R28]: https://github.com/bawanallahbilyaminu/kasafi-agent/blob/89ea576256c08bf56f0dce9660bfc30623a8ce17/app/whatsapp/webhook.py#L136
[R29]: https://github.com/bawanallahbilyaminu/kasafi-agent/blob/89ea576256c08bf56f0dce9660bfc30623a8ce17/docs/reviews/2026-11-01-external-review.md#L870
[R30]: https://github.com/bawanallahbilyaminu/kasafi-agent/blob/89ea576256c08bf56f0dce9660bfc30623a8ce17/app/main.py#L105
[R31]: https://github.com/bawanallahbilyaminu/kasafi-agent/blob/89ea576256c08bf56f0dce9660bfc30623a8ce17/evals/place/speed-report.md#L1

## Response to the follow-up review (Bilyaminu Bawan Allah / Kasafi, 1 Nov 2026)

Each Appendix A probe was turned into a failing regression test first, then fixed, in the order given. Deployed as
`DEPLOYED_COMMIT` on 1 Nov 2026 (`/version` confirmed), after the unit suite (1,620 tests), the end-to-end
conversation suite and the pre-deploy evaluation sets at 0 wrong: fresh draw 52, topics 12, patterns 22, advisories 5,
guardrails 104, place history 103 in code and 103 through the pipeline, the new routing set 56 and the new survey set
23. Evaluation spend on the day was $13.76 under a one-off $14 cap (the default cap is $5).

| Finding | Status | What was done |
| --- | --- | --- |
| 1 Claim attribution | **done for the three probes and their neighbours; still a rule-based check** | `app/agent/attribution.py` binds each figure to its row's entity, the year and quarter period of the figure's own column, its unit and kind. One shared word never binds (Basic vs Higher Education); a row with 2025 and 2026 columns binds the amount to its column (a row printing one amount in two columns binds to whichever the answer names); Q1 and Q1–Q3 are different periods; plan names and Hausa aliases bind per entity. When the row can't settle the entity, year or period the state is *figures checked*, never *attribution checked*; the README says so. Survey and statistics tables (MICS, NDHS, the MPI) bind by geography (the Sokoto row, never the national Total or the zone), indicator, survey year and sub-population, found while fixing the live MICS refusal the same afternoon. Tests: `tests/test_attribution.py`, `tests/test_survey_attribution.py` (the three probes, valid Basic/Higher and multi-year answers, the live survey cases). Rendering financial sentences from bound records (suggestion 4) remains open. |
| 2 Farm switching | **done** | A size or corner shape belongs to the plot it was given for (`LocationMemory` keeps the plot's point with the shape); a new ordinary pin outside the plot drops it, so farm B is asked its own size; corner *done* re-resolves the LGA and ward at the plot's centre; `place_answer` ignores any shape that doesn't contain the active pin. Tests: farm A → size → farm B and farm A → corners → farm B, including a move across an LGA boundary, and the same farm keeping its shape (`tests/test_place_shape.py`). |
| 3 Typed and spoken locations | **done** | One redactor (`app/privacy.py`: decimal pairs, labelled lat/lon, degrees-minutes, plus codes) at the shared boundaries: every text the user store writes (turns, saved working, pending questions and options), traces and failure records, every log record (a record factory), and the question and follow-up history sent to the models. Text stored before is cleaned when the store opens; backups rotate after 7 days. STOP and DELETE MY DATA remove the coded ID from the failed-send lists in `alert_log`, and `docs/site/privacy.md` now describes those coded IDs and the typed-location rule. Tests: `tests/test_location_privacy.py` inspects SQLite, the logs and the model-bound text after typed-coordinate and voice-transcript conversations; budget figures survive. |
| 4 Alert delivery | **not in this round** | Alerts stay in dry run. The per-recipient outbox persisted before sending, with provider IDs and delivery callbacks, is the condition for going live. |
| 5 Reply timing | **done** | The checked text is sent as soon as it is ready; maps render after it under their own 30 s deadline (a note when not drawn) and evidence crops under 45 s; nothing from an answer past its 120 s limit can be sent after the apology (a timed-out job's late message is dropped). The README states these limits instead of "never silence" and says incoming jobs are not yet persisted. Tests: `tests/test_long_jobs.py`. |
| 6 Documentation | **done** | The two linked reports are committed; the response table in the first review marks 01, 02, 14, 18, 19 and 22 partial; the README status table carries the deployed commit and date. |
| §5.1 Backups | **done** | The daily SQLite backup runs in its own maintenance thread (`app/maintenance.py`) whenever `KASAFI_BACKUP_DIR` is set, independent of hazard fetching; tested with fetching off. Off-host copies and a restore rehearsal remain planned. |

Two live misroutes found the same afternoon were fixed as a class and are part of the gate: a question naming a
publisher, survey or report goes to the planner and the document path whatever facility, place or hazard words it
contains, and a shortcut fires only on unambiguous intent for its feature (`app/agent/routing.py`, `docs/routing.md`,
with feature switches `KASAFI_SHORTCUT_*` and a 56-case routing set checked in code). The place-history scope now comes
from the user's own words, because the planner's English rewrite had been sending "my LGA" statewide.

Still open from the first review and this one: the durable inbox and recipient outbox (02, 03), readiness checks
(18), off-host backups and a restore rehearsal (19), activity-independent retention (17), an independent factual
benchmark (09), and rendering financial sentences from bound records (01, suggestion 4).

