"""Deep analysis readers (4 Nov 2026): a reading that fails or runs past its time on Muse Spark Open is read again
on the live model, and what still isn't read is reported by title, never dropped in silence; the sector's own
documents are read before budgets and financial statements; registry counts in a PHC brief are primary-level."""

import asyncio
from types import SimpleNamespace

from app.agent import deep as D
from tests.helpers import make_settings


def _reading(doc_id: str, title: str = "") -> D.Reading:
    return D.Reading(doc_id, title or doc_id.upper(), None, [(1, "page text")], ["facilities"])


def _dims():
    return [D._dim("facilities", ["q"], [("facility_count", "number of PHCs", ["q"], False)])]


def _claim(r: D.Reading) -> D.Claim:
    return D.Claim("facilities", f"{r.doc_id} figure", "1", "", "2020", "Sokoto", r.doc_id, r.title, 1,
                   measure="facility_count")


def test_a_slow_or_failing_reading_is_retried_on_the_live_model_and_the_rest_reported(monkeypatch) -> None:
    calls: list = []
    open_client = SimpleNamespace(provider="Fireworks")
    live = SimpleNamespace(provider="Meta")

    async def read_one(client, r, subject, dims):
        calls.append((client.provider, r.doc_id))
        if client.provider == "Fireworks":
            if r.doc_id == "slow":
                await asyncio.sleep(10)                    # past READ_ONE_S (patched below)
            if r.doc_id == "broken":
                raise RuntimeError("502")
            if r.doc_id == "never":
                raise RuntimeError("502")
        if client.provider == "Meta" and r.doc_id == "never":
            raise RuntimeError("502 again")
        return [_claim(r)]
    monkeypatch.setattr(D, "read_one", read_one)
    monkeypatch.setattr(D, "READ_ONE_S", 0.2)
    monkeypatch.setattr(D, "RETRY_ONE_S", 0.5)
    readings = [_reading("fine", "Health AOP"), _reading("slow", "PHC MSP 2020"), _reading("broken", "EmONC"),
                _reading("never", "ROP")]
    claims, stopped, unread = asyncio.run(D.read_all(open_client, readings, "PHCs", _dims(), make_settings(),
                                                     deadline_s=5, spent=lambda: 0.0, retry_client=live))
    assert sorted(c.doc_id for c in claims) == ["broken", "fine", "slow"]     # retried on the live model
    assert ("Meta", "slow") in calls and ("Meta", "broken") in calls and ("Meta", "never") in calls
    assert unread == ["never"] and stopped == ""                              # reported, not dropped in silence


def test_without_a_retry_client_the_unread_documents_are_still_named(monkeypatch) -> None:
    async def read_one(client, r, subject, dims):
        raise RuntimeError("down")
    monkeypatch.setattr(D, "read_one", read_one)
    claims, stopped, unread = asyncio.run(D.read_all(SimpleNamespace(provider="Fireworks"), [_reading("a"), _reading("b")],
                                                     "PHCs", _dims(), make_settings(), deadline_s=5, spent=lambda: 0.0))
    assert claims == [] and unread == ["a", "b"]


def test_the_sectors_own_documents_are_read_before_budgets() -> None:
    class Conn:
        def execute(self, sql, args):
            cats = {"budget-2026-approved": "budget", "bir-2026-q3": "budget_performance", "phc-msp-2020": "sector_plan",
                    "emonc-sokoto": "assessment", "financial-statements-2025": "accountability", "health-aop-2025": "sector_plan"}
            return SimpleNamespace(fetchall=lambda: [(i, cats.get(i, "")) for i in args[0]])

        def rollback(self):
            return None
    readings = [_reading("budget-2026-approved"), _reading("bir-2026-q3"), _reading("phc-msp-2020"),
                _reading("financial-statements-2025"), _reading("emonc-sokoto"), _reading("health-aop-2025")]
    ordered = [r.doc_id for r in D.sector_first(Conn(), readings)]
    assert ordered == ["phc-msp-2020", "emonc-sokoto", "health-aop-2025", "budget-2026-approved", "bir-2026-q3",
                       "financial-statements-2025"]


def test_the_unread_note_is_rendered_and_traced() -> None:
    r = D.DeepResult("Summary.", [("Facilities", "text")], "", "staff by cadre", [], ["phc-msp-2020"], 0.1, 30.0,
                     stopped="", coverage=[], unread=["PHC Minimum Service Package 2020", "EmONC assessment"])
    text, parts = D.render(r, "en")
    joined = text + "\n" + "\n".join(parts)
    assert "⏳ Not read in time (ask again for these): PHC Minimum Service Package 2020; EmONC assessment" in joined
    assert '"unread": ["PHC Minimum Service Package 2020", "EmONC assessment"]' in D.as_json(r)
