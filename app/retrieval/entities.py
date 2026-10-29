"""Structured budget core: budget_items, projects and perf_items, built from the extraction, with reconciliation.

The labelled cells (budget_rows) become entities with one column per year and measure as printed
(migration 0009). The analysis tools (app/agent/analysis.py) count and add up in SQL on these tables.

  budget_items  every budget line (budgets): classification, spending kind, code, name, the administrative unit
                (MDA) it belongs to. Administrative lines are their own unit; a line in a per-agency table belongs
                to the agency section it is printed under ("052100100100 Ministry of Health Code Description ...").
  projects      the statewide capital project list, parsed from the page text by its code anchors:
                "<name> <12-digit MDA> - <MDA> <8-digit economic> - <item> [<5-digit function> - <function>]
                <8-digit location> - <place> <one amount per column>". The labelled rows can't be used: a wrapped
                project name is split across two of them. One complete list per document: the per-agency and
                sector project tables repeat the same projects and are not read.
  perf_items    implementation-report lines: original / revised / final budget, the quarter's and the year-to-date
                spending.

Reconciliation checks, run at every build (counts and failures go to entity_builds and the log):
  hierarchy     inside one table, the children of every printed parent add up to it: agencies -> ministry ->
                sector -> total; economic, functional, programme and location codes by their prefixes.
  kinds         for every MDA: personnel + overhead + debt + capital = total.
  projects      the projects add up to the printed Total Capital Expenditure, and per MDA to its capital
                allocation in the administrative classification.
  grand_total   the functional and location tables' totals equal the administrative total of the same kind.
"""

from __future__ import annotations

import json
import logging
import re
from collections import defaultdict
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from pathlib import Path

import psycopg

from app.retrieval.tables import parse_column

log = logging.getLogger(__name__)

AMOUNTS = ("actual_2022", "actual_2023", "actual_2024", "jan_sep_2023", "jan_sep_2024", "jan_sep_2025",
           "revised_2023", "revised_2024", "revised_2025", "original_2025", "approved_2024", "approved_2025",
           "approved_2026", "proposal_2024", "estimate_2026", "estimate_2027", "estimate_2028")
PERF_AMOUNTS = ("original", "revised", "final", "quarter_spent", "ytd_spent")
BUDGET_CATEGORIES = {"budget"}
PERF_CATEGORIES = {"budget_performance"}
TOLERANCE = Decimal("1")                 # naira: printed figures are exact to the kobo
MAX_EXAMPLES = 8
KINDS = ("personnel", "overhead", "debt", "capital")

# a per-agency section header: "052100100100 Ministry of Health Code Description 2024 Full Year Actuals ..."
SECTION = re.compile(r"(\d{12})\s+(.{3,120}?)\s+Code\s+Description\s+\d{4}")
_NUM = r"(?:-|\(?-?\d[\d,]*\.\d{2}\)?)"
# codes can be glued to the name before them ("Laptops23010113", "EDUCATION33331800")
PROJECT = re.compile(
    r"(?<!\d)(?P<mda>\d{12}) - (?P<mda_name>.+?) ?(?<!\d)(?P<econ>2\d{7}) - (?P<econ_name>.+?) ?"
    r"(?:(?<!\d)(?P<func>7\d{4}) - (?P<func_name>.+?) ?)?(?<!\d)(?P<loc>3\d{7}) - (?P<loc_name>[^\d|]+?)"
    r"(?P<nums>(?: " + _NUM + r")+)(?= |$)")
PROJECT_TITLE = re.compile(r"Budget\s*-\s*Capital Expenditure by Project\b")
OTHER_TITLE = re.compile(r"Approved Budget\s*-\s*(?!Capital Expenditure by Project)\w")
_HEADER = re.compile(r"Location Code and Description (?P<labels>.+?) Total Capital Expenditure(?P<nums>(?: " + _NUM
                     + r")+)")
_LABEL = re.compile(r"20\d\d\D+?(?= 20\d\d |$)")


def column_of(year: int | None, measure: str, period: str) -> str | None:
    """'2025 Performance January to September' -> jan_sep_2025; '2026 Approved Budget' -> approved_2026."""
    if year is None:
        return None
    if measure == "actual":
        name = f"jan_sep_{year}" if period == "jan_sep" else f"actual_{year}" if period == "full_year" else ""
    else:
        name = f"{measure}_{year}" if period == "full_year" else ""
    return name if name in AMOUNTS else None


def _amount(v: str) -> Decimal | None:
    v = v.strip()
    if v == "-":
        return Decimal(0)
    neg = v.startswith("(") and v.endswith(")")
    try:
        d = Decimal(v.strip("()").replace(",", ""))
    except InvalidOperation:
        return None
    return -d if neg else d


def _seq(line_id: str) -> int:
    _, page, n = line_id.rsplit(":", 2)
    return int(page) * 10000 + int(n)


@dataclass
class Item:
    id: str
    page: int
    seq: int
    table_title: str
    classification: str
    spend_kind: str
    code: str | None
    name: str
    amounts: dict[str, Decimal] = field(default_factory=dict)
    other: dict[str, str] = field(default_factory=dict)
    mda_code: str | None = None
    mda_name: str | None = None


@dataclass
class Project:
    page: int
    name: str
    mda_code: str
    mda_name: str
    econ_code: str
    econ_name: str
    function_code: str | None
    function_name: str | None
    location_code: str
    location_name: str
    amounts: dict[str, Decimal] = field(default_factory=dict)
    other: dict[str, str] = field(default_factory=dict)


@dataclass
class Checks:
    results: dict[str, dict] = field(default_factory=dict)

    def add(self, check: str, ok: bool, example: str = "") -> None:
        r = self.results.setdefault(check, {"passed": 0, "failed": 0, "examples": []})
        r["passed" if ok else "failed"] += 1
        if not ok and example and len(r["examples"]) < MAX_EXAMPLES:
            r["examples"].append(example)

    @property
    def failed(self) -> int:
        return sum(r["failed"] for r in self.results.values())


# --- budget items ------------------------------------------------------------------------------

def sections(conn: psycopg.Connection, doc_id: str) -> tuple[dict[int, list[tuple[int, str, str]]], dict[int, str]]:
    """Per-agency section headers by page ([(offset, admin code, name)]) and each page's flattened text."""
    heads: dict[int, list[tuple[int, str, str]]] = {}
    texts: dict[int, str] = {}
    for page, text in conn.execute("SELECT page, text FROM pages WHERE doc_id = %s ORDER BY page", (doc_id,)):
        texts[page] = " ".join((text or "").split())
        hs = [(m.start(), m.group(1), m.group(2).strip()) for m in SECTION.finditer(texts[page])]
        if hs:
            heads[page] = hs
    return heads, texts


def unit_at(heads: dict[int, list[tuple[int, str, str]]], page: int, pos: int) -> tuple[str, str] | None:
    """The agency section printed last before this position (on this page or an earlier one)."""
    before = [h for h in heads.get(page, []) if h[0] < pos]
    if before:
        return before[-1][1], before[-1][2]
    prev = [p for p in heads if p < page]
    return (heads[max(prev)][-1][1], heads[max(prev)][-1][2]) if prev else None


def assign_units(items: list[Item], heads: dict, texts: dict) -> None:
    """Administrative lines are their own unit; a coded line on a per-agency page, the section it's printed in."""
    first = min(heads) if heads else None
    seen: dict[tuple[int, str], int] = defaultdict(int)
    for it in items:
        if it.classification == "administrative" and it.code and len(it.code) == 12:
            it.mda_code, it.mda_name = it.code, it.name
            continue
        if first is None or not it.code or it.page < first:
            continue           # the statewide and sector summaries come before the agency sections
        text = texts.get(it.page, "")
        at = [m.start() for m in re.finditer(rf"(?<!\d){it.code}(?!\d)", text)]
        n = seen[(it.page, it.code)]
        seen[(it.page, it.code)] += 1
        unit = unit_at(heads, it.page, at[n] if n < len(at) else len(text))
        if unit:
            it.mda_code, it.mda_name = unit


def budget_items(conn: psycopg.Connection, doc_id: str) -> list[Item]:
    items: dict[str, Item] = {}
    for (lid, page, title, cls, kind, code, name, label, year, measure, period, amount) in conn.execute(
            "SELECT line_id, page, COALESCE(table_title, ''), classification, spend_kind, code, name, column_label, "
            "year, measure, period, amount_naira FROM budget_rows WHERE doc_id = %s AND line_id IS NOT NULL",
            (doc_id,)):
        if cls == "project":
            # the statewide project list lives in `projects`; a per-agency economic table printed under a carried-
            # over "by Project" title (2026 budget pp. 82-209) has economic codes: it is an economic line
            if not (code and re.fullmatch(r"\d{1,8}", code)):
                continue
            cls = "economic"
        it = items.get(lid) or items.setdefault(lid, Item(lid, page, _seq(lid), title, cls, kind, code, name))
        col = column_of(year, measure, period)
        if col:
            it.amounts.setdefault(col, amount)
        else:
            it.other.setdefault(label, str(amount))
    out = sorted(items.values(), key=lambda i: i.seq)
    classify(out)
    heads, texts = sections(conn, doc_id)
    assign_units(out, heads, texts)
    return out


CONTINUED = "table starting at its Total row"
LOCATION_CODE = re.compile(r"333\d*")


def classify(items: list[Item]) -> None:
    """Fix classifications the table titles don't give.
    - A table that starts at its Total row, before its title is printed ("Capital Expenditure (table starting at its
      Total row)"), is the classification of the full title that follows for the same kind of spending.
    - Location codes (333 Sokoto, 3331 a senatorial zone, 33331800 TAMBUWAL) are the location classification,
      whatever title is carried over onto the page."""
    for i, it in enumerate(items):
        if CONTINUED in it.table_title and it.classification == "other":
            nxt = next((x for x in items[i + 1:] if x.spend_kind == it.spend_kind and CONTINUED not in x.table_title),
                       None)
            if nxt is not None:
                it.classification = nxt.classification
            if it.classification == "other" and it.code and len(it.code) == 12:
                it.classification = "administrative"      # its rows are MDAs (2025 budget p14: overhead)
    # A 12-digit MDA row printed under another table's title (the 2025 budget's overhead table runs on into p15,
    # where the next table's title "... by Fund Source" is printed first) still continues the MDA table before it.
    last: dict[str, str] = {}
    for it in items:
        if (it.classification == "other" and it.code and len(it.code) == 12 and not LOCATION_CODE.match(it.code)
                and last.get(it.spend_kind) == "administrative"):
            it.classification = "administrative"
        last[it.spend_kind] = it.classification
    for it in items:
        if it.code and LOCATION_CODE.fullmatch(it.code) and it.classification != "administrative":
            it.classification = "location"


# --- projects ----------------------------------------------------------------------------------

def _labels(text: str) -> tuple[list[str], list[Decimal]] | None:
    m = _HEADER.search(text)
    if not m:
        return None
    labels = _LABEL.findall(m.group("labels"))
    totals = [_amount(x) for x in m.group("nums").split()]
    return (labels, totals) if labels and len(labels) == len(totals) else None


def _clean_name(s: str) -> str:
    s = re.sub(r"^.*Total Capital Expenditure(?: " + _NUM + r")+", "", s)        # the table's header and total row
    s = re.sub(r"^.*?\bBudget\s*-\s*Capital Expenditure by Project\b", "", s)
    return s.strip(" -,;")


_TOKEN = re.compile(r"(?<!\S)" + _NUM + r"(?!\S)")


def _tokens(flat: str, m: re.Match, n: int) -> list[tuple[str, int]]:
    """The row's first n amount tokens with their position in the page text."""
    base = m.start("nums")
    return [(t.group(0), base + t.start()) for t in _TOKEN.finditer(m.group("nums"))][:n]


class Positions:
    """Where amounts are printed on a PDF page (right edge, in points), to tell which column a number is in when a
    row leaves empty cells blank instead of printing '-' (2026 budget p51: one number for seven columns)."""

    def __init__(self, pdf_path, page: int):
        import pypdfium2 as pdfium
        self._doc = pdfium.PdfDocument(str(pdf_path))
        self._text = self._doc[page - 1].get_textpage()
        self._cache: dict[str, list[float]] = {}

    def right_edges(self, token: str) -> list[float]:
        if token not in self._cache:
            s, out = self._text.search(token, match_case=True), []
            while (hit := s.get_next()) is not None:
                out.append(self._text.get_charbox(hit[0] + hit[1] - 1)[2])
            self._cache[token] = out
        return self._cache[token]

    def x(self, flat: str, token: str, at: int) -> float | None:
        """The right edge of this occurrence of the token (the k-th on the page is the k-th in the page text)."""
        edges = self.right_edges(token)
        k = len(re.findall(r"(?<!\S)" + re.escape(token) + r"(?!\S)", flat[:at]))
        return edges[k] if k < len(edges) else None

    def close(self) -> None:
        self._doc.close()


def place_by_position(pos: Positions, flat: str, full: list[re.Match], short: list[re.Match],
                      n: int) -> dict[int, dict[int, str]]:
    """{row start: {column index: token}} for rows with too few amounts: each printed number goes to the column
    whose numbers (in the complete rows of the page) end nearest to it. Dashes are zeros and can be left out."""
    edges: dict[int, list[float]] = defaultdict(list)
    for m in full:
        for j, (tok, at) in enumerate(_tokens(flat, m, n)):
            if tok != "-" and (x := pos.x(flat, tok, at)) is not None:
                edges[j].append(x)
    centre = {j: sorted(xs)[len(xs) // 2] for j, xs in edges.items() if xs}
    out: dict[int, dict[int, str]] = {}
    for m in short:
        placed: dict[int, str] = {}
        for tok, at in _tokens(flat, m, n):
            if tok == "-" or (x := pos.x(flat, tok, at)) is None or not centre:
                continue
            j = min(centre, key=lambda c: abs(centre[c] - x))
            if j in placed or (placed and j < max(placed)):
                placed = {}
                break                              # two numbers in one column, or out of order: can't place
            placed[j] = tok
        if placed:
            out[m.start()] = placed
    return out


def parse_projects(pages: list[tuple[int, str]], pdf_path=None) -> tuple[list[Project], dict]:
    """The statewide project list: (projects, {"labels", "printed": {column: total}, "pages", "unparsed",
    "placed"}). With the PDF, rows with blank cells are placed by where their numbers are printed."""
    projects: list[Project] = []
    info: dict = {"labels": [], "printed": {}, "pages": [], "unparsed": 0, "placed": 0}
    cols: list[str | None] = []
    in_table, carry = False, ""
    for page, raw in pages:
        flat = " ".join((raw or "").split())
        if PROJECT_TITLE.search(flat):
            if not in_table and (lab := _labels(flat)):
                in_table = True
                info["labels"] = lab[0]
                cols = []
                for label in lab[0]:
                    parsed = parse_column(label)
                    cols.append(column_of(*parsed) if parsed else None)
                info["printed"] = {c: str(v) for c, v in zip(cols, lab[1]) if c}
        elif in_table and OTHER_TITLE.search(flat):
            break                                  # the next table: the list has ended
        if not in_table:
            continue
        info["pages"].append(page)
        rows: list[tuple[re.Match, str, list[str]]] = []
        pos, first = 0, True
        while m := PROJECT.search(flat, pos):
            nums = m.group("nums").split()
            name = _clean_name(flat[pos:m.start()])
            if first and carry:
                name = f"{carry} {name}".strip()
            first, carry = False, ""
            end = m.end()
            if len(nums) > len(cols):              # the next name starts with a number-like token: give it back
                extra = " ".join(nums[len(cols):])
                end = m.end() - len(extra) - 1
                nums = nums[:len(cols)]
            rows.append((m, name, nums))
            pos = end
        tail = flat[pos:].strip()
        carry = tail if 0 < len(tail) < 300 and not re.search(r"\d{8}", tail) else ""
        short = [m for m, _, nums in rows if len(nums) != len(cols)]
        placed: dict[int, dict[int, str]] = {}
        if short and pdf_path:
            try:
                where = Positions(pdf_path, page)
                try:
                    placed = place_by_position(where, flat, [m for m, _, nums in rows if len(nums) == len(cols)],
                                               short, len(cols))
                finally:
                    where.close()
            except Exception as e:                 # no readable PDF: those rows stay unparsed and are counted
                log.warning("project positions unavailable for page %d: %s", page, e)
        for m, name, nums in rows:
            if len(nums) != len(cols):
                if m.start() not in placed:
                    info["unparsed"] += 1
                    continue
                info["placed"] += 1
                nums = [placed[m.start()].get(j, "-") for j in range(len(cols))]
            p = Project(page, name or "(name not printed)", m["mda"], m["mda_name"].strip(), m["econ"],
                        m["econ_name"].strip(), m["func"], (m["func_name"] or "").strip() or None, m["loc"],
                        m["loc_name"].strip())
            for col, label, v in zip(cols, info["labels"], nums):
                amount = _amount(v)
                if col and amount is not None:
                    p.amounts[col] = amount
                elif amount is not None and parse_column(label) is not None:
                    p.other[label] = str(amount)
            projects.append(p)
    return projects, info


# --- reconciliation ----------------------------------------------------------------------------

CHECKED = ("administrative", "economic", "function", "programme", "location")
# the table's own grand total ("Total", "Total Expenditure", "Total Capital Expenditure"), not a sub-total such as
# "Total Capital Receipts" or "Total Capital Health Sector Expenditure"
GRAND_TOTAL = re.compile(r"(?i)total(?: (?:personnel|capital|overhead|other non-debt recurrent|non-debt recurrent|"
                         r"debt service|recurrent))?(?: expenditure)?")


def _is_total(it: Item) -> bool:
    return not it.code and it.name.lower().startswith("total")


def _same_table(a: Item, b: Item) -> bool:
    return a.table_title == b.table_title or CONTINUED in a.table_title or CONTINUED in b.table_title


def segments(items: list[Item]) -> list[list[Item]]:
    """Printed tables, in reading order: a table ends when its title, classification or spending kind changes, a
    code repeats, or a new Total row starts (tables split across pages stay together)."""
    out: list[list[Item]] = []
    cur: list[Item] = []
    codes: set[str] = set()
    for it in items:
        new = bool(cur) and ((it.classification, it.spend_kind) != (cur[-1].classification, cur[-1].spend_kind)
                             or not _same_table(it, cur[-1])
                             or (it.code and it.code in codes) or (_is_total(it) and any(_is_total(x) for x in cur)))
        if new:
            out.append(cur)
            cur, codes = [], set()
        cur.append(it)
        if it.code:
            codes.add(it.code)
    if cur:
        out.append(cur)
    return out


def parent_code(code: str, codes: set[str]) -> str | None:
    """The most specific other code in the same table that contains this one: a prefix ('7063' of '70631'), or for
    12-digit administrative codes the same digits followed by zeros ('052100000000' of '052100300100')."""
    if len(code) == 12:
        # fixed levels, not trailing zeros: 017000000000 is a ministry (0170), not a sector stem "017"
        ministry, sector = code[:4] + "0" * 8, code[:2] + "0" * 10
        ups = [ministry, sector] if code != ministry else [sector]
        return next((p for p in ups if p != code and p in codes), None)
    best, best_len = None, -1
    for p in codes:
        if p != code and len(p) < len(code) and code.startswith(p) and len(p) > best_len:
            best, best_len = p, len(p)
    return best


def _admin_level_ok(code: str) -> bool:
    # sector XX0000000000 -> ministry XXXX00000000 -> unit: only codes on one of these levels are summed
    return len(code) == 12


def check_hierarchy(items: list[Item], columns: tuple[str, ...], checks: Checks, label: str = "hierarchy") -> None:
    for seg in segments(items):
        if seg[0].classification not in CHECKED:
            continue
        coded = [x for x in seg if x.code and x.code.isdigit()]
        if seg[0].classification == "administrative":
            coded = [x for x in coded if _admin_level_ok(x.code)]
        codes = {x.code for x in coded}
        children: dict[str, list[Item]] = defaultdict(list)
        for x in coded:
            if (p := parent_code(x.code, codes)) is not None:
                children[p].append(x)
        by_code = {x.code: x for x in coded}
        tops = [x for x in coded if parent_code(x.code, codes) is None]
        total = next((x for x in seg if _is_total(x) and GRAND_TOTAL.fullmatch(x.name.strip())), None)
        pairs = [(by_code[p], kids) for p, kids in children.items()]
        if total is not None and len(tops) > 1:
            pairs.append((total, tops))
        for parent, kids in pairs:
            for col in columns:
                if col not in parent.amounts or any(col not in k.amounts for k in kids):
                    continue
                s = sum((k.amounts[col] for k in kids), Decimal(0))
                ok = abs(s - parent.amounts[col]) <= TOLERANCE
                checks.add(f"{label}:{parent.classification}", ok,
                           f"p{parent.page} {parent.code or 'Total'} {parent.name[:40]} {col}: children "
                           f"{s:,.2f} vs printed {parent.amounts[col]:,.2f}")


def _first_rows(items: list[Item], classification: str) -> dict[tuple[str, str], Item]:
    out: dict[tuple[str, str], Item] = {}
    for x in items:
        if x.classification == classification and x.code:
            out.setdefault((x.code, x.spend_kind), x)
    return out


def check_kinds(items: list[Item], columns: tuple[str, ...], checks: Checks) -> None:
    rows = _first_rows(items, "administrative")
    for (code, kind), tot in rows.items():
        if kind != "total":
            continue
        parts = [rows.get((code, k)) for k in KINDS]
        if sum(p is not None for p in parts) < 2:
            continue
        for col in columns:
            if col not in tot.amounts:
                continue
            s = sum((p.amounts.get(col, Decimal(0)) for p in parts if p is not None), Decimal(0))
            checks.add("kinds", abs(s - tot.amounts[col]) <= TOLERANCE,
                       f"{code} {tot.name[:40]} {col}: personnel+overhead+debt+capital {s:,.2f} vs total "
                       f"{tot.amounts[col]:,.2f}")


def admin_totals(items: list[Item]) -> dict[str, Item]:
    """The administrative classification's Total row per spending kind (the first printed)."""
    out: dict[str, Item] = {}
    for seg in segments(items):
        if seg[0].classification == "administrative" and seg[0].spend_kind != "revenue":
            if (t := next((x for x in seg if _is_total(x)), None)) is not None:
                out.setdefault(t.spend_kind, t)
    return out


def check_grand_totals(items: list[Item], columns: tuple[str, ...], checks: Checks) -> None:
    admin = admin_totals(items)
    for seg in segments(items):
        cls = seg[0].classification
        if cls not in ("function", "location") or seg[0].spend_kind == "revenue":
            continue
        if cls == "location":                 # its top row is the state ("333 Sokoto")
            top = next((x for x in seg if x.code == "333"), None)
        else:
            top = next((x for x in seg if _is_total(x) and GRAND_TOTAL.fullmatch(x.name.strip())), None)
        ref = admin.get(seg[0].spend_kind)
        if top is None or ref is None:
            continue
        for col in columns:
            if col in top.amounts and col in ref.amounts:
                checks.add(f"grand_total:{cls}",
                           abs(top.amounts[col] - ref.amounts[col]) <= TOLERANCE,
                           f"p{top.page} {top.name[:30]} ({seg[0].spend_kind}) {col}: {top.amounts[col]:,.2f} vs "
                           f"administrative {ref.amounts[col]:,.2f}")


def check_projects(projects: list[Project], info: dict, items: list[Item], checks: Checks) -> None:
    for col, printed in info.get("printed", {}).items():
        s = sum((p.amounts.get(col, Decimal(0)) for p in projects), Decimal(0))
        checks.add("projects:total", abs(s - Decimal(printed)) <= TOLERANCE,
                   f"{col}: projects add up to {s:,.2f}, printed Total Capital Expenditure {Decimal(printed):,.2f}")
    capital = {x.code: x for x in items if x.classification == "administrative" and x.spend_kind == "capital"
               and x.code and len(x.code) == 12 and x.code[4:] != "00000000"}
    by_mda: dict[str, dict[str, Decimal]] = defaultdict(lambda: defaultdict(Decimal))
    for p in projects:
        for col, v in p.amounts.items():
            by_mda[p.mda_code][col] += v
    for code, sums in by_mda.items():
        row = capital.get(code)
        if row is None:
            continue
        for col, s in sums.items():
            if col in row.amounts:
                checks.add("projects:mda_capital", abs(s - row.amounts[col]) <= TOLERANCE,
                           f"{code} {row.name[:40]} {col}: projects {s:,.2f} vs capital {row.amounts[col]:,.2f}")


# --- build -------------------------------------------------------------------------------------

@dataclass
class Build:
    doc_id: str
    counts: dict[str, int]
    checks: Checks

    def summary(self) -> str:
        parts = [f"{k}={v}" for k, v in self.counts.items()]
        parts += [f"{c}: {r['passed']} ok / {r['failed']} failed" for c, r in sorted(self.checks.results.items())]
        return f"{self.doc_id}: " + "; ".join(parts)


def _jsonable(d: dict) -> str:
    return json.dumps(d, default=str)


def _report_meta(conn: psycopg.Connection, doc_id: str) -> tuple[int | None, int]:
    """(year, last quarter) of an implementation report, from its year-to-date column labels."""
    year, quarter = None, 0
    for label, y, period in conn.execute("SELECT DISTINCT column_label, year, period FROM budget_rows "
                                         "WHERE doc_id = %s AND year IS NOT NULL", (doc_id,)):
        year = year or y
        if m := re.search(r"Q1\s*-\s*Q(\d)", label) or re.search(r"Year to Date \(Q(\d)\)", label):
            quarter = max(quarter, int(m.group(1)))
        elif m := re.fullmatch(r"q(\d)", period or ""):
            quarter = max(quarter, int(m.group(1)))
    return year, quarter


def perf_items(conn: psycopg.Connection, doc_id: str) -> tuple[list[Item], int, int]:
    year, quarter = _report_meta(conn, doc_id)
    items: dict[str, Item] = {}
    for (lid, page, title, cls, kind, code, name, measure, period, amount) in conn.execute(
            "SELECT line_id, page, COALESCE(table_title, ''), classification, spend_kind, code, name, measure, period, "
            "amount_naira FROM budget_rows WHERE doc_id = %s AND line_id IS NOT NULL AND year = %s",
            (doc_id, year)):
        it = items.get(lid) or items.setdefault(lid, Item(lid, page, _seq(lid), title, cls, kind, code, name))
        if measure == "actual":
            col = "quarter_spent" if re.fullmatch(r"q\d", period or "") else "ytd_spent"
        else:
            col = measure if measure in ("original", "revised", "final") else None
        if col:
            it.amounts.setdefault(col, amount)
    out = sorted(items.values(), key=lambda i: i.seq)
    assign_units(out, *sections(conn, doc_id))
    return out, year or 0, quarter


DATA_DIR = Path(__file__).resolve().parents[2] / "data"


def pdf_for(doc_id: str) -> Path | None:
    """The seed PDF (data/<doc id>.pdf), when it is on this machine."""
    p = DATA_DIR / f"{doc_id}.pdf"
    return p if p.is_file() else None


def build(conn: psycopg.Connection, doc_id: str, pdf_path: Path | None = None) -> Build | None:
    """(Re)build one document's entities and run the reconciliation checks. None for other document types.
    `pdf_path` (or data/<doc id>.pdf) places project rows that leave empty cells blank."""
    row = conn.execute("SELECT category FROM documents WHERE id = %s", (doc_id,)).fetchone()
    if not row or row[0] not in BUDGET_CATEGORIES | PERF_CATEGORIES:
        return None
    checks = Checks()
    counts: dict[str, int] = {}
    with conn.transaction():
        for table in ("budget_items", "projects", "perf_items", "entity_builds"):
            conn.execute(f"DELETE FROM {table} WHERE doc_id = %s", (doc_id,))
        if row[0] in BUDGET_CATEGORIES:
            items = budget_items(conn, doc_id)
            pages = conn.execute("SELECT page, text FROM pages WHERE doc_id = %s ORDER BY page", (doc_id,)).fetchall()
            projects, info = parse_projects(pages, pdf_path or pdf_for(doc_id))
            _write_items(conn, doc_id, items)
            _write_projects(conn, doc_id, projects)
            columns = AMOUNTS
            check_projects(projects, info, items, checks)
            counts.update(budget_items=len(items), projects=len(projects), project_rows_unparsed=info["unparsed"],
                          project_rows_placed_by_position=info["placed"],
                          items_with_mda=sum(1 for x in items if x.mda_code))
        else:
            items, year, quarter = perf_items(conn, doc_id)
            _write_perf(conn, doc_id, items, year, quarter)
            columns = PERF_AMOUNTS
            counts.update(perf_items=len(items), year=year, quarter=quarter)
        check_hierarchy(items, columns, checks)
        check_kinds(items, columns, checks)
        check_grand_totals(items, columns, checks)
        conn.execute("INSERT INTO entity_builds (doc_id, counts, checks) VALUES (%s, %s, %s)",
                     (doc_id, _jsonable(counts), _jsonable(checks.results)))
    b = Build(doc_id, counts, checks)
    (log.warning if checks.failed else log.info)("entities: %s", b.summary())
    return b


def _write_items(conn: psycopg.Connection, doc_id: str, items: list[Item]) -> None:
    cols = ("id, doc_id, page, seq, table_title, classification, spend_kind, code, name, mda_code, mda_name, "
            + ", ".join(AMOUNTS) + ", other")
    with conn.cursor().copy(f"COPY budget_items ({cols}) FROM STDIN") as cp:
        for x in items:
            cp.write_row((x.id, doc_id, x.page, x.seq, x.table_title, x.classification, x.spend_kind, x.code, x.name,
                          x.mda_code, x.mda_name, *[x.amounts.get(c) for c in AMOUNTS], _jsonable(x.other)))


def _write_projects(conn: psycopg.Connection, doc_id: str, projects: list[Project]) -> None:
    cols = ("id, doc_id, page, seq, name, mda_code, mda_name, econ_code, econ_name, function_code, function_name, "
            "location_code, location_name, " + ", ".join(AMOUNTS) + ", other")
    per_page: dict[int, int] = defaultdict(int)
    with conn.cursor().copy(f"COPY projects ({cols}) FROM STDIN") as cp:
        for i, p in enumerate(projects):
            per_page[p.page] += 1
            cp.write_row((f"{doc_id}:p{p.page}:{per_page[p.page]}", doc_id, p.page, i, p.name, p.mda_code, p.mda_name,
                          p.econ_code, p.econ_name, p.function_code, p.function_name, p.location_code,
                          p.location_name, *[p.amounts.get(c) for c in AMOUNTS], _jsonable(p.other)))


def _write_perf(conn: psycopg.Connection, doc_id: str, items: list[Item], year: int, quarter: int) -> None:
    cols = ("id, doc_id, page, seq, year, quarter, table_title, classification, spend_kind, code, name, mda_code, "
            "mda_name, " + ", ".join(PERF_AMOUNTS))
    with conn.cursor().copy(f"COPY perf_items ({cols}) FROM STDIN") as cp:
        for x in items:
            cp.write_row((x.id, doc_id, x.page, x.seq, year, quarter, x.table_title, x.classification, x.spend_kind,
                          x.code, x.name, x.mda_code, x.mda_name, *[x.amounts.get(c) for c in PERF_AMOUNTS]))


def build_missing(conn: psycopg.Connection) -> list[Build]:
    """Build every budget and report document that has no entities yet (documents indexed before 0009)."""
    ids = [r[0] for r in conn.execute(
        "SELECT d.id FROM documents d LEFT JOIN entity_builds e ON e.doc_id = d.id "
        "WHERE e.doc_id IS NULL AND d.category = ANY(%s) ORDER BY d.id",
        (sorted(BUDGET_CATEGORIES | PERF_CATEGORIES),))]
    return [b for d in ids if (b := build(conn, d)) is not None]
