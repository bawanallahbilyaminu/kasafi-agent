"""Quality checks at indexing time: catch extraction problems before a user meets them.

Each check looks for a problem we have actually had (docs/extraction-lessons.md). Problems are
"fail" (the index is probably wrong somewhere) or "warn" (worth a human look). A document with
any failure goes to the review queue (the `gaps` table, reason "quality"), with the pages to look at.

Checks:
  labelled_rows  budget/performance documents must have labelled table rows ("Label: value");
                 none at all means the column labelling missed the layout.
  code_in_cell   a labelled cell holding a bare budget code ("Q1 Performance: 23020105").
  bracket_cell   a labelled cell still in brackets ("Revised Budget: (25,000)"): a quantity read
                 as a value, or an accounting negative the minus-sign rule missed.
  totals         on a page with labelled 2-digit sector rows and a Total row of the same table, the
                 sector rows must add up to the Total in each column (within 0.5%).
  units          tables in thousands or millions (N'000, =N= million): answers must say so (warn).
  page_numbers   the printed page number differs from the PDF page we cite, by a fixed offset (warn).
  image_pages    pages that are pictures with no OCR text yet (warn; OCR fills them).
"""

from __future__ import annotations

import json
import logging
import re
from collections import Counter
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation

import psycopg

log = logging.getLogger(__name__)

TABLE_CATEGORIES = {"budget", "budget_performance"}
TOTAL_TOLERANCE = Decimal("0.005")
MAX_PAGES_LISTED = 15

_CELL = re.compile(r"(?:^| \| )([^|:]{3,80}): ([^|]+?)(?= \||$)", re.M)
_SECTOR_ROW = re.compile(r"^(\d{2}) [^|]+ \| ", re.M)
_TOTAL_ROW = re.compile(r"^Total(?: Expenditure)? \| ", re.M)
_UNITS = re.compile(r"(?i)(N'000|₦'000|naira'000|in thousands|=N=\s*million|N\s*million|₦\s*million|in millions)")
_PRINTED = re.compile(r"(?i)\bpage\s*\|?\s*(\d{1,4})\b")


@dataclass
class Report:
    doc_id: str
    fails: dict[str, list[int]] = field(default_factory=dict)    # check -> pages
    warns: dict[str, str] = field(default_factory=dict)          # check -> note

    @property
    def ok(self) -> bool:
        return not self.fails

    def add(self, check: str, page: int) -> None:
        pages = self.fails.setdefault(check, [])
        if page not in pages and len(pages) < MAX_PAGES_LISTED:
            pages.append(page)


def _amount(v: str) -> Decimal | None:
    v = v.strip()
    if v in ("-", ""):
        return Decimal(0)
    try:
        return Decimal(v.replace(",", ""))
    except InvalidOperation:
        return None


def check_totals(text: str) -> bool:
    """False when a page's 2-digit rows don't add up to the Total row below them (same columns).

    Summary pages mix revenue codes (11-14) and expenditure codes (21-23): "Total Expenditure" is the sum
    of the 2x rows only (2026 budget p1: 21 + 22 + 23 = 758,700,526,537.89). Rows are grouped by their
    first digit, and a total is compared with its own group, when that group has at least two rows.
    """
    groups: dict[str, list[dict]] = {}
    for line in text.splitlines():
        if m := _SECTOR_ROW.match(line):
            groups.setdefault(m.group(1)[0], []).append(dict(_CELL.findall(line)))
        elif _TOTAL_ROW.match(line) and groups:
            kind = "2" if line.startswith("Total Expenditure") and "2" in groups else \
                   next(iter(groups)) if len(groups) == 1 else None
            rows = groups.get(kind, []) if kind else []
            if len(rows) >= 2:
                for col, tv in dict(_CELL.findall(line)).items():
                    t = _amount(tv)
                    parts = [_amount(r[col]) for r in rows if col in r]
                    if t is None or not t or len(parts) != len(rows) or any(p is None for p in parts):
                        continue
                    if abs(sum(parts) - t) > abs(t) * TOTAL_TOLERANCE:
                        return False
            groups = {}
    return True


def check_document(doc_id: str, category: str | None, pages: list[tuple[int, str, str]]) -> Report:
    """`pages`: (page, labelled text, source). The labelled text is what was chunked."""
    rep = Report(doc_id)
    labelled = waiting = 0
    offsets = Counter()
    for page, text, source in pages:
        for label, value in _CELL.findall(text):
            labelled += 1
            v = value.strip()
            if re.fullmatch(r"\d{5,}", v):
                rep.add("code_in_cell", page)
            elif re.fullmatch(r"\(\d[\d,]*(?:\.\d+)?\)", v):
                rep.add("bracket_cell", page)
        if not check_totals(text):
            rep.add("totals", page)
        if m := _PRINTED.search(text):
            offsets[page - int(m.group(1))] += 1
        waiting += source == "none"
    if waiting:
        rep.warns["image_pages"] = f"{waiting} pages wait for OCR"
    if category in TABLE_CATEGORIES and labelled == 0 and pages:
        rep.add("labelled_rows", pages[0][0])
    if any(_UNITS.search(t) for _, t, _ in pages):
        rep.warns["units"] = "tables state units in thousands or millions; answers must keep the unit"
    if offsets:
        offset, n = offsets.most_common(1)[0]
        if offset and n >= 3:
            rep.warns["page_numbers"] = f"printed page = PDF page - {offset} on {n} pages; citations use the PDF page"
    return rep


def run(conn: psycopg.Connection, doc_id: str, category: str | None, pages: list[tuple[int, str, str]]) -> Report:
    """Check a document just indexed; a failing one goes to the review queue."""
    rep = check_document(doc_id, category, pages)
    conn.execute("DELETE FROM gaps WHERE reason = 'quality' AND missing_doc = %s AND status = 'open'", (doc_id,))
    if not rep.ok:
        conn.execute("INSERT INTO gaps (question, missing_doc, reason, detail) VALUES (%s, %s, 'quality', %s)",
                     (f"Quality check failed for {doc_id}", doc_id, json.dumps({"fails": rep.fails, "warns": rep.warns})))
        log.warning("quality check failed for %s: %s", doc_id, rep.fails)
    elif rep.warns:
        log.info("quality notes for %s: %s", doc_id, rep.warns)
    return rep
