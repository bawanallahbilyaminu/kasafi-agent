import asyncio
import json

import httpx
import pytest
from pydantic import SecretStr

from app.config import Settings
from app.providers import stt
from app.providers.meta import MetaClient


def _settings() -> Settings:
    return Settings(_env_file=None, meta_api_key=SecretStr("test-key-not-real"))


def _completion(content: str) -> dict:
    return {"model": "m", "choices": [{"index": 0, "finish_reason": "stop",
            "message": {"role": "assistant", "content": content}}]}


RECONCILED = {"transcript": "Nawa aka ware wa ilimi a 2026?", "english": "How much went to education in 2026?",
              "language": "ha", "confidence": "high", "needs_confirmation": False, "uncertain": []}


def _handler(seen: list, *, asr_status: int = 200, reconciled: dict = RECONCILED):
    def handler(req: httpx.Request) -> httpx.Response:
        if req.url.path.endswith("/asr/transcribe"):
            seen.append(("asr", None))
            if asr_status != 200:
                return httpx.Response(asr_status, json={"error": {"message": "nope"}})
            return httpx.Response(200, json={"transcript": " Nowa aka wari wa ilimi 2026", "turns": []})
        body = json.loads(req.content)
        seen.append((body["model"], body))
        if body["model"] == "muse-spark-1.2":
            return httpx.Response(200, json=_completion(
                '```json\n{"transcript": "Nawa aka ware wa ilimi?", "english": "How much for education?"}\n```'))
        return httpx.Response(200, json=_completion(json.dumps(reconciled)))
    return handler


def _run(handler, **kw) -> stt.SpeechResult:
    async def go():
        async with MetaClient(_settings(), transport=httpx.MockTransport(handler)) as c:
            return await stt.transcribe_voice_note(b"ogg", c, settings=_settings(), **kw)
    return asyncio.run(go())


@pytest.fixture(autouse=True)
def _no_ffmpeg(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(stt, "to_wav16k", lambda audio: b"RIFF....WAVE")


def test_both_hypotheses_reach_reconcile() -> None:
    seen: list = []
    r = _run(_handler(seen), previous_turn="Wadanne ƙananan hukumomi?")
    assert r.transcript == RECONCILED["transcript"] and r.needs_confirmation is False
    assert set(r.hypotheses) == {"asr", "spark_audio"}
    reconcile = next(b for m, b in seen if m == "muse-spark-1.3")
    user_msg = reconcile["messages"][1]["content"]
    assert "Nowa aka wari" in user_msg and "Nawa aka ware wa ilimi?" in user_msg
    assert "Previous question" in user_msg


def test_one_failed_hypothesis_still_answers_but_forces_readback() -> None:
    r = _run(_handler([], asr_status=400))
    assert set(r.hypotheses) == {"spark_audio"}
    assert r.needs_confirmation is True


def test_low_confidence_forces_readback() -> None:
    r = _run(_handler([], reconciled={**RECONCILED, "confidence": "low", "needs_confirmation": False}))
    assert r.needs_confirmation is True


def test_parse_json_reply_handles_fences_and_prose() -> None:
    assert stt.parse_json_reply('```json\n{"a": 1}\n```') == {"a": 1}
    assert stt.parse_json_reply('Here you go: {"a": 2}') == {"a": 2}
    with pytest.raises(ValueError):
        stt.parse_json_reply("no json")
