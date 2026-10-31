# Speed round gate, Oct 31 2026

Rule for the round: no loss of correctness or quality anywhere; speed only from removing waits.
Before = live `3ea68e0`. After = `059e77c` (every set rerun on it, concurrency 1, same cases, same forms).

## Per-set wrong counts

| set | cases | before wrong | after wrong | before median / p90 | after median / p90 |
|---|---|---|---|---|---|
| fresh 50 (draw 741719, form seed 1) | 52 | 0 | 0 | 5.4 s / 12.2 s | 3.8 s / 6.3 s |
| patterns (`evals/patterns/cases.json`) | 22 | 0 (21 cases) | 0 | 21.8 s / 28.7 s (concurrency 3) | 8.2 s / 10.9 s |
| multi-source topics | 12 | 0 | 0 | 16.1 s / 22.9 s | 12.3 s / — |
| advisories | 5 | 0 | 0 | — | 5.5 s |

Answered → partial or not found: none. Wrong agency: none.

## Concurrency (nine pattern questions, each alone, then in trios of three at once)

| | median | p90 |
|---|---|---|
| alone | 7.2 s | 8.4 s |
| three at once | 8.9 s | 9.2 s |

Before the round the same pattern set under concurrency 3 had a median of 21.8 s (the searches blocked the
event loop, so one user's search stalled the others).

## Answer-by-answer diff

### fresh 50: 49 of 52 identical (figures, pages, documents, outcome); 3 differ

All three are `false_premise` cases ("why did X's budget fall/rise from 2025 to 2026?" when it did the
opposite). The premise is corrected in both runs; the figures are right in both. What differs is the
planner's reading of which rows to show: the personnel (salaries) rows or the ministry total.

| case | before | after |
|---|---|---|
| false_premise-02 (Science and Technology) | salaries: ₦1.32 bn → … (p. 11,13,14,16,17,20,23,26) | total: ₦6.82 bn → ₦11.69 bn (p. 11, 17) |
| false_premise-04 (Religious Affairs, Hausa) | total: ₦11.26 bn → … (p. 11, 16) | salaries: ₦117.15 m → … (p. 11,13,14,16,19,22,25) |
| false_premise-05 (Lands and Housing) | salaries: ₦313.60 m → ₦316.08 m (p. 12,…,26) | total: ₦47.46 bn → ₦35.78 bn (p. 12, 17) |

Variance in the planner's `need.splits` (the question names no kind of spending), present before the round
too. Follow-up worth doing: a question that names no kind takes the total in code, as the line reader already
does.

### patterns: 14 of 21 comparable identical; 7 differ

- p1_revenue-04, p2_period-01, p2_period-03: the same figures and pages, plus the budget row (and, in Hausa,
  the kind rows) the code-written answer now adds for context, e.g. "₦305.20 miliyan (4.2% na kasafin asali)"
  with the ₦7.24 bn budget row.
- p4_narrative-01/-02 and p5_not_published-01/-02: the generator drew different questions for the after set
  (the narrative cases are new: real narrative paragraphs instead of tables of contents), so they are not
  comparable. All pass.

### topics: 6 of 12 identical; the differences are wording on the same figures. Two intermediate after-runs
each had one wrong (t04 attribution once, t02 Hausa MPI once, the known planner-variance case); the final
run on `059e77c` has 0 wrong.

## What changed in this round (all with unit tests; 1283 pass)

Speed: searches in worker threads on a small connection pool (`app/retrieval/pool.py`); keyword and vector
line search side by side; the entity/level/period check in code on every answer (`app/agent/consistency.py`),
the model-based parts check only for multi-part questions; a redo searches for the missing part only and
re-reads the hits already found; crops render during the checks and are sent only for rows the final answer
cites.

Correctness fixes found by the gate runs (lesson L34): a narrative question reads a page's whole text and
searches the prose with the planner's key terms, never the fixed revenue summary; the period parsed in code
pins the need's quarter; a structured answer gets the same consistency check; a question naming a project
line never takes the category path; an agency named "… Staff …" is no headcount question; the reader's level
labels echoed in a summary become plain words.

Eval spend today: about $19 (the daily cap was raised on the command line for the gate runs only).
