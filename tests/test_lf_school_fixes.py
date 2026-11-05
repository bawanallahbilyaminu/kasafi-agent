"""Three things the live school answers of 5 Nov showed (traces 659, 660): the check sent a right answer back for a figure
nobody asked for; a label was cut mid-word; a sentence cited the page number printed on the PDF page, not the PDF page."""

import asyncio
from types import SimpleNamespace

import pytest

from app.agent import answer as A
from app.agent import answer_check as ck
from app.agent import page_refs as PR
from app.agent.understand import Understanding
from app.text import button_title, shorten
from tests.helpers import make_settings


def _u(**kw):
    return Understanding(**{"capability": "statistics", "level": "lga", "name": "Sokoto North",
                            "restatement": "How many schools are in Sokoto North LGA?", **kw})


def _answer(text="Sokoto North had 60 public schools.", **kw):
    return A.Answer(text, True, True, [A.Evidence(1, "asc", "Census", None, 31, "text", "60 schools")], None, {},
                    exact=text, verification="figures checked", **kw)


MESSAGE = "How many schools are in Sokoto North"
LFSN = dict(feedback="add the state figure printed in Table 2.4", missing=["Islamiyya Integrated schools for Sokoto State"],
            subject={"place": True, "time": True, "topic": True, "level": True}, answers_question="partly")


def test_lfsn_a_statewide_figure_nobody_asked_for_is_never_a_reason_to_revise() -> None:
    v = ck.settle(_answer(), ck.Verdict("revise", **LFSN), [], 1, message=MESSAGE, u=_u())
    assert v.verdict == "pass" and v.missing == [] and v.why.startswith("only something nobody asked for")
    assert v.not_asked == ["Islamiyya Integrated schools for Sokoto State"]


def test_what_the_user_asked_for_still_counts_as_missing() -> None:
    # lfB: IQS named by the user, so the statewide IQS figure is what they asked for
    named = _u(asked_parts=["primary", "JSS", "IQS"], restatement="How many schools in Sokoto North at primary, JSS and IQS?")
    v = ck.settle(_answer(), ck.Verdict("revise", missing=["IQS schools for Sokoto State"], subject={"topic": True}), [], 1,
                  message="I mean all the schools and IQS", u=named)
    assert v.verdict == "revise" and v.missing == ["IQS schools for Sokoto State"]
    # the level asked: a state question's state figure, and a place's own figures
    state = _u(level="state", name="Sokoto State", restatement="How many schools are in Sokoto State?")
    assert not ck.not_asked("Schools for Sokoto State", "How many schools are in Sokoto State?", state)
    assert not ck.not_asked("private schools in Sokoto North", MESSAGE, _u())
    assert not ck.not_asked("schools in Sokoto State", "How many in Sokoto North and in Sokoto State?", _u())
    # all levels of what was asked, in another language: the restatement carries the meaning
    ha = _u(restatement="How many schools are in Sokoto North LGA?")
    assert not ck.not_asked("junior secondary schools in Sokoto North", "Makarantu nawa ne a Sokoto North?", ha)


def test_a_thing_sharing_no_word_with_the_question_is_not_asked() -> None:
    u = _u(capability="budget", level="agency", name="Ministry of Health", measure="amount",
           restatement="How much is allocated to the Ministry of Health in 2026?")
    assert ck.not_asked("number of nurses employed", "How much for the Ministry of Health?", u)
    assert not ck.not_asked("2026 allocation of the ministry", "How much for the Ministry of Health?", u)


def test_other_faults_keep_the_revise_and_the_writer_is_told_not_to_add_it() -> None:
    v = ck.settle(_answer(), ck.Verdict("revise", **{**LFSN, "unsupported": ["60 public schools"]}), [], 1,
                  message=MESSAGE, u=_u())
    assert v.verdict == "revise" and "Not asked for, so leave out: Islamiyya" in v.feedback
    wrong = ck.settle(_answer(), ck.Verdict("revise", **{**LFSN, "subject": {"place": False}}), [], 1, message=MESSAGE, u=_u())
    assert wrong.verdict == "revise"
    rule = ck.settle(_answer(), ck.Verdict("revise", **LFSN), ["no_figure_found: none"], 1, message=MESSAGE, u=_u())
    assert rule.verdict == "revise"


def test_without_a_reading_nothing_is_set_aside() -> None:
    v = ck.settle(_answer(), ck.Verdict("revise", **LFSN), [], 1, message=MESSAGE, u=None)
    assert v.verdict == "revise" and v.missing and not v.not_asked


def test_the_prompt_says_it_too() -> None:
    assert "a figure for a higher level" in " ".join(ck.SYSTEM.split())


# --- labels ---------------------------------------------------------------------------------------------------------

def test_a_label_is_never_cut_mid_word() -> None:
    assert shorten("public schools with pre-primary classes (subset of the public Pre-Primary and Primary schools)", 80) == \
        "public schools with pre-primary classes"                     # the live label: the open bracket goes whole
    assert shorten("Construction of a very long road between two towns in the state", 30) == "Construction of a very long…"
    assert shorten("short label", 80) == "short label"
    assert shorten("  spaced   out  ", 80) == "spaced out"
    assert shorten("Supercalifragilisticexpialidocious and more", 10) == "Supercalifragilisticexpialidocious…"
    for text in ("Ministry of Innovation and Digital Economy", "abcdefghijklmnopqrstuvwxyz abc", "Water Board (rural)"):
        for most in (5, 12, 20, 29):
            out = shorten(text, most).rstrip("…")
            assert out == "" or any(text[i:].startswith(out) and (i + len(out) == len(text) or not text[i + len(out)].isalnum())
                                    for i in range(1)), (text, most, out)


def test_a_button_title_fits_whatsapps_limit() -> None:
    assert button_title("Primary Health Care Development Agency") == "Primary Health Care…"
    assert len(button_title("Primary Health Care Development Agency")) <= 20
    assert button_title("Water") == "Water"
    assert len(button_title("Supercalifragilisticexpialidocious")) == 20    # one long word: nothing else can fit


def test_the_part_label_from_the_writer_is_cut_at_a_word() -> None:
    long = "public schools with pre-primary classes (subset of the public Pre-Primary and Primary schools)"
    d = {"parts": [{"label": long, "value": "14", "cited": 1}]}
    ev = A.Evidence(1, "asc", "Census", None, 26, "text", "Sokoto North 14")
    parts = A.checked_parts(d, {1: ev}, [])
    assert parts[0].label == "public schools with pre-primary classes"


# --- pages ----------------------------------------------------------------------------------------------------------

P21 = "SOKOTO State ASC Report; 2023/2024\n3\nTable 2.1 Number of Schools\nPublic 2,100\n"
P22 = ("SOKOTO State ASC Report; 2023/2024\n4\nTable 2.4: Number of public schools with special curriculum\n"
       "Islamiyya Integrated 123 45,697 44,063 89,760\n")
P31 = "Dange Shuni 91 28\nWamakko 120 40\n"
PAGES = [(21, P21), (22, P22), (31, P31)]


def test_lfb_the_page_printed_on_the_sheet_becomes_the_page_verified() -> None:
    text = "The census gives Islamiyya Integrated schools only for the whole state: 123 primary schools in 2023/2024 (p. 4); " \
           "it prints no IQS figure for Dange Shuni LGA."
    out, changes = PR.verified(text, PAGES)
    assert "123 primary schools in 2023/2024 (p. 22);" in out and "p. 4" not in out
    assert changes[0]["said"] == [4] and changes[0]["now"] == [22]


def test_a_right_page_is_left_alone_and_each_figure_is_judged_on_its_own() -> None:
    text = "• public primary schools: 91 (page 31)\n• Islamiyya: 123 (page 22)"
    assert PR.verified(text, PAGES) == (text, [])
    out, changes = PR.verified("Dange Shuni has 91 schools (page 22), and the state 123 Islamiyya (p. 31).", PAGES)
    assert "91 schools (page 31)" in out and "123 Islamiyya (p. 22)" in out and len(changes) == 2


def test_trace_96_a_right_page_after_a_document_title_stays() -> None:
    """'(… Census 23-24 Report, p. 22)': the title's 23-24 aren't figures, and p. 23 of another document is no answer."""
    census = "SOKOTO State ASC Report; 2023/2024\nNomadic 81 2,000\n"
    mtss = "Education Sector MTSS 2023 2024 and 81 schools planned\n"
    pages = [(23, mtss, "Education Sector 2025-2027 Medium-Term Sector Strategy (MTSS)"),
             (22, census, "Sokoto State Annual School Census 23-24 Report")]
    text = "School Census: 81 schools with a nomadic curriculum (Sokoto State Annual School Census 23-24 Report, p. 22)"
    assert PR.verified(text, pages) == (text, [])
    # wrong page in the named document: corrected only within that document
    pages2 = [(23, mtss, pages[0][2]), (22, census, pages[1][2]), (40, "Nothing here\n", pages[1][2])]
    wrong = "81 schools (Sokoto State Annual School Census 23-24 Report, p. 40)"
    assert PR.verified(wrong, pages2)[0] == "81 schools (Sokoto State Annual School Census 23-24 Report, p. 22)"
    # a figure inside the bracket, with no document named, is still judged
    assert PR.verified("Nomadic (81 schools, p. 40)", [(22, census, "Census")])[0] == "Nomadic (81 schools, p. 22)"


def test_a_figure_on_no_cited_page_loses_its_page_number_not_the_sentence() -> None:
    out, changes = PR.verified("The total was 777 schools (p. 22). Next sentence.", PAGES)
    assert out == "The total was 777 schools. Next sentence." and changes[0]["now"] == []
    assert PR.verified("It was 777 schools, p. 22.", PAGES)[0] == "It was 777 schools."


def test_what_cant_be_judged_is_not_touched() -> None:
    no_figure = "The census prints no IQS figure by LGA (p. 22)."
    assert PR.verified(no_figure, PAGES) == (no_figure, [])
    lines = "📄 *Sources:* Census, p. 4, 99\n_Reply *show working* to see 123 on page 9_\nℹ️ Not found: 12 on page 5"
    assert PR.verified(lines, PAGES) == (lines, [])
    assert PR.verified("It was 123 (p. 4).", []) == ("It was 123 (p. 4).", [])       # nothing to verify against
    calc = "Kasafi's calculation: 66.7% (p. 31)."                     # computed in code: on no page, but its page is cited
    assert PR.verified(calc, PAGES, ["66.7%"]) == (calc, [])
    assert PR.verified("a year only: 2023 (p. 4)", PAGES) == ("a year only: 2023 (p. 4)", [])


def test_hausa_and_page_lists() -> None:
    assert PR.verified("Islamiyya 123 (shafi 4)", PAGES)[0] == "Islamiyya 123 (shafi 22)"
    assert PR.verified("Figures 91 (pp. 31, 40).", PAGES)[0] == "Figures 91 (pp. 31)."
    assert PR.verified("In all 91 and 120 (p. 31, 22)", PAGES)[0] == "In all 91 and 120 (p. 31)"
    # a house-style amount is the printed figure
    amounts = [(5, "Line 42,000,000.00\n")]
    assert PR.verified("It was ₦42 million (p. 9).", amounts)[0] == "It was ₦42 million (p. 5)."


def test_every_answer_written_by_a_model_goes_through_it_and_code_made_ones_dont(monkeypatch) -> None:
    box_answer = A.Answer("Islamiyya 123 schools (p. 4).\n\n📄 *Sources:* Census, p. 22", True, True,
                          [A.Evidence(1, "asc", "Census", None, 22, "text", P22)], None, {},
                          exact="x", verification="figures checked")

    async def fake(question, lang, conn, box=None, **kw):
        return box_answer
    monkeypatch.setattr(A, "_answer_question", fake)
    monkeypatch.setattr(A, "covered_years_line", lambda *a, **k: "")
    out = asyncio.run(A._answer_finished("q", "en", None, settings=make_settings()))
    assert out.text.startswith("Islamiyya 123 schools (p. 22).") and "Sources:* Census, p. 22" in out.text
    assert out.timings["page_refs_corrected"] == 1.0
    made = A.Answer("Rain was 123 mm (p. 4).", True, True, [A.Evidence(1, "asc", "C", None, 22, "text", P22)], None, {},
                    exact="x", verification="calculation checked")

    async def fake2(question, lang, conn, box=None, **kw):
        return made
    monkeypatch.setattr(A, "_answer_question", fake2)
    assert "(p. 4)" in asyncio.run(A._answer_finished("q", "en", None, settings=make_settings())).text


def test_the_library_page_is_read_whole() -> None:
    class Conn:
        def execute(self, sql, params=()):
            return SimpleNamespace(fetchall=lambda: [("asc", 22, P22)])
    ev = [A.Evidence(1, "asc", "C", None, 22, "text", "an extract"), A.Evidence(2, "bir", "B", None, 3, "text", "extract 2")]
    assert PR.cited_pages(Conn(), ev) == [(22, P22, "C"), (3, "extract 2", "B")]

    class Broken:
        def execute(self, sql, params=()):
            raise RuntimeError("no database")
    assert PR.cited_pages(Broken(), ev) == [(22, "an extract", "C"), (3, "extract 2", "B")]
    assert PR.cited_pages(None, []) == []


@pytest.mark.parametrize("bad", ["p. 4 and more words", "page 4 of the report"])
def test_only_a_number_after_the_page_word_is_a_page(bad) -> None:
    assert PR.REF.search(bad).group("nums") == "4"
