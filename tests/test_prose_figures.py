"""Figures written in running text (1 Nov 2026): every printed form of an amount is a value with its own rounding
(app/agent/figures.py), prose is bound sentence by sentence (attribution.prose_spans), and one figure that can't
be found no longer refuses the answer. Fixture text only, written for these tests (not from any one document)."""

from decimal import Decimal

import pytest

from app.agent import attribution, figures
from app.agent.answer import Evidence, unverified_numbers

PARA = ("Table 4 shows the sector budget for 2024. The analysis shows that the allocation to\n"
        "district hospitals, in absolute values, is low. A small fraction of the budget,\n"
        "NGN2.15 billion out of the total N31.40 billion (or 6.8 percent), was\n"
        "allocated to the agencies that manage district hospitals. This share is below the\n"
        "regional average of NGN3,2 billion per state.\n")
TABLE = "Table 4: Sector budget by unit, 2024\nMinistry 21,500,000,000.0\nTotal 31,402,118,507.4\n"


def ev(text: str, n: int = 1, title: str = "District Hospital Financing Plan") -> Evidence:
    return Evidence(n, "fixture-plan", title, 2024, 7, "text", text)


@pytest.mark.parametrize("printed, value", [
    ("NGN1.94 billion", Decimal("1940000000")), ("N29.62 billion", Decimal("29620000000")),
    ("₦4 billion", Decimal("4000000000")), ("NGN29,6 billion", Decimal("29600000000")),
    ("1.29bn", Decimal("1290000000")), ("NGN 100 billion", Decimal("100000000000")),
    ("₦1,940,000,000", Decimal("1940000000")), ("N 2.5 trillion", Decimal("2500000000000")),
    ("₦850 million", Decimal("850000000")), ("6.5 percent", Decimal("6.5")), ("6.5 per cent", Decimal("6.5")),
    ("31%", Decimal("31")),
])
def test_every_printed_form_reads_as_its_value(printed: str, value: Decimal) -> None:
    got = figures.amounts(printed)
    assert got and got[0].value == value, (printed, got)


def test_rounding_decides_agreement() -> None:
    page = figures.amounts("Total 29,617,906,608.4 and N29.62 billion")
    for said in ("₦29.62 billion", "29,617,906,608.45", "₦29.6 billion", "N29,6 billion"):
        assert figures.found_in(figures.amounts(said)[0], page), said
    assert not figures.found_in(figures.amounts("₦29.7 billion")[0], page)
    assert not figures.found_in(figures.amounts("₦2.96 billion")[0], page)
    pct = figures.amounts("6.5 percent")[0]
    assert figures.found_in(figures.amounts("6.5%")[0], [pct])
    assert not figures.found_in(figures.amounts("6.5 billion")[0], [pct])     # a percent is never an amount


def test_a_decimal_comma_before_million_is_ambiguous_and_reads_as_nothing() -> None:
    assert figures.amounts("N23,11 million") == [] or all(a.value != Decimal("23110000") for a in figures.amounts("N23,11 million"))
    assert figures.amounts("N23,762 million")[0].value == Decimal("23762000000")


def test_the_number_check_accepts_another_printed_form_of_the_same_figure() -> None:
    evidence = [ev(PARA), ev(TABLE, 2)]
    ok = "Of the ₦31,402,118,507.40 budget, ₦2,150,000,000 (6.8%) went to district hospital agencies [1]."
    assert unverified_numbers(ok, evidence) == []
    assert unverified_numbers("The regional average is ₦3.2 billion [1].", evidence) == []
    assert unverified_numbers("₦2.75 billion went to them [1].", evidence) == ["2.75"]


def test_prose_is_bound_by_whole_sentences_not_wrapped_lines() -> None:
    spans = [s for s, _ in attribution.prose_spans(PARA)]
    held = next(s for s in spans if "NGN2.15 billion" in s)
    assert "allocated to the agencies that manage district hospitals" in held     # the wrapped line joined
    this = next(s for s in spans if "regional average" in s)
    assert "NGN2.15 billion" in this and this.index("NGN2.15") < this.index("This share")   # carries its antecedent


def test_a_prose_allocation_binds_without_a_false_kind_or_year_contradiction() -> None:
    answer = ("In 2024, ₦2.15 billion of the ₦31.40 billion sector budget (6.8%) was allocated to the agencies "
              "that manage district hospitals [1].")
    att = attribution.bind(answer, [ev(PARA)])
    assert att.ok and not [p for p in att.problems if not p.startswith("missing")], att.problems
    assert att.state in ("attribution checked", "figures checked")


def test_a_real_contradiction_in_prose_still_refuses() -> None:
    spent = PARA.replace("was\nallocated to", "was\nspent by")
    att = attribution.bind("In 2024, ₦2.15 billion was allocated to the agencies that manage district hospitals [1].",
                           [ev(spent)])
    assert att.state == "unsupported" and any(p.startswith("kind") for p in att.problems)


def test_a_total_row_takes_its_table_titles_words() -> None:
    table = ("Table 4 below shows the sector budget by unit.\nTable 4: Region 2024 total hospital budget by unit\n"
             "Ministry of Hospitals 21,500,000,000.0\nHospitals Board 9,902,118,507.4\nTotal 31,402,118,507.4\n")
    att = attribution.bind("The 2024 hospital budget was ₦31,402,118,507.45 [1].", [ev(table)])
    assert att.ok and not any(p.startswith("entity") for p in att.problems), att.problems
    wrong = attribution.bind("The Ministry of Hospitals budget was ₦31,402,118,507.4 [1].", [ev(table)])
    assert wrong.state == "unsupported" and any(p.startswith("entity") for p in wrong.problems)


def test_one_figure_not_found_marks_it_instead_of_refusing() -> None:
    answer = ("₦2.15 billion of the ₦31.40 billion budget went to district hospital agencies [1], and the plan "
              "proposed ₦5.5 billion for 2025 [1].")
    att = attribution.bind(answer, [ev(PARA)])
    assert att.ok and att.state == "figures checked" and att.unverified == ["5.5 billion"]
    nothing = attribution.bind("₦7.7 billion went to them [1].", [ev(PARA)])
    assert nothing.state == "unsupported"                                    # no figure found at all: refused
