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
    plain = _answer("NEMA's report of 26 September 2025 lists 7 affected LGAs in Sokoto State, not naming Wamakko.")
    assert ck.code_rules(plain, u, (0, 0)) == []                 # no Yes/No, the place named: the model judges it


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


def test_an_answer_computed_in_code_is_judged_on_its_subject_only() -> None:
    class Says:
        provider = "fake"

        def __init__(self, reply):
            self.reply = reply

        async def chat(self, messages, **kw):
            return N(content=self.reply)
    place = ans.Answer("Greenest wards of Gwadabawa: Huchi 0.69 … Agriculture: ₦23,674,744,186 across 58 lines.",
                       True, True, exact="Greenest wards …", verification="calculation checked")
    s = N(kasafi_check_timeout_s=10)
    unsupported = '{"verdict": "revise", "subject": {"place": true, "topic": true}, "unsupported": ["Agriculture"]}'
    assert asyncio.run(ck.check("q", place, None, [], None, s, Says(unsupported))).verdict == "pass"
    off = '{"verdict": "revise", "subject": {"place": true, "topic": false, "note": "asked about people"}}'
    assert asyncio.run(ck.check("q", place, None, [], None, s, Says(off))).verdict == "revise"   # wrong subject


def test_a_check_that_cannot_run_never_blocks_the_answer() -> None:
    class Broken:
        provider = "fake"

        async def chat(self, messages, **kw):
            raise TimeoutError
    v = asyncio.run(ck.check("q", _answer("Dange Shuni has 91 public primary schools."), None, [], None,
                             N(kasafi_check_timeout_s=5), Broken()))
    assert v.verdict == "skipped" and v.why


def test_the_check_writes_no_reply_text_its_outputs_are_the_verdict_and_feedback() -> None:
    assert "safe_answer" not in ck.SYSTEM and "never write the answer yourself" in ck.SYSTEM
    assert not hasattr(ck.Verdict(), "safe_answer")


def test_the_partial_answer_is_the_drafts_supported_lines_built_in_code() -> None:
    a = _answer("Dange Shuni has 91 public primary schools. It has 40 junior secondary schools.")
    v = ck.Verdict("fail", missing=["SSS counts"], unsupported=["40 junior secondary schools"])
    text, supported, kept = ck.partial_answer(a, v, "en")
    assert supported and "91 public primary" in text and "40" not in text
    assert "Not found in the documents I read: SSS counts." in text and [e.page for e in kept] == [19]
    assert "Sokoto State Annual School Census 23-24 Report" in text            # the sources line
    flagged = ck.Verdict("fail", contradictions=["\"Dange Shuni has 91 public primary schools\" contradicts p. 19"])
    nothing, ok, kept = ck.partial_answer(_answer("Dange Shuni has 91 public primary schools."), flagged, "en")
    assert not ok and not kept
    assert nothing == "I couldn't find a checked figure for what you asked in the documents I have. The figures I " \
                      "found weren't on the pages they were cited to, so I left them out."
    # plain words: one sentence per part that couldn't be found (repeats dropped), the reason once, no checker
    # wording and no list of document titles
    v = ck.Verdict("fail", missing=["Erosion spending in Wamakko LGA approved/spent",
                                    "erosion spending in Wamakko LGA approved/spent", "Whether Wamakko was listed"],
                   subject={"place": False}, why="place")
    assert v.wrong_subject
    text = ck.nothing_text(_answer("Sokoto State spent ₦1bn on roads."), v, "en")
    assert text == "I couldn't find erosion spending in Wamakko LGA approved/spent in the documents I have. " \
                   "I couldn't find whether Wamakko was listed in the documents I have. " \
                   "What I read was about something else, so I didn't send it."
    assert "Census" not in text and "documents I read were" not in text
    ha = ck.nothing_text(_answer("x"), ck.Verdict("fail", missing=["IQS counts for Sokoto North"]), "ha")
    assert ha == "Ban samu IQS counts for Sokoto North a cikin takardun da nake da su ba. Shafukan da na karanta ba " \
                 "su buga shi ba."


def test_a_refused_or_wrong_subject_draft_keeps_nothing() -> None:
    a = _answer("I found documents about your question, but couldn't verify the figures.", verification="unsupported")
    a.verified = False
    text, ok, kept = ck.partial_answer(a, ck.Verdict("fail", missing=["the IQS count"]), "en")
    assert not ok and not kept and "couldn't verify" not in text and "the IQS count" in text
    wrong = ck.Verdict("fail", subject={"place": False}, missing=["Wamakko's figures"])
    text, ok, kept = ck.partial_answer(_answer("Sokoto State has 91 schools."), wrong, "en")
    assert not ok and "91" not in text


def test_a_missing_item_whose_figure_is_printed_is_not_called_missing() -> None:
    a = _answer("x")
    assert ck.truly_missing(["Dange Shuni primary schools: 91 (2023/24)", "IQS schools in Dange Shuni"], a) == \
        ["IQS schools in Dange Shuni"]


def test_one_bad_claim_goes_and_codes_total_and_parts_stay_first_in_the_main_answer() -> None:
    """Live, Sokoto North: the check stopped an invented IQS figure and the fallback left only private 8 and 6: the
    public 23, 23, 14 and the total 60 shared figures with the check's complaint, and 60 stayed in show working."""
    block = ("Sokoto North had *60* public schools in 2023/24.\n\n• public primary: 23 (page 19)\n"
             "• public junior secondary: 23 (page 44)\n• public senior secondary: 14 (page 53)\n\n"
             "Not added (the census counts a private school at each level it offers):\n• private junior secondary: 8 "
             "(page 44)\n• private senior secondary: 6 (page 53)")
    page = "SOKOTO NORTH 23 45,939 14\nSOKOTO NORTH 23 30,866 8\nSOKOTO NORTH 14 26,096 6"
    a = _answer(f"{block}\n\nSokoto North has 31 IQS schools.\n\n📄 *Sources:* ASC, p. 19", cited_text=page)
    a.code_block, a.working = block, "Total, calculated in code: 23 + 23 + 14 = 60"
    v = ck.Verdict("fail", unsupported=["31 IQS schools, set against the 23, 23, 14 and 60 public schools"],
                   missing=["IQS schools in Sokoto North"], round=2)
    text, ok, _ = ck.partial_answer(a, v, "en")
    assert ok and text.startswith("Sokoto North had *60* public schools in 2023/24.")
    assert "public primary: 23" in text and "public senior secondary: 14" in text and "private senior secondary: 6" in text
    assert "31" not in text and "Not found in the documents I read: IQS schools in Sokoto North." in text
    assert ck.working_note(a, v, "en", True).endswith("One part, IQS schools in Sokoto North, isn't in the documents, "
                                                      "so it was left out.")


def test_the_checks_feedback_never_reaches_a_reply() -> None:
    v = ck.Verdict("fail", subject={"place": False}, feedback="Ka dawo da rarraben da ke cikin EVIDENCE")
    text, ok, _ = ck.partial_answer(_answer("Sokoto State has 91 schools."), v, "ha")
    assert not ok and "EVIDENCE" not in text and "Ka dawo" not in text and "abin da ka tambaya" in text


def test_codes_total_survives_a_place_or_level_complaint_but_not_a_wrong_topic() -> None:
    block = "Sokoto North had *60* public schools in 2023/24.\n\n• public primary: 23 (page 19)"
    a = _answer(f"{block}\n\nA sentence the check disliked.", cited_text="SOKOTO NORTH 23")
    a.code_block, a.working = block, "Total, calculated in code: 23 + 23 + 14 = 60"
    text, ok, _ = ck.partial_answer(a, ck.Verdict("fail", subject={"place": False}), "en")
    assert ok and text.startswith("Sokoto North had *60*") and "disliked" not in text
    text, ok, _ = ck.partial_answer(a, ck.Verdict("fail", subject={"topic": False}), "en")
    assert not ok and "60" not in text


def test_a_place_the_user_named_must_be_named_in_a_written_answer() -> None:
    u = N(name="Wamakko LGA", level="lga", restatement="Was Wamakko affected?", asked_parts=[])
    no = _answer("For Sokoto State, NEMA listed 7 affected LGAs without naming them.", cited_text="Sokoto 7")
    assert any(r.startswith("subject_not_named") for r in ck.code_rules(no, u, (0, 0)))
    yes = _answer("NEMA's reports give no figure for Wamakko; for Sokoto State they list 7 LGAs.", cited_text="Sokoto 7")
    assert ck.code_rules(yes, u, (0, 0)) == []


def test_the_writer_gets_a_try_before_any_fallback_and_code_answers_keep_place_and_level() -> None:
    v = ck.settle(_answer("x"), ck.Verdict("fail", unsupported=["y"]), [], 1)
    assert v.verdict == "revise"
    place = ans.Answer("Bodinga wards …", True, True, exact="x", verification="calculation checked")
    v = ck.settle(place, ck.Verdict("revise", subject={"place": False, "level": False, "topic": True}), [], 1)
    assert v.verdict == "pass" and not v.wrong_subject
    v = ck.settle(place, ck.Verdict("revise", subject={"topic": False}), [], 1)
    assert v.verdict == "revise" and v.wrong_subject


def test_show_working_says_it_in_plain_words() -> None:
    from app.agent.attribution import state_line
    assert state_line("figures checked", "en", 4) == "All 4 figures were found on the cited pages."
    assert ck.FOUND_SOME["en"].format(found=3, figs=4) == "3 of the 4 figures were found on the cited pages."


def test_a_draft_whose_only_fault_is_a_gap_is_kept_with_its_code_total_and_the_gap_said() -> None:
    a = _answer("• public primary schools: 91 (page 19)\n• public junior secondary schools: 14 (page 19)\n\n"
                "Total (schools): *105*, added up by Kasafi from the 2 parts above.\n\n📄 *Sources:* ASC, p. 19")
    a.working = "Total, calculated in code: 91 + 14 = 105"
    v = ck.Verdict("fail", missing=["IQS schools in Dange Shuni"])
    text, ok, _ = ck.partial_answer(a, v, "en")
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


def test_questions_back_to_the_user_are_not_checked_and_deep_analyses_are() -> None:
    assert ck.should_check(_answer("Dange Shuni has 91 schools."))
    assert not ck.should_check(ans.Answer("Which one?", False, True, clarify=[{"title": "a"}]))
    assert not ck.should_check(ans.Answer("Send your pin", False, True, needs_pin=True))
    deep = _answer("A long analysis.")
    deep.deep = object()
    assert ck.should_check(deep)                    # 3 Nov: a deep answer about poverty for a child-health question


def test_a_revise_round_reads_again_and_a_second_failure_sends_only_what_is_supported(monkeypatch) -> None:
    drafts = iter([_answer("Yes, Sokoto State is listed. It can't tell whether Wamakko is one.", cited_text="Sokoto"),
                   _answer("Yes, Sokoto State is listed again.", cited_text="Sokoto")])
    seen: list[dict] = []

    async def fake_finished(question, lang, conn, **kw):
        seen.append(kw)
        return next(drafts)
    verdicts = iter([ck.Verdict("revise", subject={"place": False}, feedback="asked about Wamakko", round=1),
                     ck.Verdict("fail", subject={"place": False}, round=2, missing=["whether Wamakko is listed"])])

    async def fake_check(message, a, u, history, conn, settings, client, *, round_=1, model=None, **kw):
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
    # both drafts were about another place: nothing of them is sent, only what is missing, in code's words
    assert a.text == "I couldn't find whether Wamakko is listed in the documents I have. What I read was about " \
                     "something else, so I didn't send it."
    assert a.partial and "wasn't about what you asked, so it wasn't sent" in a.working and not a.maps
    assert [c["verdict"] for c in a.checks] == ["revise", "fail"]


def _flood_answer(text: str = "Which wards of Dange Shuni flooded most in 2026: Bodai 0.1%, Tuntube-Tsefe 0.0%.") \
        -> ans.Answer:
    """A flood answer written in code by the place path, with its map."""
    return ans.Answer(text, True, True, exact=text, working="Ranking: Bodai 0.1% … (radar, Copernicus GFM)",
                      verification="calculation checked", maps=[{"layer": "gfm", "level": "lga", "unit": "NG034005"}],
                      timings={"place_area": 0.1})


def _run_checked(monkeypatch, drafts: list, verdicts: list) -> ans.Answer:
    drafts_it, verdicts_it = iter(drafts), iter(verdicts)

    async def fake_finished(question, lang, conn, **kw):
        return next(drafts_it)

    async def fake_check(message, a, u, history, conn, settings, client, *, round_=1, model=None, **kw):
        v = next(verdicts_it)                       # the model's verdict, settled by code's rules as in check()
        return ck.settle(a, ck.Verdict(**{**ck.asdict(v), "round": round_}), ck.code_rules(a, u, ck.found_count(a)),
                         round_)

    class Client:
        provider = "fake"

        async def __aenter__(self):
            return self

        async def __aexit__(self, *a):
            return None
    monkeypatch.setattr(ans, "_answer_finished", fake_finished)
    monkeypatch.setattr(ans.answer_check, "check", fake_check)
    monkeypatch.setattr(ans, "check_client", lambda settings, factory: Client())
    from tests.helpers import make_settings
    u = N(capability="place_history", name="Dange Shuni", level="lga", restatement="Which wards flooded most?")
    return asyncio.run(ans.answer_question("Which wards of Dange Shuni flooded most in 2026?", "en", object(),
                                           settings=make_settings(kasafi_answer_check=True), understanding=u,
                                           history=[]))


def test_a_code_computed_flood_answers_map_always_reaches_the_user(monkeypatch) -> None:
    # the model calls it 'not ward-level' and a figure 'unsupported': computed in code, the subject matches: passes
    level = ck.Verdict("revise", subject={"place": True, "topic": True, "level": False}, unsupported=["0.1%"])
    a = _run_checked(monkeypatch, [_flood_answer()], [level])
    assert a.maps == [{"layer": "gfm", "level": "lga", "unit": "NG034005"}] and "Bodai 0.1%" in a.text
    # a gap the draft doesn't state: computed in code and on the subject, it passes with its map
    gap = ck.Verdict("revise", subject={"place": True, "topic": True}, missing=["hectares per ward"])
    a = _run_checked(monkeypatch, [_flood_answer()], [gap])
    assert a.maps == [{"layer": "gfm", "level": "lga", "unit": "NG034005"}] and a.text == _flood_answer().text


def test_a_partial_answer_keeps_the_attachments_of_what_it_keeps(monkeypatch) -> None:
    """A page answer with a map and a crop, failed twice for an unstated gap: its supported lines are sent with the
    map and the cited page (its crop); a calculation offer stays."""
    def draft():
        a = _answer("Dange Shuni has 91 public primary schools (page 19).")
        a.maps, a.offer = [{"layer": "schools", "level": "lga"}], "OFFER"
        return a
    gap = ck.Verdict("revise", subject={"place": True, "topic": True}, missing=["IQS schools in Dange Shuni"])
    a = _run_checked(monkeypatch, [draft(), draft()], [gap, ck.Verdict("fail", subject={"place": True},
                                                                       missing=["IQS schools in Dange Shuni"])])
    assert a.text.startswith("Dange Shuni has 91 public primary schools (page 19).")
    assert "Not found in the documents I read: IQS schools in Dange Shuni." in a.text
    assert a.maps == [{"layer": "schools", "level": "lga"}] and [e.page for e in a.cited] == [19] and a.offer == "OFFER"


LF_B_DRAFT = ("Dange Shuni LGA has 117 public schools counted as separate schools in the 2023/2024 ASC: 91 public "
              "primary + 18 public junior secondary + 8 public senior secondary = 117.\n\n"
              "• public primary schools in Dange Shuni LGA: 91 (page 19)\n"
              "• public junior secondary schools in Dange Shuni LGA: 18 (page 44)\n"
              "• public senior secondary schools in Dange Shuni LGA: 8 (page 53)")


def test_a_named_part_the_answer_leaves_out_breaks_a_rule_and_a_higher_level_line_satisfies_it() -> None:
    """3 Nov, live failure B: 'I mean all the total schools primary, senior secondary and junior secondary and IQS'
    got primary, JSS and SSS and nothing on IQS, which the census gives only for the whole state."""
    u = N(name="Dange Shuni", level="lga", restatement="How many schools of each level are in Dange Shuni LGA?",
          asked_parts=["primary", "JSS", "SSS", "IQS"])
    rules = ck.code_rules(_answer(LF_B_DRAFT), u, (0, 0))
    assert any(r.startswith("named_part_missing: IQS") for r in rules) and not any(" JSS " in r for r in rules)
    stated = LF_B_DRAFT + ("\n\nThe census gives IQS schools only for the whole state: 123 Islamiyya Integrated "
                           "primary schools (2023/24, page 22); it prints no figure for Dange Shuni.")
    assert ck.code_rules(_answer(stated), u, (0, 0)) == []
    hausa = LF_B_DRAFT + "\n\nƘidayar ta ba da makarantun IQS na jiha baki ɗaya kaɗai: 123 (shafi 22)."
    assert ck.code_rules(_answer(hausa), u, (0, 0)) == []


def test_named_parts_reach_the_writer_and_the_check() -> None:
    p = ans.Plan(english_question="q", search_queries=[], doc_ids=[], asked_parts=["primary", "IQS"])
    assert "6p. Every part, level or kind listed under PARTS THE USER NAMED" in ans.ANSWER_SYSTEM
    assert "higher level" in ans.ANSWER_SYSTEM.split("6p.")[1].split("6k.")[0] and p.asked_parts == ["primary", "IQS"]
    text = ck.user_text("I mean … and IQS", "How many schools?", [], "draft", "(none)", "figures checked", [], (0, 0), 1,
                        parts=["primary", "IQS"])
    assert "PARTS THE USER NAMED: primary, IQS" in text
    from app.agent.understand import parse
    u = parse({"restatement": "How many schools?", "asked_parts": ["primary", "JSS", "", "IQS"]})
    assert u.asked_parts == ["primary", "JSS", "IQS"]


def test_the_named_parts_rule_has_its_own_switch(monkeypatch) -> None:
    from app.agent import answer_check
    from tests.helpers import make_settings
    monkeypatch.setattr("app.config.get_settings", lambda: make_settings(kasafi_named_parts=False))
    u = N(name="Dange Shuni", level="lga", restatement="q", asked_parts=["IQS"])
    assert answer_check.named_parts_missing(_answer(LF_B_DRAFT), u) == []


def test_overnight_round_1_check_rules() -> None:
    """4 Nov overnight, round 1: 'No 2028 budget is in the library' is not a Yes/No verdict; a deep analysis is judged
    on its subject only (its claims are verified in deep.py); a draft with no figures is sent as written."""
    u = N(name="Shehu Shagari University of Education", level="agency", restatement="q", asked_parts=[])
    plain = _answer("No 2028 approved budget is in the library (approved budgets: 2024-2026).", cited_text="2024 2025 2026")
    assert ck.code_rules(plain, u, (0, 0)) == []
    assert any(r.startswith("yes_no") for r in ck.code_rules(_answer("No, it isn't in the 2026 budget.", cited_text="x"), u, (0, 0)))
    deep = _answer("Education in Sokoto: 15,039 primary teachers in 2022 …", cited_text="nothing of this")
    deep.deep = object()
    assert ck.computed_in_code(deep)
    v = ck.settle(deep, ck.Verdict("fail", unsupported=["15,039 primary teachers"], subject={"topic": True}), [], 2)
    assert v.verdict == "pass"
    text, ok, _ = ck.partial_answer(plain, ck.Verdict("fail", unsupported=["the 2028 gap isn't evidenced"]), "en")
    assert ok and text.startswith("No 2028 approved budget is in the library")
