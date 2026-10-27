"""Compare models for the STT reconcile step on identical hypotheses.

For each note in evals/questions.json, Voice Transcribe and Spark-audio hypotheses are made ONCE.
Then each candidate model reconciles those same hypotheses, and Muse Spark judges every result
against the exact wording (same judge as run_stt_eval.py). Reports score, silent errors (not
fully right AND no read-back), read-backs and reconcile latency.

Usage:  uv run python evals/compare_reconcile.py [--models muse-spark-1.3,muse-spark-1.2]
"""

import argparse
import asyncio
import json
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "evals"))

from app.config import get_settings  # noqa: E402
from app.providers.audio import to_wav16k  # noqa: E402
from app.providers.meta import MetaClient  # noqa: E402
from app.providers.stt import _hyp_asr, _hyp_spark, reconcile  # noqa: E402
from run_stt_eval import judge  # noqa: E402

AUDIO_DIR = ROOT / "data/test-audio"
SCORE = {"full": 1.0, "partial": 0.5}


async def main(models: list[str]) -> None:
    s = get_settings()
    questions = json.loads((ROOT / "evals/questions.json").read_text(encoding="utf-8"))["questions"]
    rows = []
    async with MetaClient(s) as client:
        prev: dict[str, dict[str, str]] = {m: {} for m in models}
        for q in questions:
            wav = to_wav16k((AUDIO_DIR / q["audio"]).read_bytes())
            asr, spark = await asyncio.gather(_hyp_asr(client, wav, s.stt_asr_model),
                                              _hyp_spark(client, wav, s.stt_audio_model))
            hyps = {"asr": asr, "spark_audio": spark}
            row = {"id": q["id"]}
            for m in models:
                r = await reconcile(hyps, client, model=m, previous_turn=prev[m].get(q.get("follows")))
                prev[m][q["id"]] = r.transcript
                v = await judge(client, q, f"{r.transcript} || English: {r.english}")
                row[m] = {"meaning": v.get("meaning"), "reason": v.get("reason", ""), "read_back": r.needs_confirmation,
                          "seconds": r.timings["reconcile"], "transcript": r.transcript}
            rows.append(row)
            print(f"{q['id']:>3}  " + "   ".join(
                f"{m.split('-')[-1]}: {row[m]['meaning']:<7} {'RB' if row[m]['read_back'] else '--'} {row[m]['seconds']:4.1f}s"
                for m in models))

    print()
    for m in models:
        rs = [r[m] for r in rows]
        score = sum(SCORE.get(x["meaning"], 0) for x in rs)
        silent = [r["id"] for r in rows if r[m]["meaning"] != "full" and not r[m]["read_back"]]
        secs = [x["seconds"] for x in rs]
        print(f"{m:<16} score {score:4.1f}/{len(rs)}  silent errors {len(silent)} {silent}  "
              f"read-backs {sum(x['read_back'] for x in rs)}/{len(rs)}  "
              f"reconcile median {statistics.median(secs):.1f}s  max {max(secs):.1f}s")
    (AUDIO_DIR / "reconcile-compare.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--models", default="muse-spark-1.3,muse-spark-1.2")
    asyncio.run(main(p.parse_args().models.split(",")))
