"""query_budget: filter, sum, rank and compare the structured budget rows in code (app/retrieval/tables.py).

The planner turns a comparison / ranking / share / total question into items, each a filter over the rows:
classification (function, administrative, economic, programme), spending kind (total, capital, personnel,
overhead), year, measure (approved, revised, original, final, actual), period, and either codes or name
keywords. Here, for each item:
  1. CHOOSE THE DOCUMENT  where that figure is authoritative: an approved figure for year Y from the
     year-Y budget; a revised figure from the next year's budget, then implementation reports; original,
     final and actual figures from the latest implementation report for that year.
  2. PICK ROWS  by code, or by name keyword at the highest level of the classification (7094 TERTIARY
     EDUCATION, not its 70941/70942 sub-functions, so nothing is counted twice). With `units` (several
     ministries and institutions), one row per unit is added up and units not found are listed.
  3. COMPUTE  with exact decimals: the difference and % change (compare), the sum (total), item/whole
     (share), or the top rows (rank). The model writes the wording; the numbers come from here.
Every picked row keeps its document and page, for citations and evidence crops.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from decimal import ROUND_HALF_UP, Decimal

import psycopg

OPERATIONS = ("lookup", "compare", "total", "share", "rank")
MAX_ITEMS = 6
MAX_UNITS = 12
MAX_RANK = 10
_TWO = Decimal("0.01")


@dataclass
class Item:
    label: str
    classification: str = "function"
    spend_kind: str = "total"
    year: int | None = None
    measure: str = "approved"
    period: str = "full_year"
    codes: list[str] = field(default_factory=list)
    names: list[str] = field(default_factory=list)      # keywords for one line, e.g. ["tertiary education"]
    units: list[str] = field(default_factory=list)      # several lines to add up (ministries and institutions)
    alt_measure: str = ""                               # a second reading shown alongside, e.g. "revised"

    @classmethod
    def from_dict(cls, d: dict) -> Item:
        def strs(v) -> list[str]:
            return [str(x)[:120] for x in (v or []) if str(x).strip()][:MAX_UNITS]
        year = d.get("year")
        return cls(str(d.get("label") or "")[:150], str(d.get("classification") or "function"),
                   str(d.get("spend_kind") or "total"), int(year) if str(year or "").isdigit() else None,
                   str(d.get("measure") or "approved"), str(d.get("period") or "full_year"),
                   [c for c in strs(d.get("codes")) if c.isdigit()], strs(d.get("names")), strs(d.get("units")),
                   str(d.get("alt_measure") or ""))


@dataclass
class Picked:
    doc_id: str
    title: str
    page: int
    table_title: str
    code: str | None
    name: str
    column_label: str
    amount: Decimal
    row_text: str


@dataclass
class ItemResult:
    item: Item
    rows: list[Picked] = field(default_factory=list)
    missing: list[str] = field(default_factory=list)    # units not found
    included: dict[str, str] = field(default_factory=dict)   # unit -> the picked parent that already contains it
    alt: Picked | None = None                           # the alternative reading's row

    @property
    def total(self) -> Decimal | None:
        return sum((r.amount for r in self.rows), Decimal(0)) if self.rows else None


@dataclass
class QueryResult:
    operation: str
    items: list[ItemResult]
    ranking: list[Picked] = field(default_factory=list)
    difference: Decimal | None = None
    change_pct: Decimal | None = None
    total: Decimal | None = None
    share_pct: Decimal | None = None

    @property
    def found(self) -> bool:
        return any(r.rows for r in self.items) or bool(self.ranking)

    @property
    def complete(self) -> bool:
        return all(r.rows and not r.missing for r in self.items) if self.items else bool(self.ranking)

    def computed_numbers(self) -> list[str]:
        """Figures computed here (not in any document): the number check accepts these too."""
        out = [self.difference, self.change_pct, self.total, self.share_pct]
        out += [r.total for r in self.items if r.total is not None and len(r.rows) > 1]
        return [fmt(x) for x in out if x is not None]


def fmt(x: Decimal) -> str:
    q = x.quantize(_TWO, rounding=ROUND_HALF_UP)
    return f"{q:,.2f}"


# --- choosing the document ------------------------------------------------------------------------

def _doc_rank(item: Item, series: str | None, edition: str | None) -> tuple:
    """Lower is better. Budgets are 'sokoto_budget' with edition 'YYYY'; reports 'sokoto_bir' with 'YYYY-Qn'."""
    y = item.year
    ed_year = int(edition[:4]) if edition and edition[:4].isdigit() else 0
    if item.measure in ("approved", "proposal", "estimate"):
        return (0 if series == "sokoto_budget" and ed_year == y else 1, -ed_year)
    if item.measure == "revised":
        return (0 if series == "sokoto_budget" and ed_year == (y or 0) + 1 else
                1 if series == "sokoto_bir" and ed_year == y else 2, -ed_year, edition or "")
    if item.measure in ("original", "final"):
        return (0 if series == "sokoto_bir" and ed_year == y else 1, _neg(edition))
    # actual: the latest report for that year first, then the next budget (which prints actuals)
    return (0 if series == "sokoto_bir" and ed_year == y else
            1 if series == "sokoto_budget" and ed_year > (y or 0) else 2, _neg(edition))


def _neg(edition: str | None) -> tuple:
    return tuple(-ord(c) for c in (edition or ""))


_SQL = """
SELECT b.doc_id, d.title, b.page, COALESCE(b.table_title, ''), b.code, b.name, b.column_label, b.amount_naira,
       b.row_text, d.series, d.edition
FROM budget_rows b JOIN documents d ON d.id = b.doc_id
WHERE b.classification = %(cls)s AND b.spend_kind = %(kind)s AND b.measure = %(measure)s AND b.period = %(period)s
  AND (%(year)s::int IS NULL OR b.year = %(year)s)
  AND (cardinality(%(codes)s::text[]) = 0 OR b.code = ANY(%(codes)s))
  AND (cardinality(%(pats)s::text[]) = 0 OR b.name ILIKE ANY(%(pats)s))
ORDER BY b.page
"""


def _candidates(conn: psycopg.Connection, item: Item, measure: str, names: list[str]) -> list[tuple]:
    pats = [f"%{_like(n)}%" for n in names]
    return conn.execute(_SQL, {"cls": item.classification, "kind": item.spend_kind, "measure": measure,
                               "period": item.period, "year": item.year, "codes": item.codes, "pats": pats}).fetchall()


def _like(s: str) -> str:
    return re.sub(r"[%_\\]", " ", s).strip()


def _level(code: str | None) -> tuple:
    """Highest level first: shorter codes, then administrative codes ending in more zeros (the whole ministry)."""
    c = code or ""
    return (len(c) if len(c) < 12 else 12, -len(c) + len(c.rstrip("0")))


_FILLER = {"state", "sokoto", "the", "of", "for", "and", "government", "s"}
_SPELLING = {"collage": "college"}          # the 2026 budget prints "Shehu Shagari Collage of Education"


def _words(s: str) -> set[str]:
    out = set()
    for w in re.findall(r"[a-z]+", s.lower()):
        w = _SPELLING.get(w, w)
        w = w[:-1] if len(w) > 4 and w.endswith("s") and not w.endswith("ss") else w   # colleges -> college
        if w not in _FILLER:
            out.add(w)
    return out


def _unit_matches(unit: str, name: str) -> bool:
    """'State Polytechnic' matches 'Umaru Ali Shinkafi Polytechnic Sokoto': every meaningful word is there."""
    want = _words(unit)
    return bool(want) and want <= _words(name)


def _contains(parent: str | None, child: str | None) -> bool:
    """056900000000 contains 056900400100: the parent's code without its trailing zeros is the child's prefix."""
    if not parent or not child or parent == child or len(parent) != len(child):
        return False
    stem = parent.rstrip("0")
    return len(stem) < len(parent) and child.startswith(stem)


def _picked(r: tuple) -> Picked:
    return Picked(r[0], r[1], r[2], r[3], r[4], r[5], r[6], Decimal(r[7]), r[8])


def _best_doc(rows: list[tuple], item: Item) -> str | None:
    docs = {r[0]: (r[9], r[10]) for r in rows}
    return min(docs, key=lambda d: _doc_rank(item, *docs[d])) if docs else None


def _top_row(rows: list[tuple]) -> tuple:
    return min(rows, key=lambda r: (_level(r[4]), r[2]))


def run_item(conn: psycopg.Connection, item: Item) -> ItemResult:
    res = ItemResult(item)
    if item.units:
        rows = _candidates(conn, item, item.measure, [])     # matched by meaningful words below, not by SQL
        doc = _best_doc(rows, item)
        picked: list[tuple[str, Picked]] = []
        for unit in item.units:
            mine = [r for r in rows if r[0] == doc and _unit_matches(unit, r[5])]
            if not mine:
                res.missing.append(unit)
                continue
            # Every matching line counts ("college of education" = all of them), once per code, top level first
            by_code: dict = {}
            for r in sorted(mine, key=lambda r: (_level(r[4]), r[2])):
                by_code.setdefault(r[4] or r[5], r)
            picked += [(unit, _picked(r)) for r in by_code.values() if all(p.code != r[4] for _, p in picked)]
        # Codes are hierarchical: a university (056900400100) is inside its ministry (056900000000). Count a
        # unit only once: drop it when a picked parent already contains it, and say so.
        kept_units, folded = set(), {}
        for unit, p in picked:
            parent = next((q for _, q in picked if q is not p and _contains(q.code, p.code)), None)
            if parent:
                folded.setdefault(unit, parent.name)
            elif p not in res.rows:
                res.rows.append(p)
                kept_units.add(unit)
        res.included = {u: name for u, name in folded.items() if u not in kept_units}
    else:
        rows = _candidates(conn, item, item.measure, item.names)
        if doc := _best_doc(rows, item):
            res.rows.append(_picked(_top_row([r for r in rows if r[0] == doc])))
    if item.alt_measure and item.alt_measure != item.measure and res.rows and not item.units:
        alt = Item(**{**item.__dict__, "measure": item.alt_measure, "codes": [res.rows[0].code] if res.rows[0].code else item.codes})
        alt_rows = _candidates(conn, alt, alt.measure, item.names if not alt.codes else [])
        if doc := _best_doc(alt_rows, alt):
            res.alt = _picked(_top_row([r for r in alt_rows if r[0] == doc]))
    return res


# Ministry codes are 4 digits + 8 zeros (052100000000 Ministry of Health); 2 digits + 10 zeros (050000000000
# Social Sector) is a sector grouping, not a ministry.
_RANK_LEVEL = {"administrative": r"^\d{2}(?!00)\d{2}0{8}$", "function": r"^\d{4}$", "programme": r"^\d{2}$",
               "economic": r"^\d{2}$"}


def run_rank(conn: psycopg.Connection, item: Item, top: int) -> list[Picked]:
    """The biggest lines of one classification in one document: ministries, functions, sectors."""
    rows = _candidates(conn, item, item.measure, [])
    doc = _best_doc(rows, item)
    level = re.compile(_RANK_LEVEL.get(item.classification, r"^\d+$"))
    seen, out = set(), []
    for r in sorted((r for r in rows if r[0] == doc and r[4] and level.match(r[4])), key=lambda r: -Decimal(r[7])):
        if r[4] not in seen:
            seen.add(r[4])
            out.append(_picked(r))
        if len(out) >= top:
            break
    return out


def run_budget_query(conn: psycopg.Connection, spec: dict) -> QueryResult:
    op = spec.get("operation") if spec.get("operation") in OPERATIONS else "lookup"
    items = [Item.from_dict(d) for d in (spec.get("items") or [])[:MAX_ITEMS] if isinstance(d, dict)]
    if op == "rank" and items:
        top = max(1, min(int(spec.get("top") or 5), MAX_RANK))
        return QueryResult(op, [], ranking=run_rank(conn, items[0], top))
    results = [run_item(conn, it) for it in items]
    q = QueryResult(op, results)
    totals = [r.total for r in results]
    if op == "compare" and len(totals) >= 2 and totals[0] is not None and totals[1] is not None:
        q.difference = totals[0] - totals[1]
        if totals[1]:
            q.change_pct = (q.difference / totals[1] * 100).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
    elif op == "total" and all(t is not None for t in totals) and totals:
        q.total = sum(totals, Decimal(0))
    elif op == "share" and len(totals) >= 2 and totals[0] is not None and totals[1]:
        q.share_pct = (totals[0] / totals[1] * 100).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
    return q


# --- showing the working ----------------------------------------------------------------------------

WORDS = {
    "en": {"head": "🧮 *Working* (the rows used):", "missing": "not found in the budget tables",
           "also": "also", "total": "Total", "difference": "Difference", "share": "Share", "of": "of",
           "calc": "Kasafi's calculation", "included": "included in", "not_found": "not found"},
    "ha": {"head": "🧮 *Yadda aka lissafa* (layukan da aka yi amfani da su):", "missing": "ba a samu a teburorin kasafi ba",
           "also": "har ila yau", "total": "Jimilla", "difference": "Bambanci", "share": "Kaso", "of": "na",
           "calc": "lissafin Kasafi", "included": "yana cikin", "not_found": "ba a samu ba"},
}


def _line(p: Picked, nmap: dict) -> str:
    code = f" ({p.code})" if p.code else ""
    return f"{p.name}{code}, {p.column_label}: {fmt(p.amount)} [{nmap[(p.doc_id, p.page)]}]"


def _signed(x: Decimal) -> str:
    return ("+" if x > 0 else "-" if x < 0 else "") + fmt(abs(x))


def render_working(q: QueryResult, nmap: dict, lang: str) -> str:
    """The rows used and the arithmetic, written by code (exact figures; the app makes them readable)."""
    w = WORDS.get(lang, WORDS["en"])
    out = [w["head"]]
    if q.operation == "rank":
        out += [f"{i}. {_line(p, nmap)}" for i, p in enumerate(q.ranking, 1)]
        return "\n".join(out)
    for r in q.items:
        if not r.rows:
            out.append(f"• {r.item.label}: {w['missing']}")
            continue
        if len(r.rows) == 1 and not r.item.units:
            out.append(f"• {r.item.label}: {_line(r.rows[0], nmap)}")
        else:
            out.append(f"• {r.item.label}:")
            out += [f"   – {_line(p, nmap)}" for p in r.rows]
            out += [f"   – {u}: {w['included']} {parent}" for u, parent in r.included.items()]
            out += [f"   – {u}: {w['not_found']}" for u in r.missing]
            out.append(f"   = {w['total']}: {fmt(r.total)} ({w['calc']})")
        if r.alt:
            out.append(f"   ({w['also']} {_line(r.alt, nmap)})")
    if q.difference is not None:
        pct = f" ({'+' if q.change_pct and q.change_pct > 0 else ''}{q.change_pct}%)" if q.change_pct is not None else ""
        out.append(f"• {w['difference']}: {_signed(q.difference)}{pct} ({w['calc']})")
    if q.total is not None and len(q.items) > 1:          # one item already shows its own total
        out.append(f"• {w['total']}: {fmt(q.total)} ({w['calc']})")
    if q.share_pct is not None:
        out.append(f"• {w['share']}: {q.share_pct}% ({w['calc']})")
    return "\n".join(out)


def context_text(q: QueryResult, nmap: dict) -> str:
    """What the composer is told: the computed results, with exact figures and evidence numbers."""
    lines = ["BUDGET QUERY RESULTS (computed by the app from the evidence rows; the app shows these rows and the "
             "arithmetic under your answer):"]
    lines += render_working(q, nmap, "en").splitlines()[1:]
    lines.append("Write 'summary' as one or two sentences that answer the question with these exact figures and "
                 "their [n]; leave 'items' empty. After a computed figure (difference, total, share) add "
                 "\"(Kasafi's calculation)\" (Hausa: \"(lissafin Kasafi)\"). If anything is 'not found', say "
                 "so and set found to \"partial\".")
    return "\n".join(lines)
