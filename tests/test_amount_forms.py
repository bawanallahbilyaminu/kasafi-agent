"""An amount written in house style is the printed figure it stands for, on every path (5 Nov 2026). The matcher
(`unverified_numbers`, app/agent/figures.py) is shared by the page answers' figure check, the answer check's count,
the partial answer's supported lines and the deep analysis's claim check. Trace 590 had failed only where the count
fed it bare numbers ('100' for '₦100 million'); these tests pin every written form on each of those paths, and that
an invented amount is still caught.

And an amount must sit on the row that names it: the same trace's draft gave '₦42 million for computer purchases'
when 42,000,000.00 is the office-repairs row."""

import pytest

from app.agent import answer_check as ck
from app.agent import deep as D
from app.agent.answer import Evidence, unverified_numbers

PAGE = ("Line A 100,000,000.00\nLine B 1,200,000,000\nLine C 750,000\nLine D 2500000000.00\nLine E 42,000,000.00\n"
        "Line F 3,590,123,456.78\nLine G 15.5 per cent\nLine H 1,234")
EV = [Evidence(1, "d", "Budget", None, 5, "text", PAGE)]

SAME = ["₦100 million", "N100 million", "NGN 100m", "₦100m", "100 million naira", "₦100,000,000", "100,000,000.00",
        "₦1.2 billion", "₦1.2bn", "1.2 bn", "₦1.20 billion", "₦750k", "₦750 thousand", "750,000", "₦2.5 billion",
        "₦2.50bn", "₦42 million", "₦42m", "₦3.59 billion", "₦3.6 billion", "15.5%", "1,234",
        "naira miliyan 100", "miliyan 100", "biliyan 1.2", "dubu 750"]
INVENTED = ["₦777 million", "₦4.2 billion", "₦101 million", "₦1.3bn", "₦75k", "miliyan 77", "16.5%"]


@pytest.mark.parametrize("written", SAME)
def test_a_written_form_of_a_printed_amount_is_verified(written) -> None:
    assert unverified_numbers(f"The line is {written}.", EV) == []


@pytest.mark.parametrize("written", INVENTED)
def test_an_amount_the_page_does_not_print_is_still_caught(written) -> None:
    assert unverified_numbers(f"The line is {written}.", EV) != []


def _answer(text: str):
    from types import SimpleNamespace
    return SimpleNamespace(text=text, exact=text, verification="figures checked", working="", cited=EV, verified=True,
                           found=True, code_block="")


def test_the_answer_checks_count_keeps_each_amounts_unit() -> None:
    """The count behind 'none of the answer's figures is printed in its cited pages' (not only for deep analysis)."""
    text = "Line A is ₦100 million, line B ₦1.2bn, line C ₦750k and line E ₦42 million."
    n, found = ck.found_count(_answer(text))
    assert (n, found) == (4, 4) and ck.code_rules(_answer(text), None, (n, found)) == []
    n, found = ck.found_count(_answer("Line A is ₦777 million and line B ₦4.2 billion."))
    assert (n, found) == (2, 0)
    mixed = ck.found_count(_answer("Line A is ₦100 million; line Z is ₦999 million."))
    assert mixed == (2, 1)


def test_the_partial_answer_keeps_a_house_style_line_and_drops_an_invented_one() -> None:
    kept = ck.supported("Line A is ₦100 million. Line Z is ₦999 million. Line B is ₦1.2bn.", _answer(""))
    assert "₦100 million" in kept and "₦1.2bn" in kept and "999" not in kept


def test_a_deep_claims_value_is_accepted_in_any_written_form() -> None:
    for value in ("100,000,000.00", "100 million", "₦1.2 billion", "1.2bn", "₦750k", "750 thousand", "42,000,000"):
        assert D.verify_claim({"value": value, "page": 5}, {5: PAGE}), value
    assert not D.verify_claim({"value": "777 million", "page": 5}, {5: PAGE})


def test_a_bare_letter_after_a_number_is_money_only_with_a_currency_mark() -> None:
    """The one deliberate limit (app/agent/figures.py): '5 m' may be metres and '12 k' a footnote, so the single
    letters k, m and b are a scale only after ₦ / N / NGN. Kasafi's own answers always write the mark."""
    assert unverified_numbers("The line is ₦750k.", EV) == []
    assert unverified_numbers("The road is 750k long.", EV) != []
    assert not D.verify_claim({"value": "750k", "page": 5}, {5: PAGE})


# the audited financial statement's page as it is stored (2024 Audited Financial Statement, p. 147)
ROWS = """230 CAPITAL EXPENDITURE
Admin Code Economic Code Admin Economic 2024 Revised Budget Actual 2024 Variance 2024
027900100100 23030121 Ministry of Innovation and Digital Economy REHABILITATION / REPAIRS OF OFFICE BUILDINGS 42,000,000.00 0.00 42,000,000.00
027900100100 23010112 Ministry of Innovation and Digital Economy PURCHASE OF OFFICE FURNITURE AND FITTINGS 30,000,000.00 0.00 30,000,000.00
027900100100 23010113 Ministry of Innovation and Digital Economy PURCHASE OF COMPUTERS 40,000,000.00 40,000,000.00 0.00
027900100100 23020101 Ministry of Innovation and Digital Economy CONSTRUCTION / PROVISION OF OFFICE BUILDINGS 100,000,000.00 45,000,000.00 55,000,000.00
027900100100 23010108 Ministry of Innovation and Digital Economy PURCHASE OF BUSES 80,000,000.00 0.00 80,000,000.00
027900100100 23010113 Ministry of Innovation and Digital Economy PURCHASE OF COMPUTERS 100,000,000.00 11,560,000.00 88,440,000.00"""


def test_an_amount_is_refused_when_its_row_names_something_else() -> None:
    """Trace 590: '₦42 million for computer purchases'. 42,000,000.00 is printed on the page (so the old check
    passed it), but on the office-repairs row; the computers rows print 40,000,000.00 and 100,000,000.00."""
    pages = {147: ROWS}
    wrong = {"statement": "actual spending of the Ministry of Innovation and Digital Economy on computer purchases",
             "value": "42,000,000.00", "page": 147}
    assert D.verify_claim(wrong, pages) and not D.row_bound(wrong, pages)
    wrong_scaled = {**wrong, "value": "42 million"}
    assert not D.row_bound(wrong_scaled, pages)
    right = {"statement": "revised budget for rehabilitation and repairs of office buildings", "value": "42,000,000.00",
             "page": 147}
    assert D.row_bound(right, pages)
    computers = {"statement": "revised budget for the purchase of computers", "value": "40,000,000.00", "page": 147}
    assert D.row_bound(computers, pages)
    buses = {"statement": "the ministry's revised budget for buses", "value": "100 million", "page": 147}
    assert not D.row_bound(buses, pages)                          # 100,000,000.00 is buildings and computers


def test_the_row_rule_stays_out_of_the_way_when_it_cannot_judge() -> None:
    pages = {147: ROWS}
    # the claim names nothing that tells this page's rows apart (the ministry is on every row): not judged
    vague = {"statement": "a capital line of the Ministry of Innovation and Digital Economy", "value": "42,000,000.00",
             "page": 147}
    assert D.row_bound(vague, pages)
    # a prose page is not a table: the printed check alone decides
    prose = {9: "Only 26 of the 84 primary health centres assessed met the minimum staffing standard in 2023."}
    assert D.row_bound({"statement": "PHCs meeting the staffing standard", "value": "26", "page": 9}, prose)
    # a value that sits on no row (a heading, a total elsewhere): not judged
    assert D.row_bound({"statement": "computers", "value": "999,000,000.00", "page": 147}, pages)
    # a total sums the rows a claim may name: not judged
    total = {147: ROWS + "\nTOTAL CAPITAL EXPENDITURE 392,000,000.00 96,560,000.00 295,440,000.00"}
    assert D.row_bound({"statement": "the ministry's capital budget, computers and buses included",
                        "value": "392,000,000.00", "page": 147}, total)
    # a label wrapped onto the line above its amounts still names its row
    wrapped = {147: ROWS + "\n027900100100 23010139 Ministry of Innovation and Digital Economy PURCHASE OF OTHER "
                           "FIXED ASSETS (SOLAR INVERTERS)\n65,000,000.00 5,000,000.00 60,000,000.00"}
    assert D.row_bound({"statement": "revised budget for solar inverters", "value": "65,000,000.00", "page": 147},
                       wrapped)
    assert not D.row_bound({"statement": "revised budget for buses", "value": "65,000,000.00", "page": 147}, wrapped)
