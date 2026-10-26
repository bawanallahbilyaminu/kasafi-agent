"""Audio conversion with ffmpeg.

WhatsApp voice notes arrive as OGG/Opus. Muse Voice Transcribe takes WAV only
(mono 16-bit PCM, 16/24 kHz, <= 10 min, <= 32 MB) and Muse Spark's
input_audio takes wav or mp3, so everything is normalised to 16 kHz mono WAV.
"""

import shutil
import subprocess
import tempfile
from pathlib import Path

MAX_SECONDS = 600


def to_wav16k(audio: bytes, *, timeout: float = 60.0) -> bytes:
    """Convert any ffmpeg-readable audio to 16 kHz mono s16 WAV.

    Goes via temp files rather than pipes so the WAV header carries real sizes.
    """
    if shutil.which("ffmpeg") is None:
        raise RuntimeError("ffmpeg not found on PATH")
    with tempfile.TemporaryDirectory() as tmp:
        src, dst = Path(tmp) / "in", Path(tmp) / "out.wav"
        src.write_bytes(audio)
        subprocess.run(
            ["ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error", "-y",
             "-i", str(src), "-t", str(MAX_SECONDS),
             "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", str(dst)],
            check=True, capture_output=True, timeout=timeout,
        )
        return dst.read_bytes()
