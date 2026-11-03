"""Run the generated planner place-history cases (evals/place/cases.json): in code by default (area_route and
area_answer, no model, no spend), or --full through answer_question (the planner model routes; counts against the
eval budget). Writes evals/place/report.md.

Checks per case: the route lands on the expected level and unit; the top and bottom units are named in the
ranking; the top value appears; low-data units are marked; must_have / must_not strings.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
import time
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.stdout.reconfigure(encoding="utf-8")

import psycopg  # noqa: E402

from app.config import get_settings  # noqa: E402
from app.place import planner as P  # noqa: E402


def check(case: dict, text: str, working: str, level: str, unit: str) -> list[str]:
    e, wrong = case["expect"], []
    if unit != case["unit"]:                      # the LGA asked, or NG034 for the state
        wrong.append(f"route {level}/{unit or 'none'}")
    body = text + "\n" + working
    if e.get("top") and e["top"] not in body:
        wrong.append(f"top {e['top']} missing")
    if e.get("bottom") and e["bottom"] not in body:
        wrong.append(f"bottom {e['bottom']} missing")
    if e.get("top_value") and e["top_value"] not in body:
        wrong.append(f"value {e['top_value']} missing")
    for name in e.get("low_data", []):
        if name not in body:
            wrong.append(f"low-data {name} missing")
    for name in e.get("below", []) + e.get("above", []):
        if name not in body:
            wrong.append(f"rain-flagged {name} missing")
    for s in e.get("must_have", []):
        if s not in body:
            wrong.append(f"must have '{s}'")
    for s in e.get("must_not", []):
        if s.lower() in body.lower():
            wrong.append(f"must not '{s}'")
    for s in e.get("text_must_not", []):          # technical words belong in show working, never in the answer
        if s.lower() in text.lower():
            wrong.append(f"answer must not '{s}'")
    return wrong


LAST: dict = {}          # the last --full case's reading and check verdicts, printed with --detail


async def run_full(case: dict, conn) -> tuple[str, str, str, str]:
    """As live (3 Nov): the understanding step reads the message, then answer_question, whose answer check runs."""
    from app import usage
    from app.agent.answer import answer_question
    from app.agent.understand import understand_message
    from app.config import get_settings
    s = usage.eval_settings(get_settings(), fetch=False)          # the library only: never a web search
    reading = await understand_message(case["question"], None, case.get("place"), s)
    a = await answer_question(case["question"], case["lang"], conn, settings=s, today=date.today(),
                              place=case.get("place"), **({"understanding": reading} if reading is not None else {}))
    LAST.update(reading=getattr(reading, "capability", None), level=getattr(reading, "level", None),
                restatement=getattr(reading, "restatement", ""), found=a.found,
                checks=[{k: c.get(k) for k in ("verdict", "subject", "missing", "rules", "why")}
                        for c in getattr(a, "checks", []) or []], maps=len(a.maps or []), text=(a.text or "")[:300])
    spec = (a.maps or [{}])[0]
    if spec.get("highlight"):                 # a ward answer: its map is the LGA's with the ward outlined
        return a.text, a.working, "ward", spec["highlight"]
    return a.text, a.working, spec.get("level", ""), spec.get("unit", "")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--full", action="store_true", help="through answer_question (model planner; eval spend)")
    ap.add_argument("--only", default="", help="a family or an id")
    ap.add_argument("--file", default=str(ROOT / "evals/place/cases.json"))
    ap.add_argument("--start", default="", help="resume at this id (the cases before it are skipped)")
    ap.add_argument("--chunk-s", type=float, default=0, help="stop cleanly after this many seconds and print NEXT <id>")
    ap.add_argument("--ids", default="", help="comma-separated ids: only these")
    ap.add_argument("--detail", action="store_true", help="print each case's reading and check verdicts (--full)")
    a = ap.parse_args()
    started = time.perf_counter()
    cases = json.loads(Path(a.file).read_text(encoding="utf-8"))["cases"]
    if a.only:
        cases = [c for c in cases if c["family"] == a.only or c["id"] == a.only]
    if a.ids:
        wanted = {x.strip() for x in a.ids.split(",")}
        cases = [c for c in cases if c["id"] in wanted]
    if a.start:
        cases = cases[next(i for i, c in enumerate(cases) if c["id"] == a.start):]
    lines, wrong_n, times = [], 0, []
    with psycopg.connect(get_settings().db_url()) as conn:
        for c in cases:
            if a.chunk_s and time.perf_counter() - started > a.chunk_s:     # a foreground chunk: the next one resumes
                from app import usage
                print(f"NEXT {c['id']}")
                print(usage.summary(get_settings(), answers=len(times)))
                sys.stdout.flush()
                os._exit(0)
            t0 = time.perf_counter()
            if a.full:
                try:                       # a network failure is that case's error, never the end of the run
                    text, working, level, unit = asyncio.run(run_full(c, conn))
                except Exception as e:     # noqa: BLE001
                    conn.rollback()
                    print(c["id"], c["family"], c["lang"], [f"ERROR {type(e).__name__}"])
                    lines.append(f"| {c['id']} | {c['family']} | {c['lang']} | {c['year']} | - | ERROR {type(e).__name__} |")
                    wrong_n += 1
                    continue
            else:
                r = P.area_route(c["question"], "", c.get("place"))
                if r is None:
                    text, working, level, unit = "", "", "", ""
                else:
                    ans = P.area_answer(conn, c["question"], "", c["lang"], r[0], r[1], date.today(), place=c.get("place"))
                    text, working, unit = ans.text, ans.working, ans.unit
                    level = "ward" if r[0] == "ward" else ans.level if r[0] == "lga" else "state"
            dt = time.perf_counter() - t0
            times.append(dt)
            wrong = check(c, text, working, level, unit)
            wrong_n += bool(wrong)
            lines.append(f"| {c['id']} | {c['family']} | {c['lang']} | {c['year']} | {dt:.1f} | "
                         f"{'ok' if not wrong else '; '.join(wrong)} |")
            print(c["id"], c["family"], c["lang"], "ok" if not wrong else wrong)
            if a.detail and a.full:
                print("  DETAIL", json.dumps(LAST, ensure_ascii=False, default=str)[:900])
    med = sorted(times)[len(times) // 2] if times else 0
    report = [f"# Place history planner eval ({'full pipeline' if a.full else 'in code'}), {date.today()}", "",
              f"{len(cases)} cases, **{wrong_n} wrong**, median {med:.1f} s.", "",
              "| id | family | lang | year | s | result |", "|---|---|---|---|---|---|", *lines]
    Path(ROOT / "evals/place/report.md").write_text("\n".join(report), encoding="utf-8")
    print(f"\n{len(cases)} cases, {wrong_n} wrong, median {med:.1f}s -> evals/place/report.md")
    if a.full:
        from app import usage
        print(usage.summary(get_settings(), answers=len(times)))
    sys.stdout.flush()
    os._exit(1 if wrong_n else 0)


if __name__ == "__main__":
    main()
