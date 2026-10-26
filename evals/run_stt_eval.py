"""Score Hausa STT against the exact wording in evals/questions.json.

Runs the combined pipeline (app/providers/stt.py) on every voice note in
data/test-audio/, then has Muse Spark judge each candidate against the reference.
The single-model baselines are judged the same way, from the last
scripts/test_audio.py run (data/test-audio/results.json).

A "silent error" means the pipeline's meaning was not fully right AND it did not
ask for a read-back. That is the number that has to go to zero.

Usage:  uv run python evals/run_stt_eval.py
"""

import asyncio
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.providers.meta import MetaClient  # noqa: E402
from app.providers.stt import parse_json_reply, transcribe_voice_note  # noqa: E402

AUDIO_DIR = ROOT / "data/test-audio"
JUDGE_MODEL = "muse-spark-1.3"
JUDGE_SYSTEM = (
    "You grade speech recognition of Hausa questions about public budgets. Compare the CANDIDATE with "
    "the REFERENCE (what was actually said). Judge meaning, not spelling.\n"
    "- full: same request; every year, number, sector, place, document and organisation correct.\n"
    "- partial: the main request is recognisable, but a non-critical detail is missing or vague.\n"
    "- wrong: a different request, empty, or any year/number/place/document/organisation is wrong, "
    "or a safety-relevant meaning (medical emergency, violence, politics) is lost or changed.\n"
    'Reply with JSON only: {"meaning": "full|partial|wrong", "reason": "<short>"}'
)


def baseline_text(entry: dict, model: str) -> str:
    res = entry.get(model) or {}
    if model.startswith("muse-voice"):
        return (res.get("response") or {}).get("transcript", "")
    p = res.get("parsed") or {}
    return f'{p.get("transcript", "")} || English: {p.get("english", "")}' if p else res.get("content", "")


async def judge(client: MetaClient, q: dict, candidate: str) -> dict:
    user = (f"REFERENCE (Hausa): {q['text_ha']}\nREFERENCE (English): {q['english']}\n"
            f"CANDIDATE: {candidate or '(empty)'}")
    r = await client.chat([{"role": "system", "content": JUDGE_SYSTEM}, {"role": "user", "content": user}],
                          model=JUDGE_MODEL, reasoning_effort="medium", max_tokens=4000)
    try:
        return parse_json_reply(r.content)
    except ValueError:
        return {"meaning": "error", "reason": r.content[:200]}


async def main() -> None:
    questions = json.loads((ROOT / "evals/questions.json").read_text(encoding="utf-8"))["questions"]
    baselines_path = AUDIO_DIR / "results.json"
    baselines = json.loads(baselines_path.read_text(encoding="utf-8")) if baselines_path.exists() else {}
    systems = ["muse-spark-1.3", "muse-spark-1.2", "muse-voice-transcribe-1.0", "combined"]
    out, prev = [], {}
    async with MetaClient() as client:
        for q in questions:
            prev_turn = prev.get(q.get("follows"))
            sr = await transcribe_voice_note((AUDIO_DIR / q["audio"]).read_bytes(), client, previous_turn=prev_turn)
            prev[q["id"]] = sr.transcript
            cands = {m: baseline_text(baselines.get(q["audio"], {}), m) for m in systems[:3]}
            cands["combined"] = f"{sr.transcript} || English: {sr.english}"
            verdicts = await asyncio.gather(*(judge(client, q, cands[m]) for m in systems))
            row = {"id": q["id"], "category": q["category"], "combined": sr.__dict__,
                   "verdicts": dict(zip(systems, verdicts))}
            out.append(row)
            v = row["verdicts"]
            flag = "READ-BACK" if sr.needs_confirmation else "-"
            print(f"{q['id']:>3}  " + "  ".join(f"{v[m]['meaning']:<7}" for m in systems)
                  + f"  {flag:<9} {sr.confidence:<6} {sum(sr.timings.values()):.1f}s")
            print(f"     -> {sr.transcript}\n        {sr.english}  {sr.uncertain or ''}")
            print(f"        judge: {v['combined'].get('reason', '')}")

    print("\nscore (full=1, partial=0.5):")
    for m in systems:
        s = sum({"full": 1, "partial": 0.5}.get(r["verdicts"][m]["meaning"], 0) for r in out)
        print(f"  {m:<28} {s:4.1f} / {len(out)}")
    silent = [r["id"] for r in out
              if r["verdicts"]["combined"]["meaning"] != "full" and not r["combined"]["needs_confirmation"]]
    readbacks = sum(r["combined"]["needs_confirmation"] for r in out)
    print(f"  combined read-backs: {readbacks}/{len(out)}   silent errors: {len(silent)} {silent}")
    (AUDIO_DIR / "stt-eval.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    asyncio.run(main())
