"""Replay the answer check (app/agent/answer_check.py) over drafts, to choose its model and measure it.

Bad drafts: the 3 Nov live failures as they were sent (bad_drafts.json): the check must stop every one (verdict
revise or fail). Good drafts: answers an eval scored right (JSON lines written by evals/complex/run_open.py
--drafts with KASAFI_ANSWER_CHECK=false): a revise or fail on one of them is a false alarm; under 10% is the bar.
Each draft is rebuilt with its cited pages read from the library, and checked once (round 1), as live.

    KASAFI_BATCH_PROVIDER=fireworks python evals/check/run.py --provider open --good evals/check/good_drafts.jsonl
    python evals/check/run.py --provider meta --good evals/check/good_drafts.jsonl     # Muse Spark (Meta credit)
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import statistics
import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import psycopg  # noqa: E402

from app import usage  # noqa: E402
from app.agent import answer_check as ck  # noqa: E402
from app.agent.answer import Answer, Evidence  # noqa: E402
from app.config import get_settings  # noqa: E402

HERE = Path(__file__).parent


def rebuild(conn, d: dict) -> Answer:
    cited = []
    for c in d.get("cited") or []:
        n, doc, title = c[0], c[1], c[2]
        year, page, source = (c[3], c[4], c[5]) if len(c) >= 6 else (None, c[3], c[4])
        row = conn.execute("SELECT text FROM pages WHERE doc_id = %s AND page = %s", (doc, page)).fetchone()
        cited.append(Evidence(n, doc, title, year, page, source, row[0] if row else ""))
    return Answer(d["text"], d.get("found", True), True, cited, verification=d.get("verification", ""),
                  exact=d.get("exact") or d["text"], working=d.get("working", ""))


async def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--provider", choices=("open", "meta"), default="open")
    ap.add_argument("--good", nargs="*", default=[], help="JSON-lines drafts from run_open.py --drafts")
    ap.add_argument("--most-good", type=int, default=40)
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    s = get_settings()
    bad = json.loads((HERE / "bad_drafts.json").read_text(encoding="utf-8"))["drafts"]
    good = []
    for f in a.good:
        for line in Path(f).read_text(encoding="utf-8").splitlines():
            d = json.loads(line)
            if d.get("right") and d.get("checked") and d.get("found"):
                good.append(d)
    good = good[:a.most_good]
    if a.provider == "open":
        from app.providers.fireworks import BatchModel
        client = BatchModel(s)
    else:
        from app.providers.meta import MetaClient
        client = MetaClient(s)
    rows, secs = [], []
    t0 = usage.total_dollars(s)
    with psycopg.connect(s.db_url()) as conn:
        async with client:
            for kind, items in (("bad", bad), ("good", good)):
                for d in items:
                    ans = rebuild(conn, d)
                    u = SimpleNamespace(name=d.get("name", ""), level=d.get("level", "none"),
                                        restatement=d.get("restatement") or d["question"])
                    v = await ck.check(d["question"], ans, u, d.get("history") or [], conn, s, client)
                    stopped = v.verdict in ("revise", "fail")
                    ok = stopped if kind == "bad" else not stopped
                    secs.append(v.seconds)
                    why = "; ".join([*v.rules, *v.contradictions, *v.missing, *v.unclear,
                                     str((v.subject or {}).get("note") or "")])[:220]
                    rows.append((kind, d["id"], v.verdict, ok, v.seconds, why or v.why))
                    print(f"{kind:4} {d['id']:>8} {v.verdict:<8} {'ok ' if ok else 'WRONG'} {v.seconds:5.1f}s {why[:120]}",
                          flush=True)
    cost = usage.total_dollars(s) - t0
    nb, ng = sum(1 for r in rows if r[0] == "bad"), sum(1 for r in rows if r[0] == "good")
    caught = sum(1 for r in rows if r[0] == "bad" and r[3])
    false = sum(1 for r in rows if r[0] == "good" and not r[3])
    skipped = sum(1 for r in rows if r[2] == "skipped")
    head = (f"# Answer check replay: {a.provider}\n\nBad drafts stopped: **{caught}/{nb}**. Good drafts wrongly "
            f"stopped: **{false}/{ng}** ({100 * false / ng if ng else 0:.0f}%; bar under 10%). Checks that didn't run: "
            f"{skipped}. Median {statistics.median(secs):.1f} s, p90 {sorted(secs)[int(len(secs) * 0.9) - 1]:.1f} s; "
            f"cost ${cost:.3f} (${cost / len(rows):.4f} a check).\n")
    lines = [head, "| Kind | Id | Verdict | Right | Seconds | Why |", "|---|---|---|---|---|---|"]
    lines += [f"| {k} | {i} | {v} | {'✅' if ok else '❌'} | {sec:.1f} | {why.replace('|', '/')} |"
              for k, i, v, ok, sec, why in rows]
    (HERE / f"report-{a.provider}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(head)
    sys.stdout.flush()
    os._exit(0)


if __name__ == "__main__":
    asyncio.run(main())
