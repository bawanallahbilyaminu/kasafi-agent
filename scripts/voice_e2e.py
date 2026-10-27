"""End-to-end voice-note check without WhatsApp: the real voice handler and real models on local files.

A fake WhatsApp client serves each local file in place of the media download, so the path is
exactly what the webhook runs: pilot gate, then the combined STT pipeline, then the reply text.
Nothing is sent and nothing is written to disk.

Usage:  uv run python scripts/voice_e2e.py [files...]   (default: every note in data/test-audio/)
Only use our own recordings.
"""

import asyncio
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.config import get_settings  # noqa: E402
from app.whatsapp.voice import reply_for_voice  # noqa: E402

AUDIO_DIR = Path("data/test-audio")
FAKE_SENDER = "2340000000000"  # placeholder, never a real number


class LocalFileWA:
    """Stands in for WhatsAppClient: 'downloads' a local file, records the delete."""

    def __init__(self, path: Path) -> None:
        self.path, self.deleted = path, False

    async def download_media(self, media_id: str) -> bytes:
        return self.path.read_bytes()

    async def delete_media(self, media_id: str) -> bool:
        self.deleted = True
        return True


async def main(files: list[Path]) -> None:
    files = files or sorted(p for p in AUDIO_DIR.iterdir() if p.suffix.lower() in {".ogg", ".opus", ".m4a", ".mp3"})
    settings = get_settings().model_copy(update={"kasafi_pilot_numbers": FAKE_SENDER})
    msg = {"from": FAKE_SENDER, "type": "audio", "audio": {"id": "local", "voice": True}}
    for f in files:
        wa = LocalFileWA(f)
        t0 = time.perf_counter()
        reply = (await reply_for_voice(msg, wa, settings=settings)).text
        print(f"\n=== {f.name}  ({time.perf_counter() - t0:.1f}s, media deleted: {wa.deleted})\n{reply}")


if __name__ == "__main__":
    asyncio.run(main([Path(a) for a in sys.argv[1:]]))
