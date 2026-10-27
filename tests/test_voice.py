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
                                            meta_client_factory=FakeMeta))
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


def test_english_mode_replies_in_english_with_translation(monkeypatch) -> None:
    r = SpeechResult(transcript="Nawa aka ware wa ilimi?", english="How much went to education?", language="ha",
                     confidence="high", needs_confirmation=True)
    out, _ = _run(monkeypatch, result=r, lang="en")
    assert out.startswith("I heard:") and "(English: How much went to education?)" in out and "Did you mean" in out


def test_voice_replies_only_in_hausa_mode() -> None:
    assert voice.voice_replies_enabled("ha") and not voice.voice_replies_enabled("en")


def test_pilot_numbers_normalised() -> None:
    s = _settings(" +234 000 000 0001 , 2348111111111")
    assert voice.is_pilot("2340000000001", s) and voice.is_pilot("2348111111111", s)
    assert not voice.is_pilot("2340000000002", s)
