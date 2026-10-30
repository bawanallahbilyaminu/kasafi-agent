import json
from pathlib import Path

import pytest

from app.guardrails.emergency import EMERGENCY_REPLY, is_medical_emergency
from app.providers.stt import SpeechResult
from app.whatsapp.voice import compose_reply
from tests.helpers import run_handle

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
    outs, _ = run_handle({"type": "text", "from": "2340000000001", "text": {"body": "My wife is bleeding, what medicine?"}})
    assert [o.text for o in outs] == [EMERGENCY_REPLY]  # even before consent: local check, no model


def test_emergency_found_in_raw_hypothesis_even_if_merge_dropped_it() -> None:
    # The merge can confidently lose the key words; the raw Voice Transcribe text still has them.
    r = SpeechResult(transcript="Matata tana da ciki, wane magani zan ba ta?", english="My wife is pregnant, what medicine?",
                     language="ha", confidence="high", needs_confirmation=False,
                     hypotheses={"asr": "Matata dan ada ciki, kuma tana zubar da jini.", "spark_audio": "Matata tana da ciki"})
    assert compose_reply(r) == EMERGENCY_REPLY


def test_only_verified_emergency_numbers_are_shown(tmp_path) -> None:
    from app.guardrails.emergency import CONTACTS_PATH, emergency_reply, verified_contacts
    f = tmp_path / "contacts.yaml"
    f.write_text("contacts:\n"
                 "  - {number: '112', service: National emergency number, service_ha: Lambar gaggawa, area: state-wide}\n"
                 "  - {number: '0800 000 0000', service: State ambulance, service_ha: Motar asibiti, area: Wamakko,\n"
                 "     verified_on: 2026-10-30}\n", encoding="utf-8")
    shown = verified_contacts(f)
    assert [c.number for c in shown] == ["0800 000 0000"]                    # 112 has no verified_on: never shown
    text = emergency_reply(shown)
    assert "*0800 000 0000*: Motar asibiti (Wamakko)" in text and "*0800 000 0000*: State ambulance (Wamakko)" in text
    assert "112" not in text
    assert verified_contacts(tmp_path / "missing.yaml") == []
    # the repo's own file: no number is verified yet, so the reply sends people to the nearest facility only
    assert all(c.verified_on for c in verified_contacts(CONTACTS_PATH))
    assert "112" not in EMERGENCY_REPLY and "nearest health facility *now*" in EMERGENCY_REPLY


def test_budget_question_about_emergency_care_does_not_trigger_on_raw_text() -> None:
    r = SpeechResult(transcript="Me rahoton UNFPA kan kulawar gaggawa ga mata masu haihuwa ya gano?",
                     english="What did the UNFPA report on emergency care for mothers find?", language="ha",
                     confidence="high", needs_confirmation=False,
                     hypotheses={"asr": "Merohoto nyu NFT kan kulawar gaggawa ga mata masu ayyuwa da jarirai",
                                 "spark_audio": "Mirahoto NFE kan kulawa ta gaggawa || English: emergency care report"})
    assert compose_reply(r) != EMERGENCY_REPLY
