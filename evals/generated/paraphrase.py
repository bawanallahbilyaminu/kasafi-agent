"""Paraphrase each generated case (evals/generated/cases.json) the way people ask on WhatsApp: Hausa, informal
English, Hausa-English code-switched, with typos, and as a follow-up to an earlier question. The expected answer
doesn't change: every name, number and period is kept. One model call per case.

    uv run python evals/generated/paraphrase.py        -> adds "forms" to each case in cases.json
"""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from app.config import get_settings  # noqa: E402
from app.providers.meta import MetaClient  # noqa: E402
from app.providers.stt import parse_json_reply  # noqa: E402

CASES = Path(__file__).with_name("cases.json")
FORMS = ("hausa", "informal", "code_switched", "typo", "followup")

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


async def main() -> None:
    s = get_settings()
    data = json.loads(CASES.read_text(encoding="utf-8"))
    async with MetaClient(s) as client:
        for c in data["cases"]:
            if c.get("forms"):
                continue
            r = await client.chat([{"role": "system", "content": SYSTEM},
                                   {"role": "user", "content": f"QUESTION: {c['text']}"}],
                                  model=s.meta_model, reasoning_effort="low", max_tokens=3000)
            try:
                d = parse_json_reply(r.content)
            except ValueError:
                print("no paraphrase for", c["id"])
                continue
            c["forms"] = {k: d[k] for k in FORMS if d.get(k)}
            print(c["id"], "->", ", ".join(c["forms"]))
            CASES.write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    asyncio.run(main())
