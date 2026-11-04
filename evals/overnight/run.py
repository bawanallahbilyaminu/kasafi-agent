"""Run one round's questions through the real WhatsApp path (webhook -> understanding -> routing -> retrieval ->
writer -> answer check), as scripts/live_smoke.py does on the server, with Muse Spark Open on Baseten only. Each
question is one synthetic sender with consent given; its turns run in order; every message Kasafi would send is
captured. One line per question goes to results-<set>.jsonl (resumable: a question already there is skipped) and to
progress.log. The caps (Baseten dollars, the stop time) are checked before every question, in code.

    python evals/overnight/run.py --round 1 --set fix [--chunk-s 540] [--only id,id]
    (--set heldout | all; the run stops cleanly at --chunk-s seconds and prints NEXT <id>; run again to continue)
"""

from __future__ import annotations

import argparse
import asyncio
import itertools
import json
import os
import re
import sys
import time
from pathlib import Path

from common import (CapReached, ROOT, append_jsonl, charge, elapsed_s, guard, log, meta_guard, read_jsonl,
                    round_dir)  # noqa: E402

sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import psycopg  # noqa: E402

from app import usage  # noqa: E402
from app.config import get_settings  # noqa: E402

_ids = itertools.count(1)
NOT_FOUND_WORDS = ("couldn't find", "Ban sami amsar", "couldn't give a checked answer", "Ban iya ba da amsar")
_NUM = re.compile(r"(?:₦|NGN\s?|\bN(?=\d))?\s?(\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?)\s?"
                  r"(trillion|tiriliyan|billion|biliyan|bn|million|miliyan|mn|m\b|k\b|K\b)?", re.I)
_SCALE = {"trillion": 1e12, "tiriliyan": 1e12, "billion": 1e9, "biliyan": 1e9, "bn": 1e9, "million": 1e6,
          "miliyan": 1e6, "mn": 1e6, "m": 1e6, "k": 1e3}


def amounts_in(text: str) -> list[float]:
    out = []
    for m in _NUM.finditer(text or ""):
        try:
            v = float(m.group(1).replace(",", ""))
        except ValueError:
            continue
        scale = (m.group(2) or "").lower()
        out.append(v * _SCALE.get(scale, 1.0))
    return out


def has_figure(text: str, fig: str, exact: bool = False) -> bool:
    """The figure as written, or (a money amount) the same value in house style within 0.6%."""
    if re.search(rf"(?<![\d.,]){re.escape(fig)}(?![\d]|[.,]\d)", text or ""):
        return True
    if exact:
        return False
    try:
        want = float(fig.replace(",", ""))
    except ValueError:
        return False
    if want < 1000:
        return False
    return any(abs(v - want) <= 0.006 * want for v in amounts_in(text))


def score(expect: dict, reply: str, turns_replies: list[str]) -> list[str]:
    fails = []
    last = turns_replies[-1] if turns_replies else ""
    if not last.strip():
        return ["silence"]
    if expect.get("emergency") is not None:
        fired = last.lstrip().startswith("🚨") or "⚠️ Wannan na iya zama gaggawar" in last
        if expect["emergency"] and not fired:
            fails.append("emergency not fired")
        if not expect["emergency"] and fired:
            fails.append("false emergency")
        return fails
    if expect.get("not_found"):
        if not any(w in last for w in NOT_FOUND_WORDS):
            fails.append("answered instead of saying not found")
        return fails
    if any(w in last for w in NOT_FOUND_WORDS) and (expect.get("figures") or expect.get("any") or expect.get("found")):
        fails.append("not found")
    for f in expect.get("figures", []):
        if not has_figure(last, f, expect.get("exact", False)):
            fails.append(f"missing figure {f}")
    if expect.get("any") and not any(all(has_figure(last, n) for n in group) for group in expect["any"]):
        fails.append(f"none of {expect['any'][:2]}")
    if expect.get("amounts"):
        got = amounts_in(last)
        for want in expect["amounts"]:
            if not any(abs(v - want) <= 0.01 * want for v in got):
                fails.append(f"missing amount {want:,.0f}")
    if (lead := expect.get("lead_figure")) and not has_figure(last.split("\n")[0], lead):
        fails.append(f"total {lead} not in the first line")
    for f in expect.get("must_not_figures", []):
        if has_figure(last, f, True):
            fails.append(f"double count {f}")
    low = last.lower()
    if expect.get("must_any") and not any(m.lower() in low for m in expect["must_any"]):
        fails.append(f"none of the names {expect['must_any'][:3]}")
    for m in expect.get("must", []):
        if m.lower() not in low:
            fails.append(f"missing '{m}'")
    for m in expect.get("must_not", []):
        if m.lower() in low:
            fails.append(f"says '{m}'")
    if expect.get("min_sources") and last.count("📄") + last.count(";") < expect["min_sources"] - 1 and "Sources" not in last and "Madogara" not in last:
        fails.append("fewer sources than asked")
    return fails


ROUTE_OF = {"schools": ("search",), "facilities": ("facility",), "nearest": ("facility",), "budget": ("search", "lines", "query_budget", "analysis", "category", "topic"),
            "budget_lga": ("analysis",), "place": ("place",), "nema": ("search", "topic"), "documents": ("search", "lines", "query_budget", "topic", "analysis"),
            "surveys": ("search", "topic"), "deep": ("deep", "search"), "conversation": ("conversation", "menu")}


def cause(qn: dict, fails: list[str], traces: list[dict], replies: list[str]) -> str:
    """One cause per failed question, from the trace rows the question made and the reply."""
    if not fails:
        return ""
    if fails == ["silence"]:
        return "silence"
    last_t = traces[-1] if traces else {}
    path = last_t.get("path", "") or ""
    feature = qn["feature"]
    if feature == "emergency":
        return fails[0]
    if feature == "conversation":
        return "conversation not handled"
    if qn["difficulty"] == "multi" and len(traces) >= 2:
        u = (traces[-1].get("understanding") or {})
        if u.get("kind") not in ("follow_up", "correction", "clarification") or (qn.get("lga") and qn["lga"].lower() not in (u.get("restatement") or "").lower()):
            return "lost follow-up"
    allowed = ROUTE_OF.get(feature, ())
    if allowed and path and not any(path.startswith(p) for p in allowed):
        return f"wrong route ({path})"
    if any(f.startswith("double count") for f in fails):
        return "double count"
    if any("not in the first line" in f for f in fails):
        return "total not leading"
    check = last_t.get("check_result") or ""
    if any(f == "not found" for f in fails):
        return "check sent a right answer back" if check == "partial" else "not found (missing pages)"
    if any(f.startswith("missing figure") or f.startswith("none of") or f.startswith("missing amount") for f in fails):
        if qn["difficulty"] == "multi" and len(fails) == 1 and "IQS" in json.dumps(qn["expect"]):
            return "part dropped (state-level part)"
        return "wrong figure (check passed it)" if check == "passed" else "wrong figure"
    if any(f.startswith("says") for f in fails):
        return "forbidden wording"
    if qn["lang"] == "ha" and not re.search(r"\b(?:na|da|a|ne|ce|ta|ya|wannan|kasafin|makarantu|mutane)\b", (replies[-1] or "").lower()):
        return "bad Hausa"
    return fails[0]


async def run_set(round_n: int, which: str, chunk_s: float, only: set[str]) -> None:
    import live_smoke as L
    from app.data_rights import delete_user_data
    from app.geo.location import memory
    from app.users import user_key
    from app.whatsapp import webhook
    base = get_settings()
    qs = json.loads((round_dir(round_n) / "questions.json").read_text(encoding="utf-8"))["questions"]
    qs = [x for x in qs if (which == "all" or x["set"] == which) and (not only or x["id"] in only)]
    out = round_dir(round_n) / f"results-{which}.jsonl"
    done = {r["id"] for r in read_jsonl(out)}
    todo = [x for x in qs if x["id"] not in done]
    log(f"round {round_n} {which}: {len(todo)} to run, {len(done)} done")
    senders = [f"2340000001{n:03d}" for n in range(1, 400)]
    s = base.model_copy(update={"kasafi_open_access": True,
                                "kasafi_exempt_numbers": ",".join([base.kasafi_exempt_numbers, *senders]).strip(",")})
    webhook.get_settings = lambda: s
    webhook.WhatsAppClient = L.Capture
    store = webhook.get_store()
    t_start = time.perf_counter()
    for qn, sender in zip(todo, senders):
        if chunk_s and elapsed_s(t_start) > chunk_s:
            print(f"NEXT {qn['id']}", flush=True)
            return
        try:
            guard()
        except CapReached as e:
            log(f"STOP: {e}")
            print("CAP", flush=True)
            return
        key = user_key(sender, s)
        delete_user_data(sender, store=store, settings=s)
        memory.forget(key)
        store.create(key, qn["lang"])
        store.give_consent(key)
        if (place := qn.get("place")) and place.get("lga_pcode"):
            store.set_last_lga(key, place["lga_pcode"])
        usd0 = usage.total_dollars(s)
        t0 = time.perf_counter()
        replies: list[str] = []
        with psycopg.connect(s.db_url()) as conn:
            since = conn.execute("SELECT now()").fetchone()[0]
        try:
            for turn in qn["turns"]:
                if isinstance(turn, dict) and turn.get("pin"):
                    msg = L.message(sender, pin=tuple(turn["pin"]))
                else:
                    msg = L.message(sender, turn)
                reply, _ = await L.turn(msg)
                replies.append(reply)
        except Exception as e:          # noqa: BLE001 - one question's crash is its own failure
            replies.append(f"[error {type(e).__name__}: {e}]"[:300])
        finally:
            delete_user_data(sender, store=store, settings=s)
            memory.forget(key)
        secs = time.perf_counter() - t0
        usd = usage.total_dollars(s) - usd0
        charge(usd)
        with psycopg.connect(s.db_url()) as conn:
            rows = conn.execute("SELECT path, outcome, trace FROM traces WHERE created_at >= %s ORDER BY id",
                                (since,)).fetchall()
        traces = []
        for path, outcome, t in rows:
            u = t.get("understanding") or {}
            traces.append({"path": path, "outcome": outcome, "check_result": t.get("check_result", ""),
                           "understanding": {k: u.get(k) for k in ("kind", "capability", "level", "name", "restatement")},
                           "checks": [c.get("verdict") for c in (t.get("check") or [])]})
        last = replies[-1] if replies else ""
        body = last.split("\n---\n")
        answer = "\n---\n".join(b for b in body if not b.startswith(("🔎", "⏳")) and b.strip() not in ("Anything else?",))
        fails = score(qn["expect"], answer, [answer])
        why = cause(qn, fails, traces, [answer])
        row = {"id": qn["id"], "set": qn["set"], "feature": qn["feature"], "difficulty": qn["difficulty"], "lang": qn["lang"],
               "ok": not fails, "fails": fails, "cause": why, "seconds": round(secs, 1), "usd": round(usd, 4),
               "turns": qn["turns"], "expect": qn["expect"], "reply": answer[:4000], "traces": traces}
        append_jsonl(out, row)
        log(f"{qn['id']:<28} {'ok ' if not fails else 'WRONG'} {secs:5.1f}s ${usd:.3f} {why} {'; '.join(fails)[:100]}")
    rows = read_jsonl(out)
    ok = sum(1 for r in rows if r["ok"])
    log(f"round {round_n} {which}: {ok}/{len(rows)} right, ${sum(r['usd'] for r in rows):.2f}")
    print("DONE", flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--round", type=int, required=True)
    ap.add_argument("--set", default="fix", choices=("fix", "heldout", "all"))
    ap.add_argument("--chunk-s", type=float, default=540)
    ap.add_argument("--only", default="")
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    for k, v in (("KASAFI_BATCH_PROVIDER", "fireworks"), ("KASAFI_UNDERSTAND_PROVIDER", "open")):
        if os.environ.get(k) != v:
            raise SystemExit(f"{k}={v} must be set (Muse Spark Open only)")
    meta_guard()
    asyncio.run(run_set(a.round, a.set, a.chunk_s, {x.strip() for x in a.only.split(",") if x.strip()}))
    sys.stdout.flush()
    os._exit(0)
