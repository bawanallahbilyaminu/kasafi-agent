"""A turn that fetches a document (4 Nov 2026 live): the download and index finished after the 2-minute answer
limit, the user got 'took too long', and the answer came only on asking again. Now a turn whose job has started a
fetch runs on to FETCH_LIMIT_S with a progress line every FETCH_PROGRESS_S; past that, the job keeps running and
its answer is sent on its own when ready. 'Took too long' never while a fetch is running."""

import asyncio
from types import SimpleNamespace

from app.agent.answer import FETCHING
from app.guardrails.scope import Verdict
from app.users import UserStore, user_key
from app.whatsapp import conversation as C
from tests.helpers import make_settings

SENDER = "2348000000083"


async def _ok(*a, **k):
    return Verdict("ok", "none")


async def _none(*a, **k):
    return None


def _setup(monkeypatch, limit: float):
    s = make_settings(kasafi_understanding=False, kasafi_answer_timeout_s=limit)
    monkeypatch.setattr(s.__class__, "has_database", property(lambda self: False))
    store = UserStore(":memory:")
    key = user_key(SENDER, s)
    store.create(key, "en")
    store.give_consent(key)
    return s, store, key


def _run(s, store, answer, notified, monkeypatch, resolve=None):
    async def notify(out):
        notified.append(out.text)
    msg = {"from": SENDER, "id": "w-fetch", "type": "text",
           "text": {"body": "According to the Q4 2025 Budget Implementation Report, how much was spent on social protection?"}}
    return asyncio.run(C.handle(msg, None, store=store, settings=s, answer_fn=answer, guard_fn=_ok, place_fn=_none,
                                emergency_fn=_none, classify_fn=_none, notify=notify))


def test_a_turn_that_started_a_fetch_runs_on_past_the_answer_limit_with_progress_lines(monkeypatch) -> None:
    s, store, key = _setup(monkeypatch, limit=0.2)
    monkeypatch.setattr(C, "FETCH_LIMIT_S", 5.0)
    monkeypatch.setattr(C, "FETCH_PROGRESS_S", 0.15)
    notified: list = []

    async def answer(question, lang, *, notify=None, **kw):
        await notify(FETCHING["en"].format(doc="Sokoto State Budget Implementation Report Q4 2025"))
        await asyncio.sleep(0.6)                                   # past the 0.2 s answer limit
        return SimpleNamespace(text="Social protection: ₦1.2 billion spent in 2025 (Q4 2025 report, p. 31).",
                               found=True, sources=[], working="", quotes="")
    outs = _run(s, store, answer, notified, monkeypatch)
    assert outs[0].text.startswith("Social protection: ₦1.2 billion")
    assert any(n.startswith("📥") for n in notified) and any(n.startswith(("⬇️", "📖")) for n in notified)
    assert not any("took too long" in o.text.lower() for o in outs)
    assert store.recent_turns(key)[-1]["answer"].startswith("Social protection")


def test_without_a_fetch_the_answer_limit_still_holds(monkeypatch) -> None:
    s, store, key = _setup(monkeypatch, limit=0.2)
    notified: list = []

    async def answer(question, lang, *, notify=None, **kw):
        await asyncio.sleep(1.0)
        return SimpleNamespace(text="late", found=True, sources=[], working="", quotes="")

    async def no_note(*a, **k):
        return None
    monkeypatch.setattr(C, "_note_failure", no_note)
    outs = _run(s, store, answer, notified, monkeypatch)
    assert "couldn't finish" in outs[0].text.lower()           # the usual limit, no fetch: the apology as before


def test_a_fetch_that_outruns_the_long_limit_sends_its_answer_on_its_own(monkeypatch) -> None:
    s, store, key = _setup(monkeypatch, limit=0.2)
    monkeypatch.setattr(C, "FETCH_LIMIT_S", 0.5)
    monkeypatch.setattr(C, "FETCH_PROGRESS_S", 0.1)
    notified, sent = [], []

    class Client:
        async def send_text(self, to, body):
            sent.append((to, body))

        async def aclose(self):
            return None
    import app.whatsapp.client as WC
    monkeypatch.setattr(WC, "WhatsAppClient", lambda *a, **k: Client())
    done = asyncio.Event()

    async def answer(question, lang, *, notify=None, **kw):
        await notify(FETCHING["en"].format(doc="Sokoto State Budget Implementation Report Q4 2025"))
        await asyncio.sleep(0.9)                                   # past FETCH_LIMIT_S
        return SimpleNamespace(text="Social protection: ₦1.2 billion spent in 2025 (Q4 2025 report, p. 31).",
                               found=True, sources=[], working="", quotes="")

    async def scenario():
        async def notify(out):
            notified.append(out.text)
        msg = {"from": SENDER, "id": "w-fetch2", "type": "text",
               "text": {"body": "According to the Q4 2025 Budget Implementation Report, how much was spent on social protection?"}}
        outs = await C.handle(msg, None, store=store, settings=s, answer_fn=answer, guard_fn=_ok, place_fn=_none,
                              emergency_fn=_none, classify_fn=_none, notify=notify)
        await asyncio.sleep(1.0)                                   # the job finishes and the late send goes out
        return outs
    outs = asyncio.run(scenario())
    assert "still being indexed" in outs[0].text and "took too long" not in outs[0].text.lower()
    assert sent and sent[0][0] == SENDER and sent[0][1].startswith("Social protection: ₦1.2 billion")
    assert store.recent_turns(key)[-1]["answer"].startswith("Social protection")
