"""Run generated coverage cases and report the wrong rate per family (docs/question-planning.md §6).

Each case runs in one form, picked at random per run (the template's own English, or a paraphrase: hausa,
informal, code_switched, typo, followup with its previous turn). A reply is WRONG when an expected figure is
missing (exact, or in its readable form '₦42.00 million'), a false premise is repeated, or a figure is given
for a period that isn't published. Not found where the data has the answer counts as wrong too.

    uv run python evals/generated/run.py [--forms all|template|paraphrase] [--seed 1] [--families split lookup]
    uv run python evals/generated/run.py --fresh 17      # new random entities and periods (17 per family, ~150
                                                         # cases), paraphrased, then run; cases kept in runs/
"""

from __future__ import annotations

import argparse
import asyncio
import json
import random
import re
import statistics
import sys
import time
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import psycopg  # noqa: E402

from app.agent.answer import answer_question, readable_amounts  # noqa: E402
from app.config import get_settings  # noqa: E402

CASES = Path(__file__).with_name("cases.json")
RUNS = Path(__file__).with_name("runs")          # fresh draws (not in git: the report names the seed)


def accepted(number: str, lang: str) -> list[str]:
    """The exact figure and its readable forms ('₦42.00 million' / 'miliyan'), in either language."""
    out = [number]
    if "," in number and "." in number:
        for lg in ("en", "ha"):
            out.append(readable_amounts(f"₦{number}", lg).lstrip("₦"))
    return out


def wrong(case: dict, a, lang: str) -> str:
    text = f"{a.exact}\n{a.text}"
    if case.get("expect_gap"):                       # nothing published: no figure for that period, say what exists
        if case["expect_gap"] not in a.text and "latest" not in a.text.lower() and "mafi sabo" not in a.text:
            return f"no mention of what exists ({case['expect_gap']})"
        return ""
    if not a.found:
        return "not found, though the data has it"
    groups = case.get("numbers_any") or [case.get("numbers", [])]
    if not any(all(any(f in text for f in accepted(n, lang)) for n in g) for g in groups):
        missing = [n for n in groups[0] if not any(f in text for f in accepted(n, lang))]
        return f"missing {missing}"
    if case.get("premise_false") and re.search(r"(?i)\b(?:because|due to|reason (?:is|was)|saboda)\b", a.text) \
            and not re.search(r"(?i)\b(?:actually|in fact|rose|increased|fell|decreased|ya karu|ya ragu)\b", a.text):
        return "explained a premise the figures contradict"
    return ""


async def main(forms: str, seed: int, families: list[str] | None, out: Path, cases_path: Path = CASES) -> None:
    s = get_settings()
    rng = random.Random(seed)
    data = json.loads(cases_path.read_text(encoding="utf-8"))
    cases = [c for c in data["cases"] if not families or c["family"] in families]
    per_family: dict[str, list] = defaultdict(list)
    per_form: dict[str, list] = defaultdict(list)
    times, report = [], [f"# Generated coverage run\n\nCases: {cases_path.name} (draw seed {data.get('seed')}), "
                         f"form seed {seed}\n"]
    with psycopg.connect(s.db_url()) as conn:
        for c in cases:
            options = ["template"] + list((c.get("forms") or {}).keys())
            if forms == "template":
                options = ["template"]
            elif forms == "paraphrase" and len(options) > 1:
                options = options[1:]
            form = rng.choice(options)
            q, history, lang = c["text"], None, "en"
            if form != "template":
                v = c["forms"][form]
                if form == "followup":
                    q, history = v["question"], [{"question": v["previous"], "answer": "", "sources": []}]
                else:
                    q = v
                lang = "ha" if form in ("hausa", "code_switched") else "en"
            t0 = time.perf_counter()
            try:
                a = await answer_question(q, lang, conn, settings=s, history=history)
                why = wrong(c, a, lang)
            except Exception as e:                       # one bad case must not stop the run
                conn.rollback()
                a, why = None, f"error {type(e).__name__}"
            dt = time.perf_counter() - t0
            times.append(dt)
            per_family[c["family"]].append(bool(why))
            per_form[form].append(bool(why))
            print(f"{c['id']:18} {form:13} {'WRONG ' + why if why else 'ok':60.60} {dt:5.1f}s")
            report.append(f"## {c['id']} ({form}) {'WRONG: ' + why if why else 'ok'} ({dt:.1f}s)\n\n**Q:** {q}\n\n"
                          f"```\n{a.text if a else '-'}\n```\n")
    lines = ["| family | wrong | of |", "|---|---|---|"]
    lines += [f"| {f} | {sum(v)} | {len(v)} |" for f, v in sorted(per_family.items())]
    lines += ["", "| form | wrong | of |", "|---|---|---|"]
    lines += [f"| {f} | {sum(v)} | {len(v)} |" for f, v in sorted(per_form.items())]
    total = sum(sum(v) for v in per_family.values())
    summary = f"{len(cases)} cases: wrong {total} | median {statistics.median(times):.1f}s"
    print("\n" + summary + "\n" + "\n".join(lines))
    out.write_text("\n".join([report[0], summary, "", *lines, "", *report[1:]]), encoding="utf-8")
    print("report:", out)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--forms", default="all", choices=["all", "template", "paraphrase"])
    p.add_argument("--seed", type=int, default=1)
    p.add_argument("--families", nargs="+")
    p.add_argument("--out", type=Path, default=Path(__file__).with_name("report.md"))
    p.add_argument("--fresh", type=int, metavar="N", help="draw N new entities per family (a new seed), paraphrase "
                                                          "them, then run")
    a = p.parse_args()
    cases_path = CASES
    if a.fresh:
        from evals.generated.generate import build
        from evals.generated.paraphrase import paraphrase
        draw = random.randrange(10**6)
        cases_path = build(a.fresh, draw, RUNS / f"cases-{draw}.json")
        asyncio.run(paraphrase(cases_path))
    asyncio.run(main(a.forms, a.seed, a.families, a.out, cases_path))
