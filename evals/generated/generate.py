"""Generate coverage questions from the data (docs/question-planning.md §6): templates per operation, filled with
random agencies, sub-agencies, LGAs and periods, and their expected answers computed from the budget core and the
DTM API pull. Nothing is hand-checked: the data is the answer key.

    uv run python evals/generated/generate.py [--n 6] [--seed 7] [--out ...]   -> evals/generated/cases.json
    (no --seed: a new random draw; evals/generated/run.py --fresh draws, paraphrases and runs in one go)

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

from app.agent.need import same_entity  # noqa: E402
from app.config import get_settings  # noqa: E402

OUT = Path(__file__).with_name("cases.json")
SPLITS = ("personnel", "overhead", "capital")
BUDGET_YEARS = (2024, 2025, 2026)          # the approved budgets in the library (app/agent/tools.APPROVED_YEARS)


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
    periods = [tuple(r) for r in conn.execute("SELECT DISTINCT year, quarter FROM perf_items ORDER BY 1, 2")]

    def add(family, text, **check):
        cases.append({"id": f"{family}-{sum(c['family'] == family for c in cases) + 1:02d}", "family": family,
                      "lang": "en", "text": text, **check})

    # a ministry's own unit is often printed with the ministry's name ('Ministry of Water Resources' 025200100100
    # and the ministry with its agencies 025200000000; 'Min of Lands and Housing' / 'Ministry of Lands and
    # Housing'): the question reads either way, so either answer counts
    by_code = {c: nm for nm, c in mdas + subs}

    def twin(code: str) -> str:
        """The ministry for its own unit, or the unit for its ministry, when the two print one name; else ''."""
        if code.endswith("00000000"):
            other = sorted(c for c in by_code if c[:4] == code[:4] and c != code
                           and same_entity(by_code[c], by_code[code]))
        else:
            m = code[:4] + "00000000"
            other = [m] if m in by_code and same_entity(by_code[m], by_code[code]) else []
        return other[0] if other else ""

    def readings(name: str, code: str, figures) -> dict:
        """The ministry's figures and, if a unit is printed with the same name, the unit's too."""
        codes = [code] + ([t] if (t := twin(code)) else [])
        sets = [f for c in codes if (f := figures(c))]
        return ({"numbers_any": sets} if len(sets) > 1 else {"numbers": sets[0]}) | {"codes": codes[:len(sets)]
                                                                                    if len(sets) > 1 else [code]}

    for name, code in rng.sample(mdas, min(n, len(mdas))):         # a random budget year it has a figure for
        year = rng.choice([y for y in BUDGET_YEARS if approved(conn, code, y) is not None])
        add("lookup", f"How much was approved for the {name} in the {year} budget?", code=code,
            **readings(name, code, lambda c: [money(v)] if (v := approved(conn, c, year)) is not None else None))

    def either(code: str, figures) -> dict:
        codes = [c for c in (code, twin(code)) if c]
        both = [figures(code) for code in codes]
        return ({"numbers_any": both} if len(both) > 1 else {"numbers": both[0]}) | {"codes": codes}

    split_subs = [(nm, c) for nm, c in subs if all(approved(conn, c, 2026, k) is not None for k in SPLITS)]
    for name, code in rng.sample(split_subs, min(n, len(split_subs))):
        year = rng.choice([y for y in BUDGET_YEARS if all(approved(conn, code, y, k) is not None for k in SPLITS)])
        add("split", f"What are the personnel, overhead and capital allocations of the {name} in {year}?",
            code=code, **either(code, lambda c: [money(approved(conn, c, year, k)) for k in SPLITS]
                                if all(approved(conn, c, year, k) is not None for k in SPLITS) else ["-"]))
    spend_subs = [(nm, c) for nm, c in subs if perf(conn, c, 2026, latest_q)]
    def spent(c, y, q):               # (spent to date, revised) where the report prints both
        r = perf(conn, c, y, q)
        return [money(r[2]), money(r[0])] if r and r[0] is not None and r[2] is not None else None

    for name, code in rng.sample(spend_subs, min(n, len(spend_subs))):     # a random published quarter it has
        y, q = rng.choice([p for p in periods if spent(code, *p)] or [(2026, latest_q)])
        add("spend_quarter", f"How much had the {name} spent by the end of Q{q} {y}, against its revised budget?",
            code=code, **either(code, lambda c: spent(c, y, q) or ["-"]))
    for name, code in rng.sample(mdas, min(n, len(mdas))):
        add("compare", f"Compare the {name}'s approved budget in 2025 and 2026.", code=code,
            **readings(name, code, lambda c: [money(x), money(y)]
                       if (x := approved(conn, c, 2025)) is not None and (y := approved(conn, c, 2026)) is not None
                       else None))
    def share_forms(c) -> list[list[str]]:
        cap, tot = approved(conn, c, 2026, "capital"), approved(conn, c, 2026)
        if not (cap is not None and tot):
            return []
        pct = (Decimal(cap) / Decimal(tot) * 100).quantize(Decimal("0.1"), ROUND_HALF_UP)
        return [[f"{pct}%"], [f"{pct} %"], [money(cap), money(tot)]]

    for name, code in rng.sample(split_subs, min(n, len(split_subs))):
        other = twin(code)
        forms = share_forms(code) + (share_forms(other) if other else [])
        if forms:                          # a unit printed with its ministry's name: either share counts
            add("share", f"What share of the {name}'s 2026 approved budget is capital?", numbers_any=forms, code=code,
                codes=[code] + ([other] if other else []))
    for name, code in rng.sample(mdas, min(n, len(mdas))):        # the premise is the wrong way round
        a25, a26 = approved(conn, code, 2025), approved(conn, code, 2026)
        wrong = "fell" if a26 > a25 else "rose"

        def same_way(c):               # the unit's reading counts if its change goes the same way as the ministry's
            x, y = approved(conn, c, 2025), approved(conn, c, 2026)
            return [money(x), money(y)] if x is not None and y is not None and (y > x) == (a26 > a25) else None
        add("false_premise", f"Why did the {name}'s approved budget {'fall' if wrong == 'fell' else 'rise'} from "
            f"2025 to 2026?", premise_false=True, premise="fall" if wrong == "fell" else "rise", code=code,
            **readings(name, code, same_way))
    for name, code in rng.sample(subs, min(n, len(subs))):         # a period no document can hold yet
        kind = rng.choice(["q4", "next_q", "budget"])
        codes = [c for c in (code, twin(code)) if c]
        if kind == "budget":           # no approved budget yet; the newest budget's out-year estimate, labelled, counts
            y = max(BUDGET_YEARS) + 2
            est = [money(r[0]) for c in codes if (r := conn.execute(
                f"SELECT estimate_{y} FROM budget_items WHERE doc_id = %s AND code = %s AND spend_kind = 'total' "
                f"AND estimate_{y} IS NOT NULL ORDER BY seq LIMIT 1",
                (f"budget-{max(BUDGET_YEARS)}-approved", c)).fetchone())]
            add("not_in_data", f"How much is the {name}'s approved budget for {y}?",
                expect_gap=f"{min(BUDGET_YEARS)}–{max(BUDGET_YEARS)}", numbers=[], code=code, codes=codes,
                **({"estimate": est} if est else {}))
        else:
            when = "Q4 2026" if kind == "q4" else "Q1 2027"
            add("not_in_data", f"How much did the {name} spend in {when}?", expect_gap=f"Q{latest_q} 2026",
                numbers=[], code=code, codes=codes)
    pull = dtm_pull()
    if pull:
        lgas = sorted(pull["lgas"], key=lambda x: -x["idps"])
        for top in rng.sample([3, 5, 10], min(3, n)):
            add("rank_lga", f"Which {top} LGAs in Sokoto have the most IDPs?",
                numbers=[f"{x['idps']:,}" for x in lgas[:top]], names=[x["place"] for x in lgas[:top]])
        for x in rng.sample(lgas, min(n, len(lgas))):
            add("lookup_lga", f"How many IDPs are there in {x['place']} LGA?", numbers=[f"{x['idps']:,}"])
        r = pull["rounds"]
        add("trend", "How has the number of IDPs in Sokoto State changed over the last DTM rounds?",
            numbers=[f"{r[0]['idps']:,}", f"{r[1]['idps']:,}"])
    return cases


def build(n: int, seed: int, out: Path = OUT) -> Path:
    """Cases for `n` entities per family, drawn with `seed`, written to `out`. An unchanged question keeps the
    paraphrases it already has there (paraphrase.py costs a call each)."""
    with psycopg.connect(get_settings().db_url()) as conn:
        cases = generate(conn, n, random.Random(seed))
    if out.exists():
        old = {(c["id"], c["text"]): c.get("forms") for c in json.loads(out.read_text(encoding="utf-8"))["cases"]}
        for c in cases:
            if old.get((c["id"], c["text"])):
                c["forms"] = old[(c["id"], c["text"])]
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"_about": __doc__.splitlines()[0], "seed": seed, "cases": cases}, indent=1,
                              ensure_ascii=False), encoding="utf-8")
    from collections import Counter
    print(len(cases), "cases:", dict(Counter(c["family"] for c in cases)), "->", out)
    return out


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--n", type=int, default=6)
    p.add_argument("--seed", type=int, help="default: a new random draw")
    p.add_argument("--out", type=Path, default=OUT)
    a = p.parse_args()
    build(a.n, a.seed if a.seed is not None else random.randrange(10**6), a.out)


if __name__ == "__main__":
    main()
