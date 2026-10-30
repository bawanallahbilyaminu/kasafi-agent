"""Paraphrase each generated case (evals/generated/cases.json) the way people ask on WhatsApp: Hausa, informal
English, Hausa-English code-switched, with typos, and as a follow-up to an earlier question. The expected answer
doesn't change: every name, number and period is kept. One model call per case, a few at a time.

    uv run python evals/generated/paraphrase.py [--cases evals/generated/cases.json]   -> adds "forms" to each case
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from app.config import get_settings  # noqa: E402
from app.usage import stage as usage_stage  # noqa: E402
from app.providers.meta import MetaClient  # noqa: E402
from app.providers.stt import parse_json_reply  # noqa: E402

CASES = Path(__file__).with_name("cases.json")
FORMS = ("hausa", "informal", "code_switched", "typo", "followup")
AT_ONCE = 6

SYSTEM = (
    "You write test questions for a Hausa / English WhatsApp assistant about Sokoto State budgets and displacement "
    "figures. Rewrite the QUESTION in five forms that keep its meaning exactly: every organisation name, LGA, "
    "number, year and quarter stays (names may keep their English form inside Hausa). "
    "hausa: natural Hausa as people in Sokoto type it. informal: short, casual English. code_switched: a mix of "
    "Hausa and English in one message. typo: the English question with 2-3 realistic typing mistakes (never in "
    "a number). followup: {\"previous\": a short earlier question naming the same organisation or place on a "
    "related point, \"question\": the QUESTION as a follow-up to it, using 'it' / 'there' / 'its' instead of the "
    "name}. Reply with JSON only: {\"hausa\": \"\", \"informal\": \"\", \"code_switched\": \"\", \"typo\": \"\", "
    "\"followup\": {\"previous\": \"\", \"question\": \"\"}}"
)


async def paraphrase(path: Path = CASES, at_once: int = AT_ONCE) -> None:
    s = get_settings()
    data = json.loads(path.read_text(encoding="utf-8"))
    gate = asyncio.Semaphore(at_once)
    async with MetaClient(s) as client:
        async def one(c: dict) -> None:
            async with gate:
                with usage_stage("paraphrase"):
                    r = await client.chat([{"role": "system", "content": SYSTEM},
                                           {"role": "user", "content": f"QUESTION: {c['text']}"}],
                                          model=s.meta_model, reasoning_effort="low", max_tokens=3000)
            try:
                d = parse_json_reply(r.content)
            except ValueError:
                print("no paraphrase for", c["id"])
                return
            c["forms"] = {k: d[k] for k in FORMS if d.get(k)}
        await asyncio.gather(*(one(c) for c in data["cases"] if not c.get("forms")), return_exceptions=True)
    path.write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8")
    print(sum(bool(c.get("forms")) for c in data["cases"]), "of", len(data["cases"]), "cases paraphrased ->", path)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--cases", type=Path, default=CASES)
    asyncio.run(paraphrase(p.parse_args().cases))
