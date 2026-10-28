"""Structured budget rows from the labelled tables (query_budget's data).

The indexer already labels table rows ("7094 TERTIARY EDUCATION | 2026 Approved Budget: 20,666,975,000.00 | ...")
and tracks the table title in force ("Capital Expenditure by Functional Classification"). Here each labelled
cell becomes one typed row:

    document, page, table title, classification (function / administrative / economic / programme /
    project), spending kind (total / capital / personnel / overhead / debt / revenue), code, name,
    year, measure (approved / revised / original / final / actual / estimate / proposal), period
    (full year, January-September, Q1-Q4, ...), amount in naira.

Amounts are kept exactly as printed (Decimal); "-" is 0; a table declared in thousands is scaled to naira.
Percent and balance columns are skipped: they are derived, and query_budget derives them itself.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation

_CELL = re.compile(r" \| ([^|:]{3,90}): ([^|]+?)(?= \||$)")
_CODE_NAME = re.compile(r"^(\d{2,12})\s*-?\s+(.+?)\s*$")
TABLE_CATEGORIES = {"budget", "budget_performance", "fiscal"}
_THOUSANDS = re.compile(r"(?i)(N'000|₦'000|naira'000|in thousands|=N=\s*'000)")


@dataclass
class BudgetRow:
    page: int
    table_title: str
    classification: str
    spend_kind: str
    code: str | None
    name: str
    column_label: str
    year: int | None
    measure: str
    period: str
    amount_naira: Decimal
    row_text: str


def classification(title: str) -> str:
    t = title.lower()
    if ("functional" in t or "by function" in t) and "mda" in t.split():
        return "function_by_mda"       # 2024 budget: each ministry's spending split by function (not the state total)
    if "functional" in t or "by function" in t:
        return "function"
    if "administrative" in t or "mda" in t.split():
        return "administrative"
    if "economic" in t:
        return "economic"
    if "programme" in t or "program" in t:
        return "programme"
    if "project" in t:
        return "project"
    return "other"


def spend_kind_of(title: str) -> str:
    t = title.lower()
    if "revenue" in t or "receipts" in t:
        return "revenue"
    if "capital" in t:
        return "capital"
    if "personnel" in t:
        return "personnel"
    if "overhead" in t or "non-debt recurrent" in t or "other recurrent" in t:   # before "debt": "Non-Debt"
        return "overhead"
    if "debt" in t:
        return "debt"
    if "expenditure" in t:
        return "total"
    return "other"


_PERIODS = [
    (re.compile(r"(?i)year to date \(Q1\s*-\s*Q(\d)\)"), lambda m: "q1" if m.group(1) == "1" else f"q1_q{m.group(1)}"),
    (re.compile(r"(?i)January to September"), lambda m: "jan_sep"),
    (re.compile(r"(?i)\bQ([1-4]) Performance"), lambda m: f"q{m.group(1)}"),
    (re.compile(r"(?i)Full Year Actuals?"), lambda m: "full_year"),
]


def parse_column(label: str) -> tuple[int | None, str, str] | None:
    """'2026 Approved Budget' -> (2026, 'approved', 'full_year'); percent/balance columns -> None."""
    if "%" in label or label.lower().startswith("balance") or "nutrition" in label.lower():
        return None
    m = re.match(r"^(20\d\d)\s+(.*)$", label.strip())
    if not m:
        return None
    year, rest = int(m.group(1)), m.group(2).lower()
    period = "full_year"
    for pattern, name in _PERIODS:
        if pm := pattern.search(label):
            period = name(pm)
            break
    if "approved" in rest:
        measure = "approved"
    elif "revised" in rest:
        measure = "revised"
    elif "original" in rest:
        measure = "original"
    elif "final" in rest:
        measure = "final"
    elif "actual" in rest or "performance" in rest:
        measure = "actual"
    elif "estimate" in rest:
        measure = "estimate"
    elif "proposal" in rest or "executive" in rest:
        measure = "proposal"
    else:
        return None
    return year, measure, period


def _amount(v: str) -> Decimal | None:
    v = v.strip()
    if v == "-":
        return Decimal(0)
    try:
        return Decimal(v.replace(",", ""))
    except InvalidOperation:
        return None


def rows_from_page(page: int, text: str, title: str, factor: int = 1) -> list[BudgetRow]:
    """Typed rows from one labelled line set, under the table title in force for each line."""
    out: list[BudgetRow] = []
    for line in text.splitlines():
        if " | " not in line or ": " not in line:
            continue
        head, _, _ = line.partition(" | ")
        cells = _CELL.findall(line)
        if not cells:
            continue
        m = _CODE_NAME.match(head.strip())
        code, name = (m.group(1), m.group(2)) if m else (None, head.strip())
        if not name or len(name) > 200:
            continue
        for label, value in cells:
            parsed = parse_column(label)
            amount = _amount(value)
            if parsed is None or amount is None:
                continue
            year, measure, period = parsed
            out.append(BudgetRow(page, title, classification(title), spend_kind_of(title), code, name.strip(" -"),
                                 label.strip(), year, measure, period, amount * factor, line))
    return out


def extract_rows(labelled_pages: list[str], titles: list[list[str]]) -> list[BudgetRow]:
    """`titles[i][j]` is the table title in force for line j of page i (from the indexer)."""
    rows: list[BudgetRow] = []
    for i, text in enumerate(labelled_pages, start=1):
        factor = 1000 if _THOUSANDS.search(text) else 1
        for line, title in zip(text.splitlines(), titles[i - 1]):
            rows.extend(rows_from_page(i, line, title, factor))
    return rows
