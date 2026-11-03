"""Routing eval (docs/routing.md): questions that carry another feature's words, with the route each must take.
In code, no model, no spend: `route_for` applies the shortcut predicates in the order the conversation handler and
the answer loop apply them (the planner's own document path is "planner"). Run before deploys:

    uv run python evals/routing/run.py            -> evals/routing/report.md (exit 1 when any case is wrong)

The named-facility routes need the facility registry (the dev database); without it those cases are skipped.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.stdout.reconfigure(encoding="utf-8")

ROUTES = ("emergency", "guard", "alert", "map", "facility_count", "facility_named", "facility_nearest",
          "place_area", "place_pin", "outbreak", "outlook", "hazard", "deep", "planner")


def route_for(question: str, settings, conn=None, place: dict | None = None, reading: str | None = None) -> str:
    """The shortcut that answers `question` before the planner's document path, or 'planner'. Mirrors
    app/whatsapp/conversation.py (handle) then app/agent/answer.py (_answer_question) in their order; the
    structured budget tools and the topic path are the planner's own and count as 'planner'. `reading`: the
    understanding step's capability for the case; a shortcut answers only when it names that capability (allow()
    in _answer_question), as live."""
    from app.agent.answer import MONEY_WORDS
    from app.agent.routing import document_question, facility_intent, other_subject, own_source
    from app.alerts.signup import INTENT, MENU, STOP
    from app.geo.facilities import is_facility_query
    from app.geo.facility_info import NAMED, ROUTE_TO, find_by_name, is_count
    from app.guardrails import emergency as em
    from app.guardrails.scope import keyword_check
    from app.hazards import official
    from app.hazards.answer import layers_asked
    from app.place.answer import place_route
    from app.place.planner import area_route
    from app.whatsapp.conversation import FACILITY_WORD, MAP_ONLY, _norm
    q = question or ""

    def allow(*caps: str) -> bool:
        return reading is None or reading in caps
    if em.detect(q).hit:
        return "emergency"
    if keyword_check([q]):
        return "guard"
    if settings.kasafi_shortcut_alerts and (INTENT.search(q) or _norm(q) in MENU or _norm(q) in STOP):
        return "alert"
    if MAP_ONLY.match(q):
        return "map"
    doc = document_question(q)
    from app.agent.deep import deep_question
    if reading == "deep" or allow("deep") and reading is None and deep_question(q) and \
            not (area_route(q, "", place) or place_route(q)) and not official.route(q, []) \
            and not (layers_asked(q, []) and not MONEY_WORDS.search(q)):
        return "deep"                                         # a broad question: the deep analysis, never a shortcut
    if settings.kasafi_shortcut_facilities and allow("facility") and not doc and \
            not (other_subject(q) and not is_facility_query(q)):
        if is_count(q):
            return "facility_count"
        if (FACILITY_WORD.search(q) or ROUTE_TO.search(q)) and (facility_intent(q) or ROUTE_TO.search(q)) \
                and not is_facility_query(q):
            if conn is None:
                return "facility_named?"                      # needs the registry: skipped without it
            hits = find_by_name(conn, q)
            if hits and hits[0].score >= NAMED:
                return "facility_named"
        if is_facility_query(q):
            return "facility_nearest"
    # after the plan (the planner's measures are not known here: the words alone)
    if settings.kasafi_shortcut_place and allow("place_history") and not doc:
        if area_route(q, "", place):
            return "place_area"
        if place_route(q):
            return "place_pin"
    if settings.kasafi_shortcut_hazards and allow("hazard") and (not doc or own_source(q, ("NCDC", "NiMet", "NIHSA"))):
        kind = official.route(q, [])
        if kind == "outbreaks":
            return "outbreak"
        if kind:
            return "outlook"
        if layers_asked(q, []) and not MONEY_WORDS.search(q) and (not doc or own_source(q, ("NiMet", "NIHSA", "NCDC"))):
            return "hazard"
    return "planner"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", default=str(ROOT / "evals/routing/cases.json"))
    ap.add_argument("--out", default=str(ROOT / "evals/routing/report.md"))
    a = ap.parse_args()
    from app.config import get_settings
    s = get_settings()
    conn = None
    try:
        import psycopg
        if s.has_database:
            conn = psycopg.connect(s.db_url(), connect_timeout=3)
            conn.execute("SELECT 1 FROM facility LIMIT 1").fetchone()
    except Exception:              # noqa: BLE001
        conn = None
    cases = json.loads(Path(a.file).read_text(encoding="utf-8"))["cases"]
    rows, wrong, skipped = [], 0, 0
    for c in cases:
        got = route_for(c["question"], s, conn, c.get("place"), c.get("reading"))
        if got.endswith("?"):
            skipped += 1
            rows.append(f"| {c['id']} | {c['lang']} | {c['expected']} | skipped (no registry) | {c['question']} |")
            continue
        ok = got == c["expected"]
        wrong += not ok
        rows.append(f"| {c['id']} | {c['lang']} | {c['expected']} | {got if ok else '**' + got + '**'} | {c['question']} |")
        print(c["id"], "ok" if ok else f"WRONG: {got}", "|", c["question"][:70])
    report = [f"# Routing eval (in code), {date.today()}", "",
              f"{len(cases)} cases, **{wrong} wrong**, {skipped} skipped (no facility registry).", "",
              "| id | lang | expected | got | question |", "|---|---|---|---|---|", *rows]
    Path(a.out).write_text("\n".join(report), encoding="utf-8")
    print(f"\n{len(cases)} cases, {wrong} wrong, {skipped} skipped -> {a.out}")
    sys.stdout.flush()
    os._exit(1 if wrong else 0)


if __name__ == "__main__":
    main()
