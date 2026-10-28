"""Conversation context: recent turns are kept per user and follow-ups refer to the previous answer."""

import asyncio
import json
from datetime import date, datetime, timedelta, timezone

from app.acquisition.editions import SERIES, Latest
from app.agent import answer as ans
from app.providers.chat import ChatResult
from app.users import TURNS_KEPT, UserStore
from tests.helpers import make_settings, run_handle
from tests.test_answer import EV
from tests.test_conversation_answers import consented, text

# --- the store --------------------------------------------------------------------------------------


def test_turns_keep_the_last_few_oldest_first() -> None:
    store = UserStore(":memory:")
    for i in range(TURNS_KEPT + 2):
        store.add_turn("u1", "en", f"q{i}", f"a{i}", [{"doc_id": "d", "page": i}])
    store.add_turn("u2", "ha", "other user", "x")
    turns = store.recent_turns("u1")
    assert [t["question"] for t in turns] == [f"q{i}" for i in range(2, TURNS_KEPT + 2)]
    assert turns[-1]["sources"] == [{"doc_id": "d", "page": TURNS_KEPT + 1}]
    assert [t["question"] for t in store.recent_turns("u2")] == ["other user"]


def test_turns_older_than_90_days_are_gone() -> None:
    store = UserStore(":memory:")
    old = (datetime.now(timezone.utc) - timedelta(days=91)).isoformat()
    store._exec("INSERT INTO turns (user_key, at, lang, question, answer, sources) VALUES (?,?,?,?,?,?)",
                ("u", old, "en", "old", "a", "[]"))
    assert store.recent_turns("u") == []
    store.add_turn("u", "en", "new", "a")
    assert store._exec("SELECT count(*) FROM turns WHERE question = 'old'").fetchone()[0] == 0


def test_delete_removes_turns() -> None:
    store = consented("en")
    run_handle(text("How much for health in 2026?"), store=store, answer_calls=[])
    assert store._exec("SELECT count(*) FROM turns").fetchone()[0] == 1
    run_handle(text("DELETE MY DATA"), store=store)
    assert store._exec("SELECT count(*) FROM turns").fetchone()[0] == 0


# --- the WhatsApp flow ------------------------------------------------------------------------------

def test_second_question_gets_the_first_as_history() -> None:
    store, hist = consented("en"), []
    run_handle(text("Latest CPI for Sokoto?"), store=store, answer_calls=[], history_calls=hist)
    run_handle(text("I believe this can't be the most recent report, please recheck"), store=store,
               answer_calls=[], history_calls=hist)
    assert hist[0] == []
    assert [t["question"] for t in hist[1]] == ["Latest CPI for Sokoto?"]
    assert hist[1][0]["answer"] == "ANSWER[en]: Latest CPI for Sokoto?"


def test_hausa_follow_up_also_gets_history() -> None:
    store, hist = consented("ha"), []
    run_handle(text("Nawa aka ware wa lafiya a 2026?"), store=store, answer_calls=[], history_calls=hist)
    run_handle(text("Kuma 2024 fa?"), store=store, answer_calls=[], history_calls=hist)
    assert hist[1][0]["question"] == "Nawa aka ware wa lafiya a 2026?"


# --- the answer engine ------------------------------------------------------------------------------

class FakeClient:
    def __init__(self, replies):
        self.replies, self.calls = list(replies), []

    async def __aenter__(self):
        return self

    async def __aexit__(self, *a):
        return None

    async def chat(self, messages, **kw):
        self.calls.append(messages)
        return ChatResult(content=json.dumps(self.replies.pop(0)), model="m", finish_reason="stop")


PREV = {"question": "Latest CPI for Sokoto?", "answer": "From the June 2025 CPI, Sokoto 3.01% [1]",
        "sources": [{"doc_id": "cpi-2025-06", "title": "CPI June 2025", "page": 16, "series": "nbs_cpi",
                     "edition": "2025-06"}]}
RECHECK = {"english_question": "What is the latest CPI inflation rate for Sokoto?", "search_queries": ["Sokoto inflation"],
           "doc_ids": ["cpi-2025-06"], "followup": "recheck", "recheck_doc_id": "cpi-2025-06"}
GOOD = {"summary": "128,495,868,362.13 [1].", "items": [], "found": "full", "cited": [1]}
CPI_EDITIONS = {"cpi-2025-06": ("nbs_cpi", "2025-06")}


def run(monkeypatch, replies, *, latest=None, editions=None, history=(PREV,), lang="en"):
    fake = FakeClient(replies)
    seen = {}

    async def latest_fn(conn, series, today, *, newer_than=None, notify=None, notify_text=""):
        seen.update(series=series.key, newer_than=newer_than)
        return latest

    monkeypatch.setattr(ans, "load_catalog", lambda conn: [{"id": "cpi-2025-06"}, {"id": "budget-2026-approved"}])
    monkeypatch.setattr(ans, "gather_evidence", lambda conn, plan: EV)
    monkeypatch.setattr(ans, "doc_edition", lambda conn, d: (editions or {}).get(d, (None, None)))
    monkeypatch.setattr(ans, "series_doc_ids", lambda conn, s: {"cpi-2025-06"})
    monkeypatch.setattr(ans, "log_gap", lambda *a, **k: None)
    a = asyncio.run(ans.answer_question("please recheck", lang, conn=None, settings=make_settings(),
                                        client_factory=lambda s: fake, latest_fn=latest_fn, today=date(2026, 10, 28),
                                        history=list(history)))
    return a, fake, seen


def test_planner_sees_the_history() -> None:
    hist = ans.history_text([PREV])
    assert "USER: Latest CPI for Sokoto?" in hist and "cpi-2025-06 p16 (edition 2025-06)" in hist


def test_recheck_finds_a_newer_edition_and_corrects(monkeypatch) -> None:
    newer = Latest(SERIES["nbs_cpi"], "2026-09", "cpi-2026-09", "2026-09", "newer_found", tried=["2026-09"])
    a, fake, seen = run(monkeypatch, [RECHECK, GOOD], latest=newer, editions=CPI_EDITIONS)
    assert seen == {"series": "nbs_cpi", "newer_than": "2025-06"}            # only editions after the cited one
    assert "HISTORY" in fake.calls[0][1]["content"]
    assert a.text.startswith("You're right: there is a newer edition, September 2026.")
    assert a.plan.doc_ids[0] == "cpi-2026-09" and "cpi-2025-06" not in a.plan.doc_ids


def test_recheck_confirms_when_nothing_newer_exists(monkeypatch) -> None:
    none = Latest(SERIES["nbs_cpi"], "2025-07", status="none_newer", tried=["2025-07"])
    a, fake, _ = run(monkeypatch, [RECHECK, GOOD], latest=none, editions=CPI_EDITIONS, lang="ha")
    assert a.text.startswith("Na sake dubawa: Yuni 2025 ne har yanzu bugu mafi sabo da na samu "
                             "(na kuma nemi Yuli 2025).")
    assert a.plan.doc_ids[0] == "cpi-2025-06"
    composer = fake.calls[1][1]["content"]
    assert "PREVIOUS ANSWER: From the June 2025 CPI" in composer and "recheck" in composer


def test_recheck_of_a_non_recurring_document_reverifies_the_figure(monkeypatch) -> None:
    prev = {**PREV, "sources": [{"doc_id": "budget-2026-approved", "page": 40}]}
    plan = {**RECHECK, "doc_ids": [], "recheck_doc_id": "budget-2026-approved",
            "english_question": "How much was allocated to education in 2026? (that figure looks wrong)"}
    a, fake, seen = run(monkeypatch, [plan, GOOD], history=(prev,))
    assert seen == {} and a.plan.doc_ids == ["budget-2026-approved"]
    assert "Check its figures against the evidence" in fake.calls[1][1]["content"]


def test_other_follow_up_gets_the_previous_answer_but_no_recheck(monkeypatch) -> None:
    more = {**RECHECK, "followup": "more", "english_question": "Explain more about Sokoto's CPI in June 2025"}
    a, fake, seen = run(monkeypatch, [more, GOOD], editions=CPI_EDITIONS)
    assert seen == {} and a.found
    composer = fake.calls[1][1]["content"]
    assert "PREVIOUS ANSWER" in composer and "asked to recheck" not in composer


def test_followup_is_ignored_without_history(monkeypatch) -> None:
    a, fake, seen = run(monkeypatch, [RECHECK, GOOD], history=())
    assert a.plan.followup == "none" and seen == {} and "HISTORY" not in fake.calls[0][1]["content"]
