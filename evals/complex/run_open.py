"""Run questions that have no checked answers yet and triage the replies.

For each question: outcome (answered / partial / not found / unverified / clarify), whether the figures
passed the number check, citations, whether the working was shown, the path taken (query_budget or page
search), and time. Writes a Markdown report with every reply, for a person to check the figures.

    uv run python evals/complex/run_open.py [--file evals/complex/mid_tier.json] [--ids m01 m05] [--out report.md]
"""

from __future__ import annotations

import argparse
import asyncio
import json
import statistics
import sys
import time
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import psycopg  # noqa: E402

from app.agent.answer import UNVERIFIED, answer_question  # noqa: E402
from app.config import get_settings  # noqa: E402


def outcome(a) -> str:
    if a.clarify:
        return "clarify"
    if not a.found:
        return "not found"
    if not a.verified or any(a.text.startswith(u) or u in a.text for u in UNVERIFIED.values()):
        return "unverified"
    return "partial" if a.partial else "answered"


async def main(path: Path, ids: list[str] | None, out: Path) -> None:
    s = get_settings()
    qs = [q for q in json.loads(path.read_text(encoding="utf-8"))["questions"] if not ids or q["id"] in ids]
    rows, report = [], [f"# Open-question run: {path.name}\n"]
    with psycopg.connect(s.db_url()) as conn:
        for q in qs:
            t0 = time.perf_counter()
            try:
                a = await answer_question(q["text"], q["lang"], conn, settings=s)
            except Exception as e:      # one bad question must not stop the run
                conn.rollback()
                rows.append((q["id"], "error", False, 0, False, "-", time.perf_counter() - t0))
                report.append(f"## {q['id']} ERROR {type(e).__name__}\n\n{q['text']}\n")
                print(f"{q['id']:>4} ERROR {type(e).__name__}")
                continue
            dt = time.perf_counter() - t0
            path_taken = (f"analysis:{a.analysis.tool}" if getattr(a, "analysis", None) is not None else
                          "category" if getattr(a, "category", None) is not None else
                          f"lines:{a.lines.operation}" if getattr(a, "lines", None) is not None else
                          f"query_budget:{a.budget.operation}" if a.budget is not None else
                          "latest" if a.latest else "fetch" if a.acquired else "search")
            res = (q["id"], outcome(a), a.verified, len(a.cited), "🧮" in a.text, path_taken, dt)
            rows.append(res)
            print(f"{q['id']:>4} {res[1]:<10} cites={res[3]} working={'y' if res[4] else 'n'} {path_taken:<22} {dt:5.1f}s")
            report.append(f"## {q['id']}: {res[1]} ({path_taken}, {dt:.1f}s)\n\n**Q:** {q['text']}\n"
                          + (f"\n_{q['note']}_\n" if q.get("note") else "") + f"\n```\n{a.text}\n```\n")
    counts = Counter(r[1] for r in rows)
    summary = (f"{len(rows)} questions: " + ", ".join(f"{k} {v}" for k, v in counts.most_common())
               + f" | median {statistics.median(r[6] for r in rows):.1f}s")
    print("\n" + summary)
    report.insert(1, summary + "\n")
    out.write_text("\n".join(report), encoding="utf-8")
    print(f"report: {out}")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--file", default=str(ROOT / "evals/complex/mid_tier.json"))
    p.add_argument("--ids", nargs="+")
    p.add_argument("--out", default=str(ROOT / "evals/complex/mid_tier_report.md"))
    a = p.parse_args()
    asyncio.run(main(Path(a.file), a.ids, Path(a.out)))
