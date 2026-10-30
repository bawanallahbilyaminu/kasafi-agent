"""Structured tools the planner's information need is matched to (data/catalog.yaml): they fill cells from data,
with every value's source, and code writes the answer around them. No model reads or writes a figure here.

  budget_core  approved budgets (budget_items, by year) and revised budgets and spending by quarter (perf_items),
               for a ministry or agency by its own code, total or personnel / overhead / capital;
  dtm_api      IOM DTM displacement figures by state and LGA, by round (app/sources/dtm.py).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from decimal import ROUND_HALF_UP, Decimal

import httpx

from app.agent.capabilities import Cell
from app.agent.need import Need
from app.sources import dtm as dtm_api

log = logging.getLogger(__name__)

APPROVED_YEARS = (2024, 2025, 2026)        # budget_items columns approved_<year>


@dataclass
class Source:
    doc_id: str
    title: str
    page: int
    row_id: str = ""                # the budget line (for the evidence crop)
    row_text: str = ""


@dataclass
class Filled:
    cells: list[Cell]
    sources: list[Source] = field(default_factory=list)
    api: str = ""                   # an API source named in the sources line ("IOM DTM API, Round 18 ...")


# --- budget_core -----------------------------------------------------------------------------------------------

def _source(conn, row_id: str) -> Source:
    r = conn.execute("SELECT l.doc_id, d.title, l.page, l.row_text FROM budget_lines l JOIN documents d "
                     "ON d.id = l.doc_id WHERE l.id = %s", (row_id,)).fetchone()
    return Source(r[0], r[1], r[2], row_id, r[3]) if r else Source("", "", 0, row_id)


def _perf_row(conn, code: str, kind: str, year: int, quarter: int | None):
    """The implementation report row for the year: the asked quarter, else the latest one we have."""
    return conn.execute(
        "SELECT id, quarter, original, revised, quarter_spent, ytd_spent FROM perf_items "
        "WHERE code = %s AND spend_kind = %s AND year = %s AND (%s::int IS NULL OR quarter = %s::int) "
        "ORDER BY quarter DESC, seq LIMIT 1", (code, kind, year, quarter, quarter)).fetchone()


def budget_fill(conn, cells: list[Cell]) -> Filled:
    out = Filled(cells)
    seen: dict[str, Source] = {}
    for c in cells:
        code, kind = c.entity.code, (c.split or "total")
        if not code or c.year is None:
            continue
        if c.measure == "approved":
            if c.year not in APPROVED_YEARS:
                continue
            r = conn.execute(f"SELECT id, approved_{c.year} FROM budget_items WHERE doc_id = %s AND code = %s "
                             f"AND spend_kind = %s AND approved_{c.year} IS NOT NULL ORDER BY seq LIMIT 1",
                             (f"budget-{c.year}-approved", code, kind)).fetchone()
            if r:
                c.value, row_id = Decimal(r[1]), r[0]
            else:
                continue
        else:
            r = _perf_row(conn, code, kind, c.year, c.quarter)
            if not r:
                continue
            row_id, q, original, revised, q_spent, ytd = r
            c.quarter = c.quarter or q
            value = {"original": original, "revised": revised, "quarter_spent": q_spent, "actual_ytd": ytd}.get(c.measure)
            if c.measure == "performance_pct" and revised:
                value = (Decimal(ytd or 0) / Decimal(revised) * 100).quantize(Decimal("0.1"), ROUND_HALF_UP)
                c.note = "calc"
            if value is None:
                continue
            c.value = Decimal(value)
        src = seen.get(row_id) or _source(conn, row_id)
        seen[row_id] = src
        c.source, c.by = f"{src.title}, p. {src.page}", "budget_core"
    out.sources = list({s.row_id: s for s in seen.values()}.values())
    return out


# --- dtm_api ---------------------------------------------------------------------------------------------------

async def dtm_fill(http: httpx.AsyncClient, settings, need: Need, cells: list[Cell]) -> Filled:
    """IDP figures for the state or its LGAs from the newest round (or every round for a trend)."""
    from app.agent.topics import _load_saved, _save, saved_lgas     # the last good pull, for an API outage
    out = Filled(cells)
    pulled = ""
    try:
        rounds = await dtm_api.state_rounds(http, settings) or []
        lgas = await dtm_api.lga_round(http, settings, round_number=rounds[0].round) if rounds else []
        lgas = lgas or (saved_lgas(settings, "Sokoto", rounds[0].round) if rounds else [])
        if rounds:
            _save(settings, "Sokoto", rounds, lgas or [])
    except (dtm_api.DtmError, httpx.HTTPError) as e:
        saved = _load_saved(settings, "Sokoto")
        if not saved:
            log.info("DTM API failed and no saved pull: %s", type(e).__name__)
            return out
        pulled, rounds, lgas = saved
    if not rounds:
        return out
    top = rounds[0]
    by_lga = {f.place.lower(): f for f in lgas or []}
    out.api = (f"IOM DTM API (Baseline), Round {top.round}, reporting date {top.date}"
               + (f", as pulled on {pulled}" if pulled else ""))
    for c in cells:
        if c.measure != "idp_count":
            continue
        if c.entity.type == "lga" and c.entity.resolved.lower() in by_lga:
            f = by_lga[c.entity.resolved.lower()]
            c.value, c.year = f.idps, None
        elif c.entity.type == "state" and c.level == "state":
            c.value = top.idps
        elif c.entity.type == "state" and c.level == "lga":       # all LGAs: the table is the value
            c.value = [(f.place, f.idps) for f in lgas or []]
        else:
            continue
        c.source, c.by, c.note = out.api, "dtm_api", f"Round {top.round}"
    if need.operation == "trend":
        for c in cells:
            if c.measure == "idp_count" and c.entity.type == "state":
                c.value = [(f"Round {f.round} ({f.date})", f.idps) for f in rounds]
    return out
