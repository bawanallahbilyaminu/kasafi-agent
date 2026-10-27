import json
from pathlib import Path

import pytest

from app.guardrails.emergency import EMERGENCY_REPLY, is_medical_emergency
from app.providers.stt import SpeechResult
from app.whatsapp.voice import compose_reply
from app.whatsapp.webhook import echo_reply

QUESTIONS = {q["id"]: q for q in json.loads(Path("evals/questions.json").read_text(encoding="utf-8"))["questions"]}


def test_eval_15_medical_emergency_triggers() -> None:
    q = QUESTIONS["15"]
    assert is_medical_emergency(q["text_ha"]) and is_medical_emergency(q["english"])


@pytest.mark.parametrize("qid", [k for k in QUESTIONS if k != "15"])
def test_no_other_eval_question_triggers(qid: str) -> None:
    # 05 is about emergency obstetric *care budgets*; it must not be treated as an emergency.
    q = QUESTIONS[qid]
    assert not is_medical_emergency(q["text_ha"], q["english"])


def test_emergency_beats_read_back_and_echo() -> None:
    r = SpeechResult(transcript="Mata tana da ciki kuma tana zubar da jini", english="", language="ha",
                     confidence="low", needs_confirmation=True)
    assert compose_reply(r) == EMERGENCY_REPLY
    assert echo_reply({"type": "text", "text": {"body": "My wife is bleeding, what medicine?"}}) == EMERGENCY_REPLY
