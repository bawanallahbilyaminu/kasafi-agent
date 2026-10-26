"""Compare speech-to-text options on our own Hausa voice notes.

For each file in data/test-audio/ (ogg, opus, m4a, mp3, wav, ...):
  1. ffmpeg -> 16 kHz mono WAV
  2. Muse Spark (input_audio) on each --models entry: Hausa transcript + English translation
  3. Muse Voice Transcribe (does not list Hausa; we test it anyway)
With --provider baseten, step 2 runs Muse Spark Open on Baseten (audio_url) instead
and step 3 is skipped.
Merges into data/test-audio/results.json (gitignored) and prints a summary.

Usage:  uv run python scripts/test_audio.py [--provider meta|baseten] [--models ...] [--skip-asr]
Only use recordings we made ourselves (no real user audio).
"""

import argparse
import asyncio
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.config import get_settings  # noqa: E402
from app.providers.audio import to_wav16k  # noqa: E402
from app.providers.baseten import BasetenClient  # noqa: E402
from app.providers.chat import ChatClient, ProviderError, text_part  # noqa: E402
from app.providers.meta import MetaClient  # noqa: E402

AUDIO_DIR = Path("data/test-audio")
EXTS = {".ogg", ".opus", ".oga", ".m4a", ".mp3", ".wav", ".aac", ".amr", ".webm"}

PROMPT = (
    "This is a voice note, most likely in Hausa (Nigeria), possibly mixed with English. "
    "Reply with JSON only, no markdown fences, using these keys: "
    '"language" (detected language), '
    '"transcript" (verbatim transcript in the original language, using Hausa letters ɓ ɗ ƙ ƴ where spoken), '
    '"english" (faithful English translation), '
    '"confidence" (low / medium / high). '
    "If the audio is silent or not speech, set transcript to an empty string."
)


async def spark(client: ChatClient, model: str, wav: bytes) -> dict:
    t0 = time.perf_counter()
    try:
        r = await client.chat(
            [{"role": "user", "content": [text_part(PROMPT), client.audio_part(wav)]}],
            model=model,
            reasoning_effort="low",
            max_tokens=4000,
        )
        out = {"ok": True, "content": r.content, "finish": r.finish_reason, "usage": r.usage,
               "reasoning_chars": len(r.reasoning)}
        try:
            out["parsed"] = json.loads(r.content.strip().removeprefix("```json").removesuffix("```"))
        except ValueError:
            pass
    except ProviderError as e:
        out = {"ok": False, "error": str(e)}
    out["seconds"] = round(time.perf_counter() - t0, 1)
    return out


async def asr(client: MetaClient, wav: bytes) -> dict:
    t0 = time.perf_counter()
    try:
        out = {"ok": True, "response": await client.transcribe(wav)}
    except ProviderError as e:
        out = {"ok": False, "error": str(e)}
    out["seconds"] = round(time.perf_counter() - t0, 1)
    return out


async def main(provider: str, models: list[str], skip_asr: bool, files: list[Path]) -> None:
    files = files or sorted(p for p in AUDIO_DIR.iterdir() if p.suffix.lower() in EXTS)
    if not files:
        sys.exit(f"No audio files in {AUDIO_DIR}/")
    out = AUDIO_DIR / "results.json"
    results = json.loads(out.read_text(encoding="utf-8")) if out.exists() else {}
    client_cls = BasetenClient if provider == "baseten" else MetaClient
    async with client_cls() as client:
        for f in files:
            wav = to_wav16k(f.read_bytes())
            secs = (len(wav) - 44) / 32000
            print(f"\n=== {f.name}  ({secs:.1f}s audio) ===")
            entry: dict = results.setdefault(f.name, {})
            entry["audio_seconds"] = round(secs, 1)
            for m in models:
                entry[m] = res = await spark(client, m, wav)
                print(f"\n--- {m} ({res['seconds']}s) ---")
                print(res.get("content") or res.get("error"))
            if not skip_asr and isinstance(client, MetaClient):
                entry["muse-voice-transcribe-1.0"] = res = await asr(client, wav)
                print(f"\n--- muse-voice-transcribe-1.0 ({res['seconds']}s) ---")
                print(json.dumps(res.get("response"), ensure_ascii=False, indent=1) if res["ok"] else res["error"])
    out.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nSaved {out}")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("files", nargs="*", type=Path)
    p.add_argument("--provider", choices=["meta", "baseten"], default="meta")
    p.add_argument("--models", default=None,
                   help="comma-separated; default muse-spark-1.3,muse-spark-1.2 (meta) or the Baseten model")
    p.add_argument("--skip-asr", action="store_true")
    a = p.parse_args()
    default = get_settings().baseten_model if a.provider == "baseten" else "muse-spark-1.3,muse-spark-1.2"
    asyncio.run(main(a.provider, (a.models or default).split(","), a.skip_asr, a.files))
