"""The seven planner-variance cases (docs/planner-variance.md), each answered N times through answer_question
with the planner model: a case passes a run when every expected string is in the answer (and the forbidden ones
are not); a case *flips* when its runs don't all agree. The plan's word record (overrides, conflicts, second
opinion) is shown per run.

Usage: uv run python evals/variance/run.py [--runs 5] [--only t02 p2_period-04] [--out evals/variance/report.md]
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
import time
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.stdout.reconfigure(encoding="utf-8")

CASES = [
    {"id": "t02", "lang": "ha", "q": "A cewar NBS, menene MPI na jihar Sokoto, kuma a cewar SBS nawa ne ya inganta?",
     "any": [["0.409"]], "all": [], "any2": [["0.23853", "0.239"]], "not": []},
    {"id": "t04", "lang": "en", "q": "According to SBS, what was Sokoto's multidimensional poverty incidence in 2022?",
     "any": [["91%"]], "all": [], "any2": [["as cited in", "kamar yadda"]], "not": ["Sokoto State Bureau of Statistics: 91% – 2022 baseline"]},
    {"id": "p2_period-04", "lang": "en", "q": "How much did the Ministry of Lands and Housing spend from January to September 2025?",
     "any": [["33,198,501,951.04", "33.20 billion"]], "all": [], "any2": [], "not": ["Q1–Q4", "Q1-Q4", "51.92 billion"]},
    {"id": "p3_project-01", "lang": "en", "q": "How much is budgeted for Procurment of 5n0 peugout 406 saloon for members and secretary in 2026?",
     "any": [["10,000,000.00", "10.00 million"]], "all": [], "any2": [], "not": ["25.98 billion"]},
    {"id": "p4_narrative-02", "lang": "en", "q": "What does the Sokoto State Budget Implementation Report Q3 2025 say about Revenue Performance, and what reasons does it give?",
     "any": [["526,882,142,484.39", "526.88 billion"]], "all": [], "any2": [], "not": [], "cite": ["bir-2025-q3", 4]},
    {"id": "spend_quarter-04", "lang": "en", "q": "How much had teh State Enviromental Protection Agency spent by the end of Q3 2025, agianst its revised budget?",
     "any": [["516,538,439.45", "516.54 million"]], "all": [], "any2": [["679,769,984.28", "679.77 million"]], "not": []},
    {"id": "split-06", "lang": "en", "q": "What are its personnel, overhead and capital allocations in 2025?",
     "history": [{"question": "Menene allocation na personnel, overhead da capital na Fertilizer and Agricultral Supplies Company a 2026?",
                  "answer": "Ga Fertilizer and Agricultral Supplies Company, kasafin da aka amince (albashi) shi ne ₦68.17 miliyan.",
                  "sources": [{"doc_id": "budget-2026-approved", "page": 53}]}],
     "any": [["39.78 million", "39,780,000"]], "all": [], "any2": [["4,481,100,000.00", "4.48 billion"], ["47,090,000.00", "47.09 million"]], "not": []},
]


def check(case: dict, text: str, sources) -> list[str]:
    wrong = []
    for group in case["any"] + case["any2"]:
        if not any(s in text for s in group):
            wrong.append(f"missing one of {group}")
    for s in case["not"]:
        if s in text:
            wrong.append(f"has '{s}'")
    if cite := case.get("cite"):
        pages = {(getattr(s, "doc_id", None) or (s.get("doc_id") if isinstance(s, dict) else None),
                  getattr(s, "page", None) or (s.get("page") if isinstance(s, dict) else None)) for s in sources or []}
        if tuple(cite) not in pages:
            wrong.append(f"didn't cite {cite[0]} p{cite[1]}")
    return wrong


async def main() -> int:
    import psycopg
    from app import usage
    from app.agent.answer import answer_question
    from app.config import get_settings
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", type=int, default=5)
    ap.add_argument("--only", nargs="+")
    ap.add_argument("--out", default=str(ROOT / "evals/variance/report.md"))
    a = ap.parse_args()
    s = usage.eval_settings(get_settings(), fetch=False)
    cases = [c for c in CASES if not a.only or c["id"] in a.only]
    rows = []
    t_all = time.perf_counter()
    with psycopg.connect(s.db_url()) as conn:
        for c in cases:
            results = []
            for i in range(a.runs):
                t0 = time.perf_counter()
                try:
                    ans = await answer_question(c["q"], c["lang"], conn, settings=s, history=c.get("history"))
                    wrong = check(c, ans.text, getattr(ans, "cited", None) or getattr(ans, "sources", None))
                    words = getattr(ans.plan, "words", {}) if getattr(ans, "plan", None) else {}
                    rec = {"ok": not wrong, "why": wrong, "dt": round(time.perf_counter() - t0, 1),
                           "overrides": [o["field"] for o in words.get("overrides", [])],
                           "conflicts": [x["field"] for x in words.get("conflicts", [])],
                           "second": words.get("second_opinion", {}).get("used") if words.get("second_opinion") else None,
                           "text": ans.text[:600]}
                except Exception as e:                   # noqa: BLE001
                    rec = {"ok": False, "why": [f"error {type(e).__name__}"], "dt": round(time.perf_counter() - t0, 1),
                           "overrides": [], "conflicts": [], "second": None, "text": ""}
                results.append(rec)
                print(f"{c['id']} run {i + 1}: {'ok' if rec['ok'] else 'WRONG ' + '; '.join(rec['why'])} {rec['dt']}s "
                      f"overrides={rec['overrides']}" + (f" second={rec['second']}" if rec["second"] is not None else ""), flush=True)
            rows.append((c, results))
    flips = [c["id"] for c, rs in rows if len({r["ok"] for r in rs}) > 1]
    wrong_all = [c["id"] for c, rs in rows if all(not r["ok"] for r in rs)]
    lines = [f"# Planner-variance cases, {a.runs} runs each ({date.today()})", "",
             f"{len(rows)} cases × {a.runs} runs: **{len(flips)} flip(s)** ({', '.join(flips) or 'none'}); wrong in every run: "
             f"{', '.join(wrong_all) or 'none'}; {time.perf_counter() - t_all:.0f} s in all.", "",
             "| Case | Runs ok | Overrides (per run) | Second opinion | Median s |", "| --- | --- | --- | --- | --- |"]
    for c, rs in rows:
        ok = sum(r["ok"] for r in rs)
        ov = "; ".join(",".join(r["overrides"]) or "-" for r in rs)
        sec = ", ".join(str(r["second"]) for r in rs if r["second"] is not None) or "-"
        med = sorted(r["dt"] for r in rs)[len(rs) // 2]
        lines.append(f"| {c['id']} | {ok}/{len(rs)} | {ov} | {sec} | {med} |")
    for c, rs in rows:
        bad = [(i, r) for i, r in enumerate(rs, 1) if not r["ok"]]
        if bad:
            lines += ["", f"## {c['id']}: {c['q']}"]
            for i, r in bad:
                lines += [f"- run {i}: {'; '.join(r['why'])}", "", "```", r["text"], "```"]
    Path(a.out).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\n{len(flips)} flip(s); report: {a.out}")
    return 1 if flips or wrong_all else 0


if __name__ == "__main__":
    import os
    rc = asyncio.run(main())
    sys.stdout.flush()
    os._exit(rc)
