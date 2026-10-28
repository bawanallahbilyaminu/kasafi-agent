# Complex-question eval

Questions that need more than one row: comparisons across years, rankings, shares, totals over several
ministries. They run through the `query_budget` path (`app/agent/budget_query.py`).

```bash
uv run python evals/run_answer_eval.py --suite complex --runs 3
```

## Adding a question

1. Add it to `questions.json`: `id` (c04, c05, ...), `lang` (`ha` or `en`), `text`, and an `expected`
   sentence saying what a good answer contains.
2. Add the checked answer to `answers.json` with the same `id`:
   - `numbers`: figures that must appear, exactly as printed in the document (`20,666,975,000.00`) or as
     Kasafi computes them (differences and totals: two decimals, e.g. `12,842,635,249.11`; percentages one
     decimal, e.g. `164.1`).
   - `numbers_any`: alternatives, when either is right (e.g. approved or revised).
   - `docs` and `pages`: where the figures are; at least one citation must come from them.
   - `working: true`: the answer must show the rows used and the arithmetic.
   - `partial: true/false`: whether the answer should say that something wasn't found.
   - `source`: the table, row, column and page you checked, so anyone can re-check it.

A quick way to find the row and page for a figure (dev database):

```sql
SELECT doc_id, page, table_title, code, name, column_label, amount_naira
FROM budget_rows WHERE name ILIKE '%tertiary%' AND year = 2026 AND measure = 'approved';
```
