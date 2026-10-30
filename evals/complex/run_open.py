"""Run questions that have no checked answers yet and triage the replies.

For each question: outcome (answered / partial / not found / unverified / clarify), whether the figures
passed the number check, citations, whether the working was shown, the path taken (query_budget or page
search), and time. Writes a Markdown report with every reply, for a person to check the figures.

    uv run python evals/complex/run_open.py [--file evals/complex/mid_tier.json] [--ids m01 m05] [--out report.md]
                                            [--resume]    # continue a stopped run (evals/runtime.py)
"""

from __future__ import annotations

import argparse
import asyncio
import json
import re
import statistics
import sys
import time
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from app.agent.answer import UNVERIFIED, answer_question  # noqa: E402
from app import usage  # noqa: E402
from app.config import get_settings  # noqa: E402
from evals.runtime import Checkpoint, memory_line, run_each, warm  # noqa: E402


STAGES = ("plan", "acquire", "line_search", "read", "read1", "read2", "reread", "page_search", "compose",
          "answer", "calls1", "calls2")


def wrong(check: dict | None, a) -> str:
    """Why a reply fails its checked facts (evals/complex/mid_tier_checks.json), or '' (also when unchecked)."""
    if not check:
        return ""
    if check.get("must_not") and re.search(check["must_not"], a.text):
        return f"says {re.search(check['must_not'], a.text).group(0)!r}"
    exact = f"{a.exact}\n{a.text}"
    if check.get("any") and not any(all(n in exact for n in group) for group in check["any"]):
        return f"none of {check['any']}"
    if missing := [p for p in check.get("all_re", []) if not re.search(p, a.text, re.M)]:
        return f"missing {missing}"
    if (c := check.get("count")) and len(re.findall(c["pattern"], a.text, re.M)) < c["min"]:
        return f"fewer than {c['min']} of {c['pattern']!r}"
    return ""


def outcome(a) -> str:
    if a.clarify:
        return "clarify"
    if not a.found:
        return "not found"
    if not a.verified or any(a.text.startswith(u) or u in a.text for u in UNVERIFIED.values()):
        return "unverified"
    return "partial" if a.partial else "answered"


async def main(path: Path, ids: list[str] | None, out: Path, resume: bool = False, concurrency: int = 1) -> None:
    s = get_settings()
    qs = [q for q in json.loads(path.read_text(encoding="utf-8"))["questions"] if not ids or q["id"] in ids]
    checks_file = path.with_name(f"{path.stem}_checks.json")
    checks_file = checks_file if checks_file.exists() else path.parent / "mid_tier_checks.json"
    checks = json.loads(checks_file.read_text(encoding="utf-8"))["checks"] if checks_file.exists() else {}
    ckpt = Checkpoint(out.stem, {"file": str(path), "ids": ids}, resume=resume)
    resumed = len(ckpt.done)
    warm()

    async def one(q: dict, conn) -> None:
        t0 = time.perf_counter()
        try:
            a = await answer_question(q["text"], q["lang"], conn,         # the library only: no fetching
                                      settings=usage.eval_settings(s, fetch=bool(q.get("may_fetch"))))
        except Exception as e:      # one bad question must not stop the run
            conn.rollback()
            print(f"{q['id']:>4} ERROR {type(e).__name__}")
            ckpt.add(q["id"], {"row": [q["id"], "error", False, 0, False, "-", time.perf_counter() - t0],
                               "error": type(e).__name__})
            return
        dt = time.perf_counter() - t0
        path_taken = (f"topic:{a.topic.topic}" if getattr(a, "topic", None) is not None else
                      f"analysis:{a.analysis.tool}" if getattr(a, "analysis", None) is not None else
                      "category" if getattr(a, "category", None) is not None else
                      f"lines:{a.lines.operation}" if getattr(a, "lines", None) is not None else
                      f"query_budget:{a.budget.operation}" if a.budget is not None else
                      "latest" if a.latest else "fetch" if a.acquired else "search")
        res = [q["id"], outcome(a), a.verified, len(a.cited), bool(getattr(a, "working", "")), path_taken, dt]
        why = wrong(checks.get(q["id"]), a)
        parts = " ".join(f"{k}={v:.1f}" for k, v in a.timings.items() if k in STAGES)
        print(f"{q['id']:>4} {res[1]:<10} {'WRONG ' if why else ''}cites={res[3]} {path_taken:<22} "
              f"{dt:5.1f}s  [{parts}]" + (f"  {why}" if why else ""))
        ckpt.add(q["id"], {"row": res, "timings": dict(a.timings), "why": why, "text": a.text})

    if not await run_each([q for q in qs if q["id"] not in ckpt.done], one, s.db_url(), concurrency, s):
        raise SystemExit(2)                          # the day's eval budget: --resume continues
    rows, report, stages, checked = [], [f"# Open-question run: {path.name}\n"], [], []
    for q in qs:                    # in question order, whichever session ran them
        r = ckpt.done[q["id"]]
        rows.append(tuple(r["row"]))
        if r.get("error"):
            report.append(f"## {q['id']} ERROR {r['error']}\n\n{q['text']}\n")
            continue
        stages.append(r["timings"])
        why, res = r["why"], r["row"]
        if q["id"] in checks:
            checked.append((q["id"], why))
        report.append(f"## {q['id']}: {res[1]}{' WRONG: ' + why if why else ''} ({res[5]}, {res[6]:.1f}s)\n\n"
                      f"**Q:** {q['text']}\n"
                      + (f"\n_{q['note']}_\n" if q.get("note") else "") + f"\n```\n{r['text']}\n```\n")
    counts = Counter(r[1] for r in rows)
    bad = [i for i, why in checked if why]
    summary = (f"{len(rows)} questions: " + ", ".join(f"{k} {v}" for k, v in counts.most_common())
               + f" | wrong {len(bad)} of {len(checked)} checked" + (f" ({', '.join(bad)})" if bad else "")
               + f" | median {statistics.median(r[6] for r in rows):.1f}s")
    # where the time goes: per stage, the questions that had it, their median and their share of all seconds
    total = sum(r[6] for r in rows) or 1
    lines = []
    for k in STAGES:
        vals = [s[k] for s in stages if k in s]
        if vals and not k.startswith("calls"):
            lines.append(f"{k:<13} n={len(vals):>2} median {statistics.median(vals):5.1f}s  "
                         f"{sum(vals) / total * 100:4.0f}% of all time")
    calls = [s.get("calls1", 0) + s.get("calls2", 0) for s in stages if "read1" in s]
    if calls:
        lines.append(f"row readings: {sum(calls)} model calls for {len(calls)} questions (2 = no retry)")
    print("\n" + summary + "\n" + "\n".join(lines))
    report.insert(1, summary + "\n\n```\n" + "\n".join(lines) + "\n```\n")
    out.write_text("\n".join(report), encoding="utf-8")
    print(f"report: {out}")
    print(usage.summary(s, answers=len(rows)))
    print(memory_line(resumed))


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--file", default=str(ROOT / "evals/complex/mid_tier.json"))
    p.add_argument("--ids", nargs="+")
    p.add_argument("--out", default=str(ROOT / "evals/complex/mid_tier_report.md"))
    p.add_argument("--resume", action="store_true", help="continue the stopped run with this --out")
    p.add_argument("--concurrency", type=int, default=1, choices=[1, 2])
    a = p.parse_args()
    asyncio.run(main(Path(a.file), a.ids, Path(a.out), a.resume, a.concurrency))
