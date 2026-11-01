# Place history: pre-deploy gate (1 Nov 2026)

Run before the first deploy of place history (steps 1–3 and the fixes in docs/place-history.md §14), on the dev
database, after the Sentinel-1 rerun. Model spend for the whole gate about $2.6 (under the $5 daily cap).

| Set | Cases | Wrong | Notes |
| --- | --- | --- | --- |
| Place planner, in code (`evals/place/run.py`) | 89 | 0 | expected values from `ward_history`; median 0.0 s |
| Place planner, full pipeline (`--full`, `report-full.md`) | 89 | 0 | planner model routes; median 4.0 s. A first run had 2 Hausa cases turned into a planner clarify ("which LGA?"); fixed: a place question is never pre-empted by a clarify |
| Scope guardrails (`evals/guardrails/`) | 104 | 0 | 21 new place cases (land ownership, boundaries, certificates, grazing routes, abandonment must refuse; greenness, floods, bare soil, a pond, ward comparisons must answer). First run: 3 misses, because the budget-word filter read the bot's own name as "kasafi" (budget); fixed |
| Privacy (`tests/test_place_shape.py`, `tests/test_location.py`) | unit | 0 | no coordinate, shape or corner pin in the user store, logs or memory repr; caches keyed by cell and year only |
| Speed (`evals/place/speed.py`, `speed-report.md`) | 2 pins | pass | first request 45–50 s with the progress line; cached 4–7 s (rule: under 10 s) |
| Fresh 50 (`evals/generated/run.py --fresh`) | 52 | 1 | first run 10 wrong: 9 IDP/displacement rankings were routed to ward greenness (the area route now needs a satellite-measure word) and one redo crashed on an unhashable Hit; rerun 1 wrong (a typo form of a spend-vs-revised question gives the share, 76 %, not the revised figure: planner variance, not place) |
| Patterns (`evals/patterns/run.py`) | 22 | 0 | |
| Topics (`evals/complex/run_open.py --file evals/topics/multi_source.json`) | 12 | 0 | 3 partial, as before |
| Advisories (`… --file evals/topics/advisories.json`) | 5 | 0 | |

Unit tests: 1,401 passed (the live IOM DTM test deselected: the API returned 504).
