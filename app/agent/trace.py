"""One trace record per answered question, for the admin trace page and the review queue (app/admin).

A trace holds the English wording of the question, the plan, the path the agent took, what each of the two model
readings chose and what code kept, the citations, timings and the reply. It never holds a phone number, user key or
WhatsApp name. Written in one insert after the reply is ready; a failure to write never affects the answer.
"""

from __future__ import annotations

import json
import logging

import psycopg

log = logging.getLogger(__name__)

TRACE_RETENTION_DAYS = 30

PLAN_FIELDS = ("english_question", "doc_ids", "search_queries", "key_terms", "line_search", "budget_query",
               "assumption", "missing_document", "latest", "followup")


def outcome(a) -> str:
    from app.agent.answer import UNVERIFIED
    if a.clarify:
        return "clarify"
    if not a.found:
        return "not found"
    if not a.verified or any(u in a.text for u in UNVERIFIED.values()):
        return "unverified"
    return "partial" if a.partial else "answered"


def path(a) -> str:
    if a.lines is not None:
        return f"lines:{a.lines.operation}"
    if a.budget is not None:
        return f"query_budget:{a.budget.operation}"
    return "latest" if a.latest else "fetch" if a.acquired else "search"


def flags(a, out: str) -> list[str]:
    """Why a person should look at this answer (the review queue shows flagged traces)."""
    f = [out] if out != "answered" else []
    if a.lines is not None:
        if any("fallback" in r for r in a.lines.readers):
            f.append("Muse Spark Open fell back")
        if a.lines.disputed or a.lines.uncertain:
            f.append("readings disagreed")
    return f


def record(a) -> dict:
    plan = {k: getattr(a.plan, k) for k in PLAN_FIELDS if a.plan is not None and getattr(a.plan, k, None)}
    t: dict = {"plan": plan, "timings": {k: round(v, 2) for k, v in a.timings.items()},
               "cited": [{"n": e.n, "doc": e.doc_id, "title": e.title, "page": e.page, "source": e.source}
                         for e in a.cited],
               "verified": a.verified}
    if a.lines is not None:
        from app.agent.line_answer import pick_text
        r = a.lines
        t["lines"] = {"readers": r.readers, "picks": r.picks, "kept": [pick_text(s) for s in r.selections],
                      "uncertain": r.uncertain, "disputed": r.disputed, "operation": r.operation,
                      "computed": {k: str(v) for k, v in r.computed().items()}, "missing": r.missing,
                      "found": r.found}
    if a.budget is not None:
        t["budget"] = {"operation": a.budget.operation,
                       "total": str(a.budget.total) if a.budget.total is not None else None}
    if a.acquired is not None:
        t["acquired"] = {"status": a.acquired.status, "doc": a.acquired.doc_id}
    if a.latest is not None:
        t["latest"] = {"series": a.latest.series.name, "doc": a.latest.doc_id}
    return t


def save(conn: psycopg.Connection, a, lang: str, seconds: float) -> None:
    try:
        out = outcome(a)
        t = record(a)
        t["flags"] = flags(a, out)
        question = (a.plan.english_question if a.plan else "") or "(no plan)"
        conn.execute("DELETE FROM traces WHERE created_at < now() - make_interval(days => %s)",
                     (TRACE_RETENTION_DAYS,))
        conn.execute("INSERT INTO traces (lang, question, outcome, path, seconds, trace, answer) "
                     "VALUES (%s, %s, %s, %s, %s, %s, %s)",
                     (lang, question, out, path(a), round(seconds, 2), json.dumps(t, default=str), a.text))
        conn.commit()
    except Exception as e:          # the reply is already made: a trace must never break it
        conn.rollback()
        log.warning("trace not saved: %s", type(e).__name__)
