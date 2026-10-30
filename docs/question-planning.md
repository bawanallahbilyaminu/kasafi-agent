# Question planning: answering questions we haven't seen

Status: design for kasafi-agent, 30 Oct 2026. Put in `docs/question-planning.md`.

## The problem

Kasafi still fails in ways that get fixed one question at a time. Three phone tests from 30 Oct show the pattern:

| Question | What happened | Real cause |
| --- | --- | --- |
| "which LGA have the most IDPs living there?" (follow-up) | "I couldn't find the answer" | The follow-up wasn't rewritten into a full question, and the DTM API (which has all 22 LGAs) is only called inside the topic sweep, not as a tool the planner can choose |
| "list of LGAs and number of IDPs" | Answered from the July 2025 DTM PDF; said no LGA breakdown exists | Same: page search won, the LGA-level source was never considered |
| h2-01: State Bureau of Statistics personnel/overhead/capital and Q2 spending | Gave the ₦1.02 bn total; said the split and spending weren't shown | The BIR Q2 2026 tables 4–7 print all of it; the planner didn't know the sub-agency rows existed at that level |
| "reports from the Institutionalizing Social Protection… programme" | Not found | The report is on mptf.undp.org, a domain no list contained |

None of these needs a question-specific fix. Each is the same gap: **the planner reasons about words and documents, not about what data is needed and which source can supply it.**

## The approach

Five parts, each general:

1. **Rewrite the question** so it stands alone.
2. **Describe the information need** as structured fields, not keywords.
3. **Match the need to capabilities**: what each source or tool can answer, at what level and time.
4. **Run a plan → act → check loop** until every required value is found or the budget runs out.
5. **Test by coverage**: generate many questions from the capabilities, with answers computed automatically.

### 1. Standalone rewrite

Before planning, turn every message into a question that makes sense on its own, using the last ~5 turns:

- "which LGA have the most IDPs living there?" → "Which LGAs in Sokoto State have the most IDPs (latest figures)?"
- "what about 2024?" → the previous question with the year replaced.

Keep the original text for the trace. Ask a short question only when two readings are both reasonable.

### 2. Information need (planner output, validated JSON)

```json
{
  "standalone_question": "Which LGAs in Sokoto have the most IDPs?",
  "measures": ["idp_count"],
  "entities": [{"type": "state", "name": "Sokoto"}],
  "geo_level": "lga",
  "time": {"kind": "latest"},
  "operation": "rank",            // lookup | breakdown | compare | rank | share | trend | list | explain | verify_claim
  "output_shape": "table_top_n",  // value | table | table_top_n | text
  "top_n": 5,
  "premises": [],                 // claims in the question to check (false-premise handling)
  "topics": ["displacement_humanitarian"]
}
```

The model fills these fields. Code checks them (known measure names, entity resolution against the MDA, LGA and programme lists, a valid time).

### 3. Capability catalog

Every source and tool declares what it can answer. This is data, like the source registry, not code.

```yaml
- id: dtm_api
  measures: [idp_count, returnee_count]
  geo_levels: [state, lga]
  time: rounds (reportingDate); newest round per pull
  breakdowns: [displacement_reason, sex]
- id: budget_core            # SQL on budget_items / projects / perf_items
  measures: [approved, revised, actual_ytd, performance_pct, revenue_budget, revenue_actual]
  entity_types: [mda, sub_agency, project, economic_code, function_code, lga_location, revenue_line]
  splits: [personnel, overhead, capital, debt]
  time: 2024-2026 budgets; quarterly implementation reports
- id: topic_sweep            # source registry publishers
  measures: by topic (registry)
  geo_levels: per publisher `level`
- id: page_search            # last resort for text
  measures: any (unstructured)
```

Matching is done in code: for each measure × entity × level × time cell the question needs, list the capabilities that can fill it, best first (structured before text, finer level before coarser, newer before older).

If nothing can fill a cell at the requested level, the answer says so and offers the nearest: "IDP figures exist by LGA from IOM; the SBS/JIPS survey covers Sokoto town only." That is a **coverage gap**, not "not found".

### 4. Plan → act → check loop

```
need = describe(question)
cells = required_cells(need)                # e.g. 22 LGAs × idp_count × latest
plan = match(cells, catalog)
for step in 1..6 (time budget ~60 s, longer for topic sweeps):
    run the next action(s) in the plan (in parallel where independent)
    record each value with its source, edition, date, page or API field
    missing = cells without a verified value
    if not missing: break
    plan = replan(missing)                  # other capability, wider search, open-web fallback
compute(need.operation, cells)              # rank, share, compare, trend in code
write(answer, cells, gaps)                  # plain sentences around the computed table
```

Rules:

- **Sufficiency is checked in code**, cell by cell, never by asking the model "is this enough?".
- **Every number** keeps the existing check against its page, row or API field.
- **Partial answers name the missing cells**, e.g. "I found 2025 and 2026 but not 2024."
- **False premises** are checked like any other cell, and the answer corrects them.

### 5. Open-web fallback with trust rules

The registry will never list every publisher. When registry channels and allowlisted search fail:

1. Search the open web without site filters.
2. **Auto-accept** a document only from trusted patterns: `*.gov.ng`, `*.int`, UN system domains (undp.org, mptf.undp.org, jointsdgfund.org, unicef.org, wfp.org, ilo.org, who.int …), worldbank.org, and the websites in partner hints.
3. Anything else: don't fetch. Queue the domain in the admin review page with the question that needed it, and tell the user the document was found on a site Kasafi hasn't approved yet.
4. Approved domains are added to the registry, so the list grows from real use.

Robots.txt, size limits, sandboxed parsing and the global exclusions still apply.

### 6. Coverage testing (instead of guessing user questions)

You can't predict every question, but you can test every **kind** of question the data supports.

- **Generate question families** from the capability catalog: for a random sample of MDAs, sub-agencies, projects, LGAs, years and quarters, fill templates for each operation (lookup, split, compare, rank, share, trend, false premise, not-in-data).
- **Paraphrase** each with the model: Hausa, English, code-switched, informal, typos, follow-up form.
- **Compute the expected answer** from the structured core or API directly, so no hand-checking is needed for these.
- **Run a sample nightly** (~100 questions) and report the wrong rate **per family** (e.g. "sub-agency splits: 4/10 wrong"). A failing family points at a capability gap, which gets one general fix.
- **Add real questions** from traces and the review queue as testers arrive (anonymised, same retention rules).
- The **hand-written held-out set** (h2) stays the final, unseen check.

## What changes in the code

- `planner`: rewrite → information need (schema above) → capability match. Drop keyword-routed branches as the catalog covers them.
- `catalog.yaml`: new, next to `source_registry.yaml`.
- Tools exposed to the planner, not hidden inside the sweep: `dtm_api`, `budget_core` queries, `topic_sweep`, `page_search`, `open_web_search`.
- `loop`: cell bookkeeping, replanning, time budget, partial-answer wording.
- `evals/generated/`: generators, paraphraser, nightly runner, per-family report.
- Admin: "domains awaiting approval" list.

## Order of work (time-boxed)

1. Standalone rewrite + information-need schema + catalog with `dtm_api` and `budget_core` (half a day).
2. Cell loop and coverage-gap wording (half a day).
3. Generated evals for budget and DTM families; run and report per family (half a day).
4. Open-web fallback with trust rules and the admin queue (a few hours).

Stop adding features after this; Monday is for testers.
