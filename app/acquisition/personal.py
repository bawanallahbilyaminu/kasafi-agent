"""Personal data in public documents (2 Nov 2026): pages listing people are withheld.

A page is withheld when it lists people together with a personal identifier or pay: names with phone numbers,
NIN/BVN, bank account numbers or salaries (beneficiary lists, nominal rolls, payment schedules). Budget lines for
personnel costs are not personal data: they name posts and agencies, not people. The document is still indexed;
a withheld page keeps a placeholder for its text and has no chunks, OCR, charts or crops (migration 0028).
"""

from __future__ import annotations

import re

import psycopg

PLACEHOLDER = ("[Page withheld by Kasafi: it lists people with personal data (phone numbers, ID or account numbers, "
               "or salaries). It is not searched, quoted or shown.]")

PHONE = re.compile(r"(?<!\d)(?:\+?234[\s-]?|0)[789][01]\d[\s-]?\d{3}[\s-]?\d{4}(?!\d)")
LONG_ID = re.compile(r"(?<![\d,.])\d{10,11}(?![\d,.])")          # NIN and BVN are 11 digits, NUBAN accounts 10
ID_HEADER = re.compile(r"(?i)\b(?:NIN|BVN|account\s*(?:no|number|num)|acct\.?\s*no|NUBAN|phone\s*(?:no|number)?|"
                       r"GSM|tel(?:ephone)?\.?\s*no|mobile|IPPIS|staff\s*(?:id|no)|file\s*no|salary|grade\s*level|"
                       r"net\s*pay|gross\s*pay)\b")
# a row that starts with a person's name: an optional serial, then two or three capitalised words
NAME_ROW = re.compile(r"(?m)^\s*(?:\d{1,4}[.)]?\s+)?(?:(?:Alh|Mal|Hajiya|Dr|Mr|Mrs|Miss|Engr)\.?\s+)?"
                      r"[A-Z][A-Za-z'’-]{1,20}\s+[A-Z][A-Za-z'’-]{1,20}(?:\s+[A-Z][A-Za-z'’-]{1,20})?\b")
SALARY_ROW = re.compile(r"(?m)^\s*(?:\d{1,4}[.)]?\s+)?[A-Z][A-Za-z'’-]+\s+[A-Z][A-Za-z'’-]+.*?\b\d{1,3}(?:,\d{3})+"
                        r"(?:\.\d{2})?\s*$")
AGENCY_WORDS = re.compile(r"(?i)\b(?:ministry|agency|board|commission|office|department|government|council|"
                          r"total|sub-total|programme|project|construction|purchase|fund|hospital|college|school|"
                          r"cost|costs|salary|salaries|wages|overhead|expenditure|recurrent|transport|travel|"
                          r"utilities|materials|supplies|allowance|allowances|loans?|advances|charges|maintenance|"
                          r"capital|revenue|personnel|general|others|description|code)\b")
NAME_HEADER = re.compile(r"(?i)\b(?:names?|full\s+name|surname)\b")


def personal_reason(text: str) -> str:
    """Why a page is withheld, or '' when it isn't a list of people with personal data."""
    t = text or ""
    names = [m.group(0) for m in NAME_ROW.finditer(t) if not AGENCY_WORDS.search(m.group(0))]
    if len(PHONE.findall(t)) >= 3 and len(names) >= 3:
        return "names with phone numbers"
    # an ID list has a name column and an ID column; a budget's or accounts' 11-digit codes are neither (2 Nov:
    # the 2021 proposed budget's project codes and the 2019 accounts' agency codes were withheld)
    if len(LONG_ID.findall(t)) >= 5 and len(names) >= 5 and NAME_HEADER.search(t) and \
            re.search(r"(?i)\b(?:NIN|BVN|account\s*(?:no|number)|acct\.?\s*no|NUBAN)\b", t):
        return "names with NIN, BVN or account numbers"
    # a pay list has a name column; a budget's 'SALARY' and 'PERSONNEL COST' lines have none (2 Nov: the 2023
    # approved budget's personnel tables were flagged)
    if NAME_HEADER.search(t) and re.search(r"(?i)\b(?:salary|net\s*pay|gross\s*pay|grade\s*level)\b", t):
        rows = [r for r in SALARY_ROW.findall(t) if not AGENCY_WORDS.search(r)]
        if len(rows) >= 5:
            return "names with salaries"
    return ""


def screen_pages(pages: list[str]) -> tuple[list[str], dict[int, str]]:
    """(pages with the withheld ones replaced by the placeholder, {page number: reason})."""
    out, withheld = [], {}
    for i, text in enumerate(pages, 1):
        if why := personal_reason(text):
            withheld[i] = why
            out.append(PLACEHOLDER)
        else:
            out.append(text)
    return out, withheld


def record_withheld(conn: psycopg.Connection, doc_id: str, withheld: dict[int, str]) -> None:
    """After indexing: the placeholder pages leave search (no chunks, no budget lines) and are listed."""
    if not withheld:
        return
    pages = list(withheld)
    conn.execute("UPDATE pages SET source = 'withheld', text = %s WHERE doc_id = %s AND page = ANY(%s)",
                 (PLACEHOLDER, doc_id, pages))
    conn.execute("DELETE FROM chunks WHERE doc_id = %s AND page = ANY(%s)", (doc_id, pages))
    conn.execute("DELETE FROM budget_lines WHERE doc_id = %s AND page = ANY(%s)", (doc_id, pages))
    for page, why in withheld.items():
        conn.execute("INSERT INTO withheld_pages (doc_id, page, reason) VALUES (%s, %s, %s) "
                     "ON CONFLICT (doc_id, page) DO UPDATE SET reason = EXCLUDED.reason", (doc_id, page, why))


def is_withheld(conn: psycopg.Connection, doc_id: str, page: int) -> bool:
    try:
        return bool(conn.execute("SELECT 1 FROM withheld_pages WHERE doc_id = %s AND page = %s",
                                 (doc_id, page)).fetchone())
    except Exception:              # noqa: BLE001 - before migration 0028
        conn.rollback()
        return False
