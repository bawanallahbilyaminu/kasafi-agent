"""Place history speed check (docs/place-history.md §9): a farmer's first request for a pin (the progress line
must be sent, the answer within a couple of minutes) and the same question again from the cache (under ~10 s),
through answer_question with the planner model (eval spend: one plan call per question).

Usage: uv run python evals/place/speed.py [--pins dundaye,wurno] [--out evals/place/speed-report.md]
Pins come from data/private/place_pins.yaml (outside git); their coordinates never reach the report.
"""

from __future__ import annotations

import argparse
import asyncio
import re
import sys
import time
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.stdout.reconfigure(encoding="utf-8")

QUESTIONS = [("How green was my farm in 2024?", "en"), ("Shin ruwa ya taɓa rufe gonata?", "ha")]
CACHED_MAX_S = 10.0


async def ask(conn, settings, question: str, lang: str, place: dict) -> tuple[float, list[str], str]:
    from app.agent.answer import answer_question
    notes: list[str] = []

    async def notify(text: str) -> None:
        notes.append(text)
    t0 = time.perf_counter()
    a = await answer_question(question, lang, conn, settings=settings, notify=notify, place=place, today=date.today())
    return time.perf_counter() - t0, notes, a.text


async def main() -> None:
    import psycopg
    import yaml
    from app import usage
    from app.config import get_settings
    from app.place.history import cell_id
    ap = argparse.ArgumentParser()
    ap.add_argument("--pins", default="dundaye,wurno")
    ap.add_argument("--file", default=str(ROOT / "data/private/place_pins.yaml"))
    ap.add_argument("--out", default=str(ROOT / "evals/place/speed-report.md"))
    a = ap.parse_args()
    pins = yaml.safe_load(open(a.file, encoding="utf-8"))
    pins = pins if isinstance(pins, list) else pins.get("pins", [])
    want = [w.strip() for w in a.pins.split(",") if w.strip()]
    s = usage.eval_settings(get_settings(), fetch=False)
    rows = []
    with psycopg.connect(s.db_url()) as conn:
        for p in pins:
            slug = re.sub(r"[^a-z0-9]+", "_", p["name"].lower())
            if not any(w in slug for w in want):
                continue
            lat, lon = float(p["lat"]), float(p["lon"])
            place = {"lat": lat, "lon": lon, "lga": p.get("lga", ""), "lga_pcode": p.get("lga_pcode", ""),
                     "shape": {"declined": True}}
            cell = cell_id(lat, lon)
            conn.execute("DELETE FROM sat_cache WHERE cell = %s", (cell,))
            conn.commit()
            for q, lang in QUESTIONS[:1]:
                first, notes, text = await ask(conn, s, q, lang, place)
                progress = any("🛰️" in n for n in notes)
                again, notes2, text2 = await ask(conn, s, q, lang, place)
                rows.append((p["name"], q, first, progress, again, "What the satellite" in text or "Abin da hotunan" in text,
                             text == text2, True))
                print(f"{p['name']}: first {first:.1f}s (progress line {'sent' if progress else 'MISSING'}), cached "
                      f"{again:.1f}s, same answer {text == text2}")
                if text != text2:
                    import difflib
                    for line in difflib.unified_diff(text.splitlines(), text2.splitlines(), lineterm="", n=0):
                        print("   ", line[:240])
            q, lang = QUESTIONS[1]
            t, notes, text = await ask(conn, s, q, lang, place)
            rows.append((p["name"], q, t, any("🛰️" in n for n in notes), t, bool(text), True, False))
            print(f"{p['name']}: Hausa flood question from the cache {t:.1f}s")
    # a first request must send the progress line; every cached answer must come under CACHED_MAX_S
    ok = all((r[3] or not r[7]) and r[4] <= CACHED_MAX_S and r[5] for r in rows)
    lines = [f"# Place history speed ({date.today()})", "",
             f"{len(rows)} questions on {len(set(r[0] for r in rows))} pins; cached answers must come under {CACHED_MAX_S:.0f} s "
             f"and a first request must send the progress line: **{'pass' if ok else 'FAIL'}**.", "",
             "| Pin | Question | First request | Progress line | Cached | Answered |", "| --- | --- | --- | --- | --- | --- |"]
    for name, q, first, progress, again, answered, same, fresh in rows:
        lines.append(f"| {name} | {q} | {first:.1f} s{'' if fresh else ' (cached)'} | {'yes' if progress else 'n/a'} | "
                     f"{again:.1f} s | {'yes' if answered else 'no'} |")
    lines += ["", "A first request reads ~12 years of Sentinel-2 windows, the Sentinel-1 passes and the plot outline "
                  "(SAM 3.1); the second reads the per-cell cache. Pin coordinates are not in this report."]
    Path(a.out).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("report:", a.out)
    import os
    os._exit(0 if ok else 1)


if __name__ == "__main__":
    asyncio.run(main())
