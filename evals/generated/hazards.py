"""Generated hazard questions (docs/hazard-and-services.md section 13): per layer x LGA x day x language, with the
expected values read from hazard_values at draw time. Forecasts change every 3 hours, so cases are drawn right
before a run, on the same data the answers read (run.py --hazards N draws and runs them). Model evals run only
before a deploy.

Families: hazard_heat, hazard_rain, hazard_air, hazard_flood, hazard_fires, hazard_overview. A reply is right when
it gives the expected figures (as the answer prints them) and the category label.

    uv run python evals/generated/hazards.py --n 6 [--seed 7]     -> evals/generated/runs/hazards-<seed>.json
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from datetime import timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import psycopg  # noqa: E402

from app.agent.answer import lagos_today  # noqa: E402
from app.config import get_settings  # noqa: E402
from app.hazards import categories as cat  # noqa: E402
from app.hazards import read  # noqa: E402
from app.hazards.answer import SEASON, W, discharge  # noqa: E402

RUNS = Path(__file__).with_name("runs")
WHEN = {"en": {0: "today", 1: "tomorrow", 3: "over the next 3 days"},
        "ha": {0: "yau", 1: "gobe", 3: "a cikin kwana uku masu zuwa"}}
TEMPLATES = {
    "hazard_heat": {"en": "How hot will it be in {lga} {when}?", "ha": "Yaya zafin rana zai kasance a {lga} {when}?"},
    "hazard_rain": {"en": "Will it rain in {lga} {when}?", "ha": "Za a yi ruwan sama a {lga} {when}?"},
    "hazard_air": {"en": "How bad is the harmattan dust in {lga} {when}?",
                   "ha": "Yaya ƙurar hunturu take a {lga} {when}?"},
    "hazard_flood": {"en": "Is the river high near {lga} {when}?", "ha": "Kogin da ke kusa da {lga} ya cika {when}?"},
    "hazard_fires": {"en": "Are there fires in {lga} now?", "ha": "Akwai gobara a {lga} yanzu?"},
    "hazard_overview": {"en": "What should we watch out for in {lga} this week?",
                        "ha": "Me ya kamata mu kula da shi a {lga} wannan mako?"},
}


def expected(conn, family: str, pid: int, lga: str, pcode: str, day, lang: str) -> list[str] | None:
    """The figures and label the answer must give, read from hazard_values; None when there's no data."""
    if family in ("hazard_heat", "hazard_rain"):
        r = read.heat_day(conn, pid, lga, day)
        if r is None:
            return None
        if family == "hazard_heat":
            return [f"{r.heat_index_max:.0f} °C", f"*{cat.label(r.category, lang)}*"]
        return [f"{r.rain_mm:.1f} mm"] if r.rain_mm >= 0.1 else \
            ["no rain expected" if lang == "en" else "ba a sa ran ruwan sama ba"]
    if family == "hazard_air":
        r = read.air_day(conn, pid, lga, day)
        by = f"{'set by' if lang == 'en' else 'saboda'} {r.aqi_by}" if r else ""
        return [f"{r.pm10_mean:.0f} µg/m³", by, f"*{cat.label(r.category, lang)}*"] if r else None
    if family == "hazard_flood":
        rows = read.river_days(conn, day, pcode)
        return [f"{discharge(rows[0].discharge)} m³/s", f"*{W[lang]['levels'][rows[0].level]}*"] if rows else None
    if family == "hazard_fires":
        n = sum(c.count for c in read.fire_counts(conn, 24, pcode))
        return [f": {n} {'in' if lang == 'en' else 'a'} {lga}"] if n else \
            ["No satellite heat detections" if lang == "en" else "Babu alamun zafi"]
    if family == "hazard_overview":
        names = W[lang]["season_names"]
        return [", ".join(names[x] for x in SEASON[day.month])]
    return None


def generate(conn, n: int, rng: random.Random) -> list[dict]:
    today = lagos_today()
    lgas = conn.execute("SELECT p.id, l.name, l.pcode FROM hazard_point p JOIN lga l ON l.pcode = p.lga_pcode "
                        "WHERE p.kind = 'lga'").fetchall()
    rivers = {r[0] for r in conn.execute("SELECT DISTINCT lga_pcode FROM hazard_point WHERE kind = 'river'")}
    cases = []
    for family, forms in TEMPLATES.items():
        pool = [x for x in lgas if x[2] in rivers] if family == "hazard_flood" else lgas
        for pid, lga, pcode in rng.sample(pool, min(n, len(pool))):
            lang = rng.choice(("en", "ha"))
            offset = 0 if family in ("hazard_fires", "hazard_overview") else rng.choice((0, 1, 3))
            day = today + timedelta(days=1 if offset == 1 else 0)
            want = expected(conn, family, pid, lga, pcode, day, lang)
            if want is None:
                continue
            cases.append({"id": f"{family}-{sum(c['family'] == family for c in cases) + 1:02d}", "family": family,
                          "lang": lang, "text": forms[lang].format(lga=lga, when=WHEN[lang][offset]),
                          "numbers": want, "drawn_on": today.isoformat()})
    return cases


def build(n: int, seed: int, out: Path | None = None) -> Path:
    out = out or RUNS / f"hazards-{seed}.json"
    with psycopg.connect(get_settings().db_url()) as conn:
        cases = generate(conn, n, random.Random(seed))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"_about": __doc__.splitlines()[0], "seed": seed, "cases": cases}, indent=1,
                              ensure_ascii=False), encoding="utf-8")
    from collections import Counter
    print(len(cases), "hazard cases:", dict(Counter(c["family"] for c in cases)), "->", out)
    return out


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--n", type=int, default=6, help="LGAs per family")
    p.add_argument("--seed", type=int)
    a = p.parse_args()
    build(a.n, a.seed if a.seed is not None else random.randrange(10**6))
