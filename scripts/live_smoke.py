"""Live smoke test, run inside the server container after every deploy (deploy/deploy.sh): conversations through the
real webhook reply path (app/whatsapp/webhook.py `_reply`: duplicate suppression, the conversation handler, the
understanding step, the routes, delivery) with real model calls, the real database and ORS. Only the WhatsApp send is
replaced: what would go to the phone is printed. The recorded replays in the unit and e2e suites can't catch a route
that ignores a live reading (2 Nov: 'Who are you?' read as chitchat went to the document search).

    docker compose exec -T api python scripts/live_smoke.py [--set deploy|full]

--set deploy (default, ~$0.01): "Who are you?", "Kai wanene?", a cold "But uduth is closer to me" (Wamakko on file).
--set full (~$0.15): the 8 conversations of the 2 Nov fix (pin + nearest hospital + correction, pin + flood history,
an English and a Hausa budget question, thanks), then the menu: "menu" -> tap "Budget for my area" -> share the
location -> the answer (the acknowledgement never asks "What would you like to know?"), the same for "Rain and
flood outlook", and "zaɓi" in Hausa.
--set emergency (~$0.15): the 40 off-list cases of evals/emergency (x01-x20 must fire: a miss fails; y01-y20 must
not: a false alarm is reported, not failed).

Senders are synthetic numbers (2340000000…, not valid Nigerian numbers), consented for the run and deleted after it
(DELETE MY DATA's own function). Traces are written as for any user. Exit 1 when a check fails.
"""

from __future__ import annotations

import argparse
import asyncio
import itertools
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.agent.answer import NOT_FOUND  # noqa: E402
from app.config import get_settings  # noqa: E402
from app.data_rights import delete_user_data  # noqa: E402
from app.geo.location import memory  # noqa: E402
from app.users import user_key  # noqa: E402
from app.whatsapp import webhook  # noqa: E402

PIN = (13.045, 5.155)            # the understanding eval's pin in Wamakko (tests/test_understanding.py)
_ids = itertools.count(1)


def never_not_found(r: str) -> str:
    return "" if all(v not in r for v in NOT_FOUND.values()) else "'couldn't find' for a message that isn't a question"


def no_documents(r: str) -> str:
    return never_not_found(r) or ("" if "Checking the documents" not in r and "Ina duba takardu" not in r
                                  else "went to the document search")


def facility_checked(r: str) -> str:
    return no_documents(r) or ("" if "Usman" in r and ("closer" in r or "closest" in r) else "no facility check")


def answered(r: str) -> str:
    return never_not_found(r) or ("" if len(r) > 40 else "no answer")


def a_list(r: str) -> str:
    return "" if "[list «" in r else "no menu list"


def asks_location(r: str) -> str:
    return "" if "[location request]" in r else "no location request"


def pin_answers(r: str) -> str:
    """A pin that something waited for: the acknowledgement never asks, and the waiting request is answered."""
    if any(w in r for w in ("What would you like to know", "Me kuke so ku sani")):
        return "the acknowledgement asked instead of answering"
    lines = [x for x in r.splitlines() if x.strip() and not x.startswith(("📍", "Kasafi will use your location"))]
    return "" if len(" ".join(lines)) > 80 else "no answer after the acknowledgement"


def flood_record(r: str) -> str:
    return "" if any(w in r.lower() for w in ("flood", "water", "ambaliya", "satellite")) else "no flood record"


# (name, language, place on file: None | 'lga' | 'pin', [(message, check)])
DEPLOY = [
    ("who are you", "en", None, [("Who are you?", no_documents)]),
    ("kai wanene", "ha", None, [("Kai wanene?", no_documents)]),
    ("cold uduth claim", "en", "lga", [("But uduth is closer to me", facility_checked)]),
]
FULL = DEPLOY + [
    ("pin, nearest hospital, correction", "en", "pin", [("Nearest hospital", answered),
                                                         ("But Uduth is closer to me", facility_checked)]),
    ("pin, flood history", "en", "pin", [("Has this land ever flooded?", flood_record)]),
    ("budget", "en", None, [("How much is allocated to the Ministry of Health in the 2026 budget?", answered)]),
    ("budget in Hausa", "ha", None, [("Nawa aka ware wa ilimi a kasafin 2026?", answered)]),
    ("thanks", "en", None, [("thanks", no_documents)]),
    ("menu, budget row, pin", "en", None, [("menu", a_list), ("[row:menu_budget]", asks_location),
                                           ("[pin]", pin_answers)]),
    ("menu, outlook row, pin", "en", None, [("[row:menu_outlook]", asks_location), ("[pin]", pin_answers)]),
    ("menu in Hausa", "ha", None, [("zaɓi", a_list)]),
]


def emergency_set() -> list:
    """The off-list emergency cases (evals/emergency/cases.json, x01-x20 must fire, y01-y20 must not): through the
    real handler, with the classifier and the understanding step live. A miss fails; a false alarm is reported."""
    import json
    cases = json.loads((Path(__file__).resolve().parents[1] / "evals" / "emergency" / "cases.json")
                       .read_text(encoding="utf-8"))

    def fires(r: str) -> str:
        return "" if r.startswith("🚨") else "MISSED EMERGENCY"

    def quiet(r: str) -> str:
        return "false alarm" if r.startswith("🚨") else ""
    return ([(c["id"], c["lang"], None, [(c["text"], fires)]) for c in cases["must_fire"] if c.get("set") == "off_list"]
            + [(c["id"], c["lang"], None, [(c["text"], quiet)]) for c in cases["must_not"]
               if c.get("set") == "off_list"])


class Capture:
    """Stands in for WhatsAppClient: what would be sent is kept, nothing leaves the server."""
    sent: list[str] = []

    async def send_text(self, to, body):
        Capture.sent.append(body)

    async def send_buttons(self, to, body, buttons):
        Capture.sent.append(f"{body}\n[buttons: {', '.join(t for _, t in buttons)}]")

    async def send_location_request(self, to, body):
        Capture.sent.append(f"{body}\n[location request]")

    async def send_list(self, to, body, button, sections, header=""):
        rows = [f"  {r['id']}: {r['title']} — {r.get('description', '')}" for s in sections for r in s["rows"]]
        Capture.sent.append(f"{body}\n[list «{button}»]\n" + "\n".join(rows))

    async def mark_typing(self, message_id):
        Capture.sent_typing = getattr(Capture, "sent_typing", 0) + 1

    async def send_location(self, to, latitude, longitude, name="", address=""):
        Capture.sent.append("[a location pin]")

    async def send_image(self, to, jpeg, caption=""):
        Capture.sent.append(f"[image] {caption}")

    async def send_document(self, to, data, filename, caption=""):
        Capture.sent.append(f"[document {filename}] {caption}")

    async def send_template(self, to, name, lang, values):
        Capture.sent.append(f"[template {name}]")

    async def download_media(self, media_id, *, max_bytes=0):
        return b""

    async def aclose(self):
        return None


def message(sender: str, body: str | None = None, pin: tuple | None = None) -> dict:
    base = {"from": sender, "id": f"wamid.smoke{int(time.time())}{next(_ids)}"}
    if body == "[pin]":
        pin = PIN
    elif body and body.startswith("[row:"):            # a tap on a menu row
        rid = body[5:-1]
        return {**base, "type": "interactive", "interactive": {"type": "list_reply",
                                                               "list_reply": {"id": rid, "title": rid}}}
    if pin:
        return {**base, "type": "location", "location": {"latitude": pin[0], "longitude": pin[1]}}
    return {**base, "type": "text", "text": {"body": body}}


async def turn(msg: dict) -> tuple[str, float]:
    Capture.sent = []
    t0 = time.perf_counter()
    await webhook._reply([msg])
    return "\n---\n".join(Capture.sent), time.perf_counter() - t0


async def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", default="deploy", choices=("deploy", "full", "emergency"))
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    base = get_settings()
    senders = [f"23400000000{n:02d}" for n in range(1, 60)]
    # only for these synthetic senders and only in this process: allowed, no daily limits
    s = base.model_copy(update={"kasafi_open_access": True,
                                "kasafi_exempt_numbers": ",".join([base.kasafi_exempt_numbers, *senders]).strip(",")})
    webhook.get_settings = lambda: s
    webhook.WhatsAppClient = Capture
    store = webhook.get_store()
    failed = alarms = 0
    chosen = {"deploy": DEPLOY, "full": FULL}.get(a.set) or emergency_set()
    for (name, lang, place, turns), sender in zip(chosen, senders):
        key = user_key(sender, s)
        delete_user_data(sender, store=store, settings=s)
        memory.forget(key)
        store.create(key, lang)
        store.give_consent(key)
        print(f"\n=== {name} ({lang}{', ' + place + ' on file' if place else ''})", flush=True)
        try:
            if place == "lga":
                store.set_last_lga(key, "NG034021")                     # Wamakko
            if place == "pin":
                reply, secs = await turn(message(sender, pin=PIN))
                print(f"> [pin]\n{reply}\n({secs:.1f}s)", flush=True)
            for body, check in turns:
                reply, secs = await turn(message(sender, body))
                problem = "silence" if not reply.strip() else check(reply)
                alarm = problem == "false alarm"              # acceptable in small numbers: reported, not failed
                failed += bool(problem) and not alarm
                alarms += alarm
                mark = ("NOTE: " if alarm else "FAIL: ") + problem if problem else "ok"
                print(f"> {body}\n{reply}\n({secs:.1f}s) {mark}", flush=True)
        finally:
            delete_user_data(sender, store=store, settings=s)
            memory.forget(key)
    print(f"\nlive smoke ({a.set}): {'all ok' if not failed else f'{failed} failed'}"
          f"{f', {alarms} false alarm(s)' if alarms else ''}", flush=True)
    return 1 if failed else 0


if __name__ == "__main__":
    code = asyncio.run(main())
    sys.stdout.flush()
    os._exit(code)              # model clients can hang at interpreter shutdown (scratch-script lesson)
