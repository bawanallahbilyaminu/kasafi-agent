"""One trace record per answered question, for the admin trace page and the review queue (app/admin).

A trace holds the English wording of the question, the plan, the path the agent took, what each of the two model
readings chose and what code kept, the citations, timings and the reply. It never holds a phone number, user key or
WhatsApp name: phone numbers, emails and long digit strings a user typed are removed from the wording (`redact`).
Written in one insert after the reply is ready; a failure to write never affects the answer.
"""

from __future__ import annotations

import json
import logging
import re

import psycopg

log = logging.getLogger(__name__)

TRACE_RETENTION_DAYS = 30

# Personal numbers a user might type into a question; removed before the wording is stored. Years ("2025 2026")
# and printed amounts ("70,000,000.00") don't match.
_EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
_PHONE = re.compile(r"(?<![\w+])(?:\+\d{1,3}(?:[\s.-]?\(?\d\)?){7,12}|(?:234|0)[789][01](?:[\s.-]?\d){8})(?!\d)")
_LONG_DIGITS = re.compile(r"(?<!\d)(?<!\d[,.])\d{10,}(?!\d|[,.]\d)")


def redact(text: str) -> str:
    """The wording with emails, phone numbers and long digit strings (account, NIN) taken out."""
    text = _EMAIL.sub("[email removed]", text or "")
    text = _PHONE.sub("[number removed]", text)
    return _LONG_DIGITS.sub("[number removed]", text)

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
    if getattr(a, "analysis", None) is not None:
        return f"analysis:{a.analysis.tool}"
    if getattr(a, "category", None) is not None:
        return "category"
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


def _scrub(v):
    if isinstance(v, str):
        return redact(v)
    if isinstance(v, list):
        return [_scrub(x) for x in v]
    if isinstance(v, dict):
        return {k: _scrub(x) for k, x in v.items()}
    return v


def scrub_reply(text: str) -> str:
    """The reply keeps its long figures and 12-digit budget codes; emails and phone numbers go."""
    return _PHONE.sub("[number removed]", _EMAIL.sub("[email removed]", text or ""))


def record(a) -> dict:
    plan = {k: _scrub(getattr(a.plan, k)) for k in PLAN_FIELDS if a.plan is not None and getattr(a.plan, k, None)}
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
    if getattr(a, "category", None) is not None:
        c = a.category
        t["category"] = {"doc": c.doc_id, "year": c.year, "measure": c.measure, "checked": c.checked,
                         "scope": c.scope_name, "scope_group": c.scope_group, "scope_units": c.scope_units,
                         "codes": [{"code": x.code, "name": x.name, "printed": str(x.printed.amount),
                                    "page": x.printed.page, "unit_sum": str(x.unit_sum), "units": len(x.units)}
                                   for x in c.codes]}
    if getattr(a, "analysis", None) is not None:
        r = a.analysis
        t["analysis"] = {"tool": r.tool, "subject": r.subject, "focus": r.focus, "year": r.year,
                         "facts": {k: str(v.value) for k, v in r.facts.items()}, "rows": len(r.rows)}
    if getattr(a, "working", ""):
        t["working"] = a.working[:4000]                      # shown to the user only on "nuna lissafi"
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
        question = redact(a.plan.english_question if a.plan else "") or "(no plan)"
        conn.execute("DELETE FROM traces WHERE created_at < now() - make_interval(days => %s)",
                     (TRACE_RETENTION_DAYS,))
        conn.execute("INSERT INTO traces (lang, question, outcome, path, seconds, trace, answer) "
                     "VALUES (%s, %s, %s, %s, %s, %s, %s)",
                     (lang, question, out, path(a), round(seconds, 2), json.dumps(t, default=str),
                      scrub_reply(a.text)))
        conn.commit()
    except Exception as e:          # the reply is already made: a trace must never break it
        conn.rollback()
        log.warning("trace not saved: %s", type(e).__name__)
