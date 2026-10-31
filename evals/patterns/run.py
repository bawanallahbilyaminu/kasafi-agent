"""Pattern eval (the Oct 31 phone-test patterns): cases generated from the data, never from the user's own
questions, with their expected answers taken from the structured tables.

Patterns and what makes a reply WRONG:
  p1 revenue: an MDA's expected or collected revenue, a donor or grant line, a revenue share: the figure is missing
     (the statewide summary instead of the rows is the classic failure).
  p2 period: spending by the end of a quarter that has a newer report: the named quarter's figure is missing.
  p3 project: a project named with a misspelt verb: its 2026 amount is missing.
  p4 narrative: what a BIR's narrative says: the reply doesn't cite that narrative page.
  p5 not_published: staff numbers: the reply doesn't say it isn't published, or lacks the agency's personnel figure.
  p6 multi_part: allocation and spending of one agency: either figure missing.
Every reply is also checked for: p7 non-Latin letters (Hausa above all), p8 internal labels or footnote digits in
names, p9 a line cut with '…', p11 a reply that opens with a bullet instead of a sentence.

    uv run python evals/patterns/run.py --generate [--seed 5]    -> evals/patterns/cases.json (a new draw)
    uv run python evals/patterns/run.py                          -> evals/patterns/report.md
"""

from __future__ import annotations

import argparse
import asyncio
import json
import random
import re
import sys
import time
from collections import defaultdict
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import psycopg  # noqa: E402

from app import usage  # noqa: E402
from app.agent.answer import answer_question, readable_amounts  # noqa: E402
from app.config import get_settings  # noqa: E402
from app.language import foreign_letters  # noqa: E402
from evals.runtime import run_each  # noqa: E402

HERE = Path(__file__).resolve().parent
CASES = HERE / "cases.json"
VERBS = {"Construction": "Constraction", "Rehabilitation": "Rehabilitaion", "Renovation": "Renovaton",
         "Provision": "Provison", "Procurement": "Procurment", "Completion": "Complection", "Supply": "Suply"}


def money(x) -> str:
    return f"{Decimal(x):,.2f}"


def title(name: str) -> str:
    """'MINISTRY OF LANDS AND HOUSING' -> 'Ministry of Lands and Housing' (agency names as people type them)."""
    small = {"of", "and", "for", "the", "in", "on", "to"}
    words = re.sub(r"\s+", " ", name).strip().split(" ")
    return " ".join(w.lower() if i and w.lower() in small else (w if w.isupper() and len(w) <= 5 else w.capitalize())
                    for i, w in enumerate(words))


def generate(conn, rng: random.Random) -> list[dict]:
    cases: list[dict] = []

    def add(pattern: str, text: str, expect: list[str], lang: str = "en", **kw) -> None:
        cases.append({"id": f"{pattern}-{sum(c['pattern'] == pattern for c in cases) + 1:02d}", "pattern": pattern,
                      "text": text, "lang": lang, "expect": expect, **kw})

    # p1: an MDA's expected revenue (2026 budget), its revenue collected by Q1 2026, donor / grant lines, a share
    rev = conn.execute("""SELECT DISTINCT ON (code) code, name, approved_2026 FROM budget_items
        WHERE doc_id = 'budget-2026-approved' AND classification = 'administrative' AND spend_kind = 'revenue'
          AND code ~ '^[0-9]{12}$' AND code !~ '^[0-9]{2}0{10}$' AND approved_2026 > 50000000
        ORDER BY code, seq""").fetchall()
    for code, name, amount in rng.sample(rev, min(3, len(rev))):
        add("p1_revenue", f"How much revenue does the {title(name)} expect to collect in 2026?", [money(amount)],
            code=code)
    got = conn.execute("""SELECT DISTINCT ON (code) code, name, ytd_spent FROM perf_items WHERE doc_id = 'bir-2026-q1'
        AND classification = 'administrative' AND spend_kind = 'revenue' AND code ~ '^[0-9]{12}$'
        AND code !~ '^[0-9]{2}0{10}$' AND ytd_spent > 1000000 ORDER BY code, seq""").fetchall()
    names = [r[1].lower() for r in got]
    got = [r for r in got if names.count(r[1].lower()) == 1]          # one row per name: the answer is unambiguous
    for code, name, amount in rng.sample(got, min(2, len(got))):
        add("p1_revenue", f"How much revenue had the {title(name)} collected by the end of Q1 2026?", [money(amount)],
            code=code)
    lines = conn.execute(r"""SELECT regexp_replace(l.name, '\s\d{8,}\s*-.*$', ''), b.amount_naira FROM budget_lines l
        JOIN budget_rows b ON b.line_id = l.id AND b.year = 2026 AND b.measure = 'approved'
        WHERE l.doc_id = 'budget-2026-approved' AND l.spend_kind = 'revenue' AND b.amount_naira > 0
          AND (l.name ~* ' BY [A-Z]' OR l.name ~* 'GRANT') AND l.name ~ '\d{12}'""").fetchall()
    for head, amount in rng.sample(lines, min(2, len(lines))):
        add("p1_revenue", f"How much does the 2026 budget expect to receive for the {title(head)}?", [money(amount)])
    faac = conn.execute("""SELECT approved_2026 FROM budget_items WHERE doc_id = 'budget-2026-approved' AND
        classification = 'economic' AND spend_kind = 'revenue' AND code = '11' ORDER BY seq LIMIT 1""").fetchone()
    if faac and faac[0]:
        add("p1_revenue", "What share of the state's expected 2026 revenue comes from FAAC?", [money(faac[0])])

    # p2 and p6: agencies with a 2026 budget and spending in both 2026 reports
    mdas = conn.execute("""SELECT DISTINCT ON (b.code) b.code, b.name, b.approved_2026, q1.ytd_spent, q2.ytd_spent
        FROM budget_items b
        JOIN perf_items q1 ON q1.doc_id = 'bir-2026-q1' AND q1.code = b.code AND q1.spend_kind = 'total'
        JOIN perf_items q2 ON q2.doc_id = 'bir-2026-q2' AND q2.code = b.code AND q2.spend_kind = 'total'
        WHERE b.doc_id = 'budget-2026-approved' AND b.classification = 'administrative' AND b.spend_kind = 'total'
          AND b.code ~ '^[0-9]{4}00000000$' AND b.code !~ '^[0-9]{2}0{10}$' AND b.approved_2026 > 0 AND q1.ytd_spent > 0 AND q2.ytd_spent > q1.ytd_spent
        ORDER BY b.code, b.seq, q1.seq, q2.seq""").fetchall()
    picks = rng.sample(mdas, min(6, len(mdas)))
    for code, name, appr, q1, q2 in picks[:2]:
        add("p2_period", f"How much had the {title(name)} spent by the end of Q1 2026?", [money(q1)], code=code,
            avoid=[money(q2)])
    if picks[2:3]:
        code, name, appr, q1, q2 = picks[2]
        add("p2_period", f"Nawa {title(name)} ta kashe zuwa ƙarshen Q1 2026?", [money(q1)], lang="ha", code=code,
            avoid=[money(q2)])
    q3 = conn.execute("""SELECT DISTINCT ON (p.code) p.code, p.name, p.ytd_spent FROM perf_items p
        JOIN perf_items q4 ON q4.doc_id = 'bir-2025-q4' AND q4.code = p.code AND q4.spend_kind = 'total'
        WHERE p.doc_id = 'bir-2025-q3' AND p.spend_kind = 'total' AND p.classification = 'administrative'
          AND p.code ~ '^[0-9]{4}00000000$' AND p.ytd_spent > 0 AND q4.ytd_spent > p.ytd_spent
        ORDER BY p.code, p.seq""").fetchall()
    for code, name, spent in rng.sample(q3, min(1, len(q3))):
        add("p2_period", f"How much did the {title(name)} spend from January to September 2025?", [money(spent)],
            code=code)
    for code, name, appr, q1, q2 in picks[3:5]:
        add("p6_multi_part", f"How much was allocated to the {title(name)} in 2026, and how much had it spent by "
                             f"the end of Q2 2026?", [money(appr), money(q2)], code=code)
    if picks[5:6]:
        code, name, appr, q1, q2 = picks[5]
        add("p6_multi_part", f"Nawa aka ware wa {title(name)} a 2026, kuma nawa ta kashe zuwa ƙarshen Q2 2026?",
            [money(appr), money(q2)], lang="ha", code=code)

    # p3: projects named with a misspelt verb
    projects = conn.execute(r"""SELECT regexp_replace(l.name, '\s\d{8,}\s*-.*$', ''), b.amount_naira FROM budget_lines l
        JOIN budget_rows b ON b.line_id = l.id AND b.year = 2026 AND b.measure = 'approved'
        WHERE l.doc_id = 'budget-2026-approved' AND l.classification = 'project' AND b.amount_naira > 0
          AND l.name ~* '^(construction|rehabilitation|renovation|provision|procurement|completion|supply) of'
        """).fetchall()
    for head, amount in rng.sample(projects, min(3, len(projects))):
        verb = head.split(" ", 1)[0].capitalize()
        asked = VERBS.get(verb, verb) + " " + head.split(" ", 1)[1].lower()
        add("p3_project", f"How much is budgeted for {asked} in 2026?", [money(amount)])

    # p4: a BIR narrative paragraph: the reply must cite its page
    # (running text, never a table of contents; the narrative sits under the table title the indexer carries over,
    # so '[Table:' is no sign of a table. The reply must cite the page AND give a figure the paragraph prints.)
    from app.retrieval.search import is_prose
    rows = conn.execute("""SELECT c.doc_id, c.page, c.text, d.title FROM chunks c JOIN documents d ON d.id = c.doc_id
        WHERE c.doc_id LIKE 'bir-%%' AND length(c.text) > 400
          AND c.text ~* '(increase|decrease|reason|due to|attribut|variance|explain|however|as a result)'
          AND c.text ~ '[0-9]{1,3},[0-9]{3},[0-9]{3}'""").fetchall()
    prose = []
    for doc, page, text, doc_title in rows:
        body = re.sub(r"^\[Table:[^\]]*\]\n", "", text)
        if not is_prose(body):
            continue
        m = re.search(r"(?m)^\s*\d+(?:\.[A-Z])?\s+([A-Z][A-Za-z ]{6,60}?)\s*$", body)        # the section heading
        phrases = [p for p in re.findall(r"(?:[A-Z][a-z]+ ){2,}[A-Z][a-z]+", body)
                   if not re.search(r"Sokoto State Government|Budget Implementation Report", p)]
        topic = m.group(1).strip() if m else (max(phrases, key=len) if phrases else "")
        figure = re.search(r"(?<![\d,.])\d{1,3}(?:,\d{3}){2,}(?:\.\d{2})?", body.split("\n", 1)[-1])
        if topic and figure:                    # a paragraph with a subject the question can name, and a figure
            prose.append((doc, page, doc_title, topic, figure.group(0)))
    for doc, page, doc_title, topic, figure in rng.sample(prose, min(3, len(prose))):
        add("p4_narrative", f"What does the {doc_title} say about {topic}, and what reasons does it give?",
            [figure], cites=[doc, page], narrative=True)

    # p5: staff numbers aren't published: say so and give the agency's personnel figure
    pers = conn.execute("""SELECT DISTINCT ON (code) code, name, approved_2026 FROM budget_items WHERE
        doc_id = 'budget-2026-approved' AND classification = 'administrative' AND spend_kind = 'personnel'
        AND code ~ '^[0-9]{4}00000000$' AND code !~ '^[0-9]{2}0{10}$' AND approved_2026 > 0
        ORDER BY code, seq""").fetchall()
    for code, name, amount in rng.sample(pers, min(2, len(pers))):
        add("p5_not_published", f"How many staff does the {title(name)} employ, and on which grade levels?",
            [money(amount)], code=code, must_say=r"(?i)publish|wallafa|buga")
    return cases


def accepted(number: str) -> list[str]:
    out = [number]
    for lg in ("en", "ha"):
        out.append(readable_amounts(f"₦{number}", lg).lstrip("₦"))
    return out


INTERNAL = re.compile(r"(?i)one agency or unit|all spending \(total\)|ministry total including|objective inside a "
                      r"sector|programme inside a sector")
FOOTNOTE = re.compile(r"\b[A-Za-z][a-z]{2,}\d{1,2}\b(?!\s*(?:Q|%))")


NO_TEXT = re.compile(r"(?i)(?:excerpts?|evidence|documents?|pages?)[^.\n]{0,40}(?:do|does|did)\s*n[o']t\s+"
                     r"(?:include|contain|show|give|provide)|not (?:shown|included|provided|available)|"
                     r"isn['’]t (?:available|shown|included)|no (?:narrative|overview|explanation) (?:text|is|was)|"
                     r"ba a (?:samu|nuna|bayar da) (?:bayani|rubutu)|babu (?:bayani|rubutu)")


def judge(case: dict, a) -> tuple[str, list[str]]:
    """(why the pattern case is wrong or '', the output checks that failed)."""
    text = f"{a.text}"
    why = ""
    for want in case["expect"]:
        if not any(form in text or form in (a.exact or "") for form in accepted(want)):
            why = f"missing {want}"
            break
    if not why and case.get("cites"):
        doc, page = case["cites"]
        if not any(e.doc_id == doc and e.page == page for e in a.cited or []):
            why = f"didn't cite {doc} p{page}"
    if not why and case.get("must_say") and not re.search(case["must_say"], text):
        why = "didn't say it isn't published"
    if not why and case.get("narrative") and (m := NO_TEXT.search(text)):
        why = f"says the narrative isn't there: {m.group(0)!r}"           # even with the right page cited
    if not why and case.get("avoid") and any(any(f in text for f in accepted(x)) for x in case["avoid"]) and \
            not any(any(f in text for f in accepted(x)) for x in case["expect"]):
        why = "gave the newer report's figure"
    body = [ln for ln in text.splitlines() if ln.strip() and not ln.startswith(("_", "📄", "🧮"))]
    checks = []
    if foreign_letters(text):
        checks.append("p7_letters")
    if INTERNAL.search(text) or FOOTNOTE.search(re.sub(r"https?://\S+", "", text)):
        checks.append("p8_labels")
    if any(ln.rstrip().endswith("…") and "+" not in ln for ln in body):
        checks.append("p9_cut")
    if body and body[0].lstrip().startswith(("•", "-", "*•")) and a.found:
        checks.append("p11_bullet_first")
    return why, checks


async def run(cases: list[dict], out: Path) -> None:
    s = get_settings()
    results: dict[str, dict] = {}

    async def one(c: dict, conn) -> None:
        t0 = time.perf_counter()
        try:
            a = await answer_question(c["text"], c["lang"], conn, settings=usage.eval_settings(s, fetch=False))
            why, checks = judge(c, a)
            text = a.text
        except Exception as e:                      # noqa: BLE001 - one bad case must not stop the run
            conn.rollback()
            why, checks, text = f"error {type(e).__name__}", [], "-"
        dt = time.perf_counter() - t0
        results[c["id"]] = {"why": why, "checks": checks, "text": text, "dt": dt}
        print(f"{c['id']:22} {'WRONG ' + why if why else 'ok':48.48} {','.join(checks):30} {dt:5.1f}s")

    if not await run_each(cases, one, s.db_url(), 3, s):
        raise SystemExit(2)
    per = defaultdict(lambda: [0, 0])
    checks = defaultdict(int)
    for c in cases:
        r = results.get(c["id"])
        if r is None:
            continue
        per[c["pattern"]][0] += bool(r["why"])
        per[c["pattern"]][1] += 1
        for k in r["checks"]:
            checks[k] += 1
    lines = ["# Pattern eval", "", "| pattern | wrong | of |", "|---|---|---|"]
    lines += [f"| {p} | {w} | {n} |" for p, (w, n) in sorted(per.items())]
    lines += ["", "Output checks on every reply (count of replies failing):", "", "| check | failing |", "|---|---|"]
    lines += [f"| {k} | {checks.get(k, 0)} |" for k in ("p7_letters", "p8_labels", "p9_cut", "p11_bullet_first")]
    lines.append("")
    for c in cases:
        r = results.get(c["id"], {})
        lines += [f"## {c['id']} {'WRONG: ' + r.get('why') if r.get('why') else 'ok'} {' '.join(r.get('checks', []))} "
                  f"({r.get('dt', 0):.1f}s)", "", f"**Q:** {c['text']}", "", "```", r.get("text", "-"), "```", ""]
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines[:12 + len(per)]))


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--generate", action="store_true")
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--out", default=str(HERE / "report.md"))
    args = ap.parse_args()
    if args.generate:
        seed = args.seed if args.seed is not None else random.randrange(10_000)
        with psycopg.connect(get_settings().db_url()) as conn:
            cases = generate(conn, random.Random(seed))
        CASES.write_text(json.dumps({"seed": seed, "cases": cases}, ensure_ascii=False, indent=1) + "\n",
                         encoding="utf-8")
        print(f"{len(cases)} cases (seed {seed}) -> {CASES}")
        return
    asyncio.run(run(json.loads(CASES.read_text(encoding="utf-8"))["cases"], Path(args.out)))


if __name__ == "__main__":
    main()
