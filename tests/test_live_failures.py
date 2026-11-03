"""The 3 Nov live failures (A-E) as structure, not as questions: a not-found answer never turns into a budget note
for a schools question; one document's figures aren't labelled 'Newest' or 'By source'; the progress line never
claims several sources publish figures."""

from app.acquisition.registry import Publisher, registry
from app.agent import answer as ans
from app.agent import topics as tp

ASC = Publisher("sokoto_asc", "Sokoto State Annual School Census 23-24 Report", ("sokotoeducation.gov.ng",),
                level="lga", tier=1)


def _plan(q: str) -> ans.Plan:
    return ans.Plan(english_question=q, search_queries=[], doc_ids=[], original=q)


def test_a_schools_question_that_nothing_answers_never_gets_the_lga_budget_note() -> None:
    q = "How many total primary, junior secondary, senior secondary and IQS schools are in Dange Shuni LGA?"
    a = ans._not_found(None, _plan(q), "en", None, {}, gap=False)
    assert "budget" not in a.text.lower() and "Dange Shuni" not in a.text
    money = ans._not_found(None, _plan("How much did the state budget give Dange Shuni LGA in 2025?"), "en", None,
                           {}, gap=False)
    assert money.text.startswith("The state budget doesn't show money allocated directly to Dange Shuni")


def test_one_documents_figures_are_not_newest_or_by_source() -> None:
    cards = [tp.Card(ASC, "asc", ASC.name, 19, "91", "schools", "public primary schools", "2023/2024 ASC",
                     "Dange Shuni LGA"),
             tp.Card(ASC, "asc", ASC.name, 26, "20", "schools", "public pre-primary schools", "2023/2024 ASC",
                     "Dange Shuni LGA")]
    text, _ = tp.compose(registry().topics["education"], [tp.SourceResult(ASC, "asc", status="ok", cards=cards)],
                         [], "en")
    assert text.startswith("📊 *91 schools* – public primary schools, Dange Shuni LGA")
    assert "Newest" not in text and "By source" not in text and "In this document:" in text


def test_the_progress_line_names_what_is_checked_never_several_sources() -> None:
    for lang in ("en", "ha"):
        line = tp.PROGRESS[lang].format(n=2, names="ASC, NBS")
        assert "Several sources" not in line and "majiyoyi da yawa" not in line and "2" in line
