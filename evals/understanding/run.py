"""The conversation-understanding eval (app/agent/understand.py): every case in cases.json through the live model,
scored on capability (and level, time and kind where the case gives them), with latency and cost per message. The
readings are recorded in recorded.json, which the deploy gate replays (tests/test_understanding.py) without a
model call.

    uv run python evals/understanding/run.py [--provider meta|open]   -> report.md, recorded.json
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from app import usage  # noqa: E402
from app.agent.understand import understand  # noqa: E402
from app.config import get_settings  # noqa: E402

HERE = Path(__file__).resolve().parent
PLACES = {"pin": {"lat": 13.045, "lon": 5.155, "lga_pcode": "NG034021", "lga": "Wamakko", "ward": "Kalambaina"},
          "lga": {"lga_pcode": "NG034021", "lga": "Wamakko"}, "none": None}


def history_of(case: dict) -> list[dict]:
    return [{"question": t["user"], "answer": t["kasafi"]} for t in case["turns"]]


def score(reading: dict | None, expect: dict) -> list[str]:
    """What the reading got wrong ([] when right)."""
    if reading is None:
        return ["no reading"]
    wrong = []
    caps = expect["capability"] if isinstance(expect["capability"], list) else [expect["capability"]]
    if reading["capability"] not in caps:
        wrong.append(f"capability {reading['capability']} (want {'/'.join(caps)})")
    # 'either': a conditional ('if my child has trouble breathing'); the rule says urgent when unsure, and the fast
    # path still gives the nearest suitable facility, so either reading is acceptable
    if expect.get("urgent") != "either" and bool(reading.get("urgent")) != bool(expect.get("urgent")):
        wrong.append(f"urgent {reading.get('urgent')} (want {bool(expect.get('urgent'))})")
    for k in ("level", "time", "kind", "care", "facility_level", "ownership", "satellite_context"):
        want = expect.get(k)
        if want is not None and reading.get(k) not in (want if isinstance(want, list) else [want]):
            wrong.append(f"{k} {reading.get(k)} (want {want})")
    return wrong


async def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--provider", default="meta", choices=("meta", "open"))
    ap.add_argument("--record", action="store_true", help="write recorded.json from this run whatever the provider "
                                                          "(the deploy gate replays it)")
    ap.add_argument("--only", default="", help="comma-separated case ids: re-read only these (e.g. after a network "
                                               "drop); the other recorded readings are kept")
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    cases = json.loads((HERE / "cases.json").read_text(encoding="utf-8"))["cases"]
    only = {x.strip() for x in a.only.split(",") if x.strip()}
    kept = json.loads((HERE / "recorded.json").read_text(encoding="utf-8")) if only else {}
    s = get_settings()
    if a.provider == "open":
        from app.providers.baseten import BasetenClient as Client
        model = s.baseten_model
    else:
        from app.providers.meta import MetaClient as Client
        model = None
    recorded, rows, secs = {}, [], []
    t0 = usage.total_dollars(s)
    async with Client(s) as client:
        for c in cases:
            if only and c["id"] not in only:
                reading = kept.get(c["id"])
                recorded[c["id"]] = reading
                secs.append((reading or {}).get("seconds", 0.0))
                rows.append((c["id"], c["message"], reading, score(reading, c["expect"])))
                continue
            u = await understand(c["message"], history_of(c), PLACES[c["place"]], client, s, model=model)
            reading = u.to_dict() if u else None
            recorded[c["id"]] = reading
            wrong = score(reading, c["expect"])
            secs.append(u.seconds if u else 0.0)
            rows.append((c["id"], c["message"], reading, wrong))
            print(f"{c['id']} {'OK ' if not wrong else 'WRONG'} {u.seconds if u else 0:.2f}s "
                  f"{(reading or {}).get('capability')}/{(reading or {}).get('level')}/{(reading or {}).get('time')} "
                  f"{'; '.join(wrong)}", flush=True)
    cost = usage.total_dollars(s) - t0
    n_wrong = sum(1 for r in rows if r[3])
    lines = [f"# Conversation understanding eval ({a.provider})", "",
             f"{len(rows)} cases: **{len(rows) - n_wrong} right**, {n_wrong} wrong. Latency median "
             f"{statistics.median(secs):.2f} s, p90 {sorted(secs)[int(len(secs) * 0.9) - 1]:.2f} s; cost "
             f"${cost:.4f} (${cost / (len(only) or len(rows)):.4f} per message"
             f"{f'; {len(only)} re-read with --only, the rest kept from the last run' if only else ''}).", "",
             "| Id | Message | Capability / level / time / kind | Restatement | Wrong |", "|---|---|---|---|---|"]
    for cid, msg, r, wrong in rows:
        r = r or {}
        lines.append(f"| {cid} | {msg} | {r.get('capability')} / {r.get('level')} / {r.get('time')} / {r.get('kind')} "
                     f"| {str(r.get('restatement', '')).replace('|', '/')} | {'; '.join(wrong) or '✅'} |")
    (HERE / f"report{'' if a.provider == 'meta' else '-open'}.md").write_text("\n".join(lines) + "\n",
                                                                            encoding="utf-8")
    if a.provider == "meta" or a.record:
        (HERE / "recorded.json").write_text(json.dumps(recorded, indent=1, ensure_ascii=False), encoding="utf-8")
    print(lines[2])
    sys.stdout.flush()
    os._exit(1 if n_wrong else 0)


if __name__ == "__main__":
    asyncio.run(main())
