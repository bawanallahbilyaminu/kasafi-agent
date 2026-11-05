"""scripts/ask.py: one question through the real reply path as a test user, for demo and promo content."""

import asyncio
import base64
import importlib.util
import json
import re
import sqlite3
import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest

from app.agent import conversational as CV
from app.agent.understand import Understanding
from app.evidence.crops import CropRequest
from app.users import UserStore
from app.whatsapp import client as client_module
from app.whatsapp import conversation as C
from app.whatsapp import webhook
from app.whatsapp.conversation import Out
from tests.helpers import make_settings

SCRIPT = Path("scripts/ask.py")
spec = importlib.util.spec_from_file_location("ask_script", SCRIPT)
ask = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ask)
JPEG = b"\xff\xd8\xff-a-crop"


@pytest.fixture
def inside(monkeypatch, tmp_path):
    """The server side, with the real reply path and handler: a file as the service's real user store, no database."""
    real = UserStore(str(tmp_path / "real.db"))
    monkeypatch.setattr("app.users.get_store", lambda: real)
    for name in ("get_settings", "get_store", "WhatsAppClient", "send_evidence"):
        monkeypatch.setattr(webhook, name, getattr(webhook, name))
    monkeypatch.setattr(client_module, "WhatsAppClient", client_module.WhatsAppClient)
    s = make_settings(kasafi_understanding=False, kasafi_evidence_images=True)
    monkeypatch.setattr(s.__class__, "has_database", property(lambda self: False))

    async def reply(message, lang, history, place, settings, client_cls=None, name=""):
        return f"REPLY[{lang}] to {message}", "model"
    monkeypatch.setattr(CV, "reply", reply)
    yield s, real, tmp_path / "real.db"


def _rows(path, table):
    with sqlite3.connect(path) as db:
        return db.execute(f"SELECT count(*) FROM {table}").fetchone()[0]


def test_the_test_user_is_never_in_user_records_and_nothing_reaches_whatsapp(inside, monkeypatch) -> None:
    s, real, path = inside
    from app import usage
    usage.record_chat("meta", {"prompt_tokens": 1000, "completion_tokens": 1000})   # gone: a call starts at zero

    async def understood(*a, **k):
        return Understanding(kind="chitchat", capability="conversation", restatement="thanks")
    s = s.model_copy(update={"kasafi_understanding": True})
    monkeypatch.setitem(C.handle.__kwdefaults__, "understand_fn", understood)
    r = asyncio.run(ask.run_inside({"question": "Thank you", "lang": "en"}, s))
    assert [m["kind"] for m in r["messages"]] == ["text"] and r["messages"][0]["text"] == "REPLY[en] to Thank you"
    assert r["cost"]["usd"] == 0 and r["lang"] == "en"
    for table in ("users", "turns", "usage", "alert_subs"):
        assert _rows(path, table) == 0, table
    # the real client can't be reached from here: the module's name is the capture, in the handler's late path too
    assert webhook.WhatsAppClient is ask.Capture and client_module.WhatsAppClient is ask.Capture


def test_the_days_spend_still_counts_against_the_services_cap(inside) -> None:
    s, real, path = inside
    store = ask._no_user_store(lambda: real)
    store.add_spend(0.25)
    assert real.spent_today() == 0.25 and store.spent_today() == 0.25
    store.create("k", "en")
    assert _rows(path, "users") == 0


def test_a_pin_goes_first_and_every_message_is_kept_in_order_with_its_crops(inside, monkeypatch) -> None:
    s, real, path = inside
    req = CropRequest(1, "budget-2026", "FY 2026 Budget", 17, "3,589,478,500.56")
    seen: list = []

    async def fake_handle(msg, client, *, store, settings, notify):
        seen.append(msg)
        if msg["type"] == "location":
            return [Out("📍 Got it: your pin is in Wamakko.")]
        await notify(Out("🔎 Checking the documents…"))
        store.add_turn(store_key(settings), "en", msg["text"]["body"], "ans",
                       [{"doc_id": "budget-2026", "title": "FY 2026 Budget", "page": 17, "edition": "2026"},
                        {"doc_id": "budget-2026", "title": "FY 2026 Budget", "page": 17}], "", "")
        return [Out("₦3.59 billion.", crops=[req], lang="en"), Out("Anything else?", [("x", "Show working")], lang="en"),
                Out("A map", image=b"\xff\xd8map", lang="en")]

    def store_key(settings):
        from app.users import user_key
        return user_key(ask.SENDER, settings)

    async def fake_make(req_, settings):
        return JPEG
    monkeypatch.setattr(webhook, "handle", fake_handle)
    monkeypatch.setattr("app.evidence.crops.make_crop", fake_make)
    r = asyncio.run(ask.run_inside({"question": "How much?", "lang": "en", "pin": [13.05, 5.15]}, s))
    assert seen[0]["type"] == "location" and seen[0]["location"] == {"latitude": 13.05, "longitude": 5.15}
    assert seen[1]["text"]["body"] == "How much?" and seen[0]["id"] != seen[1]["id"]
    assert [m["text"] for m in r["before_question"]] == ["📍 Got it: your pin is in Wamakko."]
    kinds = [m["kind"] for m in r["messages"]]
    assert kinds == ["text", "text", "crop", "buttons", "image"]
    crop = r["messages"][2]
    assert crop["doc_id"] == "budget-2026" and crop["page"] == 17 and base64.b64decode(crop["data"]) == JPEG
    assert r["messages"][3]["buttons"] == ["Show working"]
    assert r["messages"][-1]["kind"] == "image" and "doc_id" not in r["messages"][-1]
    assert all(isinstance(m["at_s"], float) for m in r["messages"]) and len(r["sources"]) == 2


def test_a_voice_note_is_a_real_audio_message_and_the_transcript_is_reported(inside, monkeypatch) -> None:
    s, real, path = inside
    seen: dict = {}

    async def fake_handle(msg, client, *, store, settings, notify):
        seen["msg"], seen["audio"] = msg, await client.download_media(msg["audio"]["id"])
        from app.users import user_key
        store.add_turn(user_key(ask.SENDER, settings), "ha", "Nawa ne kasafin lafiya?", "ans", [], "", "")
        return [Out("Na ji: Nawa ne kasafin lafiya?", lang="ha")]
    monkeypatch.setattr(webhook, "handle", fake_handle)
    r = asyncio.run(ask.run_inside({"voice": base64.b64encode(b"OggS-note").decode()}, s))
    assert seen["msg"]["type"] == "audio" and seen["audio"] == b"OggS-note"
    assert r["heard"] == "Nawa ne kasafin lafiya?" and r["lang"] == "ha"


def test_earlier_turns_reach_the_handler_and_only_the_throwaway_store(inside, monkeypatch) -> None:
    s, real, path = inside
    seen: dict = {}

    async def fake_handle(msg, client, *, store, settings, notify):
        from app.users import user_key
        seen["turns"] = store.recent_turns(user_key(ask.SENDER, settings))
        return [Out("ok", lang="en")]
    monkeypatch.setattr(webhook, "handle", fake_handle)
    history = [{"question": "How many schools are in Dange Shuni", "answer": "91 public primary schools."}]
    asyncio.run(ask.run_inside({"question": "I mean all the schools", "lang": "en", "history": history}, s))
    assert [(t["question"], t["answer"]) for t in seen["turns"]] == [("How many schools are in Dange Shuni",
                                                                     "91 public primary schools.")]
    assert _rows(path, "turns") == 0


RESULT = {"heard": "", "lang": "en", "total_s": 12.5, "trace_match": "text", "server_commit": "abcdef1234",
          "before_question": [{"kind": "text", "at_s": 0.1, "text": "📍 Got it"}],
          "messages": [{"kind": "text", "at_s": 1.0, "text": "🔎 Checking…"},
                       {"kind": "text", "at_s": 9.0, "text": "₦3.59 billion."},
                       {"kind": "crop", "at_s": 10.0, "text": "3,589,478,500.56\n[1] Budget, page 17",
                        "data": base64.b64encode(JPEG).decode(), "ext": "jpg", "doc_id": "b", "title": "Budget", "page": 17,
                        "figure": "3,589,478,500.56"},
                       {"kind": "image", "at_s": 11.0, "text": "Map", "data": base64.b64encode(b"map").decode(), "ext": "jpg"},
                       {"kind": "buttons", "at_s": 12.0, "text": "Anything else?", "buttons": ["Show working"]}],
          "sources": [{"doc_id": "b", "title": "Budget", "page": 17}, {"doc_id": "b", "title": "Budget", "page": 17},
                      {"doc_id": "c", "title": "BIR", "page": 3}],
          "traces": [{"id": 7, "outcome": "answered", "path": "search", "seconds": 8.0, "answer": "x",
                      "trace": {"check_result": "passed", "timings": {"plan": 2.0}}}],
          "cost": {"usd": 0.0412, "by_stage": {"meta/plan": {"calls": 1, "usd": 0.01}},
                   "by_provider": {"meta": {"calls": 1, "usd": 0.04}}}}


def test_the_json_and_the_images_next_to_it(tmp_path) -> None:
    out = tmp_path / "shots" / "budget.json"
    doc = ask.write_result(RESULT, out, "How much?", {"pin": [13.05, 5.15]})
    on_disk = json.loads(out.read_text(encoding="utf-8"))
    assert on_disk == doc and doc["question"] == "How much?" and doc["pin"] == [13.05, 5.15]
    assert [m["text"] for m in doc["messages"]][:2] == ["🔎 Checking…", "₦3.59 billion."]
    assert doc["reply_text"] == "🔎 Checking…\n\n₦3.59 billion.\n\nAnything else?"
    assert doc["before_question"][0]["text"] == "📍 Got it"
    crop = doc["page_crops"][0]
    assert crop["file"] == "budget-01-crop.jpg" and Path(crop["path"]).read_bytes() == JPEG
    assert Path(crop["path"]).parent == out.parent and crop["page"] == 17 and crop["figure"] == "3,589,478,500.56"
    assert doc["images"][0]["file"] == "budget-02-image.jpg" and "data" not in json.dumps(doc["messages"])
    assert doc["sources"] == [{"doc_id": "b", "title": "Budget", "page": 17}, {"doc_id": "c", "title": "BIR", "page": 3}]
    assert doc["trace_id"] == 7 and doc["check"] == "passed" and doc["timings"]["pipeline"] == {"plan": 2.0}
    assert doc["timings"]["first_message_s"] == 1.0 and doc["timings"]["last_message_s"] == 12.0
    text = ask.report(doc, out)
    assert "Cost of this call: $0.0412" in text and "meta/plan: 1 call(s), $0.0100" in text and "Trace 7" in text


def test_the_job_goes_on_stdin_and_a_failure_prints_nothing_secret(tmp_path, monkeypatch) -> None:
    calls: dict = {}
    marker = ask.MARKER + base64.b64encode(json.dumps(RESULT).encode()).decode()

    def good(cmd, input=None, capture_output=None, timeout=None):
        calls["cmd"], calls["input"] = cmd, input
        return SimpleNamespace(stdout=f"noise\n{marker}\n".encode(), stderr=b"", returncode=0)
    monkeypatch.setattr(subprocess, "run", good)
    job = {"question": "My secret question", "lang": "en", "pin": None}
    assert ask.run_remote(job)["total_s"] == 12.5
    assert "secret question" not in " ".join(calls["cmd"]) and calls["cmd"][-1].endswith("python -u -")
    payload = base64.b64encode(json.dumps(job).encode()).decode()
    assert payload.encode() in calls["input"] and calls["input"].rstrip().endswith(f"_inside({payload!r})".encode())

    def bad(cmd, input=None, capture_output=None, timeout=None):
        err = ("psycopg.OperationalError postgresql://kasafi:hunter2pass@203.0.113.9:5432/kasafi\n"
               "Authorization: Bearer abcdefghijklmnop0123456789\nsk-abcdefghijkl1234\n")
        return SimpleNamespace(stdout=b"", stderr=err.encode(), returncode=1)
    monkeypatch.setattr(subprocess, "run", bad)
    with pytest.raises(SystemExit) as e:
        ask.run_remote(job)
    said = str(e.value)
    for secret in ("hunter2pass", "203.0.113.9", "abcdefghijklmnop0123456789", "sk-abcdefghijkl1234"):
        assert secret not in said
    assert "exit code 1" in said


def test_the_script_sent_to_the_server_runs_only_the_appended_call() -> None:
    """Fed to `python -` on stdin it must not parse this machine's arguments, and locally it needs no project package."""
    src = SCRIPT.read_text(encoding="utf-8")
    assert 'if __name__ == "__main__" and sys.argv[0] != "-":' in src
    top = [ln for ln in src.splitlines() if ln.startswith(("import ", "from "))]
    assert not [ln for ln in top if ln.startswith(("from app", "import app"))]
    assert not re.search(r"""["'/\\]\.env\b""", src)       # the server's own environment is used; no file is read here


def test_arguments() -> None:
    a = ask.parser().parse_args(["What?", "--pin", "13.0589,5.1673", "--lang", "ha", "--out", "x.json"])
    assert a.pin == [13.0589, 5.1673] and a.lang == "ha" and a.out == Path("x.json") and a.voice is None
    for bad in (["q"], ["q", "--out", "x.json", "--lang", "fr"], ["q", "--out", "x.json", "--pin", "13.05"],
                ["q", "--out", "x.json", "--pin", "99,5"]):
        with pytest.raises(SystemExit):
            ask.parser().parse_args(bad)
    with pytest.raises(SystemExit):                  # neither a question nor a voice note
        ask.main(["--out", "x.json"])
    with pytest.raises(SystemExit):
        ask.main(["q", "--voice", "no-such-file.ogg", "--out", "x.json"])
