"""Questions for one overnight round, with expected answers computed by code from the data (never by a model):
the budget core, the school census tables (parsed from the page text), the facility registry, ward_history, NEMA's
dashboard rows, and documents whose cited figure code confirms on the cited page. A model only rephrases (English
and Hausa, formal and casual, typos, short and long); a paraphrase that loses a name or number is dropped. Three
difficulties: direct (one lookup), combine (a total or a ranking) and multi (a follow-up or correction).

    python evals/overnight/generate.py --round 1 [--n 100] [--no-paraphrase]
      -> evals/overnight/rounds/r1/questions.json  (each question tagged fix or heldout by its id's hash)
"""

from __future__ import annotations

import argparse
import asyncio
import json
import random
import re
import sys
from pathlib import Path

from common import ROOT, log, meta_guard, question_hash_half, round_dir  # noqa: E402

sys.path.insert(0, str(ROOT))

import psycopg  # noqa: E402

from app.config import get_settings  # noqa: E402

ASC = "asc-sokoto-2023-2024"
LGAS = ("Binji", "Bodinga", "Dange Shuni", "Gada", "Goronyo", "Gudu", "Gwadabawa", "Illela", "Isa", "Kebbe", "Kware",
        "Rabah", "Sabon Birni", "Shagari", "Silame", "Sokoto North", "Sokoto South", "Tambuwal", "Tangaza", "Tureta",
        "Wamakko", "Wurno", "Yabo")
NOT_FOUND_MARK = ["couldn't find", "Ban sami amsar"]


def q(feature: str, difficulty: str, lang: str, turns: list, expect: dict, source: str, lga: str = "",
      place: dict | None = None) -> dict:
    return {"feature": feature, "difficulty": difficulty, "lang": lang, "turns": turns, "expect": expect,
            "source": source, "lga": lga, **({"place": place} if place else {})}


# --- schools: the census tables parsed in code ----------------------------------------------------------------

def school_rows(conn) -> dict[str, dict]:
    """Per LGA: public and private counts by level from the census's own rows (p31 primary, p44 JSS, p53 SSS), and
    the statewide IQS figure (p22)."""
    out: dict[str, dict] = {}
    for level, page in (("primary", 31), ("jss", 44), ("sss", 53)):
        text = conn.execute("SELECT text FROM pages WHERE doc_id = %s AND page = %s", (ASC, page)).fetchone()[0]
        for ln in text.splitlines():
            m = re.match(r"^([A-Z][A-Z ]+?) (\d+) [\d,]+ [\d,]+ \d+% (\d+|-) ", ln)
            if not m:
                continue
            name = m.group(1).title().replace("Ilela", "Illela")
            lga = next((l for l in LGAS if l.lower() == name.lower()), None)
            if not lga:
                continue
            d = out.setdefault(lga, {"page": {}})
            d[f"public_{level}"] = int(m.group(2))
            d[f"private_{level}"] = int(m.group(3)) if m.group(3) != "-" else 0
            d["page"][level] = page
    p22 = conn.execute("SELECT text FROM pages WHERE doc_id = %s AND page = 22", (ASC,)).fetchone()[0]
    iqs = re.search(r"Islamiyya Integrated (\d+) ", p22)
    return {k: v for k, v in out.items() if all(f"public_{l}" in v for l in ("primary", "jss", "sss"))} | \
        {"_iqs_state": int(iqs.group(1)) if iqs else 0}


def schools(conn, rng: random.Random, n: int) -> list[dict]:
    rows = school_rows(conn)
    iqs = rows.pop("_iqs_state", 0)
    out = []
    lgas = rng.sample(sorted(rows), min(n, len(rows)))
    for i, lga in enumerate(lgas):
        r = rows[lga]
        total = r["public_primary"] + r["public_jss"] + r["public_sss"]
        double = total + r["private_primary"] + r["private_jss"] + r["private_sss"]
        kind = i % 4
        if kind == 0:
            out.append(q("schools", "direct", "en", [f"How many public primary schools are in {lga}?"],
                         {"figures": [str(r["public_primary"])], "docs": [ASC]}, "ASC p31", lga))
        elif kind == 1:
            out.append(q("schools", "combine", "en", [f"How many schools are in {lga}?"],
                         {"figures": [str(total), str(r["public_primary"]), str(r["public_jss"]), str(r["public_sss"])],
                          "lead_figure": str(total), "must_not_figures": [str(double)] if double != total else [],
                          "docs": [ASC]}, "ASC p31/44/53, total in code", lga))
        elif kind == 2:
            out.append(q("schools", "multi", "en",
                         [f"How many schools are in {lga}?", "I mean all of them: primary, JSS, SSS and IQS"],
                         {"figures": [str(total), str(iqs)], "lead_figure": str(total), "must_any": ["IQS", "Islamiyya"],
                          "must_not_figures": [str(double)] if double != total else [], "docs": [ASC]},
                         "ASC + IQS statewide p22", lga))
        else:
            out.append(q("schools", "direct", "en", [f"How many junior secondary schools does {lga} have?"],
                         {"figures": [str(r["public_jss"])], "docs": [ASC]}, "ASC p44", lga))
    return out


# --- health facilities: the registry ---------------------------------------------------------------------------

def facilities(conn, rng: random.Random, n: int) -> list[dict]:
    from app.geo.facility_info import KINDS
    conds = {k: c for _, k, c in KINDS}
    pcodes = dict(conn.execute("SELECT name, pcode FROM lga").fetchall())
    out = []
    for i, lga in enumerate(rng.sample(LGAS, min(n, len(LGAS)))):
        pcode = pcodes.get(lga)
        if not pcode:
            continue
        kind, words = rng.choice([("phc", "Primary Health Centres"), ("hospital", "hospitals"), ("all", "health facilities")])
        cnt = conn.execute(f"SELECT count(*) FROM facility f WHERE {conds[kind]} AND NOT f.hidden AND f.lga_pcode = %s",
                           (pcode,)).fetchone()[0]
        if cnt == 0:
            continue
        out.append(q("facilities", "direct", "en", [f"How many {words} are in {lga} LGA?"],
                     {"figures": [str(cnt)], "exact": True, "route": "facility"}, "facility registry", lga))
    return out


def nearest(conn, rng: random.Random, n: int) -> list[dict]:
    from app.geo.facilities import Filters, lga_point, nearest_facilities
    pcodes = dict(conn.execute("SELECT name, pcode FROM lga").fetchall())
    out = []
    for lga in rng.sample(LGAS, min(n, len(LGAS))):
        pt = lga_point(conn, pcodes[lga])
        if not pt:
            continue
        lat, lon = pt
        found = nearest_facilities(conn, lat, lon, Filters(), k=4)
        names = [f.name for f in found]
        if not names:
            continue
        out.append(q("nearest", "multi", "en", [{"pin": [lat, lon]}, "Which health facility is nearest to me?"],
                     {"must_any": names, "route": "facility"}, "registry, straight-line nearest 4", lga))
    return out


# --- budget: the budget core ------------------------------------------------------------------------------------

def budget(conn, rng: random.Random, n: int) -> list[dict]:
    sys.path.insert(0, str(ROOT / "evals" / "generated"))
    import generate as G  # evals/generated/generate.py: expected answers from the budget core
    cases = G.generate(conn, max(2, n // 6), rng)
    out = []
    for c in cases:
        if c.get("expect_not_found"):
            expect = {"not_found": True}
            diff = "direct"
        else:
            expect = {"figures": c.get("numbers", []), "any": c.get("numbers_any", []), "docs": c.get("docs", [])}
            diff = "combine" if c["family"] in ("compare", "share", "rank_lga", "trend", "split") else "direct"
        out.append(q("budget", diff, c.get("lang", "en"), [c["text"]], expect, f"budget core ({c['family']})"))
    # a correction across two ministries: 'I meant B, not A' answers B
    look = [c for c in cases if c["family"] == "lookup" and c.get("numbers")]
    for a, b in zip(look[::2], look[1::2]):
        na, nb = re.search(r"for (?:the )?(.+?) in the", a["text"]), re.search(r"for (?:the )?(.+?) in the", b["text"])
        if na and nb:
            out.append(q("budget", "multi", "en", [a["text"], f"I meant {nb.group(1)}, not {na.group(1)}"],
                         {"figures": b["numbers"], "docs": b.get("docs", [])}, "budget core, correction"))
    return out[:n]


def lga_budget(conn, rng: random.Random, n: int) -> list[dict]:
    from app.agent.analysis import run_analysis
    out = []
    for lga in rng.sample(LGAS, min(n, len(LGAS))):
        try:
            res = run_analysis(conn, {"tool": "lga_projects", "lga": lga, "year": 2026})
        except Exception:          # noqa: BLE001 - a tool that can't answer this LGA: no question
            continue
        if res is None or not getattr(res, "groups", None):
            continue
        total = sum(float(g[2]) for g in res.groups if g[2] is not None)
        if total <= 0:
            continue
        out.append(q("budget_lga", "combine", "en", [f"What is the government budgeting for {lga} LGA in 2026?"],
                     {"amounts": [total], "route": "analysis:lga_projects"}, "lga_projects tool, 2026", lga))
    return out


# --- place history: ward_history (the existing generated cases are computed from it) ---------------------------

def place(rng: random.Random, n: int) -> list[dict]:
    cases = json.loads((ROOT / "evals/place/cases.json").read_text(encoding="utf-8"))["cases"]
    pool = [c for c in cases if c["family"] in ("flood", "greenness", "rain", "water", "state_flood", "flood_map")
            and c["expect"].get("top")]
    out = []
    for c in rng.sample(pool, min(n, len(pool))):
        out.append(q("place", "combine", c["lang"], [c["question"]],
                     {"must_any": [c["expect"]["top"]], "must_not": c["expect"].get("must_not", []),
                      "route": "place_area"}, f"ward_history ({c['family']}, {c['id']})", place=c.get("place")))
    return out


# --- NEMA dashboard rows (read at index time, confirmed on the page text) --------------------------------------

def nema(conn, rng: random.Random, n: int) -> list[dict]:
    rows = conn.execute("SELECT doc_id, page, data FROM charts WHERE region_kind = 'dashboard'").fetchall()
    cands = []
    for doc, page, data in rows:
        d = data if isinstance(data, dict) else json.loads(data)
        raw = d.get("period") or ""
        m = re.search(r"\d{1,2}/\d{1,2}/\d{2,4}|\d{1,2}(?:st|nd|rd|th)? [A-Z][a-z]+ \d{4}", raw)
        period = m.group(0) if m else ""
        if not period:
            continue
        text = conn.execute("SELECT text FROM pages WHERE doc_id = %s AND page = %s", (doc, page)).fetchone()[0]
        for v in d.get("values") or []:
            if v.get("category") == "Sokoto" and v.get("value") and v["value"] in text and \
                    v.get("series", "").lower() in ("affected persons", "displaced persons", "affected lgas"):
                cands.append((doc, page, period, v["series"], v["value"]))
    out = []
    for doc, page, period, series, value in rng.sample(cands, min(n, len(cands))):
        what = {"affected persons": "people were affected by floods", "displaced persons": "people were displaced by floods",
                "affected lgas": "LGAs were affected by floods"}[series.lower()]
        out.append(q("nema", "direct", "en", [f"According to NEMA, how many {what} in Sokoto State as of {period}?"],
                     {"figures": [value], "docs": [doc], "pages": [page]}, f"charts dashboard row, {doc} p{page}"))
    return out


# --- documents: seeds whose figure code confirms on the cited page --------------------------------------------

def documents(conn, rng: random.Random, n: int) -> list[dict]:
    qs = json.loads((ROOT / "evals/questions.json").read_text(encoding="utf-8"))
    ans = json.loads((ROOT / "evals/answers.json").read_text(encoding="utf-8"))
    qs = qs["questions"] if isinstance(qs, dict) and "questions" in qs else qs
    ans = {k: v for k, v in ans.items() if not k.startswith("_")} if isinstance(ans, dict) else {}
    out = []
    for c in rng.sample(qs, len(qs)):
        a = ans.get(c["id"]) if isinstance(ans, dict) else None
        if not a or not a.get("numbers") or not a.get("docs"):
            continue
        confirmed = False
        for doc in a["docs"]:
            pages = a.get("pages") or []
            rows = conn.execute("SELECT page, text FROM pages WHERE doc_id = %s" + (" AND page = ANY(%s)" if pages else ""),
                                (doc, pages) if pages else (doc,)).fetchall()
            if any(all(num in t for num in a["numbers"]) for _, t in rows):
                confirmed = True
                break
        if not confirmed:
            continue
        out.append(q("documents", "direct", c.get("lang", "en"), [c.get("text_ha") or c["text"]],
                     {"figures": a["numbers"], "docs": a["docs"]}, f"evals/questions.json {c['id']} (confirmed on page)"))
        if len(out) >= n:
            break
    return out


def surveys(conn, rng: random.Random, n: int) -> list[dict]:
    qs = json.loads((ROOT / "evals/surveys/questions.json").read_text(encoding="utf-8"))["questions"]
    checks = json.loads((ROOT / "evals/surveys/questions_checks.json").read_text(encoding="utf-8"))["checks"]
    out = []
    for c in rng.sample(qs, len(qs)):
        ck = checks.get(c["id"]) or {}
        groups = ck.get("any") or []
        if not groups or c.get("previous"):
            continue
        group = groups[0]
        doc = next((d for d, in conn.execute(
            "SELECT DISTINCT p.doc_id FROM pages p JOIN documents d ON d.id = p.doc_id WHERE p.text LIKE %s AND "
            "(d.id ILIKE '%%mics%%' OR d.id ILIKE '%%dhs%%' OR d.title ILIKE '%%survey%%') LIMIT 1",
            (f"%{group[0]}%",)).fetchall()), None)
        if not doc:
            continue
        out.append(q("surveys", "direct", c["lang"], [c["text"]], {"any": groups, "docs": [doc]},
                     f"evals/surveys {c['id']} (figure confirmed in {doc})"))
        if len(out) >= n:
            break
    return out


# --- deep, emergencies, conversation --------------------------------------------------------------------------

def deep(rng: random.Random, n: int) -> list[dict]:
    pool = [("en", "What is the state of primary healthcare in Sokoto State?"),
            ("en", "Tell me about basic education in Sokoto State."),
            ("ha", "Yaya yanayin kiwon lafiya a Jihar Sokoto?"),
            ("en", "What's happening with maternal health in Sokoto?"),
            ("ha", "Me ke faruwa game da ilimi a Sokoto?")]
    return [q("deep", "combine", lang, [t], {"found": True, "min_sources": 2, "route": "deep"}, "hand-written prompt")
            for lang, t in rng.sample(pool, min(n, len(pool)))]


def emergencies(rng: random.Random, n: int) -> list[dict]:
    cases = json.loads((ROOT / "evals/emergency/cases.json").read_text(encoding="utf-8"))
    fire = rng.sample(cases["must_fire"], min(n // 2, len(cases["must_fire"])))
    quiet = rng.sample(cases["must_not"], min(n - len(fire), len(cases["must_not"])))
    return ([q("emergency", "direct", c["lang"], [c["text"]], {"emergency": True}, f"evals/emergency {c['id']}") for c in fire]
            + [q("emergency", "direct", c["lang"], [c["text"]], {"emergency": False}, f"evals/emergency {c['id']}") for c in quiet])


def conversation(rng: random.Random, n: int) -> list[dict]:
    pool = [("en", "Who are you?", {"must_not": NOT_FOUND_MARK, "must_any": ["Kasafi"]}),
            ("ha", "Kai wanene?", {"must_not": NOT_FOUND_MARK, "must_any": ["Kasafi"]}),
            ("en", "What can you do?", {"must_not": NOT_FOUND_MARK, "must_any": ["budget", "kasafi"]}),
            ("en", "thanks", {"must_not": NOT_FOUND_MARK}), ("ha", "Na gode", {"must_not": NOT_FOUND_MARK}),
            ("en", "menu", {"must_any": ["[list"]}), ("ha", "zaɓi", {"must_any": ["[list"]}),
            ("en", "Can you speak Hausa?", {"must_not": NOT_FOUND_MARK})]
    return [q("conversation", "direct", lang, [t], e, "fixed") for lang, t, e in rng.sample(pool, min(n, len(pool)))]


# --- paraphrase (Muse Spark Open): English and Hausa, casual, typos, short and long -----------------------------

PARA_SYSTEM = """Rewrite the user's question the way different people ask on WhatsApp in Sokoto State, Nigeria. \
Keep every place name, number, year, ministry and level exactly (the question must still have the same answer). \
Reply with JSON only: {"hausa": "<the question in Hausa, standard spelling>", "casual": "<short, casual English>", \
"typo": "<English with two realistic typos>", "long": "<a longer, polite English form>"}"""


async def paraphrase(items: list[dict], rng: random.Random, share: float = 0.6) -> None:
    from app.providers.fireworks import BatchModel
    from app.providers.stt import parse_json_reply
    s = get_settings()
    chosen = [it for it in items if rng.random() < share and isinstance(it["turns"][0], str)
              and it["feature"] not in ("conversation", "emergency", "place")]
    async with BatchModel(s) as client:
        for it in chosen:
            text = it["turns"][0]
            try:
                r = await client.chat([{"role": "system", "content": PARA_SYSTEM},
                                       {"role": "user", "content": f"QUESTION: {text}"}],
                                      reasoning_effort="low", max_tokens=2500)
                d = parse_json_reply(r.content)
            except Exception as e:      # noqa: BLE001 - the original wording stays
                log(f"paraphrase failed for a question ({type(e).__name__}); original kept")
                continue
            form = rng.choice(["hausa", "casual", "typo", "long"])
            new = str(d.get(form) or "").strip()
            keep = [w for w in re.findall(r"\b(?:[A-Z][a-z]+(?: [A-Z][a-z]+)*|\d[\d,./]*)\b", text)
                    if w not in ("How", "What", "Which", "According", "I", "The", "In")]
            lost = [w for w in keep if w.lower() not in new.lower()]
            if not new or lost:
                continue
            it["turns"][0] = new
            it["form"] = form
            if form == "hausa":
                it["lang"] = "ha"


def build(round_n: int, n: int, do_paraphrase: bool) -> Path:
    rng = random.Random(1000 + round_n)
    s = get_settings()
    with psycopg.connect(s.db_url()) as conn:
        items = []
        items += schools(conn, rng, 20)
        items += facilities(conn, rng, 8)
        items += nearest(conn, rng, 4)
        items += budget(conn, rng, 22)
        items += lga_budget(conn, rng, 6)
        items += place(rng, 8)
        items += nema(conn, rng, 6)
        items += documents(conn, rng, 8)
        items += surveys(conn, rng, 6)
        items += deep(rng, 3)
        items += emergencies(rng, 8)
        items += conversation(rng, 6)
    rng.shuffle(items)
    items = items[:n]
    if do_paraphrase:
        asyncio.run(paraphrase(items, rng))
    for i, it in enumerate(items, 1):
        it["id"] = f"r{round_n}-{i:03d}-{it['feature']}"
        it["set"] = question_hash_half(it["id"])
    out = round_dir(round_n) / "questions.json"
    out.write_text(json.dumps({"round": round_n, "questions": items}, indent=1, ensure_ascii=False), encoding="utf-8")
    from collections import Counter
    log(f"round {round_n}: {len(items)} questions -> {out} | by feature {dict(Counter(i['feature'] for i in items))} | "
        f"by set {dict(Counter(i['set'] for i in items))} | by difficulty {dict(Counter(i['difficulty'] for i in items))}")
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--round", type=int, required=True)
    ap.add_argument("--n", type=int, default=100)
    ap.add_argument("--no-paraphrase", action="store_true")
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    meta_guard()
    build(a.round, a.n, not a.no_paraphrase)
