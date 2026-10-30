"""Generate coverage questions from the data (docs/question-planning.md §6): templates per operation, filled with
random agencies, sub-agencies, LGAs and periods, and their expected answers computed from the budget core and the
DTM API pull. Nothing is hand-checked: the data is the answer key.

    uv run python evals/generated/generate.py [--n 6] [--seed 7]     -> evals/generated/cases.json

Families: lookup, split, spend_quarter, compare, share, rank_lga, lookup_lga, trend, false_premise, not_in_data.
Then evals/generated/paraphrase.py adds Hausa, informal, code-switched, typo and follow-up forms.
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import psycopg  # noqa: E402

from app.config import get_settings  # noqa: E402

OUT = Path(__file__).with_name("cases.json")
SPLITS = ("personnel", "overhead", "capital")


def money(x) -> str:
    return f"{Decimal(x):,.2f}"


def agencies(conn, *, sub: bool) -> list[tuple[str, str]]:
    """Agencies with an approved 2025 and 2026 line (sub-agencies: own rows, not the ministry with its agencies)."""
    like = "NOT LIKE '%%00000000'" if sub else "LIKE '%%00000000'"
    return conn.execute(f"""
        SELECT DISTINCT b.name, b.code FROM budget_items b
        WHERE b.doc_id = 'budget-2026-approved' AND b.spend_kind = 'total' AND b.code ~ '^[0-9]{{12}}$'
          AND b.code {like} AND b.approved_2026 > 0
          AND EXISTS (SELECT 1 FROM budget_items o WHERE o.doc_id = 'budget-2025-approved' AND o.code = b.code
                      AND o.spend_kind = 'total' AND o.approved_2025 > 0)
        ORDER BY 1""").fetchall()


def approved(conn, code: str, year: int, kind: str = "total"):
    r = conn.execute(f"SELECT approved_{year} FROM budget_items WHERE doc_id = %s AND code = %s AND spend_kind = %s "
                     f"AND approved_{year} IS NOT NULL ORDER BY seq LIMIT 1",
                     (f"budget-{year}-approved", code, kind)).fetchone()
    return r[0] if r else None


def perf(conn, code: str, year: int, quarter: int, kind: str = "total"):
    return conn.execute("SELECT revised, quarter_spent, ytd_spent FROM perf_items WHERE code = %s AND spend_kind = %s "
                        "AND year = %s AND quarter = %s ORDER BY seq LIMIT 1", (code, kind, year, quarter)).fetchone()


def dtm_pull() -> dict | None:
    p = ROOT / get_settings().kasafi_fetch_dir / "dtm-api-sokoto.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def generate(conn, n: int, rng: random.Random) -> list[dict]:
    cases: list[dict] = []
    mdas, subs = agencies(conn, sub=False), agencies(conn, sub=True)
    latest_q = conn.execute("SELECT max(quarter) FROM perf_items WHERE year = 2026").fetchone()[0]

    def add(family, text, **check):
        cases.append({"id": f"{family}-{sum(c['family'] == family for c in cases) + 1:02d}", "family": family,
                      "lang": "en", "text": text, **check})

    for name, code in rng.sample(mdas, min(n, len(mdas))):
        add("lookup", f"How much was approved for the {name} in the 2026 budget?",
            numbers=[money(approved(conn, code, 2026))], code=code)
    # a ministry's own unit is often printed with the ministry's name ('Ministry of Water Resources' 025200100100
    # and the ministry with its agencies 025200000000): the question reads either way, so either answer counts
    ministry = dict(mdas)

    def either(name: str, figures) -> dict:
        both = [figures(code) for code in (dict(subs)[name], ministry.get(name)) if code]
        return {"numbers_any": both} if len(both) > 1 else {"numbers": both[0]}

    split_subs = [(nm, c) for nm, c in subs if all(approved(conn, c, 2026, k) is not None for k in SPLITS)]
    for name, code in rng.sample(split_subs, min(n, len(split_subs))):
        add("split", f"What are the personnel, overhead and capital allocations of the {name} in 2026?",
            code=code, **either(name, lambda c: [money(approved(conn, c, 2026, k)) for k in SPLITS]
                                if all(approved(conn, c, 2026, k) is not None for k in SPLITS) else ["-"]))
    spend_subs = [(nm, c) for nm, c in subs if perf(conn, c, 2026, latest_q)]
    for name, code in rng.sample(spend_subs, min(n, len(spend_subs))):
        add("spend_quarter", f"How much had the {name} spent by the end of Q{latest_q} 2026, against its revised budget?",
            code=code, **either(name, lambda c: [money(r[2]), money(r[0])] if (r := perf(conn, c, 2026, latest_q))
                                else ["-"]))
    for name, code in rng.sample(mdas, min(n, len(mdas))):
        add("compare", f"Compare the {name}'s approved budget in 2025 and 2026.",
            numbers=[money(approved(conn, code, 2025)), money(approved(conn, code, 2026))], code=code)
    for name, code in rng.sample(split_subs, min(n, len(split_subs))):
        cap, tot = approved(conn, code, 2026, "capital"), approved(conn, code, 2026)
        if tot:
            pct = (Decimal(cap) / Decimal(tot) * 100).quantize(Decimal("0.1"), ROUND_HALF_UP)
            add("share", f"What share of the {name}'s 2026 approved budget is capital?",
                numbers_any=[[f"{pct}%"], [f"{pct} %"], [money(cap), money(tot)]], code=code)
    for name, code in rng.sample(mdas, min(n, len(mdas))):        # the premise is the wrong way round
        a25, a26 = approved(conn, code, 2025), approved(conn, code, 2026)
        wrong = "fell" if a26 > a25 else "rose"
        add("false_premise", f"Why did the {name}'s approved budget {'fall' if wrong == 'fell' else 'rise'} from "
            f"2025 to 2026?", numbers=[money(a25), money(a26)], premise_false=True, code=code)
    for name, code in rng.sample(subs, min(n, len(subs))):         # a quarter not published yet
        add("not_in_data", f"How much did the {name} spend in Q4 2026?", expect_gap=f"Q{latest_q} 2026",
            numbers=[], code=code)
    pull = dtm_pull()
    if pull:
        lgas = sorted(pull["lgas"], key=lambda x: -x["idps"])
        top = rng.choice([3, 5])
        add("rank_lga", f"Which {top} LGAs in Sokoto have the most IDPs?",
            numbers=[f"{x['idps']:,}" for x in lgas[:top]], names=[x["place"] for x in lgas[:top]])
        for x in rng.sample(lgas, min(n, len(lgas))):
            add("lookup_lga", f"How many IDPs are there in {x['place']} LGA?", numbers=[f"{x['idps']:,}"])
        r = pull["rounds"]
        add("trend", "How has the number of IDPs in Sokoto State changed over the last DTM rounds?",
            numbers=[f"{r[0]['idps']:,}", f"{r[1]['idps']:,}"])
    return cases


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--n", type=int, default=6)
    p.add_argument("--seed", type=int, default=7)
    a = p.parse_args()
    with psycopg.connect(get_settings().db_url()) as conn:
        cases = generate(conn, a.n, random.Random(a.seed))
    if OUT.exists():                  # an unchanged question keeps its paraphrases (paraphrase.py costs a call each)
        old = {(c["id"], c["text"]): c.get("forms") for c in json.loads(OUT.read_text(encoding="utf-8"))["cases"]}
        for c in cases:
            if old.get((c["id"], c["text"])):
                c["forms"] = old[(c["id"], c["text"])]
    OUT.write_text(json.dumps({"_about": __doc__.splitlines()[0], "seed": a.seed, "cases": cases}, indent=1,
                              ensure_ascii=False), encoding="utf-8")
    from collections import Counter
    print(len(cases), "cases:", dict(Counter(c["family"] for c in cases)), "->", OUT)


if __name__ == "__main__":
    main()
