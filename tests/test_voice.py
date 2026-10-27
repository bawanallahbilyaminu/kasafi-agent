import asyncio

import pytest
from pydantic import SecretStr

from app.config import Settings
from app.providers.chat import ProviderError
from app.providers.stt import SpeechResult, TranscriptionFailed, VoiceNoteTooLong
from app.whatsapp import voice
from app.whatsapp.messages import t

PILOT = "2340000000001"


def _settings(pilots: str = PILOT) -> Settings:
    return Settings(_env_file=None, meta_api_key=SecretStr("k"), kasafi_pilot_numbers=pilots)


class FakeWA:
    def __init__(self, fail: bool = False) -> None:
        self.fail, self.downloaded, self.deleted = fail, [], []

    async def download_media(self, media_id: str) -> bytes:
        if self.fail:
            raise voice.MediaError("boom")
        self.downloaded.append(media_id)
        return b"ogg"

    async def delete_media(self, media_id: str) -> bool:
        self.deleted.append(media_id)
        return True


class FakeMeta:
    def __init__(self, settings=None) -> None: ...
    async def __aenter__(self): return self
    async def __aexit__(self, *a): return None


def _msg(sender: str = PILOT) -> dict:
    return {"from": sender, "type": "audio", "audio": {"id": "media-1", "voice": True}}


def _run(monkeypatch, *, result=None, exc=None, wa=None, settings=None, sender=PILOT, lang="ha"):
    async def fake_transcribe(audio, client, **kw):
        assert kw["max_seconds"] == 180
        if exc:
            raise exc
        return result
    monkeypatch.setattr(voice, "transcribe_voice_note", fake_transcribe)
    wa = wa or FakeWA()
    out = asyncio.run(voice.reply_for_voice(_msg(sender), wa, lang=lang, settings=settings or _settings(),
                                            meta_client_factory=FakeMeta)).text
    return out, wa


def _result(transcript="Nawa aka ware wa ilimi a 2026?", confirm=False) -> SpeechResult:
    return SpeechResult(transcript=transcript, english="", language="ha", confidence="high",
                        needs_confirmation=confirm, hypotheses={"asr": "x", "spark_audio": "y"})


def test_confident_transcript_is_heard_and_media_deleted(monkeypatch) -> None:
    out, wa = _run(monkeypatch, result=_result())
    assert out.startswith("Na ji tambayarka") and "ilimi a 2026" in out
    assert wa.downloaded == ["media-1"] and wa.deleted == ["media-1"]


def test_uncertain_transcript_gets_read_back(monkeypatch) -> None:
    out, _ = _run(monkeypatch, result=_result(confirm=True))
    assert "Kana nufin haka?" in out


@pytest.mark.parametrize("exc, expected", [
    (VoiceNoteTooLong("too long"), "ya yi tsawo"),
    (TranscriptionFailed("no speech"), "ban ji"),
    (ProviderError("Meta", 503, "busy"), "ban ji"),
])
def test_failures_reply_politely_and_still_delete_media(monkeypatch, exc, expected) -> None:
    out, wa = _run(monkeypatch, exc=exc)
    assert expected in out and wa.deleted == ["media-1"]


def test_empty_transcript_and_download_failure(monkeypatch) -> None:
    assert _run(monkeypatch, result=_result(transcript=""))[0] == t("not_heard", "ha")
    assert _run(monkeypatch, result=_result(), wa=FakeWA(fail=True))[0] == t("not_heard", "ha")


def test_read_back_shows_what_was_spoken_not_the_translation(monkeypatch) -> None:
    r = SpeechResult(transcript="Nawa aka ware wa ilimi?", english="How much went to education?", language="ha",
                     confidence="high", needs_confirmation=True)
    out, _ = _run(monkeypatch, result=r, lang="en")              # English-mode user who spoke Hausa
    assert out.startswith("I heard:") and "«Nawa aka ware wa ilimi?»" in out and "Did you mean" in out
    assert "How much went to education" not in out


def test_voice_replies_only_in_hausa_mode() -> None:
    assert voice.voice_replies_enabled("ha") and not voice.voice_replies_enabled("en")


def test_pilot_numbers_normalised() -> None:
    s = _settings(" +234 000 000 0001 , 2348111111111")
    assert voice.is_pilot("2340000000001", s) and voice.is_pilot("2348111111111", s)
    assert not voice.is_pilot("2340000000002", s)


def test_voice_log_has_stage_timings_and_no_transcript(monkeypatch, caplog) -> None:
    import logging
    r = SpeechResult(transcript="Nawa aka ware wa ilimi a 2026?", english="How much for education in 2026?",
                     language="ha", confidence="high", needs_confirmation=False,
                     hypotheses={"asr": "x", "spark_audio": "y"},
                     timings={"audio": 9.6, "convert": 0.1, "asr": 4.2, "spark_audio": 6.3, "reconcile": 3.1})
    with caplog.at_level(logging.INFO):
        _run(monkeypatch, result=r)
    line = next(rec.getMessage() for rec in caplog.records if "voice note from" in rec.getMessage())
    for part in ["audio=10s", "download=", "convert=0.1s", "asr=4.2s", "spark_audio=6.3s", "reconcile=3.1s", "total="]:
        assert part in line
    assert "ilimi" not in caplog.text and "education" not in caplog.text and PILOT not in caplog.text
