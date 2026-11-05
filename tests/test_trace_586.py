"""Live trace 586 (5 Nov 2026, a real tester): "How much was released for MNCH from the local government budget in
Sokoto State?" got "No line in the documents is exactly that…" with three state lines at 0.00, no word that the
library holds only the state's documents, the planned health plans unread, and the answer check skipped on a 30 s
timeout. Now: the level asked against the level held is said first; a zero is never listed as a 'nearest line';
with none left the planned documents' pages are read; a check that times out is tried again on the live model."""

import asyncio
from types import SimpleNamespace

from app.agent import answer as A
from app.agent import answer_check as ck
from tests.helpers import make_settings


class _Conn:
    def __init__(self, lg_docs: bool = False) -> None:
        self.lg_docs = lg_docs

    def execute(self, sql, args=None):
        return SimpleNamespace(fetchone=lambda: (1,) if self.lg_docs else None)

    def rollback(self):
        return None


def test_lga_budgets_asked_and_only_state_documents_held_is_said_first() -> None:
    q = "How much was released for MNCH from the local government budget in Sokoto State?"
    lead = A.lg_budget_note(_Conn(), q, None, True, "en")
    assert lead == ("I don't have Sokoto's local government (LGA) budgets, only the state budget and its reports. "
                    "What the state's documents show:")
    none = A.lg_budget_note(_Conn(), q, None, False, "en")
    assert none.startswith("I don't have Sokoto's local government (LGA) budgets, only the state budget") and \
        "don't give a figure" in none
    assert A.lg_budget_note(_Conn(), "Nawa aka saki daga kasafin ƙananan hukumomi don lafiya?", None, True, "ha") \
        .startswith("Ba ni da kasafin kuɗin ƙananan hukumomin Sokoto")
    # the library holds LGA budgets: no note; a question about the state's lines located in an LGA: no note
    assert A.lg_budget_note(_Conn(lg_docs=True), q, None, True, "en") == ""
    assert A.lg_budget_note(_Conn(), "What is budgeted for projects in Wamakko LGA in 2026?", None, True, "en") == ""
    assert A.lg_budget_note(_Conn(), "How much is allocated to the Ministry of Health in 2026?", None, True, "en") == ""
    assert A.lg_budget_note(None, q, None, True, "en") == ""


def test_the_note_leads_a_found_answer_and_replaces_a_not_found_one(monkeypatch) -> None:
    q = "How much was released for MNCH from the local government budget in Sokoto State?"
    plan = A.Plan(english_question=q, search_queries=[], doc_ids=[])

    async def checked(a_, *args):
        return a_
    monkeypatch.setattr(A, "checked_answer", checked)

    def run(a):
        async def finished(question, lang, conn, **kw):
            return a
        monkeypatch.setattr(A, "_answer_finished", finished)
        return asyncio.run(A.answer_question(q, "en", _Conn(), settings=make_settings()))
    found = run(SimpleNamespace(text="Free Maternal and Child Healthcare (MNCH+N): ₦960 million in 2025 (MTSS, p. 12).",
                                found=True, plan=plan, clarify=None, needs_pin=False))
    assert found.text.startswith("I don't have Sokoto's local government (LGA) budgets, only the state budget and its "
                                 "reports. What the state's documents show:\n\nFree Maternal and Child Healthcare")
    missing = run(SimpleNamespace(text="I couldn't find the answer in the documents I have.", found=False, plan=plan,
                                  clarify=None, needs_pin=False))
    assert missing.text.startswith("I don't have Sokoto's local government (LGA) budgets") and \
        "couldn't find the answer" not in missing.text


def test_a_zero_is_never_listed_as_a_nearest_line() -> None:
    zero = SimpleNamespace(cell=SimpleNamespace(amount=0), line=None)
    zero_dec = SimpleNamespace(cell=SimpleNamespace(amount=__import__("decimal").Decimal("0.00")), line=None)
    real = SimpleNamespace(cell=SimpleNamespace(amount=__import__("decimal").Decimal("120000000")), line=None)
    assert A.shown_nearest([zero, zero_dec]) == []                 # the page path then reads the planned documents
    assert A.shown_nearest([zero, real, zero_dec]) == [real]


class _Client:
    def __init__(self, reply=None, error=None, provider="Fireworks"):
        self.reply, self.error, self.provider, self.calls = reply, error, provider, 0

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return None

    async def chat(self, messages, **kw):
        self.calls += 1
        if self.error:
            raise self.error
        return SimpleNamespace(content=self.reply)


PASS = ('{"answers_question": "yes", "subject": {"place": true, "time": true, "topic": true, "level": true}, '
        '"contradictions": [], "missing": [], "missing_stated": false, "unclear": [], "unsupported": [], '
        '"verdict": "pass", "feedback": ""}')


def _answer():
    return SimpleNamespace(text="The 2026 health budget is ₦118.83 billion.", found=True, cited=[], verification="",
                           exact="", working="", verified=True, code_block="", plan=None, timings={}, clarify=None,
                           needs_pin=False, needs_size=False, deep=None, maps=[], partial=False)


def test_a_check_that_times_out_is_tried_again_on_the_live_model(monkeypatch) -> None:
    monkeypatch.setattr(ck, "evidence_text", lambda conn, a: "")
    monkeypatch.setattr(ck, "found_count", lambda a: (0, 0))
    monkeypatch.setattr(ck, "code_rules", lambda a, u, counts: [])
    slow = _Client(error=asyncio.TimeoutError())
    live = _Client(reply=PASS, provider="Meta")
    s = make_settings(kasafi_check_timeout_s=1.0)
    v = asyncio.run(ck.check("What is the 2026 health budget?", _answer(), None, [], object(), s, slow,
                             retry=lambda: live))
    assert v.verdict == "pass" and v.provider == "Meta" and slow.calls == 1 and live.calls == 1
    # both fail: skipped, and the reason names both attempts
    dead = _Client(error=RuntimeError("503"), provider="Meta")
    v = asyncio.run(ck.check("q", _answer(), None, [], object(), s, _Client(error=asyncio.TimeoutError()),
                             retry=lambda: dead))
    assert v.verdict == "skipped" and "retry: RuntimeError" in v.why
    # no retry client (an eval run): skipped as before
    v = asyncio.run(ck.check("q", _answer(), None, [], object(), s, _Client(error=asyncio.TimeoutError())))
    assert v.verdict == "skipped" and "retry" not in v.why
