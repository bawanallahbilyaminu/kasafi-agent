"""The answer check (app/agent/answer_check.py): the rules code decides, the verdict parse, the honest partial answer
built only from supported sentences, the second round with the check's feedback, and the trace's result."""

import asyncio
from types import SimpleNamespace as N

from app.agent import answer as ans
from app.agent import answer_check as ck
from app.agent.trace import check_result

PAGE = ("Table 2.1 Number of schools by LGA. DANGE SHUNI 91 20 28. BINJI 77 15 9. Junior secondary DANGE SHUNI 14.")


def _answer(text: str, cited_text: str = PAGE, verification: str = "figures checked", exact: str = "") -> ans.Answer:
    ev = [ans.Evidence(1, "asc-sokoto-2023-2024", "Sokoto State Annual School Census 23-24 Report", 2024, 19, "text",
                       cited_text)]
    return ans.Answer(text, True, True, ev, verification=verification, exact=exact or text)


def test_a_yes_about_another_place_breaks_the_subject_rule() -> None:
    u = N(name="Wamakko LGA", level="lga", restatement="Was Wamakko LGA affected by floods in 2025, according to NEMA?")
    a = _answer("Yes, Sokoto State is listed as affected by floods in 2025 with 4 LGAs affected. The pages don't "
                "show whether Wamakko is one of the 4.", cited_text="Sokoto 4 4 4,278")
    assert any(r.startswith("yes_no") for r in ck.code_rules(a, u, (0, 0)))
    ok = _answer("Yes: Wamakko LGA is listed among the affected LGAs in 2025.", cited_text="Wamakko")
    assert ck.code_rules(ok, u, (0, 0)) == []
    plain = _answer("NEMA's report of 26 September 2025 lists 7 affected LGAs in Sokoto State but doesn't name them.")
    assert ck.code_rules(plain, u, (0, 0)) == []                 # no Yes/No: the model judges it


def test_an_answer_none_of_whose_figures_is_printed_can_never_pass() -> None:
    a = _answer("Dange Shuni has 93 public primary schools.")
    assert ck.found_count(a) == (1, 0)
    assert ck.code_rules(a, None, ck.found_count(a))[0].startswith("no_figure_found")
    good = _answer("Dange Shuni has 91 public primary schools, 20 public and 28 private pre-primary schools.")
    assert ck.found_count(good) == (3, 3) and ck.code_rules(good, None, ck.found_count(good)) == []
    computed = _answer("Total: 139 schools.", verification="calculation checked")
    assert ck.found_count(computed) == (0, 0)                    # computed in code: the rule doesn't apply


def test_years_and_pages_are_not_figures() -> None:
    assert ck.figures_in("In the 2023/2024 census (p. 19, 26), 91 schools [1]") == ["91"]


def test_a_code_rule_turns_a_model_pass_into_revise_then_fail() -> None:
    a = _answer("Yes, Sokoto State is listed. It can't tell whether Wamakko is one.", cited_text="Sokoto")
    u = N(name="Wamakko", level="lga", restatement="Was Wamakko affected?")

    class Passes:
        provider = "fake"

        async def chat(self, messages, **kw):
            return N(content='{"verdict": "pass", "answers_question": "yes", "subject": {"place": true}}')
    s = N(kasafi_check_timeout_s=10)
    v1 = asyncio.run(ck.check("Was Wamakko affected?", a, u, [], None, s, Passes()))
    v2 = asyncio.run(ck.check("Was Wamakko affected?", a, u, [], None, s, Passes(), round_=2))
    assert v1.verdict == "revise" and v2.verdict == "fail" and v1.wrong_subject


def test_a_check_that_cannot_run_never_blocks_the_answer() -> None:
    class Broken:
        provider = "fake"

        async def chat(self, messages, **kw):
            raise TimeoutError
    v = asyncio.run(ck.check("q", _answer("Dange Shuni has 91 public primary schools."), None, [], None,
                             N(kasafi_check_timeout_s=5), Broken()))
    assert v.verdict == "skipped" and v.why


def test_the_partial_answer_keeps_only_sentences_whose_figures_are_printed() -> None:
    a = _answer("Dange Shuni has 91 public primary schools and 40 JSS.")
    v = ck.Verdict("fail", safe_answer="Dange Shuni has 91 public primary schools (p. 19). It has 40 junior "
                                       "secondary schools. The census tables for SSS weren't in the pages read.",
                   missing=["SSS counts"], unsupported=["40 JSS"])
    text, supported = ck.safe_answer(a, v, "en")
    assert supported and "91 public primary" in text and "40 junior" not in text and "SSS" in text
    assert "Sokoto State Annual School Census 23-24 Report" in text            # the sources line
    nothing, ok = ck.safe_answer(a, ck.Verdict("fail", missing=["the number of IQS in Dange Shuni"],
                                               contradictions=["x"]), "en")
    assert not ok and nothing.startswith("I couldn't give a checked answer to that: the number of IQS")


def test_a_draft_whose_only_fault_is_a_gap_is_kept_with_its_code_total_and_the_gap_said() -> None:
    a = _answer("• public primary schools: 91 (page 19)\n• public junior secondary schools: 14 (page 19)\n\n"
                "Total (schools): *105*, added up by Kasafi from the 2 parts above.\n\n📄 *Sources:* ASC, p. 19")
    a.working = "Total, calculated in code: 91 + 14 = 105"
    v = ck.Verdict("fail", safe_answer="• public primary schools: 91", missing=["IQS schools in Dange Shuni"])
    text, ok = ck.safe_answer(a, v, "en")
    assert ok and "*105*" in text and "14 (page 19)" in text
    assert "Not found in the documents I read: IQS schools in Dange Shuni." in text and text.count("📄") == 1


def test_parse_reads_the_verdict_and_unknowns_become_revise() -> None:
    v = ck.parse({"verdict": "maybe", "missing": ["JSS", "", "SSS"], "subject": {"place": False, "x": 1}}, 1)
    assert v.verdict == "revise" and v.missing == ["JSS", "SSS"] and v.subject == {"place": False}
    assert v.wrong_subject


def test_the_trace_says_how_the_check_ended() -> None:
    assert check_result([{"verdict": "pass"}]) == "passed"
    assert check_result([{"verdict": "revise"}, {"verdict": "pass"}]) == "revised"
    assert check_result([{"verdict": "revise"}, {"verdict": "fail"}]) == "partial"
    assert check_result([{"verdict": "fail"}]) == "partial"
    assert check_result([]) == ""


def test_questions_back_to_the_user_and_deep_analyses_are_not_checked() -> None:
    assert ck.should_check(_answer("Dange Shuni has 91 schools."))
    assert not ck.should_check(ans.Answer("Which one?", False, True, clarify=[{"title": "a"}]))
    assert not ck.should_check(ans.Answer("Send your pin", False, True, needs_pin=True))
    deep = _answer("A long analysis.")
    deep.deep = object()
    assert not ck.should_check(deep)


def test_a_revise_round_reads_again_and_a_second_failure_sends_only_what_is_supported(monkeypatch) -> None:
    drafts = iter([_answer("Yes, Sokoto State is listed. It can't tell whether Wamakko is one.", cited_text="Sokoto"),
                   _answer("Yes, Sokoto State is listed again.", cited_text="Sokoto")])
    seen: list[dict] = []

    async def fake_finished(question, lang, conn, **kw):
        seen.append(kw)
        return next(drafts)
    verdicts = iter([ck.Verdict("revise", subject={"place": False}, feedback="asked about Wamakko", round=1),
                     ck.Verdict("fail", subject={"place": False}, round=2,
                                safe_answer="NEMA lists 4 affected LGAs in Sokoto State without naming them.")])

    async def fake_check(message, a, u, history, conn, settings, client, *, round_=1, model=None):
        return next(verdicts)

    async def fake_understand(message, history, place, settings, fallbacks=None, feedback=""):
        return N(capability="statistics", name="Wamakko", level="lga", restatement="Was Wamakko affected?")

    class Client:
        provider = "fake"

        async def __aenter__(self):
            return self

        async def __aexit__(self, *a):
            return None
    monkeypatch.setattr(ans, "_answer_finished", fake_finished)
    monkeypatch.setattr(ans.answer_check, "check", fake_check)
    monkeypatch.setattr("app.agent.understand.understand_message", fake_understand)
    monkeypatch.setattr(ans, "check_client", lambda settings, factory: Client())
    from tests.helpers import make_settings
    s = make_settings(kasafi_answer_check=True)
    u = N(capability="place_history", name="Wamakko", level="lga", restatement="Was Wamakko affected?")
    a = asyncio.run(ans.answer_question("Was Wamakko affected?", "en", object(), settings=s, understanding=u,
                                        history=[]))
    assert seen[1]["review"]["feedback"] == "asked about Wamakko"            # the second round got the feedback
    assert seen[1]["understanding"].capability == "statistics"              # and the message read again
    assert a.text.startswith("NEMA lists 4 affected LGAs in Sokoto State without naming them.")   # never the draft
    assert a.partial and "Answer check: the first answer wasn't sent" in a.working
    assert [c["verdict"] for c in a.checks] == ["revise", "fail"]
