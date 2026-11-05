"""Live trace 629 (5 Nov 2026), 'Tell me about the Ministry of Innovation and Digital Economy': the check said 'drop the
unrelated health-insurance and state-target claims' and was overridden because the budget profile above them was
computed in code; both page crops were of those off-subject figures.

Now: 'computed in code' covers only the part code computed; a part written from documents keeps the check's verdict,
and a revise there triggers the rewrite. An overview of one subject (ministry, LGA, facility, sector) keeps only
document figures whose page names that subject, and its crops come from rows about it."""

import asyncio
import re
import time
from contextlib import asynccontextmanager
from types import SimpleNamespace

import pytest

from app.agent import answer as A
from app.agent import answer_check as ck
from app.agent import deep as D
from app.agent.need import Entity, Need
from app.evidence.crops import CropRequest, plan_crops
from tests.helpers import make_settings

MINISTRY = "Ministry of Innovation and Digital Economy"
ABOUT = D.subject_pattern("agency", MINISTRY, "027900000000")
ROWS = f"""230 CAPITAL EXPENDITURE
027900100100 23030121 {MINISTRY} REHABILITATION / REPAIRS OF OFFICE BUILDINGS 42,000,000.00 0.00 42,000,000.00
027900100100 23010113 {MINISTRY} PURCHASE OF COMPUTERS 40,000,000.00 40,000,000.00 0.00
027900100100 23010113 {MINISTRY} PURCHASE OF COMPUTERS 100,000,000.00 42,000,000.00 58,000,000.00
021500100100 23010113 Ministry of Finance PURCHASE OF COMPUTERS 75,000,000.00 75,000,000.00 0.00
021500100100 23010108 Ministry of Finance PURCHASE OF BUSES 58,000,000.00 0.00 58,000,000.00"""
WRAPPED = f"""027900100100 23030121 {MINISTRY}
REHABILITATION / REPAIRS 33,000,000.00 3,000,000.00 30,000,000.00
027900100100 23010113 {MINISTRY}
PURCHASE OF COMPUTERS 40,000,000.00 40,000,000.00 0.00
021500100100 23010113 Ministry of Finance
PURCHASE OF COMPUTERS 75,000,000.00 75,000,000.00 0.00
021500100100 23010108 Ministry of Finance
PURCHASE OF BUSES 66,000,000.00 0.00 66,000,000.00"""
DEFICIT = ("The budget deficit of N233,813,940,788 exists which is the shortfall of total recurrent revenue plus grant "
           "compared to the total budget.")
INSURANCE = "The JP worked with SOCHEMA and the Ministry of Women and Children Affairs to give cover to 6,000 people."


def _answer(text="", code_block="", deep=None, cited=(), parts=(), verification="figures checked", exact="", **kw):
    return A.Answer(text, True, True, list(cited), None, {}, exact=exact or text, parts=list(parts), deep=deep,
                    code_block=code_block, verification=verification, **kw)


def _ev(text="", n=1, doc="d", page=1):
    return A.Evidence(n, doc, "Doc", None, page, "text", text)


# --- 1. the override covers only what code computed ---------------------------------------------------------------

PROFILE = "In 2026 the ministry is allocated ₦3.59 billion. It has 26 capital projects."
BRIEF = "The state deficit was 233,813,940,788 Naira (Citizen Budget, p. 10)."


def _overview():
    return _answer(f"{PROFILE}\n\n*From the documents*\n{BRIEF}", code_block=PROFILE, deep=object(),
                   parts=["*Plans*\nThe state targets 90% employment."], cited=[_ev(f"state deficit {DEFICIT}")],
                   verification="calculation checked")


def test_the_parts_of_an_answer_are_told_apart() -> None:
    a = _overview()
    assert ck.code_part(a) == PROFILE and BRIEF in ck.document_part(a) and "90% employment" in ck.document_part(a)
    assert PROFILE not in ck.document_part(a) and not ck.computed_in_code(a)
    # all code: a place or structured answer
    code = _answer("Rain was 12 mm.", verification="calculation checked")
    assert ck.computed_in_code(code) and ck.document_part(code) == "" and ck.code_part(code) == "Rain was 12 mm."
    # a page answer with code's total
    parts = _answer("Total: 60.\n\nIQS isn't printed by LGA.", code_block="Total: 60.", cited=[_ev("x")])
    assert ck.code_part(parts) == "Total: 60." and ck.document_part(parts) == "IQS isn't printed by LGA."
    # all a model: a deep analysis alone, and a budget query whose sentences a model wrote from code's rows
    alone = _answer("Brief.", deep=object(), parts=["*Staffing*\nOne line."], cited=[_ev("x")])
    assert not ck.computed_in_code(alone) and ck.code_part(alone) == "" and "One line." in ck.document_part(alone)
    wrote = _answer("Health gets ₦118 billion.", verification="calculation checked", model_wrote=True)
    assert not ck.computed_in_code(wrote) and ck.document_part(wrote) == "Health gets ₦118 billion."


def test_a_revise_about_the_document_part_stands_though_code_computed_the_rest() -> None:
    """Trace 629's verdict: it had been turned into a pass ('computed in code, subject matches')."""
    v = ck.Verdict("revise", feedback="drop the unrelated claims", subject={"topic": True},
                   unsupported=["state deficit of 233,813,940,788"])
    out = ck.settle(_overview(), v, [], 1)
    assert out.verdict == "revise" and out.feedback == "drop the unrelated claims" and not out.why
    # the same on a deep analysis alone, and on a page answer beside code's total
    alone = _answer("Brief with 42 figures.", deep=object(), cited=[_ev("x")])
    assert ck.settle(alone, ck.Verdict("revise", unsupported=["42 figures"]), [], 1).verdict == "revise"
    parts = _answer("Total: 60.\n\nIQS is 9.", code_block="Total: 60.", cited=[_ev("x")])
    assert ck.settle(parts, ck.Verdict("revise", unsupported=["IQS is 9"]), [], 1).verdict == "revise"
    wrote = _answer("Health gets ₦118 billion.", verification="calculation checked", model_wrote=True)
    assert ck.settle(wrote, ck.Verdict("revise", contradictions=["x"]), [], 1).verdict == "revise"


def test_a_fault_only_in_the_code_part_doesnt_send_the_answer_back() -> None:
    v = ck.Verdict("revise", unsupported=["It has 26 capital projects", "allocated ₦3.59 billion"],
                   subject={"topic": True}, answers_question="yes")
    a = _answer(f"{PROFILE}\n\n*From the documents*\nIt plans 9 digital hubs.", code_block=PROFILE, deep=object(),
                cited=[_ev("9 digital hubs")], verification="calculation checked")
    out = ck.settle(a, v, [], 1)
    assert out.verdict == "pass" and out.why.startswith("only the part computed in code") and out.unsupported == []
    # a fault in each part: the verdict stands, and only the documents part's fault is left for the writer
    v = ck.Verdict("revise", unsupported=["26 capital projects", "9 digital hubs"], subject={"topic": True})
    out = ck.settle(a, v, [], 1)
    assert out.verdict == "revise" and out.unsupported == ["9 digital hubs"]


def test_an_answer_code_wrote_whole_keeps_its_override_and_a_broken_rule_never_passes() -> None:
    code = _answer("Rain was 12 mm.", verification="calculation checked")
    out = ck.settle(code, ck.Verdict("revise", unsupported=["12 mm"], subject={"topic": True}), [], 1)
    assert out.verdict == "pass" and out.why.startswith("computed in code")
    out = ck.settle(code, ck.Verdict("revise", subject={"topic": False}), [], 1)
    assert out.verdict == "revise"                              # the wrong topic is still the check's to say
    out = ck.settle(_overview(), ck.Verdict("pass"), ["no_figure_found: none"], 1)
    assert out.verdict == "revise"


def test_the_check_sees_the_two_parts_labelled_and_no_brief_as_its_own_evidence() -> None:
    a = _overview()
    prompt = ck.user_text("q", "q", [], a.text, ck.evidence_text(None, a), a.verification, [], (0, 0), 1,
                          code=ck.code_part(a), doc=ck.document_part(a))
    assert "PART COMPUTED IN CODE" in prompt and "PART WRITTEN FROM DOCUMENTS (judge in full)" in prompt
    assert prompt.index("26 capital projects") < prompt.index("PART WRITTEN FROM DOCUMENTS") < prompt.index("233,813")
    assert "90% employment" in prompt                           # the section messages are judged too
    evidence = ck.evidence_text(None, _answer("Brief says 77.", deep=object(), exact="Brief says 77.", cited=[_ev("pg")]))
    assert "Brief says 77" not in evidence
    assert "26 capital projects" in ck.evidence_text(None, a).split("COMPUTED OR WRITTEN IN CODE")[1]
    assert "PART COMPUTED IN CODE" in " ".join(ck.SYSTEM.split())


def test_every_figures_count_is_the_documents_parts() -> None:
    a = _answer(f"{PROFILE}\n\n*From the documents*\nThe ministry plans ₦40 million (p. 1).", code_block=PROFILE,
                deep=object(), cited=[_ev("internet 40,000,000.00")], verification="calculation checked")
    assert ck.found_count(a) == (1, 1)
    a2 = _answer(f"{PROFILE}\n\n*From the documents*\nThe ministry plans ₦777 million (p. 1).", code_block=PROFILE,
                 deep=object(), cited=[_ev("internet 40,000,000.00")], verification="calculation checked")
    assert ck.found_count(a2) == (1, 0)                         # no longer exempt: a rule code decides


class _Fake:
    def __init__(self, settings=None, **kw):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return None


def test_a_revise_on_the_documents_part_rewrites_it_and_keeps_the_profile(monkeypatch) -> None:
    calls, seen = [], {}
    verdicts = iter([ck.Verdict("revise", feedback="drop the state deficit", unsupported=["deficit"]),
                     ck.Verdict("pass", round=2)])

    async def fake_check(message, a_, u, history, conn, settings, client, *, round_=1, model=None, **kw):
        calls.append((round_, a_.text))
        return next(verdicts)

    async def synthesise(client, question, lang, claims, dims, settings, feedback=""):
        seen["feedback"] = feedback
        return {"summary": "It plans 9 digital hubs [C1].", "sections": [], "differ": ""}

    @asynccontextmanager
    async def client_cm(settings, factory):
        yield object()
    monkeypatch.setattr(A.answer_check, "check", fake_check)
    monkeypatch.setattr(A, "check_client", client_cm)
    monkeypatch.setattr(D, "synthesise", synthesise)
    claim = D.Claim("programmes", "digital hubs", "9", "", "2025", "Sokoto", "mbp", "MBP", 175, printed="")
    r = D.DeepResult("The deficit was large.", [], "", "", [claim], ["mbp"], 0.1, 60.0, pool=[claim], about=ABOUT)
    profile = A.Answer(PROFILE, True, True, [A.Evidence(1, "budget", "Budget", None, 17, "text", "")], None, {},
                       exact="exact profile", verification="calculation checked",
                       crop_requests=[CropRequest(1, "budget", "Budget", 17, "3,589,478,500.56")])
    a = A.mda_overview(profile, A.deep_as_answer(r, None, {}, "en"), "en")
    out = asyncio.run(A.checked_answer(a, "Tell me about the ministry", "en", object(),
                                       {"settings": make_settings(kasafi_answer_check=True), "client_factory": _Fake},
                                       time.perf_counter()))
    assert [c[0] for c in calls] == [1, 2] and seen["feedback"] == "drop the state deficit"
    assert out.text.startswith(PROFILE) and "9 digital hubs" in out.text and "deficit" not in out.text
    assert out.code_block == PROFILE and out.exact.count("exact profile") == 1 and "The deficit" not in out.exact
    assert out.crop_requests[0].figure == "3,589,478,500.56"    # the profile's crop survives the rewrite


def test_a_deep_reading_gets_the_deep_time_limit_whatever_its_words(monkeypatch) -> None:
    """Dev, 5 Nov: a 'deep' reading restated as '… including its budget and spending' got the 165 s limit."""
    question = f"Tell me about the {MINISTRY} in Sokoto State including its budget and spending"
    assert not D.deep_question(question)
    seen = {}
    real_wait = asyncio.wait_for

    async def wait_for(aw, timeout=None):
        seen["limit"] = timeout
        aw.close()
        raise asyncio.TimeoutError
    monkeypatch.setattr(A.asyncio, "wait_for", wait_for)
    try:
        asyncio.run(A._answer_finished(question, "en", None, understanding=SimpleNamespace(capability="deep")))
        assert seen["limit"] == D.TIME_BUDGET_S
        asyncio.run(A._answer_finished(question, "en", None, understanding=SimpleNamespace(capability="budget")))
        assert seen["limit"] == A.LOOP_BUDGET_S
    finally:
        monkeypatch.setattr(A.asyncio, "wait_for", real_wait)


# --- 2. an overview keeps only figures whose page names the subject -----------------------------------------------

def test_how_a_page_names_each_kind_of_subject() -> None:
    assert ABOUT.search(f"{MINISTRY} budget") and ABOUT.search("the INNOVATION & DIGITAL ECONOMY desk")
    assert ABOUT.search("027900100100 23010113 PURCHASE OF COMPUTERS")          # the code alone, on a budget row
    assert not ABOUT.search(DEFICIT) and not ABOUT.search(INSURANCE) and not ABOUT.search("021500100100 buses")
    # a one-word ministry: the word alone is on any page
    health = D.subject_pattern("agency", "Ministry of Health")
    assert health.search("State Ministry of Health") and not health.search("one-year health insurance")
    lga = D.subject_pattern("lga", "Dange Shuni LGA")
    assert lga.search("Dange-Shuni") and lga.search("DANGE SHUNI 117") and not lga.search("Wamakko 12")
    fac = D.subject_pattern("facility", "Specialist Hospital Sokoto")
    assert fac.search("Specialist Hospital, Sokoto") and not fac.search("Women and Children Hospital")
    dims = [D.Dimension("coverage", ["immunization coverage"], False, [D.Measure("a", "antenatal care", ["midwives"])])]
    sector = D.subject_pattern("sector", "health", "", dims)
    assert sector.search("the hospital") and sector.search("Antenatal care, four visits")
    assert sector.search("Immunization, 12 months") and not sector.search(DEFICIT)
    assert D.subject_pattern("lga", "Sokoto State") is None and D.subject_pattern("agency", "") is None


class _Conn:
    def __init__(self, pages):
        self.pages = pages

    def execute(self, sql, params=()):
        return SimpleNamespace(fetchone=lambda: (self.pages.get(params),) if params in self.pages else None)


def _claim(value, doc, page, statement="x", **kw):
    return D.Claim("dim", statement, value, "", "", "", doc, doc, page, **kw)


def test_only_figures_whose_page_names_the_subject_stay() -> None:
    conn = _Conn({("citizen", 10): DEFICIT, ("isp", 14): INSURANCE, ("fs", 147): ROWS,
                  ("plan", 3): f"The {MINISTRY} will set up 9 Digital Hubs and train 1,200 teachers."})
    claims = [_claim("233,813,940,788", "citizen", 10, "the ministry's deficit"),      # says the ministry; the page doesn't
              _claim("6,000", "isp", 14),
              _claim("58,000,000.00", "fs", 147, "computers"), _claim("9", "plan", 3), _claim("1,200", "plan", 3),
              _claim("75,000,000.00", "fs", 147, "computers"),                         # another ministry's row
              _claim("₦1.2 billion", "budget", 2, from_rows=True),                     # code's own: no page check
              _claim("26.6%", "budget", 2, calculated=True), _claim("12", "registry:x", 0)]
    kept = D.about_subject(conn, claims, ABOUT)
    assert [c.value for c in kept] == ["58,000,000.00", "9", "1,200", "₦1.2 billion", "26.6%", "12"]
    assert D.about_subject(conn, claims, None) == claims        # not an overview: nothing filtered


def test_a_table_row_of_another_subject_is_refused_on_a_page_that_names_the_subject() -> None:
    assert D.page_about(ROWS, "40,000,000.00", ABOUT) and D.page_about(ROWS, "₦42 million", ABOUT)
    assert not D.page_about(ROWS, "75 million", ABOUT)
    assert D.page_about(WRAPPED, "33 million", ABOUT) and not D.page_about(WRAPPED, "66 million", ABOUT)
    # a table about the subject whose rows don't repeat its name: the heading names it
    headed = f"{MINISTRY}\n" + "\n".join(f"Line {i} 1{i},000,000.00 2,000,000.00" for i in range(5))
    assert D.page_about(headed, "12,000,000.00", ABOUT)
    assert not D.page_about("Line 1 12,000,000.00 2,000,000.00\n" * 5, "12,000,000.00", ABOUT)


def test_the_overviews_subject_is_read_from_the_plan_and_the_reading() -> None:
    def plan(*entities):
        return A.Plan(english_question="q", search_queries=[], doc_ids=[], need=Need(standalone_question="q", entities=list(entities)))
    u = lambda level, name="": SimpleNamespace(level=level, name=name)  # noqa: E731
    one = Entity("mda", MINISTRY, resolved=MINISTRY, code="027900000000")
    assert A.overview_subject(plan(one), u("agency", MINISTRY), None) == ("agency", MINISTRY, "027900000000")
    assert A.overview_subject(plan(), u("agency", "SEMA"), None) == ("agency", "SEMA", "")
    assert A.overview_subject(plan(), u("lga", "Wamakko"), None) == ("lga", "Wamakko", "")
    assert A.overview_subject(plan(), u("lga"), {"lga": "Bodinga"}) == ("lga", "Bodinga", "")
    assert A.overview_subject(plan(), u("facility", "Specialist Hospital Sokoto"), None) == \
        ("facility", "Specialist Hospital Sokoto", "")
    assert A.overview_subject(plan(), u("state", "Sokoto State"), None, "tell me about health in Sokoto") == \
        ("sector", "health", "")
    assert A.overview_subject(plan(), u("state", "Sokoto State"), None, "What's the state of PHCs in Sokoto?") == \
        ("sector", "health", "")
    assert A.overview_subject(plan(), u("facility", "PHCs"), None, "the state of PHCs") == ("sector", "health", "")
    # wider than one subject: not filtered
    assert A.overview_subject(plan(), u("state", "Sokoto State"), None, "Compare health and education") is None
    assert A.overview_subject(plan(), u("state", "Sokoto State"), None, "How is Sokoto State doing?") is None
    assert A.overview_subject(plan(), u("ward", "Kalambaina"), None, "what's happening in my area?") is None


# --- 3. crops come from rows about the subject ---------------------------------------------------------------------

def test_a_crop_is_only_from_a_row_about_the_subject() -> None:
    assert D.subject_figure(ROWS, "₦40 million", ABOUT) == "40,000,000.00"
    assert D.subject_figure(WRAPPED, "33 million", ABOUT) == "33,000,000.00"
    assert D.subject_figure(ROWS, "75,000,000.00", ABOUT) == ""
    # printed on the subject's row and on another's: the crop goes to the first on the page, so it can't be used
    assert D.subject_figure(ROWS, "58,000,000.00", ABOUT) == ""
    assert D.subject_figure(f"The {MINISTRY} will spend 12.5% of the total.", "12.5%", ABOUT) == "12.5"


def test_an_overview_never_falls_back_to_a_crop_off_its_subject() -> None:
    claims = [_claim("9", "plan", 3, printed="9"), _claim("₦40 million", "fs", 147, printed="40,000,000.00"),
              _claim("₦1.2 billion", "budget", 2, from_rows=True)]
    r = D.DeepResult("It plans hubs.", [], "", "", claims, ["plan"], 0.0, 1.0, about=ABOUT)
    a = A.deep_as_answer(r, None, {}, "en")
    assert [(c.doc_id, c.figure) for c in plan_crops(a, 2)] == [("fs", "40,000,000.00")]
    bare = D.DeepResult("It plans hubs.", [], "", "", [claims[0]], ["plan"], 0.0, 1.0, about=ABOUT)
    assert plan_crops(A.deep_as_answer(bare, None, {}, "en"), 2) == []
    # not an overview: the crops are chosen from the answer's figures, as before
    wide = D.DeepResult("It costs 40,000,000.00.", [], "", "", [_claim("40,000,000.00", "fs", 147)], ["fs"], 0.0, 1.0)
    assert A.deep_as_answer(wide, None, {}, "en").crop_requests is None
    assert [c.figure for c in plan_crops(A.deep_as_answer(wide, None, {}, "en"), 2)] == ["40,000,000.00"]


def test_an_overviews_two_crops_are_the_profiles_row_and_the_documents_row() -> None:
    profile = A.Answer(PROFILE, True, True, [A.Evidence(1, "budget", "Budget", None, 17, "text", ""),
                                             A.Evidence(2, "budget", "Budget", None, 26, "text", "")], None, {},
                       verification="calculation checked",
                       crop_requests=[CropRequest(1, "budget", "Budget", 17, "3,589,478,500.56"),
                                      CropRequest(2, "budget", "Budget", 26, "2,751,000,000.00")])
    claim = _claim("₦40 million", "fs", 147, printed="40,000,000.00")
    r = D.DeepResult("It spent ₦40 million.", [], "", "", [claim], ["fs"], 0.0, 1.0, about=ABOUT)
    out = A.mda_overview(profile, A.deep_as_answer(r, None, {}, "en"), "en")
    assert [(c.n, c.doc_id, c.figure) for c in plan_crops(out, 2)] == [(1, "budget", "3,589,478,500.56"),
                                                                        (3, "fs", "40,000,000.00")]
    assert out.cited[2].doc_id == "fs" and out.cited[2].n == 3
    none = D.DeepResult("It plans hubs.", [], "", "", [_claim("9", "plan", 3)], ["plan"], 0.0, 1.0, about=ABOUT)
    assert [c.figure for c in plan_crops(A.mda_overview(profile, A.deep_as_answer(none, None, {}, "en"), "en"), 2)] == \
        ["3,589,478,500.56", "2,751,000,000.00"]


def test_every_claim_from_a_page_is_the_checks_evidence() -> None:
    r = D.DeepResult("x", [], "", "", [_claim("₦21 million", "fs", 189, "salary gap"), _claim("₦40 million", "fs", 189, "internet")],
                     ["fs"], 0.0, 1.0)
    a = A.deep_as_answer(r, None, {}, "en")
    assert len(a.cited) == 1 and "salary gap" in a.cited[0].text and "internet" in a.cited[0].text


@pytest.mark.parametrize("text", [DEFICIT, INSURANCE])
def test_the_two_figures_trace_629_cropped_arent_about_the_ministry(text) -> None:
    assert not ABOUT.search(text) and not re.search(ABOUT, text)
