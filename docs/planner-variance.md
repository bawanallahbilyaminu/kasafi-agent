# Planner variance: root cause (1 Nov 2026)

The same question, planned twice, can get two different plans; downstream code then reads a different document,
measure or split and the answer flips. This note collects every such flip in the eval logs since 30 Oct, reruns
five of the questions five times each to see which plan fields move, and proposes fixes ranked by the cases they
remove. No code was changed for this note.

## 1. The cases

"Variance" means the same question (same wording, same code) right in one run and wrong in another. The reports
record the answer, not the plan, so the plan differences below come from the reruns in §2 and from what the wrong
answer read. Development iterations of 30 Oct (the complex set's `plan1`–`plan12`, where the prompt changed
between runs) are left out.

| Case | Set, runs | What flipped between runs | Do the words settle it? |
| --- | --- | --- | --- |
| t02 "A cewar NBS, menene MPI na jihar Sokoto, kuma a cewar SBS nawa ne ya inganta?" | topics, Hausa; wrong 2 of 7 runs (31 Oct 10:45 search path, 120 s timeout; 31 Oct 18:18 partial: SBS's figure not taken), right in the other 5 | **topic** set (`poverty_welfare`) in 2 of 5 plans, empty in 3: topic path vs document search; **operation** compare 3 of 5, lookup 2 of 5; **time** a 2022–2025 range in 1 of 5, none in 4; the SBS **entity** missing in 1 of 5 | Yes: two publishers named ("a cewar NBS … a cewar SBS"), a change asked ("ya inganta"), the measure named (MPI) → compare, both publishers required, poverty topic |
| t04 "According to SBS, what was Sokoto's multidimensional poverty incidence in 2022?" | topics; wrong 1 of 7 (31 Oct 18:08: "Sokoto State Bureau of Statistics: 91%" shown as SBS's own, from p. 36 "2022 baseline headcount") | the **reader's** publisher field on one fact card, not the plan: the same page gave "NBS, as cited in SBS" in the other runs | Yes: "according to SBS" + 2022 → NBS's figure as cited (the rule exists; it was applied to one card and not the other) |
| p2_period-04 "How much did the Ministry of Lands and Housing spend from January to September 2025?" | patterns; wrong 1 of 6 (31 Oct 18:26: Q1–Q4 ₦51.92 bn from the Q4 report), right in 5 | **doc_ids**: `bir-2025-q3` + `budget-2025-approved` in 4 of 5 plans, `bir-2025-q3` + `bir-2025-q4` in 1 of 5; with the Q4 report in the plan the structured reader took the newest report | Yes: January–September is Q1–Q3 → the Q3 report only |
| p3_project-01 "How much is budgeted for Procurment of 5n0 peugout 406 saloon for members and secretary in 2026?" | patterns; wrong 1 of 6 (31 Oct 18:53: the statewide economic code 23010105 "purchase of motor vehicles" ₦25.98 bn), right in 5 | the **entity text** ("5 No" / "500" / "5no Peugeot 406 …") and the **line_search terms** differ every run; **key_terms** dropped the line's name in 1 of 5 ("Capital Expenditure, House of Assembly, Vehicles") → the aggregate (category) path answered instead of the line | Yes: a quoted line name → that line, never an economic-code aggregate |
| p4_narrative-02 "What does the BIR Q3 2025 say about Revenue Performance, and what reasons does it give?" | patterns; wrong 3 of 6 (no narrative page cited; the ₦526.88 bn total missing), right in 3 | **search_queries** and so the pages read: the narrative page (p. 4) is found by some query sets and not others | Yes: "what reasons does it give" → the report's narrative section, by page title |
| spend_quarter-04 "How much had teh State Enviromental Protection Agency spent by the end of Q3 2025, agianst its revised budget?" (typo form) | fresh 50, 1 Nov 08:58: spent ₦516.54 m and 76 % given, the revised ₦679.77 m missing | **splits**: `["total"]` in 4 of 5 plans, `[]` in 1 of 5; **measures** always include `revised` (order varies); **key_terms** "Revised Budget, Actual Expenditure" in 3 of 5, "Recurrent/Capital/Total Expenditure" in 2 of 5 | Yes: "spent … against its revised budget" → actual_ytd + revised on the total |
| split-06 follow-up "What are its personnel, overhead and capital allocations in 2025?" (after a question about the Fertilizer and Agricultural Supplies Company) | fresh 50, 1 Nov 08:47: only personnel ₦39.78 m answered | the **standalone rewrite** of a follow-up: the standalone form planned 5 of 5 times with all three splits and the same measures | Yes: three splits named |
| false_premise-04 (Hausa) | fresh 50, 1 Nov 08:47: TypeError | a crash in the redo (unhashable Hit), fixed the same day | — |

Seven variance cases in all (t02, t04, p2_period-04, p3_project-01, p4_narrative-02, spend_quarter-04,
split-06). In every one the question's words settle the field that moved.

## 2. Five questions planned five times each

`plan_question` only (the planner call, Meta Muse Spark with the Open second reading as in production), 1 Nov
09:55–10:00, 2.1–4.7 s a plan. Only the fields that differed across the five runs are shown.

**p2_period-04** — doc_ids: runs 1, 2, 3, 5 `[bir-2025-q3, budget-2025-approved]`; run 4 `[bir-2025-q3, bir-2025-q4]`. key_terms: five different sets (Actual / Total / Recurrent / Capital Expenditure in varying combinations). topic: "" ×4, `fiscal_governance` ×1.

**p3_project-01** — entity: "Procurement of 5 No Peugeot 406 …" / "… 500 Peugeot …" / "… 5no Peugeot …" ×3. key_terms: run 1 `[Capital Expenditure, House of Assembly, Vehicles]` (no line name); runs 2–5 carry a version of the line name. line_search terms: five different lists (8–10 terms each). topics: [] ×2, `fiscal_governance` ×3.

**spend_quarter-04** — measures: `[revised, actual_ytd, performance_pct]` ×3, `[actual_ytd, revised, performance_pct]` ×2. splits: `[total]` ×4, `[]` ×1. key_terms: `[… Revised Budget, Actual Expenditure]` ×3, `[… Recurrent, Capital(, Total) Expenditure]` ×2.

**split-06 (standalone)** — stable: measures, splits and entity identical in all five; only key_terms wording ("Personnel Expenditure" vs "Personnel") and search queries differ.

**t02** — doc_ids: three docs ×4, two docs ×1 (mpi-2026-sokoto dropped). entities: `[Sokoto State]` ×1; `[Sokoto State, NBS, SBS]` ×4 (SBS resolved to "State Bureau of Statistics" in 1). operation: compare ×3, lookup ×2. time: range 2022–2025 ×1, none ×4. topics: `poverty_welfare` ×2, [] ×3.

Deterministic settings were tried on the same prompt (three calls each): both APIs accept `temperature: 0` and
`seed`, and the replies still differ (Muse Spark and Muse Spark Open reason before answering; at low
`max_tokens` Muse Spark's visible JSON is even cut off). They give no determinism.

## 3. Fixes, ranked by the cases they remove

1. **Decide the structured fields in code from the words, before the planner, and enforce them after it** (5 of
   7 cases: p2_period-04, spend_quarter-04, split-06, p3_project-01, t02).
   - *Period → document*: "January–September", "by the end of Q3", "first half", "year to date", "full year",
     "Q1–Q2", Hausa "har zuwa ƙarshen Q3", "watanni tara na farko" → the quarter; the plan's `doc_ids` are then
     filtered to that quarter's report (the Q4 report can't enter a January–September question).
   - *Measure words → measures*: "spent / kashe / actual" → `actual_ytd`; "against / compared with / idan aka
     kwatanta da … revised" → `revised`; "approved / budgeted / aka ware" → `approved`; "performance / share /
     kashi" → `performance_pct`. The word-derived set is unioned into the plan's `measures`.
   - *Split words → splits*: personnel / overhead / capital / albashi / gudanarwa / jari named → those splits;
     none named → `total`. (Follow-ups: the rewrite can't drop a split the user's own words name.)
   - *Publishers and change words → operation*: two "according to X" / "a cewar X" clauses, or "improved /
     changed / ya inganta / ya ragu" → `compare`, both publishers required, the topic from a keyword map (MPI →
     poverty_welfare) so the topic path is taken every time.
   - *A named line beats an aggregate*: when the question carries a long line name (5+ words, or a quoted name),
     `line_search.terms` must contain the whole name and the category/aggregate path is off for that question.
   Cost: regexes, under a millisecond; both model readings untouched; the planner still runs for everything else.
2. **Narrative questions read the narrative pages deterministically** (1 case: p4_narrative-02): "what does the
   report say about X / what reasons does it give" → the named report's pages whose heading matches X (page-title
   index already exists for the structured core) join the evidence regardless of the search queries.
3. **Attribution check in code on fact cards** (1 case: t04): a card from a state report whose figure equals
   NBS's national-report figure for the same measure and year, or whose page text says "according to NBS / as
   reported by", is labelled "NBS, as cited in SBS", never SBS's own. The reader's publisher field is advisory.
4. **Constrain the planner's `measures`/`splits` fields with definitions in the prompt** (overlaps 1; on its own
   it reduces but doesn't remove the flips: the reruns show the enum already holds and the variance is in
   *which* valid values are chosen).
5. **A second-opinion plan only when the word-derived fields disagree with the plan** (the residual after 1): one
   extra planner call from the second model, only on disagreement (rare), so the median stays within 1 s.
6. **Deterministic sampling** (0 cases): tested above; not worth a setting.

Proposed order: 1, then 2 and 3, with 5 as the safety net; 4 as a one-line prompt change alongside 1. Expected
result: the 7 recorded flips removed, no path changed for questions whose words name nothing (the plan stands as
today), and no new model calls on the common path.
