# Overnight eval loop: rules and status

Re-read this file at the start of every round. It is the whole contract for the night of 3-4 Nov 2026.

## Hard limits (enforced in code, `evals/overnight/common.py`)

1. **Baseten $20 for the whole night**, every model call priced from its token usage. Checked before every question
   (`guard()`); the run stops at the cap.
2. **Stop at 06:30** (laptop local time = Lagos). Checked before every question. At 06:30 the report is written and
   nothing else runs.
3. **No Meta calls, $0 Meta spend.** `META_API_KEY` in the loop's environment is the deliberately invalid key
   (`invalid-key-…`); `meta_guard()` refuses to start otherwise. Every place the app asks for a Muse Spark client is
   served by Muse Spark Open (Baseten, then Fireworks). Any attempt that would still reach Meta is recorded in
   `state.json` (`meta_attempts`) and refused before any network call. The morning report lists every attempt
   (expected: none).
4. **No deploys.** Nothing touches the server. Work is on the branch `overnight-evals`, from the deployed commit
   `a7836ff`; `main` is not changed.
5. **One job at a time on this laptop**, in chunks under 10 minutes (`--chunk-s 540`); each chunk resumes from the
   results file. No Modal (the evals need the local database).

## Questions

6. About 100 new questions a round, split 50/50 into **fix** and **held-out** by the id's hash, across the features:
   budget (LGA, sector, project, ministry), schools and health facilities per LGA, surveys, nearest facility by pin,
   place history, NEMA figures, deep analysis, emergencies and non-emergencies, conversation, Hausa, multi-turn
   follow-ups and corrections.
7. **Expected answers are computed by code** from the structured data (budget core, census rows parsed from the page
   text, facility registry, ward_history, NEMA dashboard rows confirmed on the page). Where only a document has the
   figure, the expected answer cites the document and code confirms the figure is on its pages; otherwise the
   question is dropped at generation time.
8. **A model only rephrases** (English and Hausa, formal and casual, typos, short and long); a paraphrase that loses
   a name or number is dropped. Three difficulties: direct, combine (totals, rankings), multi (follow-ups,
   corrections, a part published only at state level).
9. **Never edit or delete a question to make it pass.** A question found to be wrong (a bad expected answer, a
   generator bug) is marked `invalid` with the reason in the results and reported; it is never rewritten to fit.

## Fixes

10. Failures are grouped by cause, most common first. Fixes are **general changes only: never keywords, never
    question-specific rules**, never a change to a question.
11. A fix is **kept only if the held-out half improves or stays the same AND live-failures, routing and understanding
    don't get worse** (`evals/live_failures`, `evals/routing/run.py`, `tests/test_understanding.py` replay). Otherwise
    it is reverted.
12. **One commit per fix**, with the before/after scores in the message (held-out, live-failures, routing,
    understanding). Reverted fixes are recorded in `state.json` with their scores.
13. After **every round**: kept fixes committed, `state.json` updated (`last_round_done`), `docs/overnight-report.md`
    regenerated and committed, so a stop at any point leaves the report and fixes up to that round saved.

## End of the night

14. From about **05:15**: place, surveys, newdocs, prose and live-failures on the final branch commit, compared with
    the deployed commit (tonight's runs of the deployed code on the same sets where they exist).
15. At **06:30**: `docs/overnight-report.md` with scores per round (fix vs held-out), per feature and per difficulty;
    each fix kept or reverted; the final comparison table; the top remaining failures with 3 examples each; the exact
    spend; every Meta attempt. Then stop.

## Status

- 00:03 round 1 (95 questions: 47 fix, 48 held-out) started on the fix half at `41af978` (harness) = app code of
  `a7836ff`.
- 01:08 round 1 done: fix 38/47, held-out 41/48 before and 45/48 after the 10 fixes (one commit each, 6ad37a3..c57988f);
  live-failures 13/13, routing 88/88, understanding replay unchanged. Spend $7.64. Next: round 2.
- Spend and rounds: see `state.json`; the log: `progress.log`.
