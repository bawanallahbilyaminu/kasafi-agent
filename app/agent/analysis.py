"""Analysis tools on the structured budget core (budget_items, projects, perf_items). Every count and sum is SQL.

The planner picks a tool and its parameters ("analysis" in the plan); a tool returns facts (each one money, a count
or a percentage, with the page it comes from) and the rows behind them. The reply is written from those facts by
code (app/agent/answer.py), so no model writes a figure here. Anything else goes to search plus model reading.

  project_status    the latest budget's projects against the year before, from the same project list (a 2026
                    budget prints each project's 2025 revised budget and its January-September 2025 spending):
                    continuing = budgeted in the previous year and again; started = money spent in the previous
                    year and budgeted again; idle = budgeted in the previous year, nothing spent, budgeted again;
                    new = not budgeted the year before; dropped = budgeted the year before, not this year.
  lga_projects      projects whose location is that LGA (statewide projects are not split by LGA, and say so).
  ranking           projects, LGAs (by their tagged projects) or agencies, by allocation or by spending.
  mda_profile       one ministry (with its agencies) or agency: total, salaries, running costs, debt, capital; last
                    year's budget and spending; this year's spending so far (latest implementation report).
  function_profile  one function of government (health, secondary education, ...), the same way.
  revenue           where the money comes from: FAAC, independent revenue (IGR), aid and grants, capital receipts
                    and loans; budgeted, and received so far.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from decimal import ROUND_HALF_UP, Decimal
from difflib import SequenceMatcher

import psycopg

from app.agent.budget_query import SOKOTO_LGAS
from app.agent.category import matches, resolve_scope
from app.retrieval.entities import AMOUNTS

log = logging.getLogger(__name__)

TOOLS = ("project_status", "lga_projects", "ranking", "mda_profile", "function_profile", "revenue")
STATUSES = ("all", "continuing", "started", "idle", "new", "dropped")
TOP = 5
STATEWIDE = "33342400"
KINDS = ("personnel", "overhead", "debt", "capital")


@dataclass
class Fact:
    value: Decimal | int
    kind: str                     # money | count | pct
    doc_id: str
    page: int | None


@dataclass
class Row:
    name: str
    amount: Decimal
    doc_id: str
    page: int
    detail: dict = field(default_factory=dict)     # e.g. {"place": "TAMBUWAL", "spent": Decimal, "budget_prev": ...}


@dataclass
class AnalysisResult:
    tool: str
    found: bool
    year: int = 0                 # the budget year (approved)
    prev: int = 0                 # the year before (revised budget and spending printed in the same budget)
    subject: str = ""             # the resolved MDA, function, LGA or topic
    focus: str = ""               # project_status: which group the question is about; revenue: which source
    facts: dict[str, Fact] = field(default_factory=dict)
    rows: list[Row] = field(default_factory=list)
    working: list[str] = field(default_factory=list)       # what was counted and added, for "show working"
    titles: dict[str, str] = field(default_factory=dict)   # doc_id -> title
    report: str = ""              # the implementation report used for spending so far, e.g. "Q2 2026"
    clarify: list[dict] = field(default_factory=list)
    reason: str = ""              # why nothing was found

    def money(self, key: str, value, doc_id: str, page: int | None) -> None:
        if value is not None:
            self.facts[key] = Fact(Decimal(value), "money", doc_id, page)

    def count(self, key: str, value: int, doc_id: str, page: int | None) -> None:
        self.facts[key] = Fact(int(value or 0), "count", doc_id, page)

    def pct(self, key: str, part, whole, doc_id: str, page: int | None) -> None:
        if part is not None and whole:
            self.facts[key] = Fact((Decimal(part) / Decimal(whole) * 100).quantize(Decimal("0.1"), ROUND_HALF_UP),
                                   "pct", doc_id, page)


def _col(name: str) -> str:
    if name not in AMOUNTS:
        raise ValueError(f"unknown column {name}")
    return name


def budget_doc(conn: psycopg.Connection, year: int | None, need_projects: bool = False) -> tuple[str, int] | None:
    """The approved budget for the year asked (or the latest one): (doc_id, year)."""
    table = "projects" if need_projects else "budget_items"
    rows = conn.execute(f"SELECT DISTINCT t.doc_id, d.year FROM {table} t JOIN documents d ON d.id = t.doc_id "
                        "WHERE d.category = 'budget' AND t.doc_id LIKE 'budget-%%-approved' ORDER BY d.year DESC"
                        ).fetchall()
    rows = [(d, y) for d, y in rows if y]
    if not rows:
        return None
    if year:
        exact = [r for r in rows if r[1] == year]
        if exact:
            return exact[0]
        if need_projects:          # project status for a year: the next budget prints that year's spending
            later = [r for r in rows if r[1] == year + 1]
            if later:
                return later[0]
    return rows[0]


def latest_report(conn: psycopg.Connection, year: int) -> tuple[str, int] | None:
    """The implementation report with the most quarters of that year: (doc_id, quarter)."""
    r = conn.execute("SELECT doc_id, max(quarter) FROM perf_items WHERE year = %s GROUP BY doc_id "
                     "ORDER BY max(quarter) DESC, doc_id DESC LIMIT 1", (year,)).fetchone()
    return (r[0], r[1]) if r else None


def _titles(conn: psycopg.Connection, ids: set[str]) -> dict[str, str]:
    return dict(conn.execute("SELECT id, title FROM documents WHERE id = ANY(%s)", (list(ids),)).fetchall())


def _norm(s: str) -> str:
    return re.sub(r"[^a-z]", "", (s or "").lower())


def lga_code(conn: psycopg.Connection, doc_id: str, lga: str) -> tuple[str, str] | None:
    """(location code, printed name) of an LGA among the project list's locations."""
    want = _norm(lga.replace("Local Government", "").replace("LGA", ""))
    if not want:
        return None
    places = conn.execute("SELECT DISTINCT location_code, location_name FROM projects WHERE doc_id = %s",
                          (doc_id,)).fetchall()
    best = max(places, key=lambda p: SequenceMatcher(None, want, _norm(p[1])).ratio(), default=None)
    if best and SequenceMatcher(None, want, _norm(best[1])).ratio() >= 0.85 and best[0] != STATEWIDE:
        return best
    return None


def _terms_sql(terms: list[str], cols=("p.name", "p.econ_name")) -> tuple[str, list]:
    terms = [t.strip() for t in terms if len(t.strip()) >= 3][:6]
    if not terms:
        return "", []
    likes = [f"%{t}%" for t in terms]
    return "(" + " OR ".join(f"{c} ILIKE ANY(%s)" for c in cols) + ")", [likes] * len(cols)


def _mda_scope(conn: psycopg.Connection, doc_id: str, mda: str, table: str = "projects") -> tuple[str, list, str,
                                                                                                   list[dict]]:
    """(SQL condition on mda_code, args, resolved name, clarify options) for a ministry (with its agencies) or an
    agency, by the names the budget prints."""
    names = dict(conn.execute("SELECT DISTINCT code, name FROM budget_items WHERE doc_id = %s AND classification = "
                              "'administrative' AND length(code) = 12 AND substr(code, 5) <> '00000000'",
                              (doc_id,)).fetchall())
    name, group, units, clarify = resolve_scope(mda, names)
    if clarify:
        return "", [], "", clarify
    if not units:
        return "", [], "", []
    return "mda_code = ANY(%s)", [units], (f"{name} (+)" if group else name), []


# --- project_status ----------------------------------------------------------------------------

def project_status(conn: psycopg.Connection, spec: dict) -> AnalysisResult:
    picked = budget_doc(conn, spec.get("year"), need_projects=True)
    res = AnalysisResult("project_status", False, focus=spec.get("status") if spec.get("status") in STATUSES
                         else "all")
    if not picked:
        res.reason = "no_projects"
        return res
    doc, year = picked
    prev = year - 1
    cur, rev, spent = _col(f"approved_{year}"), _col(f"revised_{prev}"), _col(f"jan_sep_{prev}")
    res.year, res.prev = year, prev
    where, args, subject = ["p.doc_id = %s"], [doc], []
    if spec.get("mda"):
        cond, a, name, clarify = _mda_scope(conn, doc, spec["mda"])
        if clarify:
            res.clarify = clarify
            return res
        if not cond:
            res.reason = "no_mda"
            res.subject = spec["mda"]
            return res
        where.append("p." + cond)
        args += a
        subject.append(name)
    if spec.get("lga"):
        loc = lga_code(conn, doc, spec["lga"])
        if not loc:
            res.reason, res.subject = "no_lga", spec["lga"]
            return res
        where.append("p.location_code = %s")
        args.append(loc[0])
        subject.append(loc[1].title())
    cond, a = _terms_sql(spec.get("terms") or [])
    if cond:
        where.append(cond)
        args += a
        subject.append(", ".join(spec["terms"][:3]))
    res.subject = " – ".join(subject)
    base = " AND ".join(where)
    groups = {
        "all": f"COALESCE(p.{cur}, 0) > 0",
        "continuing": f"COALESCE(p.{rev}, 0) > 0 AND COALESCE(p.{cur}, 0) > 0",
        "started": f"COALESCE(p.{spent}, 0) > 0 AND COALESCE(p.{cur}, 0) > 0",
        "idle": f"COALESCE(p.{rev}, 0) > 0 AND COALESCE(p.{spent}, 0) = 0 AND COALESCE(p.{cur}, 0) > 0",
        "new": f"COALESCE(p.{rev}, 0) = 0 AND COALESCE(p.{spent}, 0) = 0 AND COALESCE(p.{cur}, 0) > 0",
        "dropped": f"COALESCE(p.{rev}, 0) > 0 AND COALESCE(p.{cur}, 0) = 0",
    }
    page = conn.execute(f"SELECT min(p.page) FROM projects p WHERE {base}", args).fetchone()[0]
    for g, cond in groups.items():
        n, s_cur, s_rev, s_spent = conn.execute(
            f"SELECT count(*), sum(p.{cur}), sum(p.{rev}), sum(p.{spent}) FROM projects p WHERE {base} AND {cond}",
            args).fetchone()
        res.count(f"n_{g}", n, doc, page)
        res.money(f"{g}_cur", s_cur or 0, doc, page)
        res.money(f"{g}_prev", s_rev or 0, doc, page)
        res.money(f"{g}_spent", s_spent or 0, doc, page)
        res.working.append(f"{g}: {cond.replace('p.', '').replace('COALESCE(', '').replace(', 0)', '')} → {n} "
                           f"project lines; {cur} {s_cur or 0:,.2f}; {rev} {s_rev or 0:,.2f}; {spent} {s_spent or 0:,.2f}")
    focus = res.focus
    order = rev if focus in ("idle", "dropped") else cur
    for name, a_cur, a_rev, a_spent, pg, place in conn.execute(
            f"SELECT p.name, p.{cur}, p.{rev}, p.{spent}, p.page, p.location_name FROM projects p "
            f"WHERE {base} AND {groups[focus]} ORDER BY p.{order} DESC NULLS LAST, p.seq LIMIT {TOP}", args):
        res.rows.append(Row(name, a_rev if focus in ("idle", "dropped") else a_cur, doc, pg,
                            {"place": place, "budget_prev": a_rev or 0, "spent": a_spent or 0, "budget": a_cur or 0}))
    res.found = res.facts["n_all"].value > 0 or res.facts["n_dropped"].value > 0
    res.reason = "" if res.found else "no_match"
    res.titles = _titles(conn, {doc})
    res.working.insert(0, f"Source: the {year} budget's capital project list ({doc}, from p{page}); "
                          f"{rev} and {spent} are printed in the same rows.")
    return res


# --- lga_projects ------------------------------------------------------------------------------

def other_lga(name: str, here: str, lgas: set[str]) -> str:
    """The LGA a project's name places it in, when that isn't where the budget files it ("Completion of Premier
    Hospital at Binji LGA", location TAMBUWAL); empty when the name names this LGA or none."""
    def named(lga: str) -> bool:
        return re.search(rf"(?<![a-z]){re.escape(lga.lower())}(?![a-z])", name.lower()) is not None
    if named(here):
        return ""
    return next((x.title() for x in sorted(lgas, key=len, reverse=True)
                 if _norm(x) != _norm(here) and len(x) > 2 and named(x)), "")


def lga_projects(conn: psycopg.Connection, spec: dict) -> AnalysisResult:
    res = AnalysisResult("lga_projects", False)
    picked = budget_doc(conn, spec.get("year"), need_projects=True)
    if not picked or not spec.get("lga"):
        res.reason = "no_projects"
        return res
    doc, year = picked
    prev = year - 1
    cur, rev, spent = _col(f"approved_{year}"), _col(f"revised_{prev}"), _col(f"jan_sep_{prev}")
    res.year, res.prev = year, prev
    loc = lga_code(conn, doc, spec["lga"])
    res.subject = loc[1].title() if loc else spec["lga"]
    res.titles = _titles(conn, {doc})
    if not loc:
        res.reason = "no_lga"
        return res
    cond, a = _terms_sql(spec.get("terms") or [])
    extra = f" AND {cond}" if cond else ""
    args = [doc, loc[0]] + a
    n, s_cur, n_prev, s_rev, s_spent, page = conn.execute(
        f"SELECT count(*) FILTER (WHERE COALESCE({cur}, 0) > 0), sum({cur}), "
        f"count(*) FILTER (WHERE COALESCE({rev}, 0) > 0), sum({rev}), sum({spent}), min(page) "
        f"FROM projects p WHERE doc_id = %s AND location_code = %s{extra}", args).fetchone()
    res.count("n", n, doc, page)
    res.money("cur", s_cur or 0, doc, page)
    res.count("n_prev", n_prev, doc, page)
    res.money("prev", s_rev or 0, doc, page)
    res.money("spent", s_spent or 0, doc, page)
    sw_n, sw_cur = conn.execute(f"SELECT count(*), sum({cur}) FROM projects p WHERE doc_id = %s AND location_code = "
                                f"%s AND COALESCE({cur}, 0) > 0" + extra, [doc, STATEWIDE] + a).fetchone()
    res.count("statewide_n", sw_n, doc, None)
    res.money("statewide_cur", sw_cur or 0, doc, None)
    lgas = {n for (n,) in conn.execute("SELECT DISTINCT location_name FROM projects WHERE doc_id = %s AND "
                                       "location_code <> %s", (doc, STATEWIDE))} | set(SOKOTO_LGAS)
    for name, a_cur, a_rev, a_spent, pg, mda in conn.execute(
            f"SELECT name, {cur}, {rev}, {spent}, page, mda_name FROM projects p WHERE doc_id = %s AND "
            f"location_code = %s AND COALESCE({cur}, 0) > 0{extra} ORDER BY {cur} DESC, seq LIMIT {TOP}", args):
        res.rows.append(Row(name, a_cur, doc, pg, {"mda": mda, "budget_prev": a_rev or 0, "spent": a_spent or 0,
                                                    "other_lga": other_lga(name, loc[1], lgas)}))
    res.found = n > 0 or n_prev > 0
    res.reason = "" if res.found else "none_tagged"
    res.working = [f"Source: the {year} budget's capital project list ({doc}); only lines whose location is "
                   f"{loc[0]} {loc[1]}" + (f", matching {', '.join(spec['terms'][:4])}" if cond else "") + ".",
                   f"{year} budget: {n} lines, {cur} {s_cur or 0:,.2f}; {prev}: {n_prev} lines, {rev} "
                   f"{s_rev or 0:,.2f}, {spent} {s_spent or 0:,.2f}",
                   f"Not counted: {sw_n} statewide lines ({cur} {sw_cur or 0:,.2f}) the budget doesn't split by LGA."]
    return res


# --- ranking -----------------------------------------------------------------------------------

def ranking(conn: psycopg.Connection, spec: dict) -> AnalysisResult:
    of = spec.get("of") if spec.get("of") in ("project", "lga", "agency") else "project"
    res = AnalysisResult("ranking", False, focus=of)
    picked = budget_doc(conn, spec.get("year"), need_projects=of != "agency")
    if not picked:
        res.reason = "no_projects"
        return res
    doc, year = picked
    res.year, res.prev = year, year - 1
    by = spec.get("by") if spec.get("by") in ("approved", "revised", "spent") else "approved"
    col = _col({"approved": f"approved_{year}", "revised": f"revised_{year - 1}",
                "spent": f"jan_sep_{year - 1}"}[by])
    order = "ASC" if spec.get("order") == "lowest" else "DESC"
    top = max(1, min(int(spec.get("top") or TOP), 10))
    res.subject = by
    where, args = ["doc_id = %s", f"COALESCE({col}, 0) > 0"], [doc]
    if spec.get("mda") and of != "agency":
        cond, a, name, clarify = _mda_scope(conn, doc, spec["mda"])
        if clarify:
            res.clarify = clarify
            return res
        if cond:
            where.append(cond)
            args += a
            res.subject = f"{by}: {name}"
    cond, a = _terms_sql(spec.get("terms") or [], ("name", "econ_name")) if of != "agency" else ("", [])
    if cond:
        where.append(cond)
        args += a
    w = " AND ".join(where)
    if of == "project":
        sql = (f"SELECT name, {col}, page, location_name FROM projects WHERE {w} ORDER BY {col} {order}, seq "
               f"LIMIT {top}")
        rows = [(n, v, p, {"place": loc}) for n, v, p, loc in conn.execute(sql, args)]
        n_all = conn.execute(f"SELECT count(*) FROM projects WHERE {w}", args).fetchone()[0]
    elif of == "lga":
        sql = (f"SELECT initcap(location_name), sum({col}), min(page), count(*) FROM projects WHERE {w} AND "
               f"location_code <> '{STATEWIDE}' GROUP BY location_name ORDER BY 2 {order} LIMIT {top}")
        rows = [(n, v, p, {"lines": k}) for n, v, p, k in conn.execute(sql, args)]
        n_all = conn.execute(f"SELECT count(DISTINCT location_code) FROM projects WHERE {w} AND location_code <> "
                             f"'{STATEWIDE}'", args).fetchone()[0]
    else:
        kind = spec.get("kind") if spec.get("kind") in KINDS + ("total",) else "total"
        sql = (f"SELECT DISTINCT ON (code) name, {col}, page, code FROM budget_items WHERE {w} AND classification = "
               f"'administrative' AND spend_kind = %s AND length(code) = 12 AND substr(code, 5) <> '00000000' "
               f"ORDER BY code, seq")
        rows = sorted(((n, v, p, {"code": c}) for n, v, p, c in conn.execute(sql, args + [kind])),
                      key=lambda r: r[1], reverse=order == "DESC")
        n_all, rows = len(rows), rows[:top]
    for name, v, p, d in rows:
        res.rows.append(Row(name, v, doc, p, d))
    res.count("n_ranked", n_all, doc, None)
    res.money("top_total", sum((r.amount for r in res.rows), Decimal(0)), doc, None)
    res.found = bool(res.rows)
    res.reason = "" if res.found else "no_match"
    res.titles = _titles(conn, {doc})
    res.working = [f"Source: {doc}; ranked {n_all} {of} entries by {col} ({'lowest' if order == 'ASC' else 'highest'} "
                   f"first)" + (" ; LGAs by the projects located in them (statewide projects not counted)"
                                if of == "lga" else "")]
    res.working += [f"{i}. {r.name[:80]}: {r.amount:,.2f} (p{r.page})" for i, r in enumerate(res.rows, 1)]
    return res


# --- mda_profile / function_profile ------------------------------------------------------------

def _kind_rows(conn: psycopg.Connection, doc: str, cls: str, code: str, year: int) -> dict[str, dict]:
    """The first printed row of this code per kind of spending: {kind: {name, page, cur, prev, prev_spent}}."""
    cur, rev, spent = _col(f"approved_{year}"), _col(f"revised_{year - 1}"), _col(f"jan_sep_{year - 1}")
    return {kind: {"name": n, "page": p, "cur": a, "prev": b, "prev_spent": c} for kind, n, p, a, b, c in conn.execute(
        f"SELECT DISTINCT ON (spend_kind) spend_kind, name, page, {cur}, {rev}, {spent} FROM budget_items WHERE "
        f"doc_id = %s AND classification = %s AND code = %s AND spend_kind <> 'revenue' ORDER BY spend_kind, seq",
        (doc, cls, code))}


def _spending(conn: psycopg.Connection, res: AnalysisResult, cls: str, code: str, key: str, year: int) -> None:
    """Spending so far in that year (the latest implementation report) as facts `{key}_spent`, `{key}_budget`."""
    rep = latest_report(conn, year)
    if not rep:
        return
    doc, quarter = rep
    r = conn.execute("SELECT ytd_spent, COALESCE(final, revised, original), page FROM perf_items WHERE doc_id = %s "
                     "AND classification = %s AND code = %s AND spend_kind = 'total' ORDER BY seq LIMIT 1",
                     (doc, cls, code)).fetchone()
    if not r or r[0] is None:
        return
    res.money(f"{key}_spent", r[0], doc, r[2])
    res.money(f"{key}_budget", r[1], doc, r[2])
    res.pct(f"{key}_rate", r[0], r[1], doc, r[2])
    res.facts[f"{key}_quarter"] = Fact(quarter, "count", doc, r[2])
    res.titles.update(_titles(conn, {doc}))
    res.working.append(f"{year} spending to Q{quarter} ({doc} p{r[2]}): {r[0]:,.2f} of a budget of {r[1]:,.2f}")


def _profile_facts(conn: psycopg.Connection, res: AnalysisResult, doc: str, cls: str, code: str) -> bool:
    year = res.year
    rows = _kind_rows(conn, doc, cls, code, year)
    if "total" not in rows:
        return False
    for kind in ("total",) + KINDS:
        if kind in rows:
            r = rows[kind]
            res.money(kind, r["cur"], doc, r["page"])
            res.working.append(f"{kind}: {code} {r['name']} approved_{year} {r['cur'] or 0:,.2f} (p{r['page']})")
    t = rows["total"]
    res.money("prev_revised", t["prev"], doc, t["page"])                # as printed in this budget
    res.money("prev_spent_jan_sep", t["prev_spent"], doc, t["page"])
    _spending(conn, res, cls, code, "prev", res.prev)      # full year (Q4) if the report is in
    _spending(conn, res, cls, code, "cur", year)
    return True


def mda_profile(conn: psycopg.Connection, spec: dict) -> AnalysisResult:
    res = AnalysisResult("mda_profile", False)
    picked = budget_doc(conn, spec.get("year"))
    if not picked or not spec.get("mda"):
        res.reason = "no_mda"
        return res
    doc, year = picked
    res.year, res.prev = year, year - 1
    names = dict(conn.execute("SELECT DISTINCT code, name FROM budget_items WHERE doc_id = %s AND classification = "
                              "'administrative' AND spend_kind = 'total' AND length(code) = 12 AND substr(code, 5) "
                              "<> '00000000'", (doc,)).fetchall())
    name, group, units, clarify = resolve_scope(spec["mda"], names)
    res.titles = _titles(conn, {doc})
    if clarify:
        res.clarify = clarify
        return res
    if not units:
        res.reason, res.subject = "no_mda", spec["mda"]
        return res
    code = units[0][:4] + "0" * 8 if group else units[0]
    if group and len(units) == 1:            # a commission with no agencies: its own line, not "and its agencies"
        group = False
    res.subject = f"{name} (code {code})" + (" (+)" if group else "")
    if not _profile_facts(conn, res, doc, "administrative", code):
        res.reason = "no_mda"
        return res
    cur = _col(f"approved_{year}")
    res.facts["n_projects"] = Fact(conn.execute(
        f"SELECT count(*) FROM projects WHERE doc_id = %s AND mda_code = ANY(%s) AND COALESCE({cur}, 0) > 0",
        (doc, units)).fetchone()[0], "count", doc, None)
    for pname, v, pg, place in conn.execute(
            f"SELECT name, {cur}, page, location_name FROM projects WHERE doc_id = %s AND mda_code = ANY(%s) AND "
            f"COALESCE({cur}, 0) > 0 ORDER BY {cur} DESC, seq LIMIT {TOP}", (doc, units)):
        res.rows.append(Row(pname, v, doc, pg, {"place": place}))
    res.found = True
    return res


def function_profile(conn: psycopg.Connection, spec: dict) -> AnalysisResult:
    res = AnalysisResult("function_profile", False)
    picked = budget_doc(conn, spec.get("year"))
    if not picked or not spec.get("function"):
        res.reason = "no_function"
        return res
    doc, year = picked
    res.year, res.prev = year, year - 1
    names = conn.execute("SELECT DISTINCT code, name FROM budget_items WHERE doc_id = %s AND classification = "
                         "'function' AND spend_kind = 'total' AND code ~ '^7[0-9]{2,4}$'", (doc,)).fetchall()
    want = spec["function"].lower().replace("&", "and")

    def score(c: str, n: str) -> float:
        n2 = n.lower().replace("&", "and")
        s = 1.0 if matches(want, n2) else SequenceMatcher(None, want, n2).ratio()
        return s - 0.01 * len(c)              # the broadest function on a tie: "health" is 707, not 7074
    best = max(names, key=lambda r: score(*r), default=None)
    res.titles = _titles(conn, {doc})
    if not best or score(*best) < 0.75:
        res.reason, res.subject = "no_function", spec["function"]
        return res
    code, fname = best
    res.subject = fname.title()
    if not _profile_facts(conn, res, doc, "function", code):
        res.reason = "no_function"
        return res
    cur = _col(f"approved_{year}")
    for n, v, pg in conn.execute(
            f"SELECT DISTINCT ON (code) name, {cur}, page FROM budget_items WHERE doc_id = %s AND classification = "
            f"'function' AND spend_kind = 'total' AND code LIKE %s AND length(code) = %s ORDER BY code, seq",
            (doc, code + "%", len(code) + 1)):
        if v:
            res.rows.append(Row(n.title(), v, doc, pg))
    res.rows = sorted(res.rows, key=lambda r: r.amount, reverse=True)[:TOP]
    res.found = True
    return res


# --- revenue -----------------------------------------------------------------------------------

REVENUE_CODES = {"faac": "11", "igr": "12", "grants": "13", "capital_receipts": "14"}


def revenue(conn: psycopg.Connection, spec: dict) -> AnalysisResult:
    focus = spec.get("focus") if spec.get("focus") in REVENUE_CODES else "all"
    res = AnalysisResult("revenue", False, focus=focus)
    picked = budget_doc(conn, spec.get("year"))
    if not picked:
        res.reason = "no_revenue"
        return res
    doc, year = picked
    res.year, res.prev = year, year - 1
    cur, rev, got = _col(f"approved_{year}"), _col(f"revised_{year - 1}"), _col(f"jan_sep_{year - 1}")
    codes = [REVENUE_CODES[focus]] if focus != "all" else list(REVENUE_CODES.values())
    rows = {c: r for c, *r in conn.execute(
        f"SELECT DISTINCT ON (code) code, name, {cur}, {rev}, {got}, page FROM budget_items WHERE doc_id = %s AND "
        f"classification = 'economic' AND spend_kind = 'revenue' AND code = ANY(%s) ORDER BY code, seq",
        (doc, codes))}
    if not rows:
        res.reason = "no_revenue"
        return res
    res.titles = _titles(conn, {doc})
    total = sum((Decimal(r[1] or 0) for r in rows.values()), Decimal(0))
    page = min(r[4] for r in rows.values())
    res.money("cur", total, doc, page)
    res.money("prev", sum((Decimal(r[2] or 0) for r in rows.values()), Decimal(0)), doc, page)
    res.money("prev_got_jan_sep", sum((Decimal(r[3] or 0) for r in rows.values()), Decimal(0)), doc, page)
    res.subject = rows[codes[0]][0].title() if focus != "all" else ""
    rep = latest_report(conn, year)
    if spec.get("report"):              # a period the question names: that report, even when a newer one exists
        q = conn.execute("SELECT max(quarter), max(year) FROM perf_items WHERE doc_id = %s", (spec["report"],)).fetchone()
        rep = (spec["report"], q[0]) if q and q[0] and q[1] == year else rep
    if rep:
        got_now = conn.execute("SELECT sum(ytd_spent), min(page) FROM (SELECT DISTINCT ON (code) code, ytd_spent, page "
                               "FROM perf_items WHERE doc_id = %s AND classification = 'economic' AND spend_kind = "
                               "'revenue' AND code = ANY(%s) ORDER BY code, seq) x", (rep[0], codes)).fetchone()
        if got_now[0] is not None:
            res.money("cur_got", got_now[0], rep[0], got_now[1])
            res.pct("cur_rate", got_now[0], total, rep[0], got_now[1])
            res.facts["cur_quarter"] = Fact(rep[1], "count", rep[0], got_now[1])
            res.titles.update(_titles(conn, {rep[0]}))
            res.working.append(f"Received in {year} to Q{rep[1]} ({rep[0]} p{got_now[1]}): {got_now[0]:,.2f}")
    if focus == "all":
        items = [(r[0].title(), r[1], r[4]) for c, r in sorted(rows.items())]
    else:
        items = [(n.title(), v, p) for n, v, p in conn.execute(
            f"SELECT DISTINCT ON (code) name, {cur}, page FROM budget_items WHERE doc_id = %s AND classification = "
            f"'economic' AND spend_kind = 'revenue' AND code LIKE %s AND length(code) = 4 ORDER BY code, seq",
            (doc, codes[0] + "%"))]
    for n, v, p in sorted(items, key=lambda x: x[1] or 0, reverse=True)[:TOP]:
        if v:
            res.rows.append(Row(n, v, doc, p))
    res.working.insert(0, f"Source: {doc}, Revenue by Economic Classification; codes {', '.join(codes)}: "
                          + "; ".join(f"{c} {r[0]} {cur} {Decimal(r[1] or 0):,.2f}" for c, r in sorted(rows.items())))
    res.found = True
    return res


RUN = {"project_status": project_status, "lga_projects": lga_projects, "ranking": ranking,
       "mda_profile": mda_profile, "function_profile": function_profile, "revenue": revenue}


def run_analysis(conn: psycopg.Connection, spec: dict) -> AnalysisResult | None:
    """None when the core has no data for the tool (not built yet): the caller falls back to search."""
    tool = spec.get("tool")
    if tool not in RUN:
        return None
    try:
        res = RUN[tool](conn, spec)
    except (psycopg.errors.UndefinedTable, ValueError) as e:
        conn.rollback()
        log.warning("analysis %s unavailable: %s", tool, e)
        return None
    log.info("analysis: %s found=%s subject=%s rows=%d reason=%s", tool, res.found, res.subject or "-",
             len(res.rows), res.reason or "-")
    return res
