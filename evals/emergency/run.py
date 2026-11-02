"""The emergency fast path eval (cheap and safety-critical, so it runs before every deploy):

1. Detection: every case in evals/emergency/cases.json through em.decide as a consented user (the phrase list, then
   the Muse Spark classifier where the design sends it), and as a user before consent (phrase list only).
   must_fire cases that don't fire and must_not cases that fire are the wrong ones.
2. Timing: the whole fast path through the real conversation handler (PostGIS lookup, no ORS) for a point in each
   of a few LGAs, from the message to the replies.

    uv run python evals/emergency/run.py        -> evals/emergency/report.md
"""

from __future__ import annotations

import asyncio
import json
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from app import usage  # noqa: E402
from app.config import get_settings  # noqa: E402
from app.geo.location import Spot, memory  # noqa: E402
from app.agent.understand import understand_message  # noqa: E402
from app.guardrails import emergency as em  # noqa: E402
from app.users import UserStore, user_key  # noqa: E402
from app.whatsapp.conversation import handle  # noqa: E402

HERE = Path(__file__).parent
TIMING_POINTS = [("Sokoto city", 13.06, 5.24, "NG034017"), ("Goronyo", 13.44, 5.67, "NG034006"),
                 ("Tureta", 12.58, 5.59, "NG034020"), ("Kebbe", 12.03, 4.78, "NG034010"),
                 ("Illela", 13.73, 5.30, "NG034008")]


async def detection(settings, cases: dict) -> list[dict]:
    out = []
    for group, want in (("must_fire", True), ("must_not", False)):
        for c in cases[group]:
            d = em.detect(c["text"])
            t0 = time.perf_counter()
            after = await em.decide(c["text"], settings, True)
            took = time.perf_counter() - t0
            before = await em.decide(c["text"], settings, False)
            path = "phrase" if d.hit and not d.ambiguous else "classifier" if (d.hit or d.health) else "none"
            # the second layer (2 Nov): when the fast path stays quiet, the understanding step's 'urgent' (as the
            # conversation handler runs it after consent)
            urgent, reason = None, ""
            if after is None:
                u = await understand_message(c["text"], [], None, settings)
                urgent, reason = (u.urgent, u.urgent_reason) if u is not None else (None, "no reading")
            fired_by = (after.by or "phrase") if after is not None else "understanding" if urgent else "none"
            out.append({**c, "want": want, "fired": after is not None or bool(urgent),
                        "fired_before_consent": before is not None, "path": path, "fired_by": fired_by,
                        "urgent": urgent, "reason": reason, "seconds": round(took, 2)})
    return out


async def timing(settings) -> list[dict]:
    # the fast reply itself (no ORS, as the label says): on WhatsApp the road distance follows it as a second message
    settings = settings.model_copy(update={"ors_api_key": None})
    store, sender, out = UserStore(":memory:"), "2340000000777", []
    key = user_key(sender, settings)
    store.create(key, "en")
    store.give_consent(key)
    for name, lat, lon, pcode in TIMING_POINTS:
        for text, maternal in (("My wife is pregnant and bleeding", True), ("My father collapsed", False)):
            memory.remember(key, Spot(lat, lon, pcode, name))
            t0 = time.perf_counter()
            outs = await handle({"from": sender, "id": "t", "type": "text", "text": {"body": text}}, None,
                                store=store, settings=settings, answer_fn=None)
            took = time.perf_counter() - t0
            out.append({"place": name, "maternal": maternal, "seconds": round(took, 3),
                        # pins carry coordinates only since 1 Nov: the facility is named in the text
                        "facility": next((ln.strip(" *📍") for o in outs for ln in (o.text or "").splitlines()
                                          if ln.startswith("📍")), None) if any(o.location for o in outs) else None,
                        "first_line": outs[0].text.splitlines()[0]})
    memory.forget(key)
    return out


def report(det: list[dict], tim: list[dict]) -> str:
    fire = [r for r in det if r["want"]]
    quiet = [r for r in det if not r["want"]]
    missed = [r for r in fire if not r["fired"]]
    false = [r for r in quiet if r["fired"]]
    by_path = {p: sum(1 for r in det if r["path"] == p) for p in ("phrase", "classifier", "none")}
    cls = [r["seconds"] for r in det if r["path"] == "classifier"]
    lines = ["# Emergency fast path eval", "",
             f"- must fire: {len(fire) - len(missed)}/{len(fire)} fired "
             f"(before consent, phrase list only: {sum(r['fired_before_consent'] for r in fire)}/{len(fire)})",
             f"- must not fire: {len(quiet) - len(false)}/{len(quiet)} quiet "
             f"(before consent: {len(quiet) - sum(r['fired_before_consent'] for r in quiet)}/{len(quiet)})",
             f"- decided by: phrase list {by_path['phrase']}, classifier {by_path['classifier']}, "
             f"neither {by_path['none']}",
             f"- fired by (must fire): " + ", ".join(
                 f"{k} {sum(1 for r in fire if r['fired_by'] == k)}"
                 for k in ("phrase", "classifier", "understanding", "none")),
             f"- off-list set (x/y): must fire {sum(r['fired'] for r in fire if r.get('set') == 'off_list')}/"
             f"{sum(1 for r in fire if r.get('set') == 'off_list')}, false alarms "
             f"{sum(r['fired'] for r in quiet if r.get('set') == 'off_list')}/"
             f"{sum(1 for r in quiet if r.get('set') == 'off_list')}",
             f"- classifier time: median {statistics.median(cls):.2f} s, max {max(cls):.2f} s" if cls else "",
             f"- fast path end to end (handler, PostGIS, no ORS): median {statistics.median(t['seconds'] for t in tim):.3f}"
             f" s, max {max(t['seconds'] for t in tim):.3f} s over {len(tim)} runs", "",
             "## Wrong", ""]
    lines += [f"- {r['id']} ({r['lang']}, {r['path']}): \"{r['text']}\": "
              f"{'did not fire' if r['want'] else 'fired by ' + r['fired_by']}"
              f"{' (understanding: ' + r['reason'] + ')' if r.get('reason') else ''}" for r in missed + false] \
        or ["- none"]
    lines += ["", "## Caught only by the understanding step", ""]
    lines += [f"- {r['id']}: \"{r['text']}\": {r['reason']}" for r in fire if r["fired_by"] == "understanding"] \
        or ["- none"]
    lines += ["", "## Before consent (phrase list only): wrong", ""]
    lines += [f"- {r['id']}: \"{r['text']}\": {'did not fire' if r['want'] else 'fired'}"
              for r in det if r["fired_before_consent"] != r["want"]] or ["- none"]
    lines += ["", "## Timing", "", "| place | case | seconds | facility pinned |", "|---|---|---|---|"]
    lines += [f"| {t['place']} | {'maternal' if t['maternal'] else 'general'} | {t['seconds']} | {t['facility']} |"
              for t in tim]
    return "\n".join(x for x in lines if x is not None) + "\n"


async def main() -> None:
    settings = get_settings()
    cases = json.loads((HERE / "cases.json").read_text(encoding="utf-8"))
    det = await detection(settings, cases)
    (HERE / "results.json").write_text(json.dumps({"detection": det}, indent=1, ensure_ascii=False),
                                       encoding="utf-8")                 # kept even if the timing part fails
    tim = await timing(settings)
    text = report(det, tim)
    (HERE / "report.md").write_text(text, encoding="utf-8")
    (HERE / "results.json").write_text(json.dumps({"detection": det, "timing": tim}, indent=1, ensure_ascii=False),
                                       encoding="utf-8")
    print(text)
    print(usage.summary(settings))


if __name__ == "__main__":
    asyncio.run(main())
