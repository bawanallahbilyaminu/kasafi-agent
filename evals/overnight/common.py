"""The overnight eval loop's shared state (3-4 Nov 2026): the state file, the hard caps enforced in code (Baseten
dollars for the night, the stop time), the progress log, and the Meta guard (no Meta call can spend: the key in
the environment is deliberately invalid, every Muse Spark client the app asks for is served by Muse Spark Open, and
any attempt that would still reach Meta is recorded and refused).

Files (evals/overnight/, outside the report):
  state.json          rounds done, spend, fixes kept or reverted, Meta attempts, the final comparison
  progress.log        one line per question and per phase: `tail -f evals/overnight/progress.log`
  rounds/r<N>/        questions.json (fix and held-out halves), results-<set>.jsonl (one line per question, resumable)
"""

from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

DIR = Path(__file__).parent
STATE = DIR / "state.json"
LOG = DIR / "progress.log"
ROUNDS = DIR / "rounds"
BASETEN_CAP_USD = 20.0
STOP_AT = (6, 30)            # local time (the laptop is on Lagos time, UTC+1)


class CapReached(RuntimeError):
    pass


def now() -> datetime:
    return datetime.now()


def stop_time() -> datetime:
    t = now()
    stop = t.replace(hour=STOP_AT[0], minute=STOP_AT[1], second=0, microsecond=0)
    if t.hour >= 12:                       # started in the evening: the stop is tomorrow morning
        stop += timedelta(days=1)
    return stop


def load_state() -> dict:
    if STATE.exists():
        return json.loads(STATE.read_text(encoding="utf-8"))
    return {"started": now().isoformat(timespec="minutes"), "spend_usd": 0.0, "rounds": [], "fixes": [],
            "meta_attempts": [], "final": {}, "last_round_done": 0}


def save_state(s: dict) -> None:
    STATE.write_text(json.dumps(s, indent=1, ensure_ascii=False, default=str), encoding="utf-8")


def log(line: str) -> None:
    stamp = now().strftime("%H:%M:%S")
    with LOG.open("a", encoding="utf-8") as f:
        f.write(f"{stamp} {line}\n")
    print(f"{stamp} {line}", flush=True)


def guard(extra_usd: float = 0.0) -> None:
    """Raise CapReached when the night's Baseten spend has reached the cap or the stop time has passed."""
    s = load_state()
    if s["spend_usd"] + extra_usd >= BASETEN_CAP_USD:
        raise CapReached(f"Baseten cap reached: ${s['spend_usd']:.2f} of ${BASETEN_CAP_USD:.0f}")
    if now() >= stop_time():
        raise CapReached(f"stop time {STOP_AT[0]:02d}:{STOP_AT[1]:02d} reached")


def charge(delta_usd: float, what: str = "") -> float:
    s = load_state()
    s["spend_usd"] = round(s["spend_usd"] + max(0.0, delta_usd), 4)
    save_state(s)
    return s["spend_usd"]


def record_meta_attempt(where: str) -> None:
    s = load_state()
    s["meta_attempts"].append({"at": now().isoformat(timespec="seconds"), "where": where})
    save_state(s)


def meta_guard() -> None:
    """No Meta call can spend tonight. The environment's META_API_KEY is deliberately invalid (checked here); every
    place the app asks for a Muse Spark client gets Muse Spark Open instead (app.providers.meta.MetaClient is
    replaced for this process); and the original client's chat() records the attempt and refuses without a network
    call, in case any code path kept a reference to it."""
    from app.providers import meta as meta_mod
    from app.providers.chat import ProviderError
    from app.providers.fireworks import BatchModel
    key = os.environ.get("META_API_KEY", "")
    if not key.startswith("invalid-key"):
        raise SystemExit("META_API_KEY must be the deliberately invalid key for the overnight loop")
    original = meta_mod.MetaClient

    async def refused(self, messages, *, model=None, **params):
        record_meta_attempt("MetaClient.chat (refused before any network call)")
        raise ProviderError("Meta", 401, "refused by the overnight Meta guard", "overnight_guard")
    original.chat = refused

    class OpenAsMeta(BatchModel):
        """Muse Spark Open standing in wherever the app asks for Muse Spark (same constructor shape)."""
        provider = "Muse Spark Open"

        def __init__(self, settings=None, *, timeout: float = 120.0, **kw):
            from app.config import get_settings
            super().__init__(settings or get_settings())
    meta_mod.MetaClient = OpenAsMeta


def question_hash_half(qid: str) -> str:
    """fix or heldout by the id's hash: a stable 50/50 split."""
    import hashlib
    return "fix" if int(hashlib.sha1(qid.encode()).hexdigest(), 16) % 2 == 0 else "heldout"


def round_dir(n: int) -> Path:
    d = ROUNDS / f"r{n}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(ln) for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]


def append_jsonl(path: Path, row: dict) -> None:
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False, default=str) + "\n")


def elapsed_s(t0: float) -> float:
    return time.perf_counter() - t0
