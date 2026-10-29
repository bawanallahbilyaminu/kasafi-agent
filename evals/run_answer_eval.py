"""Grounded-answer eval: run the real answer pipeline on evals/answers.json cases and check facts.

Checks for each case:
- found and verified (every number in the answer appears in its cited evidence)
- every expected figure appears in the answer exactly as written in the document
- at least one citation from an expected document (and page, if given)
- expected terms present (any of the alternatives), and an assumption stated when required
Usage:  uv run python evals/run_answer_eval.py [--ids 01 11] [--runs 2]
"""

import argparse
import asyncio
import json
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import psycopg  # noqa: E402

from app.agent.answer import answer_question  # noqa: E402
from app.config import get_settings  # noqa: E402



def check(case: dict, a) -> list[str]:
    fails = []
    if case.get("expect_not_found"):    # e.g. "how many IDPs now?" without a current report: say so, give no figure
        if a.found:
            return ["answered from other documents instead of saying the document wasn't found"]
        return ["a naira figure in a not-found reply"] if "₦" in a.text else []
    if not a.found:
        return ["not found"]
    if not a.verified:
        fails.append("unverified figures")
    for n in case.get("numbers", []):
        if n not in a.exact:
            fails.append(f"missing figure {n}")
    if case.get("numbers_any") and not any(all(n in a.exact for n in group) for group in case["numbers_any"]):
        fails.append(f"none of the accepted figures {case['numbers_any']}")
    cites = [(e.doc_id, e.page) for e in a.cited]
    if case.get("edition"):    # "latest" questions: the edition used, named in the reply
        got = a.latest.edition if a.latest else None
        if got not in case["edition"]["any"]:
            fails.append(f"edition {got}, expected one of {case['edition']['any']}")
        if "📅" not in a.text:
            fails.append("edition not named")
    elif not any(d in case["docs"] and (not case.get("pages") or p in case["pages"]) for d, p in cites):
        fails.append(f"no citation from {case['docs']} {case.get('pages', '')} (got {cites})")
    lowered = a.text.lower()
    for alts in case.get("terms_any", []):
        if not any(t.lower() in lowered for t in alts):
            fails.append(f"missing term {alts[0]}")
    if case.get("must_state_assumption"):
        note = a.plan.assumption_for(case["lang"]) if a.plan else ""
        if not note or note not in a.text:
            fails.append("assumption not stated")
    # complex questions must offer the rows and arithmetic (sent on "nuna lissafi"), or show them when there's no lead
    if case.get("working") and "🧮" not in (getattr(a, "working", "") or a.text):
        fails.append("working not shown")
    if case.get("partial") is not None and bool(a.partial) != case["partial"]:
        fails.append(f"partial should be {case['partial']}")
    return fails


async def main(ids: list[str] | None, runs: int, plan_reasoning: str | None = None, suite: str = "main") -> int:
    s = get_settings()
    if plan_reasoning:
        s = s.model_copy(update={"kasafi_plan_reasoning": plan_reasoning})
    base = ROOT / "evals" if suite == "main" else ROOT / "evals" / suite
    print(f"suite: {suite} | planner reasoning: {s.kasafi_plan_reasoning}")
    cases = json.loads((base / "answers.json").read_text(encoding="utf-8"))["cases"]
    questions = {q["id"]: q for q in json.loads((base / "questions.json").read_text(encoding="utf-8"))["questions"]}
    cases = [c for c in cases if not ids or c["id"] in ids]
    passed, times, plan_t, answer_t = 0, [], [], []
    with psycopg.connect(s.db_url()) as conn:
        for run in range(runs):
            for c in cases:
                t0 = time.perf_counter()
                q = questions[c["id"]]
                a = await answer_question(q.get("text_ha") or q["text"], c["lang"], conn, settings=s)
                times.append(time.perf_counter() - t0)
                plan_t.append(a.timings.get("plan", 0))
                answer_t.append(a.timings.get("answer", 0))
                fails = check(c, a)
                # A fetch on a question the library can already answer costs ~15 s and money: flag it.
                if a.plan and a.plan.missing_document and not c.get("may_fetch"):
                    fails.append(f"unexpected fetch for '{a.plan.missing_document}'")
                passed += not fails
                print(f"[run {run + 1}] {c['id']:>3} {'PASS' if not fails else 'FAIL'} {times[-1]:5.1f}s  "
                      f"{'; '.join(fails)}"
                      + (f"  [fetch: {a.acquired.status} {a.acquired.doc_id or ''}]" if a.acquired else ""))
                if fails:
                    print("      " + a.text.replace("\n", "\n      "))
    total = len(cases) * runs
    print(f"\n{passed}/{total} passed  |  total median {statistics.median(times):.1f}s, max {max(times):.1f}s  |  "
          f"plan median {statistics.median(plan_t):.1f}s  |  answer median {statistics.median(answer_t):.1f}s")
    return 0 if passed == total else 1


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--ids", nargs="+")
    p.add_argument("--runs", type=int, default=1)
    p.add_argument("--plan-reasoning", choices=["minimal", "low", "medium"])
    p.add_argument("--suite", default="main", help="main (evals/) or a folder under evals/, e.g. complex")
    a = p.parse_args()
    raise SystemExit(asyncio.run(main(a.ids, a.runs, a.plan_reasoning, a.suite)))
