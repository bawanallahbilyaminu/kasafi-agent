import shutil
import subprocess
import wave
from io import BytesIO

import pytest

from app.providers.audio import to_wav16k

pytestmark = pytest.mark.skipif(shutil.which("ffmpeg") is None, reason="ffmpeg not installed")


def test_ogg_opus_to_16k_mono_wav() -> None:
    # Synthesise a 1 s stereo 48 kHz Opus clip, like a WhatsApp voice note.
    ogg = subprocess.run(
        ["ffmpeg", "-nostdin", "-loglevel", "error", "-f", "lavfi", "-i", "sine=f=440:d=1:r=48000",
         "-ac", "2", "-c:a", "libopus", "-f", "ogg", "-"],
        check=True, capture_output=True,
    ).stdout
    with wave.open(BytesIO(to_wav16k(ogg))) as w:
        assert (w.getnchannels(), w.getframerate(), w.getsampwidth()) == (1, 16000, 2)
        assert 0.9 < w.getnframes() / 16000 < 1.1
