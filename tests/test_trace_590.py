"""Live trace 590 (5 Nov 2026, a real tester): "Tell me about the Ministry of Innovation and Digital Economy in
Sokoto State" went to a deep analysis that covered 2024 only; its 17 figures were all printed on their cited pages,
but the code check counted 0 of 17 (house-style '₦100 million' against the page's '100,000,000.00'), the answer
check said 'revise', and with no second round the brief was cut to one sentence. The user had also given their name
and job title. Now: house-style amounts are matched with their unit; one MDA starts from the structured budget
core with the documents on top; a deep analysis sent back is written again once from its checked claims; a name a
user gives for themselves is removed before the message is saved, and Kasafi never claims to know who they are."""

import asyncio
from types import SimpleNamespace

from app import privacy
from app.agent import answer as A
from app.agent import answer_check as ck
from app.agent import deep as D
from app.agent.need import Entity, Need
from tests.helpers import make_settings

PAGE = ("Ministry of Innovation and Digital Economy REHABILITATION / REPAIRS OF OFFICE BUILDINGS 42,000,000.00 0.00 "
        "42,000,000.00 PURCHASE OF COMPUTERS 40,000,000.00 40,000,000.00 0.00 total 100,000,000.00 90,000,000.00 "
        "58,000,000.00")


def _answer(text: str):
    return SimpleNamespace(text=text, exact=text, verification="figures checked", working="",
                           cited=[A.Evidence(1, "audited-fs-2024", "2024 Audited Financial Statement", None, 147, "text",
                                             PAGE)])


def test_house_style_amounts_are_counted_as_the_printed_figures_they_are() -> None:
    brief = _answer("Its revised budget was ₦100 million in 2024, with ₦42 million for office buildings and "
                    "₦90 million for 9 digital hubs.")
    assert ck.found_count(brief) == (3, 3)                      # was 0 of 3: '100' against '100,000,000.00'
    assert ck.code_rules(brief, None, ck.found_count(brief)) == []
    invented = _answer("Its budget was ₦777 million in 2024 and ₦333 million in 2025.")
    assert ck.found_count(invented) == (2, 0)                   # still caught
    assert any(r.startswith("no_figure_found") for r in ck.code_rules(invented, None, ck.found_count(invented)))
    assert ck.found_count(_answer("The lines print 42,000,000.00 and 58,000,000.00.")) == (2, 2)


def _plan(entities):
    return A.Plan(english_question="Tell me about the Ministry of Innovation and Digital Economy", search_queries=[],
                  doc_ids=[], need=Need(standalone_question="q", entities=entities, time={"kind": "year", "year": 2026}))


def test_one_resolved_mda_is_an_overview_and_several_or_none_are_not() -> None:
    one = _plan([Entity("mda", "Ministry of Innovation and Digital Economy",
                        resolved="Ministry of Innovation and Digital Economy", code="027900100100")])
    assert A.single_mda(one) == "Ministry of Innovation and Digital Economy"
    two = _plan([Entity("mda", "Ministry of Health", resolved="Ministry of Health", code="052100100100"),
                 Entity("mda", "Ministry of Finance", resolved="Ministry of Finance", code="022000100100")])
    assert A.single_mda(two) == "" and A.single_mda(_plan([Entity("function", "Health")])) == ""
    assert A.single_mda(_plan([Entity("mda", "some ministry")])) == ""          # not resolved in the data


def _profile():
    return A.Answer("The Ministry of Innovation and Digital Economy's 2026 approved budget is ₦1.20 billion: personnel "
                    "₦0.10 billion, overhead ₦0.20 billion, capital ₦0.90 billion.\n\n📄 *Sources:* Sokoto State FY 2026 "
                    "Budget, p. 18", True, True,
                    [A.Evidence(1, "budget-2026-approved", "Sokoto State FY 2026 Budget", None, 18, "text", "row")],
                    None, {"answer": 0.2}, exact="1,200,000,000.00", verification="calculation checked",
                    sources=[{"doc_id": "budget-2026-approved", "page": 18}])


def _deep_answer(found=True):
    r = D.DeepResult("It plans 9 digital hubs (2025 MDA Budget Proposals, p. 175).", [("Programmes", "text")], "", "",
                     [D.Claim("programmes", "digital hubs", "9", "", "2025", "Sokoto", "budget-2025-proposed",
                              "2025 MDA Budget Proposals", 175, measure="other")] if found else [],
                     ["budget-2025-proposed"], 0.1, 60.0)
    return A.deep_as_answer(r, None, {"deep": 60.0}, "en")


def test_an_mda_overview_leads_with_the_structured_budget_and_adds_the_documents() -> None:
    out = A.mda_overview(_profile(), _deep_answer(), "en")
    assert out.text.startswith("The Ministry of Innovation and Digital Economy's 2026 approved budget is ₦1.20 billion")
    assert out.text.index("2026 approved budget") < out.text.index("*From the documents*") < out.text.index("9 digital hubs")
    assert [(e.n, e.doc_id, e.page) for e in out.cited] == [(1, "budget-2026-approved", 18), (2, "budget-2025-proposed", 175)]
    assert out.deep is not None and out.parts and out.code_block.startswith("The Ministry of Innovation")
    assert ck.computed_in_code(out)                              # judged on subject, not on a figure count
    alone = A.mda_overview(_profile(), _deep_answer(found=False), "en")
    assert alone.text == _profile().text and alone.deep is None  # the documents gave nothing checked: the profile


def test_a_deep_analysis_sent_back_is_written_again_once_with_the_feedback(monkeypatch) -> None:
    seen: dict = {}

    async def synthesise(client, question, lang, claims, dims, settings, feedback=""):
        seen["feedback"], seen["claims"] = feedback, len(claims)
        return {"summary": "In 2026 the ministry plans 9 digital hubs [C1].", "sections": [], "differ": ""}
    monkeypatch.setattr(D, "synthesise", synthesise)
    claim = D.Claim("programmes", "digital hubs", "9", "", "2026", "Sokoto", "budget-2026-approved",
                    "Sokoto State FY 2026 Budget", 61, measure="other")
    first = D.DeepResult("Only 2024 figures.", [], "", "", [claim], ["budget-2026-approved"], 0.1, 60.0, pool=[claim])
    r2 = asyncio.run(D.rewrite(object(), "Tell me about the ministry", "en", first, "covers 2024 only; 2026 exists",
                               make_settings()))
    assert seen == {"feedback": "covers 2024 only; 2026 exists", "claims": 1}
    assert r2.summary.startswith("In 2026 the ministry plans 9 digital hubs") and r2.claims == [claim]

    # through the check: revise -> one rewrite -> checked again -> sent (never straight to a partial answer)
    a = A.deep_as_answer(first, None, {}, "en")
    verdicts = iter([ck.Verdict("revise", feedback="covers 2024 only; 2026 exists"), ck.Verdict("pass", round=2)])
    calls: list = []

    async def fake_check(message, a_, u, history, conn, settings, client, *, round_=1, model=None, **kw):
        calls.append(round_)
        return next(verdicts)

    class Writer:
        def __init__(self, settings=None, **kw):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *exc):
            return None
    from contextlib import asynccontextmanager

    @asynccontextmanager
    async def client_cm(settings, factory):
        yield object()
    monkeypatch.setattr(A.answer_check, "check", fake_check)
    monkeypatch.setattr(A, "check_client", client_cm)
    s = make_settings(kasafi_answer_check=True)
    import time
    out = asyncio.run(A.checked_answer(a, "Tell me about the ministry", "en", object(),
                                       {"settings": s, "client_factory": Writer}, time.perf_counter()))
    assert calls == [1, 2] and out.text.startswith("In 2026 the ministry plans 9 digital hubs")
    assert [c["verdict"] for c in out.checks] == ["revise", "pass"]


def test_a_name_the_user_gives_is_removed_before_the_message_is_kept() -> None:
    cases = {
        "My name is Musa Bello and I am the Director of Budget. Tell me about the Ministry of Innovation":
            "My name is [name removed] and I am the Director of Budget. Tell me about the Ministry of Innovation",
        "I am Dr. Aisha Umar, Permanent Secretary. How much is the 2026 health budget?":
            "I am [name removed], Permanent Secretary. How much is the 2026 health budget?",
        "Sunana Abubakar Sadiq, ina so in san kasafin lafiya": "Sunana [name removed], ina so in san kasafin lafiya",
        "I'm Hauwa from the Ministry of Finance": "I'm [name removed] from the Ministry of Finance",
    }
    for given, kept in cases.items():
        assert privacy.strip_identity(given) == kept
    # a question is never touched: places, ministries and 'I am a farmer' stay
    for same in ("Tell me about the Ministry of Innovation and Digital Economy in Sokoto State",
                 "I am a farmer in Wamakko. Has my farm ever flooded?", "This is Sokoto State's 2026 budget?",
                 "Ni manomi ne a Wurno"):
        assert privacy.strip_identity(same) == same
    from app.agent.trace import redact
    assert "[name removed]" in redact("My name is Musa Bello. What is the 2026 budget?") and "Musa" not in \
        redact("My name is Musa Bello. What is the 2026 budget?")
    from app.users import UserStore
    store = UserStore(":memory:")
    store.create("k", "en")
    store.add_turn("k", "en", "My name is Musa Bello. What is the 2026 health budget?", "₦118.83 billion.", [], "", "")
    assert store.recent_turns("k")[-1]["question"] == "My name is [name removed]. What is the 2026 health budget?"


def test_the_prompts_never_claim_or_repeat_who_the_user_is() -> None:
    from app.agent import conversational as CV
    from app.agent import understand as U
    assert "never say you know, remember or have a record of who they are" in CV.SYSTEM
    assert "A name, job title or employer the user" in U.system_prompt(make_settings())
