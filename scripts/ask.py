"""Ask Kasafi one question for demo and promo content, and keep exactly what WhatsApp would have shown.

    python scripts/ask.py "<question>" [--pin LAT,LON] [--lang ha|en] [--voice path.ogg] [--history turns.json] --out <file.json>

The question goes through the same reply path as a real WhatsApp message (app/whatsapp/webhook.py `_reply`: the
conversation handler, understanding, routing, the answer check, page crops), on the LIVE server, against its library
and with its own keys and models: this script sends itself to the running container over ssh and reads the result back.
It needs only the Python standard library and the `vps` ssh alias on this machine; no secret is read or printed here.

What differs from a real message, and nothing else:
- Nothing goes to WhatsApp: what would be sent is captured.
- The sender is a test user that is never stored in user records: it lives in a throwaway in-memory store and in this
  one process's memory (consent, language, location, follow-ups), all gone when the command ends. Each call is a new
  conversation.

What it does leave on the server, as any question does: an answer trace (no user ID; that is the trace id reported), the
model spend (counted against the daily cap and the Meta credit), and, if the question needs a document the library
doesn't hold, a live fetch that indexes it, or a review-queue entry.

The JSON: question (the transcript for a voice note), messages (each one in order, as WhatsApp would show it, with
`at_s`), reply_text, sources and pages, page_crops (image files saved next to the JSON), images (maps), timings, trace
id, cost. Costs real money: about $0.002 for a greeting, $0.05 for a budget question, $0.20-0.30 for a long analysis.
"""

from __future__ import annotations

import argparse
import asyncio
import base64
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

MARKER = "ASK_RESULT "
SENDER = "2340000000098"          # synthetic (not a valid Nigerian number), and never sent to: see Capture
MAX_VOICE_BYTES = 16 * 1024 * 1024         # WhatsApp's own limit for audio
REMOTE_LIMIT_S = 900              # a turn with a document fetch runs up to 5 minutes, then its crops
LATE_DELIVERY_S = 330             # an answer delivered after the turn (a long fetch)
HOST = os.environ.get("KASAFI_ASK_HOST", "vps")
CONTAINER = os.environ.get("KASAFI_ASK_CONTAINER", "kasafi-agent-api")
WINDOWS_SSH = Path("C:/Windows/System32/OpenSSH/ssh.exe")     # the one that can use the Windows ssh-agent


# --- on the server ---------------------------------------------------------------------------------------------------

def _no_user_store(real):
    """The user store for this call: in memory, gone with the process, so the test user is never in user records. Only
    the day's spend is the real one (the service's daily cap covers these calls too; it has no user in it)."""
    from app.users import UserStore

    class NoUserStore(UserStore):
        def __init__(self) -> None:
            super().__init__(":memory:")

        def spent_today(self) -> float:
            return real().spent_today()

        def add_spend(self, usd: float) -> None:
            real().add_spend(usd)
    return NoUserStore()


class Capture:
    """Stands in for WhatsAppClient: what would be sent is kept, nothing leaves the server."""
    sent: list[dict] = []
    t0 = 0.0
    crop_of: dict[str, object] = {}     # a crop's caption -> its request, while the evidence images are being sent
    voice = b""

    def __init__(self, *a, **k) -> None:
        pass

    def _keep(self, kind: str, **fields) -> None:
        Capture.sent.append({"kind": kind, "at_s": round(time.perf_counter() - Capture.t0, 1), **fields})

    async def send_text(self, to, body):
        self._keep("text", text=body)

    async def send_buttons(self, to, body, buttons):
        self._keep("buttons", text=body, buttons=[t for _, t in buttons])

    async def send_location_request(self, to, body):
        self._keep("location_request", text=body)

    async def send_list(self, to, body, button, sections, header=""):
        self._keep("list", text=body, button=button, header=header,
                   rows=[{"title": r.get("title", ""), "description": r.get("description", "")}
                         for s in sections for r in s.get("rows", [])])

    async def send_location(self, to, latitude, longitude, name="", address=""):
        self._keep("location", latitude=latitude, longitude=longitude, name=name, address=address)

    async def send_image(self, to, jpeg, caption=""):
        req = Capture.crop_of.get(caption)
        extra = {"doc_id": req.doc_id, "title": req.title, "page": req.page, "figure": req.figure} if req else {}
        self._keep("crop" if req else "image", text=caption, data=base64.b64encode(jpeg).decode(), ext="jpg", **extra)

    async def send_document(self, to, data, filename, caption=""):
        self._keep("document", text=caption, data=base64.b64encode(data).decode(), ext=filename.rsplit(".", 1)[-1],
                   filename=filename)

    async def send_template(self, to, name, lang, values):
        self._keep("template", text=name)

    async def mark_typing(self, message_id):
        return None

    async def download_media(self, media_id, *, max_bytes=0):
        return Capture.voice

    async def aclose(self):
        return None


def _trace_rows(settings, before: int, texts: str) -> tuple[list[dict], str]:
    """This call's trace rows: those written since it started whose reply was sent here. Other users may be asking at
    the same moment, so when no reply matches (a multi-part answer is shortened when sent), every new row is given and
    `trace_match` says 'time'."""
    import psycopg
    with psycopg.connect(settings.db_url(), connect_timeout=5) as conn:
        rows = conn.execute("SELECT id, outcome, path, seconds, trace, answer FROM traces WHERE id > %s ORDER BY id",
                            (before,)).fetchall()
    out = [{"id": r[0], "outcome": r[1], "path": r[2], "seconds": float(r[3] or 0), "trace": r[4], "answer": r[5] or ""}
           for r in rows]
    same = [r for r in out if r["answer"].strip() and r["answer"].strip()[:60] in texts]
    return (same, "text") if same else (out, "time")


def _cost(settings) -> dict:
    from app import usage
    prices = usage.prices(settings)
    usd = lambda provider, t: usage.dollars(t, *prices[provider]) if provider in prices else 0.0  # noqa: E731
    return {"usd": round(usage.total_dollars(settings), 4),
            "by_provider": {p: {"calls": t.calls, "usd": round(usd(p, t), 4)} for p, t in sorted(usage.chat.items())},
            "by_stage": {k: {"calls": t.calls, "usd": round(usd(k.split("/")[0], t), 4)}
                         for k, t in sorted(usage.by_stage.items())},
            "counts": dict(usage.counts)}


async def run_inside(job: dict, settings=None) -> dict:
    """One question through the live reply path, as the test user. Returns the result (images as base64)."""
    from app import usage
    from app.config import get_settings
    from app.evidence import crops as crops_module
    from app.language import detect_language
    from app.users import get_store, user_key
    from app.whatsapp import client as client_module
    from app.whatsapp import webhook

    base = settings or get_settings()
    settings = base.model_copy(update={"kasafi_open_access": True, "kasafi_exempt_numbers": ",".join(
        x for x in (base.kasafi_exempt_numbers, SENDER) if x)})
    store = _no_user_store(get_store)
    webhook.get_settings = lambda: settings
    webhook.get_store = lambda: store
    webhook.WhatsAppClient = Capture
    client_module.WhatsAppClient = Capture      # an answer delivered after the turn makes its own client

    real_evidence = crops_module.send_evidence

    async def send_evidence(wa, to, requests, lang, settings_):
        Capture.crop_of = {r.caption(lang): r for r in requests}
        return await real_evidence(wa, to, requests, lang, settings_)
    webhook.send_evidence = send_evidence

    question, lang = job.get("question") or "", job.get("lang")
    key = user_key(SENDER, settings)
    store.create(key, lang or (detect_language(question) if question else None))
    store.give_consent(key)
    if lang:
        store.set_lang(key, lang)
    for turn in job.get("history") or []:      # earlier turns of this conversation (the in-memory store only)
        store.add_turn(key, lang or "en", turn["question"], turn["answer"], [], "", "")
    Capture.voice = base64.b64decode(job.get("voice") or "")
    Capture.sent = []
    usage.reset()

    before = 0
    if settings.has_database:
        import psycopg
        with psycopg.connect(settings.db_url(), connect_timeout=5) as conn:
            before = conn.execute("SELECT coalesce(max(id), 0) FROM traces").fetchone()[0]

    stamp = time.time_ns()
    after_pin: list[dict] = []
    if job.get("pin"):
        Capture.t0 = time.perf_counter()
        await webhook._reply([{"from": SENDER, "id": f"wamid.ask{stamp}pin", "type": "location",
                               "location": {"latitude": job["pin"][0], "longitude": job["pin"][1]}}])
        after_pin, Capture.sent = Capture.sent, []
    msg = {"from": SENDER, "id": f"wamid.ask{stamp}"}
    if job.get("voice"):
        msg.update(type="audio", audio={"id": "ask-voice", "mime_type": "audio/ogg; codecs=opus", "voice": True})
    else:
        msg.update(type="text", text={"body": question})
    Capture.t0 = time.perf_counter()
    await webhook._reply([msg])
    total = time.perf_counter() - Capture.t0
    # an answer that outlives the turn (a long document fetch) is delivered by a task of its own
    others = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    if others:
        await asyncio.wait(others, timeout=LATE_DELIVERY_S)
        total = max(total, max((m["at_s"] for m in Capture.sent), default=0.0))

    turns = store.recent_turns(key)
    last = turns[-1] if turns else {}
    texts = "\n".join(m.get("text", "") for m in Capture.sent)
    traces, match = _trace_rows(settings, before, texts) if settings.has_database else ([], "")
    if settings.has_database:
        try:
            from app import spend
            with psycopg.connect(settings.db_url(), connect_timeout=5) as conn:
                spend.flush(conn)                # the Meta credit guard's ledger: this process ends now
        except Exception:                        # noqa: BLE001 - the ledger is never worth losing the answer
            pass
    return {"heard": last.get("question", "") if job.get("voice") else "", "lang": last.get("lang") or lang or "",
            "before_question": after_pin, "messages": Capture.sent, "sources": last.get("sources") or [],
            "total_s": round(total, 1), "traces": traces, "trace_match": match, "cost": _cost(settings),
            "server_commit": os.environ.get("KASAFI_COMMIT", "unknown")}


def _inside(payload: str) -> int:
    import logging
    logging.disable(logging.INFO)              # stderr stays with this process; only warnings and worse reach it
    sys.path.insert(0, os.getcwd())
    result = asyncio.run(run_inside(json.loads(base64.b64decode(payload))))
    print(MARKER + base64.b64encode(json.dumps(result, default=str).encode()).decode(), flush=True)
    sys.stdout.flush()
    os._exit(0)                                # model clients can hang at interpreter shutdown


# --- on this machine -------------------------------------------------------------------------------------------------

_SECRETISH = re.compile(r"(?i)(?:bearer\s+\S+|\b(?:sk|fw|key|token)[-_][\w-]{8,}|\b[a-z]+ql(?:\+\w+)?://\S+|\b[\w-]{32,}\b|"
                        r"\b\d{1,3}(?:\.\d{1,3}){3}\b)")


def scrub(text: str) -> str:
    """Anything from the server that might carry a key, a database address or the server's IP, made safe to print."""
    return _SECRETISH.sub("[removed]", text or "")


def parse_pin(value: str) -> list[float]:
    try:
        lat, lon = (float(x) for x in value.split(","))
    except ValueError:
        raise argparse.ArgumentTypeError("--pin takes LAT,LON, for example 13.0589,5.1673") from None
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        raise argparse.ArgumentTypeError("--pin is outside the valid range of latitude and longitude")
    return [lat, lon]


def parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description="Ask Kasafi one question through the live reply path, as a test user "
                                             "(never stored in user records). Costs real model money.")
    ap.add_argument("question", nargs="?", default="", help="the message; optional with --voice")
    ap.add_argument("--pin", type=parse_pin, help="LAT,LON: shared as a WhatsApp location first")
    ap.add_argument("--lang", choices=("ha", "en"), help="the user's saved language (default: detected, as on first "
                                                         "contact; a voice note is answered in the language spoken)")
    ap.add_argument("--voice", type=Path, help="a voice note (.ogg, as WhatsApp sends it): sent instead of the text")
    ap.add_argument("--history", type=Path, help="a JSON file of earlier turns, [{\"question\": ..., \"answer\": ...}], "
                                                 "oldest first: for a follow-up (each call is otherwise a new conversation)")
    ap.add_argument("--out", type=Path, required=True, help="the JSON file; images are saved next to it")
    return ap


def remote_command() -> list[str]:
    ssh = str(WINDOWS_SSH) if WINDOWS_SSH.exists() else "ssh"
    return [ssh, "-o", "BatchMode=yes", "-o", "ServerAliveInterval=15", HOST,
            f"docker exec -i -e PYTHONUNBUFFERED=1 {CONTAINER} python -u -"]


def run_remote(job: dict) -> dict:
    """This file, sent to the container's Python on stdin, so the job is never in a command line."""
    payload = base64.b64encode(json.dumps(job).encode()).decode()
    program = f"{Path(__file__).read_text(encoding='utf-8')}\n\n_inside({payload!r})\n"
    try:
        p = subprocess.run(remote_command(), input=program.encode(), capture_output=True, timeout=REMOTE_LIMIT_S)
    except subprocess.TimeoutExpired:
        raise SystemExit(f"ask: no result from the server within {REMOTE_LIMIT_S} s") from None
    for line in p.stdout.decode("utf-8", "replace").splitlines():
        if line.startswith(MARKER):
            return json.loads(base64.b64decode(line[len(MARKER):]))
    tail = "\n".join(p.stderr.decode("utf-8", "replace").splitlines()[-6:])
    raise SystemExit(f"ask: the server gave no result (exit code {p.returncode}).\n{scrub(tail)}")


def write_result(result: dict, out: Path, question: str, job: dict) -> dict:
    """The JSON, and each image next to it; what the command reports is what is on disk."""
    out = out.resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    page_crops, images, n = [], [], 0

    def saved(messages: list[dict]) -> list[dict]:
        nonlocal n
        kept = []
        for m in messages:
            m = dict(m)
            if data := m.pop("data", None):
                n += 1
                kind = m["kind"]
                path = out.with_name(f"{out.stem}-{n:02d}-{kind}.{m.pop('ext', 'jpg')}")
                path.write_bytes(base64.b64decode(data))
                m.update(file=path.name, path=str(path))
                if kind == "crop":
                    page_crops.append({k: m.get(k) for k in ("file", "path", "doc_id", "title", "page", "figure")}
                                      | {"caption": m.get("text", "")})
                elif kind == "image":
                    images.append({"file": m["file"], "path": m["path"], "caption": m.get("text", "")})
            kept.append(m)
        return kept

    before = saved(result.get("before_question") or [])
    messages = saved(result.get("messages") or [])
    traces = result.get("traces") or []
    sources, seen = [], set()
    for s in result.get("sources") or []:
        ref = (s.get("doc_id"), s.get("page"))
        if ref not in seen:
            seen.add(ref)
            sources.append({k: s.get(k) for k in ("doc_id", "title", "page", "series", "edition") if s.get(k) is not None})
    doc = {
        "question": question or result.get("heard") or "",
        "heard": result.get("heard") or "",
        "lang": result.get("lang") or "",
        "pin": job.get("pin"),
        "voice": bool(job.get("voice")),
        "before_question": before,        # the reply to the shared pin, when --pin was given
        "messages": messages,
        "reply_text": "\n\n".join(m["text"] for m in messages if m.get("text") and m["kind"] not in ("crop", "image")),
        "sources": sources,
        "page_crops": page_crops,
        "images": images,
        "timings": {"total_s": result.get("total_s"), "first_message_s": messages[0]["at_s"] if messages else None,
                    "last_message_s": messages[-1]["at_s"] if messages else None,
                    "pipeline": (traces[-1].get("trace") or {}).get("timings") if traces else None},
        "trace_id": traces[-1]["id"] if traces else None,
        "trace_ids": [t["id"] for t in traces],
        "trace_match": result.get("trace_match") or "",
        "outcome": traces[-1].get("outcome") if traces else None,
        "check": (traces[-1].get("trace") or {}).get("check_result") if traces else None,
        "cost": result.get("cost") or {},
        "server_commit": result.get("server_commit") or "",
    }
    out.write_text(json.dumps(doc, indent=1, ensure_ascii=False), encoding="utf-8")
    return doc


def report(doc: dict, out: Path) -> str:
    cost = doc["cost"]
    lines = [f"Saved {out}", f"Reply: {len(doc['messages'])} message(s), {len(doc['page_crops'])} page crop(s), "
             f"{len(doc['images'])} other image(s), {len(doc['sources'])} source page(s), in {doc['timings']['total_s']} s",
             f"Trace {doc['trace_id']} ({doc['outcome']}, check: {doc['check']}), server at {doc['server_commit'][:7]}",
             f"Cost of this call: ${cost.get('usd', 0):.4f}"]
    lines += [f"  {k}: {v['calls']} call(s), ${v['usd']:.4f}" for k, v in (cost.get("by_stage") or {}).items()]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = parser()
    a = ap.parse_args(argv)
    if not a.question.strip() and not a.voice:
        ap.error("give a question, or --voice")
    job: dict = {"question": a.question, "lang": a.lang, "pin": a.pin}
    if a.history:
        try:
            job["history"] = [{"question": str(t["question"]), "answer": str(t["answer"])}
                              for t in json.loads(a.history.read_text(encoding="utf-8"))]
        except (OSError, ValueError, KeyError, TypeError):
            ap.error('--history: a JSON file of [{"question": ..., "answer": ...}]')
    if a.voice:
        if not a.voice.is_file():
            ap.error(f"--voice: no such file: {a.voice}")
        if a.voice.stat().st_size > MAX_VOICE_BYTES:
            ap.error("--voice: larger than WhatsApp's 16 MB limit")
        job["voice"] = base64.b64encode(a.voice.read_bytes()).decode()
    print("Asking Kasafi on the live server (real model calls)…", flush=True)
    doc = write_result(run_remote(job), a.out, a.question, job)
    print(report(doc, a.out.resolve()))
    return 0


if __name__ == "__main__" and sys.argv[0] != "-":
    raise SystemExit(main())
