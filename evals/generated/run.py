"""Run generated coverage cases and report the wrong rate per family (docs/question-planning.md §6).

Each case runs in one form, picked at random per run (the template's own English, or a paraphrase: hausa,
informal, code_switched, typo, followup with its previous turn). A reply is WRONG when an expected figure is
missing (exact, or in its readable form '₦42.00 million'), a false premise is repeated, or a figure is given
for a period that isn't published. Not found where the data has the answer counts as wrong too.

    uv run python evals/generated/run.py [--forms all|template|paraphrase] [--seed 1] [--families split lookup]
    uv run python evals/generated/run.py --fresh         # ~50 new random cases (development), paraphrased, then
                                                         # run; cases kept in runs/
    uv run python evals/generated/run.py --fresh 155     # the full ~155, only before a deploy
    uv run python evals/generated/run.py --resume --out ...   # continue a stopped run (same draw, same forms)

Each case's result is written to evals/.checkpoints/<out stem>.jsonl as it finishes (evals/runtime.py).
"""

from __future__ import annotations

import argparse
import asyncio
import json
import random
import re
import statistics
import sys
import time
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from app.agent.answer import answer_question, readable_amounts  # noqa: E402
from app import usage  # noqa: E402
from app.config import get_settings  # noqa: E402
from evals.runtime import Checkpoint, Progress, memory_line, run_each, warm  # noqa: E402

CASES = Path(__file__).with_name("cases.json")
RUNS = Path(__file__).with_name("runs")          # fresh draws (not in git: the report names the seed)
FETCH_FAMILIES = {"missing_document"}             # the only families that may fetch or search the open web


def accepted(number: str, lang: str) -> list[str]:
    """The exact figure and its readable forms ('₦42.00 million' / 'miliyan'), in either language."""
    out = [number]
    if "," in number and "." in number:
        for lg in ("en", "ha"):
            out.append(readable_amounts(f"₦{number}", lg).lstrip("₦"))
    return out


AGENCY_CODE = re.compile(r"\bcode (\d{12})\b")


def wrong_agency(case: dict, a) -> bool:
    """The reply's agency rows are another agency's: it prints 12-digit codes, none of them the case's own (or,
    for a unit printed with its ministry's name, the ministry's)."""
    want = set(case.get("codes") or ([case["code"]] if case.get("code") else []))
    got = set(AGENCY_CODE.findall(f"{a.exact}\n{a.text}"))
    return bool(want and got and not want & got)


def wrong(case: dict, a, lang: str) -> str:
    text = f"{a.exact}\n{a.text}"
    if wrong_agency(case, a):
        return "WRONG AGENCY " + ", ".join(sorted(set(AGENCY_CODE.findall(text))))
    if case.get("expect_gap"):                       # nothing published: no figure for that period, say what exists
        est = case.get("estimate") or []             # ... or the budget's own out-year estimate, labelled as one
        est = [est] if isinstance(est, str) else est
        if any(f in text for e in est for f in accepted(e, lang)) and re.search(r"(?i)estimate|[kƙ]iyasi|hasashe",
                                                                                 a.text):
            return ""
        if case["expect_gap"] not in a.text and "newest" not in a.text.lower() and "latest" not in a.text.lower() \
                and "mafi sabo" not in a.text:
            return f"no mention of what exists ({case['expect_gap']})"
        return ""
    if not a.found:
        return "not found, though the data has it"
    groups = case.get("numbers_any") or [case.get("numbers", [])]
    if not any(all(any(f in text for f in accepted(n, lang)) for n in g) for g in groups):
        missing = [n for n in groups[0] if not any(f in text for f in accepted(n, lang))]
        return f"missing {missing}"
    if case.get("premise_false") and not corrects(a.text, case.get("premise", "")):
        return "didn't correct a premise the figures contradict"
    return ""


# a reply corrects a false premise when it says the change didn't happen ("did not go up", "there was no rise",
# Hausa "bai karu ba") or names the real direction, the opposite of the premise's; a "because" is no sign either way
DENIES = re.compile(r"(?i)\b(?:did not|didn't|does not|not (?:an? )?(?:go|rise|fall|increase|decrease|drop)|"
                    r"no (?:rise|fall|increase|decrease|drop)|actually|in fact|instead|rather|"
                    r"bai (?:karu|ƙaru|ragu)|ba (?:ta|ya) (?:karu|ƙaru|ragu))\b")
DIRECTION = {"rise": re.compile(r"(?i)\b(?:rose|increased|went up|grew|an increase|a rise|ya karu|ya ƙaru)\b"),
             "fall": re.compile(r"(?i)\b(?:fell|decreased|dropped|went down|declined|a decrease|a drop|a fall|"
                                r"ya ragu)\b")}


def corrects(text: str, premise: str) -> bool:
    real = {"rise": "fall", "fall": "rise"}.get(premise)
    return bool(DENIES.search(text) or (real and DIRECTION[real].search(text)))


def per_family(cases: int) -> int:
    """Entities per family for about `cases` cases: 8 families take one each, rank_lga up to 3, trend 1
    (50 -> 6 per family, 52 cases; 155 -> 19, 156 cases)."""
    return max(1, round((cases - 4) / 8))


def pick_form(c: dict, forms: str, seed: int) -> str:
    """The case's form for this run: drawn per case from the seed, so a resumed run asks the same forms."""
    options = ["template"] + list((c.get("forms") or {}).keys())
    if forms == "template":
        options = ["template"]
    elif forms == "paraphrase" and len(options) > 1:
        options = options[1:]
    return random.Random(f"{seed}:{c['id']}").choice(options)


async def main(forms: str, seed: int, families: list[str] | None, out: Path, cases_path: Path = CASES,
               ckpt: Checkpoint | None = None, concurrency: int = 1) -> None:
    s = get_settings()
    data = json.loads(cases_path.read_text(encoding="utf-8"))
    cases = [c for c in data["cases"] if not families or c["family"] in families]
    ckpt = ckpt or Checkpoint(out.stem, {"cases": str(cases_path), "forms": forms, "seed": seed,
                                         "families": families}, resume=False)
    resumed = len(ckpt.done)
    warm()
    prog = Progress(out.stem, len(cases), s, resumed, sum(bool(r["why"]) for r in ckpt.done.values()))

    async def one(c: dict, conn) -> None:
        form = pick_form(c, forms, seed)
        q, history, lang = c["text"], None, "en"
        if form != "template":
            v = c["forms"][form]
            if form == "followup":
                q, history = v["question"], [{"question": v["previous"], "answer": "", "sources": []}]
            else:
                q = v
            lang = "ha" if form in ("hausa", "code_switched") else "en"
        t0 = time.perf_counter()
        try:
            a = await answer_question(q, lang, conn, history=history,     # fetching only where a family needs it
                                      settings=usage.eval_settings(s, fetch=c["family"] in FETCH_FAMILIES))
            why, text = wrong(c, a, lang), a.text
        except Exception as e:                       # one bad case must not stop the run
            conn.rollback()
            why, text = f"error {type(e).__name__}", "-"
        dt = time.perf_counter() - t0
        print(f"{c['id']:18} {form:13} {'WRONG ' + why if why else 'ok':60.60} {dt:5.1f}s")
        prog.case(c["id"], why, dt)
        ckpt.add(c["id"], {"family": c["family"], "form": form, "q": q, "why": why, "dt": dt, "text": text})

    if not await run_each([c for c in cases if c["id"] not in ckpt.done], one, s.db_url(), concurrency, s):
        raise SystemExit(2)                          # the day's eval budget: --resume continues
    per_family: dict[str, list] = defaultdict(list)
    per_form: dict[str, list] = defaultdict(list)
    times, report = [], [f"# Generated coverage run\n\nCases: {cases_path.name} (draw seed {data.get('seed')}), "
                         f"form seed {seed}\n"]
    for c in cases:                                  # in case order, whichever session ran them
        r = ckpt.done[c["id"]]
        times.append(r["dt"])
        per_family[r["family"]].append(bool(r["why"]))
        per_form[r["form"]].append(bool(r["why"]))
        report.append(f"## {c['id']} ({r['form']}) {'WRONG: ' + r['why'] if r['why'] else 'ok'} ({r['dt']:.1f}s)\n\n"
                      f"**Q:** {r['q']}\n\n```\n{r['text']}\n```\n")
    lines = ["| family | wrong | of |", "|---|---|---|"]
    lines += [f"| {f} | {sum(v)} | {len(v)} |" for f, v in sorted(per_family.items())]
    lines += ["", "| form | wrong | of |", "|---|---|---|"]
    lines += [f"| {f} | {sum(v)} | {len(v)} |" for f, v in sorted(per_form.items())]
    total = sum(sum(v) for v in per_family.values())
    agency = sum(r.startswith("## ") and "WRONG: WRONG AGENCY" in r for r in report)
    summary = (f"{len(cases)} cases: wrong {total} ({100 * total / max(len(cases), 1):.1f}%), of them wrong agency "
               f"{agency} | median {statistics.median(times):.1f}s")
    print("\n" + summary + "\n" + "\n".join(lines))
    cost = usage.summary(s, answers=len(cases)) + "\n" + memory_line(resumed)
    print(cost)
    out.write_text("\n".join([report[0], summary, "", *lines, "", "```", cost, "```", "", *report[1:]]),
                   encoding="utf-8")
    print("report:", out)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--forms", default="all", choices=["all", "template", "paraphrase"])
    p.add_argument("--seed", type=int, default=1)
    p.add_argument("--families", nargs="+")
    p.add_argument("--out", type=Path, default=Path(__file__).with_name("report.md"))
    p.add_argument("--fresh", type=int, nargs="?", const=50, metavar="CASES",
                   help="draw about CASES new cases (default 50 for development; 155 before a deploy), paraphrase "
                                                          "them, then run")
    p.add_argument("--resume", action="store_true", help="continue the stopped run with this --out (same draw and "
                                                         "seed), running only the cases it hadn't finished")
    p.add_argument("--concurrency", type=int, default=1, choices=[1, 2])
    p.add_argument("--hazards", type=int, metavar="N", help="draw N LGAs per hazard family (evals/generated/"
                                                             "hazards.py: expected values from hazard_values now) "
                                                             "and run them")
    a = p.parse_args()
    cases_path = CASES
    header = {"forms": a.forms, "seed": a.seed, "families": a.families}
    ckpt = Checkpoint(a.out.stem, header, resume=True) if a.resume else None
    if ckpt and ckpt.header.get("cases"):
        cases_path = Path(ckpt.header["cases"])      # a fresh draw is resumed from its own cases file
    elif a.hazards:
        from evals.generated.hazards import build as build_hazards
        cases_path = build_hazards(a.hazards, random.randrange(10**6))
    elif a.fresh:
        from evals.generated.generate import build
        draw = random.randrange(10**6)
        cases_path = build(per_family(a.fresh), draw, RUNS / f"cases-{draw}.json")
    if ckpt is None or not ckpt.header.get("cases"):  # the cases file is known before any model call is made
        ckpt = Checkpoint(a.out.stem, header | {"cases": str(cases_path)}, resume=False)
    if a.fresh:                                      # paraphrases only the cases that don't have them yet
        from evals.generated.paraphrase import paraphrase
        asyncio.run(paraphrase(cases_path))
    asyncio.run(main(a.forms, a.seed, a.families, a.out, cases_path, ckpt, a.concurrency))
