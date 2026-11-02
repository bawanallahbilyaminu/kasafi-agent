"""The bulk import of a publisher's site (app/acquisition/bulk.py) and the personal-data screen
(app/acquisition/personal.py). Free: no network, no model."""

import pytest

from app.acquisition import bulk
from app.acquisition.personal import PLACEHOLDER, personal_reason, screen_pages

U = "https://mof.sk.gov.ng/wp-content/uploads/"


@pytest.mark.parametrize("title, file, cls", [
    ("Sokoto State 2026 Q3 BIR WORD REPORT CN CR", "Sokoto-State-2026-Q3-BIR-WORD-REPORT-CN-CR.pdf", "bir"),
    ("BPR3-C BPR Publication Q4 2024", "BPR3-C-BPR-Publication-Q4-2024-.pdf", "bir"),
    ("Sokoto State Government 2025 AMENDED BUDGET", "x.pdf", "budget"),
    ("2026-Citizens-Budget-ENGLISH-&-HAUSA-VERSION-FOR-WEBSITE", "x.pdf", "citizens"),
    ("2021 MTEF", "propossed-budget-2021-2023.pdf", "mtef"),
    ("Sokoto-Health-Sector-2025-202-MTSS-updated", "x.pdf", "mtef"),
    ("9-Point-Agenda-2026-Sokoto-State", "x.pdf", "plans"),
    ("Sokoto State audited financial statements 2019", "x.pdf", "accounts"),
    ("Invitation-to-One-Day-Town-Hall-Meeting-on-2020 Covid 19 Budget", "x.pdf", "other"),
    ("Call Circular for Year 2026 Budget Proposals", "x.pdf", "other"),
    ("Report on banditry attacks in the eastern LGAs", "x.pdf", "excluded"),
    ("APC campaign manifesto", "x.pdf", "excluded"),
])
def test_classes_from_the_title_and_file_name(title, file, cls) -> None:
    assert bulk.classify(title, U + file) == cls


def test_editions_from_the_title() -> None:
    assert bulk.edition_of("Sokoto State 2026 Q3 BIR WORD REPORT", U + "a.pdf", "bir")[:2] == ("sokoto_bir", "2026-Q3")
    assert bulk.edition_of("budget-performance-report-for-2nd-quarter-2023", U + "a.pdf", "bir")[:2] == \
        ("sokoto_bir", "2023-Q2")
    assert bulk.edition_of("Appropriation Law, 2025", U + "a.pdf", "budget")[:2] == ("sokoto_budget", "2025")
    assert bulk.edition_of("2026-First-Amended-Budget", U + "a.pdf", "budget")[:2] == (None, None)


class FakeConn:
    def __init__(self, docs):
        self.docs = docs

    def execute(self, sql, params=None):
        class R:
            def __init__(self, rows):
                self.rows = rows

            def fetchall(self):
                return self.rows
        if "source_url" in sql:
            return R([(d, u, "") for d, u, _, _ in self.docs])
        return R([(d, s, e) for d, _, s, e in self.docs if s])


def test_the_plan_dedupes_known_urls_site_copies_and_same_editions_and_orders_by_class() -> None:
    conn = FakeConn([("bir-2025-q3", U + "q3.pdf", "sokoto_bir", "2025-Q3"),
                     ("budget-2026-approved", "", "sokoto_budget", "2026")])
    items = [bulk.Item(U + "q3.pdf", "Sokoto State 2025 Q3 BIR", "pdf"),
             bulk.Item(U + "laws.pdf", "Fiscal responsibility law", "pdf", size=1000),
             bulk.Item(U + "laws-1.pdf", "Fiscal responsibility law", "pdf", size=1000),
             bulk.Item(U + "law26.pdf", "Sokoto State 2026 Appropriation Law", "pdf"),
             bulk.Item(U + "q3-26.pdf", "Sokoto State 2026 Q3 BIR", "pdf", date="2026-10-27"),
             bulk.Item(U + "bandits.pdf", "Bandit attacks report", "pdf")]
    out = bulk.plan(conn, items)
    by = {i.url.rsplit("/", 1)[-1]: i for i in out}
    assert by["q3.pdf"].status == "duplicate" and "bir-2025-q3" in by["q3.pdf"].dedupe
    assert by["laws-1.pdf"].status == "duplicate" and "site copy" in by["laws-1.pdf"].dedupe
    assert by["law26.pdf"].status == "new" and by["law26.pdf"].dedupe == "same edition as budget-2026-approved"
    assert by["bandits.pdf"].status == "excluded"
    order = [i.cls for i in out if i.status == "new"]
    assert order.index("budget") < order.index("bir") < order.index("other")
    assert "| budgets and amendments | 1 |" in bulk.report(out, [])


def test_near_duplicate_text_is_found_by_shingles() -> None:
    text = " ".join(f"word{i} figure {i * 7} line" for i in range(200))
    prints = {"rop": bulk.shingles(text), "other": bulk.shingles("something else entirely " * 50)}
    assert bulk.near_duplicate([text], prints)[0] == "rop"
    assert bulk.near_duplicate(["a completely different document " + " ".join(map(str, range(300)))], prints)[0] == ""


PAYROLL = "\n".join(["S/N NAME GRADE LEVEL STEP NET PAY"] +
                    [f"{i} Abubakar Musa{i % 3 and 'wa' or ''} GL 07 3 {45 + i},{100 + i}.00" for i in range(1, 9)])
PHONES = "\n".join(["S/N NAME LGA PHONE NUMBER"] + [f"{i} Fatima Bello Wamakko 0803{i:03d}{i:04d}" for i in range(1, 6)])
BVN = "\n".join(["S/N NAME BVN ACCOUNT NO"] + [f"{i} Usman Garba 2234567890{i} 012345678{i}" for i in range(1, 7)])
BUDGET = "\n".join(["Personnel Expenditure by Administrative Classification",
                    "Primary Health Care Development Agency 707,835,812.00 919,210,444.94",
                    "Ministry of Health 1,203,000,000.00 1,500,000,000.00",
                    "Total Personnel 12,000,000,000.00 13,000,000,000.00"])


def test_lists_of_people_with_phones_ids_or_pay_are_withheld_and_budget_lines_are_not() -> None:
    assert personal_reason(PHONES) == "names with phone numbers"
    assert personal_reason(BVN) == "names with NIN, BVN or account numbers"
    assert personal_reason(PAYROLL) == "names with salaries"
    assert personal_reason(BUDGET) == ""
    pages, withheld = screen_pages([BUDGET, PHONES, "Introduction"])
    assert pages[0] == BUDGET and pages[1] == PLACEHOLDER and withheld == {2: "names with phone numbers"}
