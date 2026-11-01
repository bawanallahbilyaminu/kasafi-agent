# Kasafi: Comprehensive Review and Recommendations

**Prepared for:** Bilyaminu Bawan Allah / Halal Numeriq Limited  
**Review date:** 1 November 2026, Africa/Lagos  
**Repository:** https://github.com/bawanallahbilyaminu/kasafi-agent  
**Reviewed commit:** [`645456d034ec1e96e0d3ed2bc800ef198b3b3a0e`][S01]  
**Purpose:** A candid product and engineering assessment, followed by individually actionable recommendations.  
**Status:** Review and proposed work only. No application fixes or deployments were performed as part of this report.

## Contents

- [1. Overall assessment](#1-overall-assessment)
- [2. Scope, evidence, and limitations](#2-scope-evidence-and-limitations)
- [3. Feature-by-feature assessment](#3-feature-by-feature-assessment)
- [4. Findings and recommendations, one by one](#4-findings-and-recommendations-one-by-one)
- [5. Suggested implementation sequence](#5-suggested-implementation-sequence)
- [6. Release and pilot acceptance checklist](#6-release-and-pilot-acceptance-checklist)
- [Appendix A: Reproducing the three demonstrated defects](#appendix-a-reproducing-the-three-demonstrated-defects)
- [Appendix B: Source references](#appendix-b-source-references)

## 1. Overall assessment

Kasafi has a strong, useful core and substantial engineering behind it. Its most developed capabilities connect Hausa questions to structured Sokoto budget data, public documents, calculations, citations, and source images. The implementation addresses difficult details: approved versus revised budgets, spending periods, ambiguous questions, disagreeing readings, missing documents, and source provenance.

The central weakness is the uneven level of reliability across an expanding feature set. The project now combines public-finance analysis, policy/statistical research, hazard information, facility navigation, alerts, and satellite-based place history. Those capabilities have different failure modes and require different evidence before they can be trusted.

### Preserve the broader vision

The recommendation is to **keep the broader feature set and strengthen its integration and reliability**. Feature breadth can be Kasafi's differentiator. The earlier suggestion to centre the public product only on budgets was a conservative release strategy, not a conclusion that the other features lack value.

A coherent positioning is:

> Kasafi is a Hausa-speaking local information assistant that connects public spending, official information, services, and environmental evidence to people's questions about Sokoto.

The strongest demonstration is a connected journey. A farmer asking about flooding could receive dated historical evidence, a current official outlook where available, and relevant flood-control or irrigation budget lines. Each component should preserve its own scope and uncertainty. Combining them must not imply that a budget allocation proves work was completed, or that a satellite observation predicts what will happen next.

### What deserves credit

1. **A clear local use case.** Hausa interaction and Sokoto-specific information give the product a concrete audience.
2. **A structured financial core.** The system uses extracted entities and code-based calculations instead of relying entirely on generated prose.
3. **Inspectable answers.** Citations, source images, working, quotes, and admin traces help people examine how an answer was produced.
4. **Meaningful agent behaviour.** Planning, source discovery, acquisition, indexing, and multi-document answering are implemented capabilities.
5. **Attention to failures.** The evaluation reports record limitations, regressions, model variability, and known extraction gaps.
6. **A substantial test suite.** The local run recorded 1,284 passing tests. This is useful engineering evidence, although it is not proof of end-to-end factual accuracy.
7. **Thoughtful controls.** Consent, signed webhooks, HMAC user identifiers, encrypted alert recipients, guarded admin pages, and source restrictions are valuable foundations.

### The candid judgment

Kasafi is a substantial prototype suitable for a carefully monitored pilot. Its differentiation is credible. Its strongest claims about verification, delivery, location handling, and broad readiness need tightening. The next development cycle should concentrate on making the existing capabilities dependable and demonstrably useful.

## 2. Scope, evidence, and limitations

This document consolidates the repository review and the subsequent discussion about keeping Kasafi's breadth. It refers to the pinned commit above, not to an unspecified future version of `main`.

### Work performed during the review

- Cloned and inspected the repository, including implementations, configuration, tests, evaluation reports, architecture notes, and deployment files.
- Reviewed every major feature family listed in Section 3. This was not a line-by-line audit of every file.
- Ran the local test suite. The final recorded result was **1,284 passed, 86 skipped, 9 warnings**.
- Installed an environment-only SOCKS dependency needed by the review environment before the successful test run. The project source and lockfile were not changed.
- Ran controlled local checks that reproduced incorrect claim verification, suppressed alert retries, and incorrect outline-cache reuse.
- Checked the public API during the review: `/health` returned HTTP 200, and `/version` reported `cac8918e7808c052ee3b84e1ebc5336d22a331b7`, a different commit from the source snapshot reviewed.

The API observations are point-in-time observations from the preceding review, not a continuing availability check. A successful health response did not establish that every dependency or feature was ready.

### What was not independently established

- Full WhatsApp behaviour with real users and production configuration.
- Current production database contents or the freshness of every source.
- Paid-model accuracy, cost, and latency across the full live evaluation suites.
- Ground-truth accuracy of the budget corpus, facility registry, or satellite-derived results.
- Real-world emergency performance, user comprehension, retention, or willingness to pay.
- Commercial licensing or legal compliance. References to privacy describe implementation/documentation consistency, not a legal determination.

The 86 skipped tests primarily depended on databases, source files, credentials, or explicitly enabled network tests. Passing the remaining tests does not validate the skipped paths.

### Evidence labels

| Label | Meaning |
|---|---|
| **Reproduced defect** | A controlled local check demonstrated the behaviour in the reviewed implementation. |
| **Source finding** | The behaviour or omission is supported by inspected code/configuration; a production incident was not demonstrated. |
| **Repository-reported result** | A measurement or deployment status is documented by the project and was not independently rerun here. |
| **Recommendation** | A proposed design, validation, or product improvement, rather than an established defect. |

### Priority labels

| Priority | Meaning |
|---|---|
| **P1** | Address before enabling or expanding the affected capability, especially where incorrect information, missed delivery, privacy inconsistency, or data loss is possible. |
| **P2** | Important work for the next reliability and product-improvement cycle. |
| **P3** | Longer-term optimisation or expansion after the main reliability gates are satisfied. |

Priority is conditional on use. For example, fixing live alert delivery is a P1 gate for enabling live alerts; it does not require removing a properly labelled dry-run demonstration.

## 3. Feature-by-feature assessment

“Implemented” means code was found. It does not independently establish that the feature is enabled, populated with data, or working in production.

| No. | Feature | Assessment | Suggested next action |
|---|---|---|---|
| 1 | Hausa/English WhatsApp text | Implemented with consent, language selection, message splitting, and preferences. A strong interface choice. | Test complete journeys with new users and simultaneous messages. |
| 2 | Hausa voice recognition | Dual transcription and reconciliation address genuine recognition weaknesses. Read-back and correction flows exist. | Expand independent testing across speakers, noise, numbers, dates, and locations. |
| 3 | Spoken Hausa answers | Described in the architecture, but no synthesis/outgoing audio-answer path was found in the reviewed implementation. | Complete and validate short voice summaries. |
| 4 | Budget and implementation-report questions | The strongest feature family: allocations, revisions, actual spending, comparisons, shares, and trends. | Close semantic verification gaps and independently audit extraction. |
| 5 | Structured analysis tools | Project status, LGA projects, rankings, ministry profiles, function profiles, and revenue analysis are implemented. | Preserve period, coverage, and interpretation limits in every result. |
| 6 | Multi-source policy and statistical answers | Source selection, dates, definitions, geographic scope, and disagreement handling are substantive. | Test attribution and comparisons against independent source-based answers. |
| 7 | IOM DTM integration | Structured LGA-level information is a useful complement to PDF search. | Validate edition selection, missing areas, definitions, and totals when credentials are configured. |
| 8 | Autonomous document discovery and acquisition | Trusted-source search, download limits, OCR, indexing, provenance, and review support are implemented. | Strengthen parser isolation and add reliable background acquisition states. |
| 9 | Two-model reading and verification | Independent readings and reconciliation provide useful checks. Some paths still equate numerical presence with factual support. | Bind claims to specific evidence records and qualify verification status. |
| 10 | Citations and evidence crops | Strong inspectability feature. Crop selection can be ambiguous on repeated numbers or multi-table scans. | Target the cited row/table and retain headers and units. |
| 11 | Follow-ups and corrections | Context, confirmation, clarification, and correction paths are implemented. | Test interruptions, concurrent turns, and stale pending state. |
| 12 | Calculations, working, and quotes | Code-based calculations and on-demand working are useful and can avoid extra model calls. | Keep working tied to the exact answer version and period. |
| 13 | Scope guardrails and emergency referral | Extensive rules and tests exist; checking raw speech hypotheses is a strong design choice. | Expand adversarial and varied-speech evaluation; retain immediate local referral behaviour. |
| 14 | Location, facilities, and routing | Gazetteer lookup, PostGIS queries, filters, corrections, routes, and fallbacks are implemented. | Improve facility freshness and maintain explicit service-availability limits. |
| 15 | Hazard layers | Heat, air/dust, rain, river discharge, and fire detections are implemented with provenance and timing. | Monitor freshness and validate meanings and thresholds with domain reviewers. |
| 16 | Official advisories, outlooks, and outbreaks | Official-source routing and dated reporting are meaningful additions. | Distinguish successful checks, partial coverage, stale results, and unavailable sources. |
| 17 | Maps | Useful for facilities, routes, hazards, and place-history comparisons. | Keep scale, age, resolution, missingness, and classification rules visible. |
| 18 | Opt-in hazard alerts | Sign-up, encryption, language handling, quiet hours, caps, and dry-run logging exist. Project notes report dry-run deployment. | Fix per-recipient retries and delivery-state handling before live expansion. |
| 19 | Point-level satellite history and plot outlines | Ambitious implementation covering vegetation, rainfall, water evidence, radar, and SAM-based outlines. Project notes describe it as not yet deployed. | Fix cache identity and privacy handling; validate against independent observations. |
| 20 | Ward/LGA/state environmental comparisons | Precomputation, summaries, rankings, and maps are implemented. Generated tests check consistency with precomputed data. | Validate spatial/temporal comparability and external accuracy before decision-grade claims. |
| 21 | Admin traces and review queues | Useful operational tooling with guarded access and source inspection. | Add clear ownership, resolution states, and regression links for reviewed problems. |
| 22 | Privacy, deployment, and operations | Consent and security foundations exist; durable processing, recovery, readiness, and cost accounting need improvement. | Work through the operational recommendations below. |

## 4. Findings and recommendations, one by one

### 01. Bind every financial claim to the correct evidence

**Priority:** P1  
**Evidence:** Reproduced defect  
**Affected capability:** Page-based answers and the meaning of `verified=True`

**Finding.** A synthetic page contained a health allocation of ₦100 million and an education allocation of ₦200 million. A deliberately incorrect model reply assigned ₦200 million to health. The page-answer path returned that statement with a citation and `verified=True`; the consistency check returned no mismatch. This demonstrates a verification weakness, not the frequency with which a live model makes that mistake.

The numeric check confirms that figures occur in cited material. It does not fully bind each figure to the claimed entity, measure, period, unit, and relationship. Two readers can also agree on a shared extraction error or both miss a relevant row. [Sources: numeric check][S02], [page-answer path][S03], [consistency check][S04].

**Suggested changes, in order:**

1. Represent critical claims as structured records containing entity, measure, year/period, unit, value, document, page, and source cell or span.
2. Require the renderer to use those records for financial statements and comparisons.
3. Preserve the distinction between a supported figure and a supported interpretation of that figure.
4. Replace a broad verification boolean with more explicit states, such as value checked, attribution checked, calculation checked, or unsupported.
5. Add wrong-entity, wrong-year, wrong-unit, allocation-versus-spending, and swapped-comparison tests.

**Acceptance criteria:** The reproduced health/education substitution is rejected or corrected. A citation alone cannot promote an unsupported claim to a verified result. Valid supported statements remain answerable.

### 02. Track alert delivery per recipient and retry failures

**Priority:** P1 before live alerts  
**Evidence:** Reproduced defect  
**Affected capability:** Hazard notifications

**Finding.** A controlled send function returned failure. Dispatch recorded `sent` with zero delivered recipients, and a second dispatch made no further attempt. The completed-status logic therefore suppresses recovery from failed or partially failed delivery. [Source: dispatch and completed states][S05].

**Suggested changes, in order:**

1. Create an outbox row for each alert/recipient combination with a stable idempotency key.
2. Track pending, attempting, API-accepted, delivered, retryable failure, and terminal failure separately where supported.
3. Record the provider message ID and process delivery-status callbacks.
4. Retry transient failures with bounded backoff; preserve unsuccessful recipients after partial sends.
5. Keep dry-run records separate from live-send eligibility so a dry run does not silently consume a future live notification.
6. Define a policy for old alerts: recovery must not send an expired warning as if it were current.

**Acceptance criteria:** Zero successful sends remain retryable. A partial failure retries only failed recipients. A process restart does not lose pending work, and a successfully completed recipient does not receive duplicate alerts from ordinary retries.

### 03. Make WhatsApp message processing durable and ordered

**Priority:** P1 before broader unattended use  
**Evidence:** Source finding  
**Affected capability:** Every WhatsApp journey

**Finding.** The webhook acknowledges the request, records message IDs in memory, and schedules application-background work. It does not first persist a processing job. A restart can lose acknowledged work; a failed attempt can be suppressed as already seen; deduplication disappears on restart. [Source: webhook][S06].

**Suggested changes, in order:**

1. Persist a validated inbound message or minimal processing payload before acknowledging acceptance.
2. Use the WhatsApp message ID as a database uniqueness key.
3. Run a worker with explicit queued, processing, completed, and retryable-failure states.
4. Serialize state-changing turns per user so confirmations, corrections, and subsequent questions cannot overwrite each other unpredictably.
5. Add a durable outbound mechanism for replies and meaningful failure visibility for operators.
6. Apply the existing retention and access controls to queued payloads; avoid creating an indefinite second conversation store.

**Acceptance criteria:** A restart after acknowledgement does not lose the message. Duplicate webhooks do not produce duplicate processing. A recoverable failure can be retried. Two rapid messages from the same user maintain sensible conversational order.

### 04. Key plot outlines and histories by the actual analysis area

**Priority:** P1 before expanding place-history use  
**Evidence:** Reproduced outline defect; related history-cache source finding

**Finding.** Two different pins within one rounded coordinate cell shared an outline-cache key. The second received the first outline even though the new pin lay outside it. History caching also does not include the requested polygon in its identity. [Sources: outline cache][S07], [history cache][S08].

**Suggested changes, in order:**

1. Separate reusable coarse grid statistics from results for a specific plot.
2. Include a canonical geometry hash, analysis method/version, source version, and relevant time window in plot-result keys.
3. Validate that a cached outline is appropriate for the requested pin and geometry before returning it.
4. Give fallback or failed outlines an explicit retry/expiry policy; avoid keeping a temporary failure as a permanent answer.
5. Invalidate or rebuild incompatible old cache entries after changing the key design.

**Acceptance criteria:** The two-pin reproduction no longer returns an outline excluding the new pin. Different polygons receive independently valid results. Exact repeated requests still benefit from caching.

### 05. Align location storage with the privacy promise

**Priority:** P1 before enabling the affected place-history path  
**Evidence:** Source finding  
**Affected capability:** Place history, maps, cached geometry, documentation

**Finding.** The privacy policy says exact locations remain in memory and are never written to the database. The plot cache persists geometry; its fallback circle is centred on the original pin. That geometry retains the location even without a user identifier. The newer place-history processing also needs a complete inventory of what reaches external imagery and segmentation services. [Sources: policy][S09], [outline persistence][S07], [fallback geometry][S10].

**Suggested changes, in order:**

1. Map coordinate flow through memory, database caches, traces, logs, map images, external requests, and backups.
2. Choose an explicit contract: genuinely coarse shared-cell results, ephemeral plot geometry, or disclosed storage with a defined purpose and retention period.
3. Implement the chosen contract before changing the wording to match it.
4. Check that user-supplied coordinates cannot leak through free text, exception strings, or trace fields.
5. Add tests that inspect stored records and logs after representative location requests and deletion.

**Acceptance criteria:** The public promise matches actual behaviour. Any exact geometry retained has an explicit purpose, lifecycle, and user-facing explanation. Dropping a user ID is not treated as equivalent to removing location information.

### 06. Crop the cited evidence, including its meaning

**Priority:** P2  
**Evidence:** Source finding; production error frequency was not measured

**Finding.** For scanned pages, `_table_crop` selects the largest detected table. For text pages, figure location begins with the first occurrence of the number. A page can contain multiple tables or repeated amounts. Cropping the wrong region could undermine otherwise useful citations. [Sources: crop selection][S11], [figure search][S12].

**Suggested changes, in order:**

1. Carry row/table identities and bounding boxes from extraction through to the final claim.
2. Match the entity label, amount, column, and nearby header rather than only the amount.
3. Include the unit and relevant year/measure headers in the crop, or attach them unambiguously in the caption.
4. When targeting is uncertain, show a clearly labelled page excerpt or omit the crop instead of implying that an arbitrary region proves the claim.

**Acceptance criteria:** Test pages with duplicate amounts, multiple tables, and cropped-away unit headers produce the correct evidence or an explicit fallback. Images and citations refer to the same claim.

### 07. Complete the voice experience with short Hausa audio replies

**Priority:** P2, high product value  
**Evidence:** Source finding  
**Affected capability:** Accessibility and the voice-first promise

**Finding.** Voice input, transcription, and correction are implemented. The architecture describes Hausa TTS, but no synthesis or outgoing audio-answer path was found in the reviewed application. Text and source images may be insufficient for some of the intended users. [Sources: architecture][S13], [WhatsApp client][S14].

**Suggested changes, in order:**

1. Generate a short spoken summary from the same checked result used by the text answer.
2. Normalize Hausa numbers, naira amounts, years, percentages, and place names before synthesis.
3. Keep the full text, citations, and working available alongside audio.
4. Offer an audio preference and preserve text delivery when synthesis fails.
5. Validate pronunciation, comprehension, latency, and the chosen provider/model's permitted use before release.

**Acceptance criteria:** A Hausa voice question can receive a comprehensible spoken answer. Audio and text agree on values, periods, and uncertainty. Synthesis failure does not prevent the checked text response.

### 08. Evaluate Hausa speech beyond the development recordings

**Priority:** P1 for a broad voice-reliability claim  
**Evidence:** Repository-reported results plus recommendation

**Finding.** The speech report contains a small set of developer recordings, frequent read-backs, and variability across repeated runs. Some later comparisons record silent errors. The report acknowledges that vocabulary was informed by the examples and that model judging is noisy. [Source: speech evaluation][S15].

**Suggested changes, in order:**

1. Build a consented, held-out set with varied speakers, age groups, speech speeds, accents, device quality, background noise, and Hausa/English code-switching.
2. Establish human-reviewed reference wording and intended meaning before evaluating the pipeline.
3. Score critical details separately: year, amount, location, entity, negation, and emergency meaning.
4. Measure silent errors, unnecessary read-backs, successful corrections, abandonment, and complete-turn time.
5. Keep evaluation recordings separate from vocabulary and prompt tuning; version the set and repeat runs to expose variability.

**Acceptance criteria:** Performance is reported by critical-error type and speaker conditions, not only one average score. Read-back confidence is evaluated against actual errors. Each serious discovered failure becomes a regression case.

### 09. Add an independent factual benchmark

**Priority:** P1 for strong accuracy claims  
**Evidence:** Source finding and recommendation

**Finding.** Generated budget evaluation answers are calculated from the same structured core the application reads. A shared extraction error can therefore appear correct in both the application and the expected result. Some checks confirm numbers and phrases without evaluating every assertion. The place-history checks likewise compare outputs to precomputed data. [Sources: generated cases][S16], [generated checker][S17], [place evaluation][S18].

**Suggested changes, in order:**

1. Create a separate set of answers independently checked against original source pages or authoritative structured records.
2. Include swapped entities, wrong units, wrong periods, misleading premises, missing evidence, contradictory sources, and unsupported causal explanations.
3. Score claim-level correctness, citation correctness, completeness, appropriate abstention, and user comprehension separately.
4. Retain generated tests for regression coverage; explicitly label what they establish.
5. Publish the denominator, test-set provenance, model/configuration versions, and variation across repeated runs.

**Acceptance criteria:** A deliberately corrupted extraction cannot pass solely because the expected result was generated from the same corruption. Reports distinguish software consistency from independently checked factual accuracy.

### 10. Treat extraction quality and dataset versions as product features

**Priority:** P2  
**Evidence:** Source finding and repository-reported reconciliation gaps

**Finding.** Reconciliation checks are a strength, and the README discloses missing/interleaved rows and incomplete totals. Structured calculations remain dependent on extraction correctness. The entity model also contains year-specific amount columns, which will need a deliberate evolution strategy as new editions arrive. [Sources: structured entities][S19], [README][S20].

**Suggested changes, in order:**

1. Store extraction version, source hash, page/cell provenance, unit, period, and quality status with the data used by answers.
2. Define what happens when reconciliation fails: quarantine affected aggregates, show explicit coverage limits, or require review.
3. Make known missing rows visible to the answering layer so incomplete subtotals cannot be presented as exhaustive totals.
4. Test new editions before promoting them; preserve rollback to a previous accepted index.
5. Plan a year/measure/period representation or controlled schema-extension process that does not silently drop unfamiliar columns.

**Acceptance criteria:** A known extraction gap produces an honest limitation in affected answers. New editions can be validated and rolled back. Independently audited sample rows retain correct amounts, units, agencies, and periods.

### 11. Keep inferred project status distinct from physical progress

**Priority:** P2  
**Evidence:** Source finding; interpretation recommendation

**Finding.** Project-status categories are derived from a budget's allocation and previous-spending columns. This supports useful financial analysis, but a zero in those columns does not independently establish that no physical work occurred. Likewise, an allocation or expenditure does not prove completion. [Source: project-status analysis][S21].

**Suggested changes, in order:**

1. Describe the result as status inferred from the cited budget/spending columns.
2. State the coverage period, especially when spending is January–September rather than the full year.
3. Prefer wording such as “no spending recorded in these columns” over an unqualified claim that a project is abandoned or inactive.
4. When physical-progress records become available, represent them as separate evidence with dates and sources.

**Acceptance criteria:** A user can distinguish budget presence, recorded spending, and independently observed physical progress. Questions about completed projects do not silently receive a financial proxy as if it were confirmation.

### 12. Validate satellite interpretations independently

**Priority:** P1 before presenting results as dependable plot-level decision support  
**Evidence:** Source finding, repository-reported measurements, and recommendation

**Finding.** The remote-sensing implementation includes useful limitations and several sensible checks. However, implementation agreement and generated tests do not establish field accuracy. The radar method uses a fixed water threshold with a small documented calibration set. SAM outlines and vegetation/rain relationships also need independent validation. [Sources: radar method][S22], [place-history design and measurements][S23].

**Suggested changes, in order:**

1. Keep the feature available as a clearly labelled experimental capability while validation proceeds.
2. Obtain independently checked sites spanning water, cropland, built-up areas, bare soil, irrigated land, and known flooding.
3. Measure false positives and false negatives for water/flood interpretation; validate outlines against separately established boundaries where available.
4. Test sensitivity to clouds, observation counts, vegetation cover, seasonal timing, sensor resolution, and the selected threshold.
5. Validate rain-adjusted greenness on held-out years/locations and communicate it as an empirical relationship, not proof of cause.
6. Keep “no water observed in available passes” distinct from “never flooded.” Preserve the restrictions on ownership and cadastral boundaries.

**Acceptance criteria:** Results include observation support and limitations. Reported environmental accuracy comes from an independent reference set. A generated software-evaluation score is not presented as a flood-detection or boundary-accuracy score.

### 13. Make facility data freshness and capability verification operational

**Priority:** P1 for stronger emergency-navigation promises; P2 for ordinary directory improvements  
**Evidence:** Source finding and repository documentation

**Finding.** The facility implementation provides useful filters, route fallbacks, and corrections. The documented registry is dated November 2024 and lacks confirmed opening hours and functional status. A location correction does not by itself confirm current services or emergency capability. [Sources: facility implementation][S24], [hazard and services documentation][S25].

**Suggested changes, in order:**

1. Track location verification, service/capability verification, operational status, and last review as separate fields.
2. Prioritize confirmation of the facilities used in emergency referral paths.
3. Give corrections an evidence source, reviewer, verification date, and recheck date.
4. Continue labelling straight-line distance separately from road distance and estimated travel time.
5. Avoid claiming the globally fastest facility when only a limited nearby candidate set has been routed.
6. Provide a review mechanism for disputed or outdated records without automatically treating user submissions as verified.

**Acceptance criteria:** Answers distinguish registry facts from recently confirmed facts. Unavailable routing falls back honestly. Emergency paths do not infer current service availability from a historic registry entry alone.

### 14. Monitor hazard freshness and source coverage explicitly

**Priority:** P1 for live alerts; P2 for broader operational improvements  
**Evidence:** Existing controls plus recommendation

**Finding.** Kasafi already contains useful source/time labels, official-first behaviour, and checks around advisory freshness. The remaining task is to ensure those distinctions survive fetch failures, partial source coverage, summaries, maps, and alert generation. This finding does not claim that freshness handling is absent. [Sources: hazard reads][S26], [official-source handling][S27], [fetch scheduler][S28].

**Suggested changes, in order:**

1. Maintain per-source status: last attempt, last success, issue time, valid time, coverage, and next expected update.
2. Distinguish an explicit official absence statement from an empty result on the monitored sources.
3. Define freshness thresholds per layer and prevent stale or incomplete inputs from producing a current-looking alert.
4. Surface stale data and failed refreshes in admin tooling and in affected user answers.
5. Have a qualified domain reviewer check category meanings, calculations, and Hausa wording before expanding advisory claims.

**Acceptance criteria:** Simulated source outages cannot become “no risk” or “no alert” claims. Text and maps agree about the date and source. Operators can identify which layer stopped updating and why.

### 15. Turn the spending estimate into an enforceable operating budget

**Priority:** P1 before broad open access or paid-provider expansion  
**Evidence:** Source finding

**Finding.** Conversation handling adds fixed estimated amounts for a voice note or question. Separate usage counters collect model-token information, but the user-facing daily spend gate is not a reconciliation of all actual provider usage. Retries, OCR, second readings, background tasks, and image operations can have different costs. [Sources: conversation gate][S29], [usage accounting][S30], [configuration][S31].

**Suggested changes, in order:**

1. Introduce a persistent usage ledger with provider, model, operation, tokens/units, estimated charge, and correlation ID.
2. Reserve a conservative budget before an expensive operation and reconcile it after the provider reports usage.
3. Apply atomic reservations across workers; separate interactive, background-fetch, evaluation, and alert budgets.
4. Define fallback behaviour when a budget is exhausted, preserving locally available emergency referral information.
5. Reconcile recorded estimates against provider billing and include external search, messaging, and infrastructure costs in operating reports.

**Acceptance criteria:** Concurrent work cannot independently spend the same remaining budget. Provider usage is attributable to an operation. The system clearly distinguishes an application estimate from a provider-enforced spending ceiling.

### 16. Strengthen containment for untrusted document parsing

**Priority:** P1 for stronger automatic-ingestion security claims  
**Evidence:** Source finding; no exploit was attempted or demonstrated

**Finding.** The parser subprocess strips environment variables and applies resource limits. These measures improve resilience, but the child still runs within the application's surrounding filesystem and network environment. “Resource-limited subprocess” is a more precise description than full security isolation. [Source: parser launcher][S32].

**Suggested changes, in order:**

1. Run parsing under a separate restricted identity or isolated worker/container with a minimal filesystem view.
2. Mount only the required input and output locations; deny access to application state, credentials, and backups.
3. Disable outbound network access for the parser where it is unnecessary.
4. Enforce memory, CPU, process, page-count, output-size, archive-expansion, and wall-clock limits.
5. Inspect the full ingestion path so later rendering or OCR preparation does not bypass containment.

**Acceptance criteria:** A test parser process cannot read a sentinel file outside its allowed mounts or make an outbound request. Malformed documents fail in a bounded way without compromising the main application's availability.

### 17. Enforce retention without depending on future user activity

**Priority:** P2  
**Evidence:** Source finding

**Finding.** Several expiry and deletion operations occur when records are read or new records are written. For example, pending questions and stored LGAs expire when accessed; trace and conversation pruning are tied to subsequent writes. That is useful for application behaviour but is weaker than guaranteed removal from storage on a schedule. [Sources: user state][S33], [trace saving][S34], [privacy policy][S09].

**Suggested changes, in order:**

1. Add a scheduled retention job that covers conversations, pending state, locations, traces, gaps, alerts, and new queue/outbox tables.
2. Define what happens to deleted data in backups and during restore; avoid promising immediate removal from all backups unless implemented.
3. Review free-text traces for residual identifying details; regex redaction does not establish complete anonymisation.
4. Keep deletion instructions consistent across published pages and the actual deletion implementation.
5. Record retention-job success/failure without retaining the content being deleted.

**Acceptance criteria:** Old records disappear even when a user never returns and no new answers are generated. Restoring a backup does not silently defeat documented deletion handling. Privacy wording describes actual trace and backup behaviour.

### 18. Separate liveness, readiness, and feature availability

**Priority:** P2  
**Evidence:** Source finding

**Finding.** `/health` returns a static success response. This establishes that the process can answer that route, but not that PostgreSQL, required schema/data, background fetches, or a particular feature are ready. The differing observed deployment/source commits also show why release identity matters. [Source: health endpoint][S35].

**Suggested changes, in order:**

1. Keep a cheap liveness endpoint for process health.
2. Add readiness checks for essential local dependencies, migration compatibility, and required data availability without triggering expensive model calls.
3. Expose guarded capability status for configured, disabled, dry-run, stale-data, and unavailable features.
4. Track queue age, send failures, provider errors, stale fetches, verification failures, and latency distributions.
5. Include release/configuration identity in operator diagnostics while excluding secrets.

**Acceptance criteria:** Database failure causes readiness to fail while liveness can remain healthy. Operators can distinguish a disabled capability from a broken one. Deployment verification identifies the exact serving commit.

### 19. Back up and restore the complete service state

**Priority:** P1 before expanding the pilot  
**Evidence:** Source finding

**Finding.** The supplied backup service performs PostgreSQL dumps. Consent, language, recent turns, usage, and alert subscriptions are stored separately in SQLite on the data volume. That state needs its own consistent backup and recovery plan. Project notes also acknowledge that off-server copies remain to be addressed. [Sources: deployment configuration][S36], [user store][S33], [architecture][S13].

**Suggested changes, in order:**

1. Inventory PostgreSQL, SQLite, public-document files, corrections, private configuration, encryption keys, and future inbox/outbox state.
2. Back up SQLite using a consistent backup method rather than copying a potentially active database file without its transaction state.
3. Keep encrypted off-host backups with a defined retention policy and restricted access.
4. Preserve key recovery procedures without placing secrets in the repository or in an unprotected report.
5. Rehearse a full restoration in an isolated environment, keeping outbound messaging disabled during the exercise.

**Acceptance criteria:** A restore exercise recovers consent, subscriptions, and required documents as well as PostgreSQL. Pending alerts do not replay unintentionally. Recovery time and the maximum acceptable data-loss window are documented and measured.

### 20. Make setup, continuous checks, and deployment reproducible

**Priority:** P2  
**Evidence:** Source finding

**Finding.** The README quick start omits migration and indexing steps needed for useful document-backed answers. A clean clone cannot reproduce data-dependent features from the listed commands alone. No committed GitHub Actions workflow was found, although the deployment script does run tests. [Sources: setup][S20], [project dependencies][S37], [deployment script][S38].

**Suggested changes, in order:**

1. Provide a clean-machine setup sequence covering dependencies, database extensions, migrations, seed documents, indexing, and a sample query.
2. Explain which capabilities require additional keys or separately obtained datasets, and why some tests skip.
3. Add continuous checks for offline tests and a small PostgreSQL/PostGIS integration suite using redistributable or synthetic fixtures.
4. Add a secrets scan and a policy for dependency updates; keep paid-model evaluation explicit and budgeted.
5. Validate the release artifact, schema, configuration, and a small smoke-test set before promoting it.

**Acceptance criteria:** A new developer can follow the documented instructions and obtain the documented sample answer. CI reports skips explicitly. A release can be tied to a commit, migrations, and data/configuration requirements.

### 21. Split the central answer workflow into explicit capabilities

**Priority:** P2  
**Evidence:** Source finding and design recommendation

**Finding.** The reviewed `answer.py` exceeds 3,000 lines; topic handling and conversation state are also substantial. Routing rules, retries, calculations, document lookup, hazards, facilities, and satellite paths interact through a large central workflow. File size alone is not a defect, but it increases the difficulty of understanding cross-feature changes. [Sources: answer orchestration][S39], [topics][S40], [capability catalogue][S41].

**Suggested changes, in order:**

1. Define a common result contract covering evidence, checked claims, missing information, freshness, limitations, costs, and renderable outputs.
2. Extract budget, topic, hazard, facility, and place-history capabilities behind stable interfaces.
3. Keep orchestration responsible for routing and combining results; keep domain interpretation inside each capability.
4. Preserve existing regression behaviour while moving code, and add tests at the boundaries where capabilities interact.
5. Avoid a full rewrite while the pilot is changing rapidly. Refactor incrementally around the highest-risk paths first.

**Acceptance criteria:** A change to one capability can be tested without exercising unrelated integrations. Combined answers retain source, period, and uncertainty per component. The router does not depend on undocumented result shapes.

### 22. Measure the complete user wait, including cold paths

**Priority:** P2  
**Evidence:** Repository-reported timing results plus recommendation

**Finding.** The repository records useful latency improvements and a small concurrency comparison. Some paths still involve transcription, several model calls, acquisition, imagery, and multiple outgoing messages. A cached text answer and a first satellite request are very different experiences. [Sources: speed gate][S42], [place-history timings][S23], [speech timings][S15].

**Suggested changes, in order:**

1. Measure from received message to first useful content and to completion of text/audio/images separately.
2. Report median and tail latency for text, voice, indexed lookup, new-document acquisition, cached place history, and cold place history.
3. Test realistic concurrency and provider failures after durable processing is in place.
4. Put bounded parallelism and explicit time budgets around expensive operations.
5. Preserve progress messages and useful partial results without allowing them to imply that unfinished checks have passed.

**Acceptance criteria:** Published speed claims identify the path, cache state, sample size, and concurrency. Slow-path failures resolve to an understandable result. Other users' simple queries remain responsive while imagery or acquisition is running.

### 23. Demonstrate connected user journeys and measure usefulness

**Priority:** P2  
**Evidence:** Product recommendation; market demand was not established by this review

**Finding.** The wider feature set can be Kasafi's distinction when it answers connected local questions. It becomes harder to explain when demonstrated as a long menu of separate tools. Technical sophistication alone does not establish comprehension, repeat use, or a paying customer.

**Suggested changes, in order:**

1. Keep the broad vision and organise the product around a small number of repeatable journeys.
2. Test those journeys with citizens, civil servants, farmers, and development partners rather than assuming all groups need the same interface.
3. Ask users to explain the answer back in their own words, particularly allocation versus spending and observation versus forecast.
4. Measure completion without developer help, critical misunderstandings, repeat use, time saved, and useful-answer cost.
5. Identify the prospective buyer and funding model through actual pilot conversations. Any commercial expansion should resolve the provider/data-use questions already recorded in the repository.

| Journey | Connected capabilities | What the user should understand |
|---|---|---|
| Farmer investigating flooding | Location, historical water evidence, official outlook, relevant budget lines | What was observed, what is forecast, and what funding is documented are separate facts. |
| Citizen or civil servant examining a service budget | Hausa voice, allocation/spending comparison, citations, source crop, working | Money allocated and money recorded as spent are different measures. |
| Development partner assessing a locality | Multi-source statistics, LGA context, facilities, plans and budgets | Sources can disagree because dates, areas, populations, and definitions differ. |

**Acceptance criteria:** Pilot users can complete and correctly interpret these journeys without coaching. The demo communicates why the connected result is useful, while avoiding unsupported causal or completion claims.

### 24. Make the README, demo, and status claims match the product

**Priority:** P2  
**Evidence:** Source/documentation findings and recommendation

**Finding.** The README remains strongly budget-focused while the code now includes substantially more. Some architecture descriptions are ahead of the implementation, and project notes distinguish live, dry-run, and not-yet-deployed capabilities. Those distinctions should be visible to a reviewer without reading development notes. [Sources: README][S20], [architecture][S13], [project status notes][S43].

**Suggested changes, in order:**

1. Open with the coherent local-information proposition and two or three representative questions.
2. Publish a capability/status table: implemented, demonstrated, deployed, dry-run, experimental, or planned, with an update date.
3. Provide a clear working entry point and a concise demo built around connected journeys.
4. State the scope of verification and evaluation claims accurately; avoid turning “zero failures in this test set” into a general accuracy guarantee.
5. Keep TTS, deployment, privacy, data coverage, and known limitations synchronized across the README and public pages.
6. Include a brief limitation demonstration, such as missing evidence or a correction, to show how the product behaves when it cannot confidently answer.

**Acceptance criteria:** A new reviewer can identify the target user, try the intended entry point, understand the connected value, and distinguish available capabilities from planned or experimental work within a few minutes.

## 5. Suggested implementation sequence

The numbered findings are individually actionable. The sequence below groups dependencies so that the work does not become 24 unrelated tasks. It preserves the full product vision.

| Stage | Work | Findings | Exit condition |
|---|---|---|---|
| A — Protect answer and delivery correctness | Fix semantic verification, alert retry states, durable WhatsApp processing, plot identity, and location handling. | 01–05 | The three demonstrated defects are covered by regression tests and resolved; restart/delivery recovery works. |
| B — Protect operation and recovery | Add reliable cost controls, parsing containment, full-state backups, retention jobs, and meaningful readiness. | 15–19 | Resource and recovery failures are visible, bounded, and recoverable. |
| C — Establish independent trust | Audit source extraction, improve crop targeting, validate speech and environmental interpretations, and confirm critical facility/hazard data. | 06, 08–14 | Accuracy claims are supported by independent evidence and limitations are explicit. |
| D — Complete and simplify the experience | Add spoken summaries, modularise capability interfaces incrementally, and measure complete-turn performance. | 07, 21–22 | Connected text/voice journeys are understandable and behave predictably under load. |
| E — Make the product reviewable and repeatable | Finish setup/CI, align public documentation, and run the connected-journey pilot. | 20, 23–24 | A new user or reviewer can try, understand, and assess the product without the developer narrating missing steps. |

Some tasks can proceed independently, but fixes should not be hidden inside a broad rewrite. Prioritise a narrow change with a meaningful regression test, review its effect, and then move to the next item.

### How to turn each finding into a development task

For each numbered finding, record:

1. The exact problem and affected capability.
2. The evidence classification and source links from this report.
3. The smallest proposed change that resolves it.
4. The acceptance criteria and necessary regression tests.
5. Any migration, cache invalidation, documentation, or operator action required.
6. The implementation commit and the results of validation.

Mark a finding complete only when behaviour and documentation agree. A passing test for an isolated helper is insufficient when the user-facing path still bypasses it.

## 6. Release and pilot acceptance checklist

These are proposed release gates, not results already achieved.

### Reliability and data gates

- [ ] **01:** A number assigned to the wrong entity/year/measure cannot pass the verification gate merely because it appears on the cited page.
- [ ] **02:** Failed alert recipients remain retryable; successful recipients are protected against ordinary duplicate retries.
- [ ] **03:** Acknowledged WhatsApp work survives restart, and rapid turns from one user preserve conversational order.
- [ ] **04:** Plot caches distinguish the relevant geometry and method; the nearby-pin regression is fixed.
- [ ] **05:** Exact-location storage and external processing match the public explanation.
- [ ] **06:** Evidence images target the cited claim and preserve enough context to interpret the figure.
- [ ] **08–09:** Held-out speech and factual benchmarks are independently reviewed and versioned.
- [ ] **10–11:** Extraction coverage and financial interpretations remain explicit in affected answers.
- [ ] **12:** Experimental environmental results retain clear limits until independent validation supports stronger claims.
- [ ] **13–14:** Critical facility records and hazard inputs have visible verification/freshness states.

### Operational gates

- [ ] **15:** Concurrent expensive work has an accountable budget reservation and usage record.
- [ ] **16:** Parser containment tests establish the restrictions actually claimed.
- [ ] **17:** Scheduled retention runs without depending on a user's return.
- [ ] **18:** Readiness detects essential dependency failures; capability state and serving commit are visible to operators.
- [ ] **19:** A full isolated restore recovers PostgreSQL and SQLite state without unintended outbound messages.
- [ ] **20:** Clean setup and automated checks reproduce the documented sample workflow.

### Product gates

- [ ] **07:** Short Hausa audio answers are checked for meaning, pronunciation, and consistency with text.
- [ ] **21–22:** Capability boundaries and latency measurements cover complete user journeys, including slow and failed paths.
- [ ] **23:** Pilot users can obtain and explain useful answers without developer coaching.
- [ ] **24:** The README, demo, entry point, deployment status, and evaluation claims match the implementation.

### Pilot measurements to report

| Measure | What to record | Why it matters |
|---|---|---|
| Critical factual errors | Incorrect entity, year, amount, unit, spending interpretation, or unsupported conclusion | Measures the failures that undermine trust. |
| Citation/evidence correctness | Whether the cited page and crop support the actual statement | Distinguishes an attached citation from supporting evidence. |
| Voice critical-detail accuracy | Years, amounts, names, places, negation, and emergency meaning | Captures errors an overall transcription score can hide. |
| Confirmation burden | Read-backs, unnecessary read-backs, corrections, and abandonment | Shows whether the voice interface is usable. |
| Comprehension | Whether users can explain the answer and its limitations correctly | Establishes whether technically correct information is useful. |
| Delivery reliability | Accepted, delivered, failed, retried, expired, and duplicated messages | Tests the full communication workflow. |
| Complete-turn latency | First useful content and full completion, by path and cache state | Reflects the user's actual wait. |
| Data freshness | Age and coverage of each result's sources | Identifies current-looking answers built on old data. |
| Cost per useful completed answer | Models, messaging, searches, imagery, and an appropriate share of infrastructure | Supports an honest operating and pricing model. |
| Repeat usefulness | Return use and tasks completed without assistance | Helps establish product demand beyond a demonstration. |

Set acceptance thresholds before evaluating the held-out set. Report sample sizes and uncertainty; zero observed errors in a finite test does not establish zero real-world error.

## Appendix A: Reproducing the three demonstrated defects

The following is a local diagnostic harness for the reviewed commit. It does not send WhatsApp messages, call model APIs, query the production database, or alter application source. It uses synthetic evidence and mocked dependencies to exercise the relevant implementation paths.

Run from the repository after installing its dependencies. If your execution environment requires optional proxy support, prepare that environment separately. Results can change after the defects are fixed; that is expected.

```bash
uv run python - <<'PY'
import asyncio
import json
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

from shapely.geometry import Point, shape

from app.agent import answer as answer_module, consistency
from app.alerts.dispatch import dispatch
from app.alerts.triggers import Candidate
from app.config import Settings
from app.place import outline
from app.place.history import cell_id
from app.users import UserStore


async def check_alert_retry():
    settings = Settings(
        _env_file=None,
        kasafi_alerts_dry_run=False,
        kasafi_alerts_daily_cap=10,
        kasafi_alert_template_langs="ha",
    )
    store = UserStore(":memory:")
    store.subscribe("synthetic-user", ["NG034006"], ["heat"], "ha")
    candidate = Candidate(
        hazard="heat",
        lga_pcode="NG034006",
        key="synthetic-audit-alert",
        official=False,
        what={"ha": "test", "en": "test"},
        source={"ha": "test", "en": "test"},
    )
    attempts = []

    async def failed_send(*args):
        attempts.append(True)
        return False

    now = datetime(2026, 11, 1, 12, tzinfo=timezone.utc)
    first = await dispatch([candidate], store, settings, now, failed_send)
    second = await dispatch([candidate], store, settings, now, failed_send)
    row = store.alert_log()[0]
    return {
        "first_dispatch": dict(first),
        "second_dispatch": dict(second),
        "send_attempts": len(attempts),
        "recorded_status": row["status"],
        "delivered_count": row["recipients"],
    }


async def check_wrong_attribution():
    evidence = [answer_module.Evidence(
        1,
        "budget-2026-approved",
        "2026 Approved Budget",
        2026,
        10,
        "text",
        "Health allocation: 100,000,000.00. "
        "Education allocation: 200,000,000.00.",
    )]
    plan = answer_module.Plan(
        "How much was allocated to health in 2026?",
        ["health"],
        ["budget-2026-approved"],
    )
    incorrect_model_output = {
        "summary": "Health was allocated 200,000,000.00 in 2026 [1].",
        "cited": [1],
        "found": "full",
    }
    with (
        patch.object(answer_module, "compose",
                     AsyncMock(return_value=incorrect_model_output)),
        patch.object(answer_module.pool, "run",
                     AsyncMock(return_value=evidence)),
        patch.object(answer_module, "scope_notes", return_value=""),
        patch.object(answer_module, "off_topic_note", return_value=""),
    ):
        result = await answer_module._page_path(
            None, plan, plan.english_question, "en", None,
            Settings(_env_file=None), {},
            acq=None, latest=None, prev=None, context="",
            recheck_note="", cache={"evidence": evidence},
        )
    return {
        "correct_health_amount": "100,000,000.00",
        "found": result.found,
        "verified": result.verified,
        "response": result.text,
        "consistency_errors": len(consistency.check(
            plan, plan.english_question, result, years=[2026]
        )),
    }


async def check_outline_cache():
    first_lat, first_lon = 13.12801, 5.23501
    second_lat, second_lon = 13.12849, 5.23549
    cached_outline = outline.fallback(first_lon, first_lat, "no_chip")
    with patch.object(outline, "_load", return_value=cached_outline):
        result = await outline.plot_outline(
            object(), None, second_lat, second_lon
        )
    return {
        "first_cell": cell_id(first_lat, first_lon),
        "second_cell": cell_id(second_lat, second_lon),
        "same_geometry_returned": result.geometry == cached_outline.geometry,
        "new_pin_inside_returned_outline": shape(result.geometry).covers(
            Point(second_lon, second_lat)
        ),
    }


async def main():
    results = {
        "alert_retry": await check_alert_retry(),
        "wrong_attribution": await check_wrong_attribution(),
        "outline_cache": await check_outline_cache(),
    }
    print(json.dumps(results, indent=2, ensure_ascii=False))


asyncio.run(main())
PY
```

### Observed behaviour on the reviewed commit

| Diagnostic | Observed result | What this establishes |
|---|---|---|
| Failed alert | First dispatch reported `sent`; delivered count was `0`; second dispatch made no new attempt. | Failure is recorded as a completed event and suppresses retry. |
| Wrong attribution | Health was assigned the education amount, with `verified=True` and zero consistency errors. | The exercised page-answer checks do not establish entity/value attribution. |
| Outline cache | Both pins had key `13.128,5.235`; the old geometry was returned; the new pin was outside it. | The cache-return path does not validate the new pin against the cached outline. |

The attribution harness intentionally injects a wrong composition result. It tests the verifier, not how often a live model generates that result. The outline harness supplies a cached object to the real cache-return path; it does not measure satellite segmentation accuracy. These distinctions should be retained when converting the examples into regression tests.

## Appendix B: Source references

All repository links below are pinned to the reviewed commit so that later edits do not change the evidence underlying this report. Live deployment state can evolve independently.

| Reference | File | Evidence area |
|---|---|---|
| S01 | [Reviewed commit][S01] | Reviewed commit |
| S02 | [app/agent/answer.py][S02] | Numeric verification |
| S03 | [app/agent/answer.py][S03] | Page-answer pipeline |
| S04 | [app/agent/consistency.py][S04] | Entity and period consistency checks |
| S05 | [app/alerts/dispatch.py][S05] | Alert dispatch and delivery states |
| S06 | [app/whatsapp/webhook.py][S06] | Webhook acknowledgement and background processing |
| S07 | [app/place/outline.py][S07] | Outline persistence and cache lookup |
| S08 | [app/place/history.py][S08] | Point-history cache identity |
| S09 | [docs/site/privacy.md][S09] | Privacy promises and retention |
| S10 | [app/place/raster.py][S10] | Pin-centred fallback geometry |
| S11 | [app/evidence/crops.py][S11] | Scanned-table crop selection |
| S12 | [app/acquisition/parse_worker.py][S12] | Figure occurrence lookup |
| S13 | [docs/architecture.md][S13] | Architecture, planned voice output, and recovery notes |
| S14 | [app/whatsapp/client.py][S14] | Implemented outgoing message types |
| S15 | [evals/stt-hausa-2026-10-26.md][S15] | Hausa speech evaluation and limitations |
| S16 | [evals/generated/generate.py][S16] | Generated expected-answer provenance |
| S17 | [evals/generated/run.py][S17] | Generated-answer checks |
| S18 | [evals/place/run.py][S18] | Place-history evaluation modes |
| S19 | [app/retrieval/entities.py][S19] | Structured entities and reconciliation |
| S20 | [README.md][S20] | Product claims, known gaps, and setup |
| S21 | [app/agent/analysis.py][S21] | Inferred project-status calculations |
| S22 | [app/place/radar.py][S22] | Radar method and documented limitations |
| S23 | [docs/place-history.md][S23] | Place-history implementation and measurements |
| S24 | [app/geo/facilities.py][S24] | Facility search, routing, and capability limitations |
| S25 | [docs/hazard-and-services.md][S25] | Hazard/service design, data dates, and status |
| S26 | [app/hazards/read.py][S26] | Hazard data retrieval |
| S27 | [app/hazards/official.py][S27] | Official-source and advisory handling |
| S28 | [app/hazards/fetch.py][S28] | Hazard refresh scheduling |
| S29 | [app/whatsapp/conversation.py][S29] | Estimated conversation spending gate |
| S30 | [app/usage.py][S30] | Provider usage counters |
| S31 | [app/config.py][S31] | Configuration, defaults, and estimated prices |
| S32 | [app/acquisition/sandbox.py][S32] | Parser subprocess containment |
| S33 | [app/users.py][S33] | SQLite state and opportunistic expiry |
| S34 | [app/agent/trace.py][S34] | Trace storage and pruning |
| S35 | [app/main.py][S35] | Health endpoint |
| S36 | [deploy/docker-compose.yml][S36] | Deployment volumes and PostgreSQL backup service |
| S37 | [pyproject.toml][S37] | Dependencies and test configuration |
| S38 | [deploy/deploy.sh][S38] | Deployment checks |
| S39 | [app/agent/answer.py][S39] | Answer orchestration |
| S40 | [app/agent/topics.py][S40] | Multi-source topic workflow |
| S41 | [data/catalog.yaml][S41] | Capability catalogue |
| S42 | [evals/speed-gate-1031.md][S42] | Repository-reported latency and concurrency gate |
| S43 | [CLAUDE.md][S43] | Dated implementation and deployment status |

[S01]: https://github.com/bawanallahbilyaminu/kasafi-agent/commit/645456d034ec1e96e0d3ed2bc800ef198b3b3a0e "Reviewed commit"
[S02]: https://github.com/bawanallahbilyaminu/kasafi-agent/blob/645456d034ec1e96e0d3ed2bc800ef198b3b3a0e/app/agent/answer.py#L735 "Numeric verification"
[S03]: https://github.com/bawanallahbilyaminu/kasafi-agent/blob/645456d034ec1e96e0d3ed2bc800ef198b3b3a0e/app/agent/answer.py#L1507 "Page-answer pipeline"
[S04]: https://github.com/bawanallahbilyaminu/kasafi-agent/blob/645456d034ec1e96e0d3ed2bc800ef198b3b3a0e/app/agent/consistency.py#L76 "Entity and period consistency checks"
[S05]: https://github.com/bawanallahbilyaminu/kasafi-agent/blob/645456d034ec1e96e0d3ed2bc800ef198b3b3a0e/app/alerts/dispatch.py#L60 "Alert dispatch and delivery states"
[S06]: https://github.com/bawanallahbilyaminu/kasafi-agent/blob/645456d034ec1e96e0d3ed2bc800ef198b3b3a0e/app/whatsapp/webhook.py#L183 "Webhook acknowledgement and background processing"
[S07]: https://github.com/bawanallahbilyaminu/kasafi-agent/blob/645456d034ec1e96e0d3ed2bc800ef198b3b3a0e/app/place/outline.py#L222 "Outline persistence and cache lookup"
[S08]: https://github.com/bawanallahbilyaminu/kasafi-agent/blob/645456d034ec1e96e0d3ed2bc800ef198b3b3a0e/app/place/history.py#L497 "Point-history cache identity"
[S09]: https://github.com/bawanallahbilyaminu/kasafi-agent/blob/645456d034ec1e96e0d3ed2bc800ef198b3b3a0e/docs/site/privacy.md "Privacy promises and retention"
[S10]: https://github.com/bawanallahbilyaminu/kasafi-agent/blob/645456d034ec1e96e0d3ed2bc800ef198b3b3a0e/app/place/raster.py#L25 "Pin-centred fallback geometry"
[S11]: https://github.com/bawanallahbilyaminu/kasafi-agent/blob/645456d034ec1e96e0d3ed2bc800ef198b3b3a0e/app/evidence/crops.py#L165 "Scanned-table crop selection"
[S12]: https://github.com/bawanallahbilyaminu/kasafi-agent/blob/645456d034ec1e96e0d3ed2bc800ef198b3b3a0e/app/acquisition/parse_worker.py#L68 "Figure occurrence lookup"
[S13]: https://github.com/bawanallahbilyaminu/kasafi-agent/blob/645456d034ec1e96e0d3ed2bc800ef198b3b3a0e/docs/architecture.md "Architecture, planned voice output, and recovery notes"
[S14]: https://github.com/bawanallahbilyaminu/kasafi-agent/blob/645456d034ec1e96e0d3ed2bc800ef198b3b3a0e/app/whatsapp/client.py "Implemented outgoing message types"
[S15]: https://github.com/bawanallahbilyaminu/kasafi-agent/blob/645456d034ec1e96e0d3ed2bc800ef198b3b3a0e/evals/stt-hausa-2026-10-26.md "Hausa speech evaluation and limitations"
[S16]: https://github.com/bawanallahbilyaminu/kasafi-agent/blob/645456d034ec1e96e0d3ed2bc800ef198b3b3a0e/evals/generated/generate.py#L1 "Generated expected-answer provenance"
[S17]: https://github.com/bawanallahbilyaminu/kasafi-agent/blob/645456d034ec1e96e0d3ed2bc800ef198b3b3a0e/evals/generated/run.py#L63 "Generated-answer checks"
[S18]: https://github.com/bawanallahbilyaminu/kasafi-agent/blob/645456d034ec1e96e0d3ed2bc800ef198b3b3a0e/evals/place/run.py#L63 "Place-history evaluation modes"
[S19]: https://github.com/bawanallahbilyaminu/kasafi-agent/blob/645456d034ec1e96e0d3ed2bc800ef198b3b3a0e/app/retrieval/entities.py "Structured entities and reconciliation"
[S20]: https://github.com/bawanallahbilyaminu/kasafi-agent/blob/645456d034ec1e96e0d3ed2bc800ef198b3b3a0e/README.md "Product claims, known gaps, and setup"
[S21]: https://github.com/bawanallahbilyaminu/kasafi-agent/blob/645456d034ec1e96e0d3ed2bc800ef198b3b3a0e/app/agent/analysis.py#L169 "Inferred project-status calculations"
[S22]: https://github.com/bawanallahbilyaminu/kasafi-agent/blob/645456d034ec1e96e0d3ed2bc800ef198b3b3a0e/app/place/radar.py "Radar method and documented limitations"
[S23]: https://github.com/bawanallahbilyaminu/kasafi-agent/blob/645456d034ec1e96e0d3ed2bc800ef198b3b3a0e/docs/place-history.md "Place-history implementation and measurements"
[S24]: https://github.com/bawanallahbilyaminu/kasafi-agent/blob/645456d034ec1e96e0d3ed2bc800ef198b3b3a0e/app/geo/facilities.py "Facility search, routing, and capability limitations"
[S25]: https://github.com/bawanallahbilyaminu/kasafi-agent/blob/645456d034ec1e96e0d3ed2bc800ef198b3b3a0e/docs/hazard-and-services.md "Hazard/service design, data dates, and status"
[S26]: https://github.com/bawanallahbilyaminu/kasafi-agent/blob/645456d034ec1e96e0d3ed2bc800ef198b3b3a0e/app/hazards/read.py "Hazard data retrieval"
[S27]: https://github.com/bawanallahbilyaminu/kasafi-agent/blob/645456d034ec1e96e0d3ed2bc800ef198b3b3a0e/app/hazards/official.py "Official-source and advisory handling"
[S28]: https://github.com/bawanallahbilyaminu/kasafi-agent/blob/645456d034ec1e96e0d3ed2bc800ef198b3b3a0e/app/hazards/fetch.py "Hazard refresh scheduling"
[S29]: https://github.com/bawanallahbilyaminu/kasafi-agent/blob/645456d034ec1e96e0d3ed2bc800ef198b3b3a0e/app/whatsapp/conversation.py#L248 "Estimated conversation spending gate"
[S30]: https://github.com/bawanallahbilyaminu/kasafi-agent/blob/645456d034ec1e96e0d3ed2bc800ef198b3b3a0e/app/usage.py "Provider usage counters"
[S31]: https://github.com/bawanallahbilyaminu/kasafi-agent/blob/645456d034ec1e96e0d3ed2bc800ef198b3b3a0e/app/config.py "Configuration, defaults, and estimated prices"
[S32]: https://github.com/bawanallahbilyaminu/kasafi-agent/blob/645456d034ec1e96e0d3ed2bc800ef198b3b3a0e/app/acquisition/sandbox.py#L39 "Parser subprocess containment"
[S33]: https://github.com/bawanallahbilyaminu/kasafi-agent/blob/645456d034ec1e96e0d3ed2bc800ef198b3b3a0e/app/users.py "SQLite state and opportunistic expiry"
[S34]: https://github.com/bawanallahbilyaminu/kasafi-agent/blob/645456d034ec1e96e0d3ed2bc800ef198b3b3a0e/app/agent/trace.py#L130 "Trace storage and pruning"
[S35]: https://github.com/bawanallahbilyaminu/kasafi-agent/blob/645456d034ec1e96e0d3ed2bc800ef198b3b3a0e/app/main.py#L106 "Health endpoint"
[S36]: https://github.com/bawanallahbilyaminu/kasafi-agent/blob/645456d034ec1e96e0d3ed2bc800ef198b3b3a0e/deploy/docker-compose.yml "Deployment volumes and PostgreSQL backup service"
[S37]: https://github.com/bawanallahbilyaminu/kasafi-agent/blob/645456d034ec1e96e0d3ed2bc800ef198b3b3a0e/pyproject.toml "Dependencies and test configuration"
[S38]: https://github.com/bawanallahbilyaminu/kasafi-agent/blob/645456d034ec1e96e0d3ed2bc800ef198b3b3a0e/deploy/deploy.sh "Deployment checks"
[S39]: https://github.com/bawanallahbilyaminu/kasafi-agent/blob/645456d034ec1e96e0d3ed2bc800ef198b3b3a0e/app/agent/answer.py#L1006 "Answer orchestration"
[S40]: https://github.com/bawanallahbilyaminu/kasafi-agent/blob/645456d034ec1e96e0d3ed2bc800ef198b3b3a0e/app/agent/topics.py "Multi-source topic workflow"
[S41]: https://github.com/bawanallahbilyaminu/kasafi-agent/blob/645456d034ec1e96e0d3ed2bc800ef198b3b3a0e/data/catalog.yaml "Capability catalogue"
[S42]: https://github.com/bawanallahbilyaminu/kasafi-agent/blob/645456d034ec1e96e0d3ed2bc800ef198b3b3a0e/evals/speed-gate-1031.md "Repository-reported latency and concurrency gate"
[S43]: https://github.com/bawanallahbilyaminu/kasafi-agent/blob/645456d034ec1e96e0d3ed2bc800ef198b3b3a0e/CLAUDE.md "Dated implementation and deployment status"


## Response to the external review (Bilyaminu Bawan Allah / Kasafi, 1 Nov 2026)

Each finding: **done** (built, tested, deployed), **planned** (accepted, after the hackathon freeze) or **not
accepted** (with why). The work is in commit `0d1b31b` and the ones after it; regression tests are named.

| # | Finding | Status | What was done / why |
| --- | --- | --- | --- |
| 01 | Bind every financial claim to the correct evidence | **done** | `app/agent/attribution.py`: on the page path every cited figure is bound in code to the row or sentence holding it, and the entity written next to the figure, the year, the unit and the kind (allocation vs spending) are checked against that row. States replace the single flag: *attribution checked*, *figures checked* (figure found, binding not established, e.g. Hausa wording without a resolved name), *calculation checked* (rows and arithmetic in code: the structured paths, confirmed unchanged), *unsupported*. A contradiction is composed again with the mismatch named, then refused. The state is in show working and the admin trace. Appendix A's harness is `tests/test_attribution.py::test_appendix_a_wrong_attribution_is_refused_not_verified`; wrong-entity, wrong-year, wrong-unit, allocation-vs-spending and swapped-comparison cases are parametrised there. Structured records as the renderer's input (suggestion 1–2) stay planned. |
| 02 | Track alert delivery per recipient and retry failures | **done (minimum)**; outbox planned | Dispatch never records `sent` with nobody reached: `failed` (0 delivered, retried next round), `partial` (only the failed recipients retried, no duplicates), `no_recipient` (no numbers: nothing to retry). Dry-run records never consume a live send. Appendix A's harness is `tests/test_review_round.py::test_appendix_a_failed_send_is_never_recorded_as_sent_and_stays_retryable`. A per-recipient outbox with provider message IDs, delivery callbacks and backoff is on the roadmap. |
| 03 | Durable, ordered WhatsApp message processing | **planned** | Today: WhatsApp's redeliveries are deduplicated by message id, each reply runs as a background task, and a crash or timeout now ends in an apology with a trace row (1 Nov). A persisted inbox with ordering per sender is roadmap work. |
| 04 | Key plot outlines and histories by the actual analysis area | **done** | An outline kept for a cell is reused only when it contains the requested pin (Appendix A: `test_appendix_a_two_pins_in_one_cell_do_not_share_an_outline_that_excludes_the_second`). Plot results are keyed by a geometry hash plus a method version; the bare-pin results are the cell's (its centre circle), shared. `plot_outline_cache` is dropped (migration 0022). |
| 05 | Align location storage with the privacy promise | **done** | Plot geometry (outline, size circle, corner pins) lives in memory under the 30-minute rule and is never persisted; only 100 m cell statistics are cached, with no user link. Coordinates were removed from the place logs, exception logs print types only, traces carry fields only. `docs/site/privacy.md` now says what is cached and what is sent to Planetary Computer, SAM 3.1 and Open-Meteo. Test: `test_a_place_conversation_leaves_only_cell_statistics_without_coordinates_or_users` inspects the database and the logs. |
| 06 | Crop the cited evidence, including its meaning | **planned** | Crops stay as they are for the hackathon; the row-identity binding of finding 01 is the first step towards cropping the bound row. |
| 07 | Short Hausa audio replies | **planned** | No text-to-speech is claimed anywhere; Meta's API has none. A Hausa TTS trial is roadmap work. |
| 08 | Evaluate Hausa speech beyond the development recordings | **planned** | The pilot will collect consented recordings for a held-out set. |
| 09 | An independent factual benchmark | **planned** | The generated evals draw expected values from the extracted tables; an independent hand-checked set is planned with the pilot's partners. |
| 10 | Extraction quality and dataset versions as product features | **partly done** | `docs/extraction-lessons.md` records every document problem with a regression test on the real page; document hashes and fetch dates are stored. Versioned datasets with quality metrics on the admin page are planned. |
| 11 | Keep inferred project status distinct from physical progress | **partly done** | Status comes only from the budget's own previous-year columns and is labelled as such; a clearer wording line is planned. |
| 12 | Validate satellite interpretations independently | **partly done** | The Goronyo pin was cross-checked against an independent pixel-level implementation (place history §11); the radar threshold was set against known pixels and the Gudu sand artefact was found and fixed by probe (§14). Field validation with farmers is planned; every answer is labelled experimental. |
| 13 | Facility data freshness and capability verification | **planned** | Corrections are a reviewed file; verification dates per facility are planned. |
| 14 | Monitor hazard freshness and source coverage | **planned** | Fetch rounds are logged; an admin freshness page is planned. |
| 15 | An enforceable operating budget | **partly done** | Per-number daily limits, the global daily spend cap and the eval ledger exist; a cost dashboard is planned. |
| 16 | Strengthen containment for untrusted document parsing | **not accepted now** | The parse runs in a separate resource-limited subprocess (time and memory limits) and the README and docs now say exactly that instead of "sandbox". A real isolation sandbox is planned after the hackathon. |
| 17 | Enforce retention without depending on user activity | **planned** | Turns, traces and the alert log are pruned on write; a time-based job independent of activity is planned. |
| 18 | Separate liveness, readiness and feature availability | **planned** | `/health` and `/version` exist; readiness per dependency is planned. |
| 19 | Back up and restore the complete service state | **done (on-server)**; off-host planned | The SQLite store is copied daily with sqlite's online backup (`UserStore.backup_to`) and before every deploy, next to the PostgreSQL dump (`deploy/remote.sh`). Off-host encrypted copies and a restore rehearsal are planned. |
| 20 | Reproducible setup, continuous checks, deployment | **partly done** | The deploy gate runs the end-to-end conversation suite and the unit suite; CI is planned. |
| 21 | Split the central answer workflow into explicit capabilities | **not accepted before the freeze** | A refactor of the answer loop days before the deadline risks the gates; planned after. |
| 22 | Measure the complete user wait, including cold paths | **partly done** | Timings per stage are in every trace; the speed gates and the place speed eval measure first and cached requests. |
| 23 | Demonstrate connected user journeys and measure usefulness | **partly done** | The end-to-end suite scripts the journeys; the demo and pilot measurements are planned. |
| 24 | Make the README, demo and status claims match the product | **done (wording)**; table planned | "Resource-limited subprocess", place history labelled experimental in every answer and the README, no spoken-reply claim. A capability/status table is planned. |
