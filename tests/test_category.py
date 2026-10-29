"""Category-of-spending answers: economic codes, per-agency sums checked against printed totals (app/agent/category.py)."""

import asyncio
from decimal import Decimal

import pytest

from app.agent import answer as ans
from app.agent import category as cat
from app.agent.line_answer import listing
from app.retrieval.line_search import Line
from tests.helpers import make_settings

NAMES = {"052100100100": "Ministry of Health", "052100300100": "Primary Health Care Development Agency",
         "052111400100": "Agency for Malaria Control", "053500100100": "Ministry of Environment",
         "051400100100": "Ministry for Women Affairs", "025210200100": "Water Board"}


def test_term_words_must_each_start_a_word_of_the_code_name() -> None:
    assert cat.matches("drugs", "DRUGS/LABORATORY/MEDICAL SUPPLIES")
    assert cat.matches("medical supplies", "DRUGS/LABORATORY/MEDICAL SUPPLIES")
    assert cat.matches("medical equipment", "PURCHASE OF HEALTH / MEDICAL EQUIPMENT")
    assert not cat.matches("medical equipment", "PURCHASE OF OFFICE EQUIPMENT")


def test_a_ministry_scope_includes_its_agencies_by_the_first_four_digits() -> None:
    name, group, units, clarify = cat.resolve_scope("Ministry of Health", NAMES)
    assert (name, group, clarify) == ("Ministry of Health", True, [])
    assert set(units) == {"052100100100", "052100300100", "052111400100"}
    name, group, units, _ = cat.resolve_scope("Agency for Malaria Control", NAMES)
    assert (name, group, units) == ("Agency for Malaria Control", False, ["052111400100"])
    name, group, units, _ = cat.resolve_scope("Primary Health Care Development Agency", NAMES)
    assert (name, group, units) == ("Primary Health Care Development Agency", False, ["052100300100"])
    assert cat.resolve_scope("", NAMES)[2] == []
    assert cat.resolve_scope("Ministry of Space Travel", NAMES)[2] == []        # nothing fits: no scope


def test_two_ministries_fitting_equally_ask_which() -> None:
    names = {"052100100100": "Ministry of Health", "059900100100": "Ministry of Health"}
    assert len(cat.resolve_scope("Ministry of Health", names)[3]) == 2


def test_rows_are_labelled_by_their_level_for_the_composer() -> None:
    def ln(code, cls):
        return Line("x", "t", "d", 1, "T", "n", "n", cls, "", "", 1.0, code=code)
    assert ans.level(ln("11", "programme")) == "sector total"
    assert ans.level(ln("050601", "programme")) == "programme inside a sector"
    assert ans.level(ln("027900000000", "administrative")) == "ministry total including its agencies"
    assert ans.level(ln("027900100100", "administrative")) == "one agency or unit"
    gh = Line("x", "t", "d", 1, "T", "Government House", "n", "administrative", "", "", 1.0, code="011100100100",
              spend_kind="overhead")
    assert ans.kind_of(gh) == "overhead (running costs)"
    assert "level: one agency or unit | spending: overhead (running costs)" in listing([gh])


@pytest.fixture(scope="module")
def conn():
    psycopg = pytest.importorskip("psycopg")
    from app.config import get_settings
    s = get_settings()
    if not s.has_database:
        pytest.skip("no database configured")
    try:
        c = psycopg.connect(s.db_url(), connect_timeout=3)
        if not c.execute("SELECT 1 FROM budget_lines WHERE doc_id = 'budget-2026-approved' LIMIT 1").fetchone():
            pytest.skip("2026 budget not indexed")
    except psycopg.OperationalError:
        pytest.skip("dev database not available")
    yield c
    c.close()


class Pick:
    """The code-mapping call: picks the drugs and medical-equipment codes from the candidates it is shown."""
    def __init__(self):
        self.shown = ""

    async def __call__(self, client, messages, **kw):
        self.shown = messages[-1]["content"]
        return {"codes": ["22020307", "23010122"]}


def test_m05_statewide_totals_and_the_ministry_of_health_share(conn) -> None:
    """Checked against the 2026 budget: 22020307 = 2,713,572,400 (p28), 23010122 = 31,556,212,445 (p29); the
    agencies' rows add up to both exactly."""
    pick = Pick()
    spec = {"terms": ["drugs", "medical supplies", "medical equipment"], "scope": "Ministry of Health",
            "year": 2026, "measure": "approved"}
    res = asyncio.run(cat.run_category(conn, spec, "drugs and hospital equipment, Ministry of Health, 2026",
                                       ["budget-2026-approved"], None, make_settings(), pick))
    assert "22020307 DRUGS/LABORATORY/MEDICAL SUPPLIES" in pick.shown and "2,713" not in pick.shown  # names only
    printed = {c.code: (c.printed.amount, c.printed.page) for c in res.codes}
    assert printed == {"22020307": (Decimal("2713572400.00"), 28), "23010122": (Decimal("31556212445.00"), 29)}
    assert res.checked and res.scope_group and res.scope_name == "Ministry of Health"
    assert res.scope_total == Decimal("32746446845.00")
    a = ans.category_answer(conn, ans.Plan("q", [], ["budget-2026-approved"], category=spec), res, "en", {}, None)
    assert "2,713,572,400.00" in a.exact and "31,556,212,445.00" in a.exact and "32,746,446,845.00" in a.exact
    assert "95.6%" in a.text and "add up exactly" in a.text and not a.partial
    assert ("budget-2026-approved", 28) in {(e.doc_id, e.page) for e in a.cited}


def test_spending_so_far_comes_from_the_latest_report_and_is_said_apart(conn) -> None:
    spec = {"terms": ["drugs", "medical equipment"], "scope": "Ministry of Health", "year": 2026, "measure": "approved"}
    res = asyncio.run(cat.run_category(conn, spec, "q", ["budget-2026-approved"], None, make_settings(), Pick()))
    assert res.report and res.report[0].startswith("bir-2026") and res.spent is not None
    a = ans.category_answer(conn, ans.Plan("how much was allocated and spent", [], [], category=spec), res, "en",
                            {}, None)
    assert "had been spent statewide" in a.text and any(e.doc_id == res.report[0] for e in a.cited)


class PickSport:
    async def __call__(self, client, messages, **kw):
        return {"codes": ["22021009"]}          # SPORTING ACTIVITIES, near "office running costs" in meaning only


def test_codes_that_name_none_of_the_terms_are_not_a_category(conn) -> None:
    """m19: "office running costs" mapped to SPORTING ACTIVITIES; that is not added up."""
    spec = {"terms": ["office running costs", "overhead"], "scope": "", "year": 2026, "measure": "approved"}
    assert asyncio.run(cat.run_category(conn, spec, "q", ["budget-2026-approved"], None, make_settings(),
                                        PickSport())) is None


def test_unchecked_sums_give_the_printed_totals_only(conn) -> None:
    pick = Pick()
    spec = {"terms": ["drugs", "medical equipment"], "scope": "Ministry of Health", "year": 2026, "measure": "approved"}
    res = asyncio.run(cat.run_category(conn, spec, "q", ["budget-2026-approved"], None, make_settings(), pick))
    res.codes[0].unit_sum += Decimal("1000")             # as if an agency row had been misread
    a = ans.category_answer(conn, ans.Plan("q", [], [], category=spec), res, "en", {}, None)
    assert "don't give a breakdown" in a.text and "largest" not in a.text and "95.6%" not in a.text and a.partial
