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
    assert outs[0].text == "🚨 This sounds like an emergency. Get help now."   # before consent: local, no model
    assert outs[-1].location_request and "medicine" not in " ".join(o.text for o in outs)


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
    shown = verified_contacts(f, private=())
    assert [c.number for c in shown] == ["0800 000 0000"]                    # 112 has no verified_on: never shown
    assert "0800" not in emergency_reply(shown)                              # no LGA known: state-wide numbers only
    from app.guardrails.emergency import contact_lines
    assert contact_lines("en", shown, lga="Wamako") == ["📞 *0800 000 0000*: State ambulance (Wamakko)"]
    assert contact_lines("ha", shown, lga="Wamakko") == ["📞 *0800 000 0000*: Motar asibiti (Wamakko)"]
    assert contact_lines("en", shown, lga="Goronyo") == [] and contact_lines("en", shown) == []
    assert "112" not in emergency_reply(shown)
    assert verified_contacts(tmp_path / "missing.yaml", private=()) == []
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


def test_private_role_numbers_load_only_when_verified_and_never_name_a_person(tmp_path) -> None:
    from app.guardrails.emergency import PRIVATE_CONTACTS, contact_lines, verified_contacts
    public = tmp_path / "public.yaml"
    public.write_text("contacts: []\n", encoding="utf-8")
    private = tmp_path / "private.yaml"
    private.write_text("contacts:\n"
                       "  - {number: '08000000001', service: 'SEMA desk officer, Goronyo', area: Goronyo,\n"
                       "     service_ha: \"Jami'in SEMA na Ƙaramar Hukumar Goronyo\", verified_on: 2026-11-02}\n"
                       "  - {number: '08000000002', service: 'SEMA desk officer, Wurno', area: Wurno}\n",
                       encoding="utf-8")
    shown = verified_contacts(public, private=(tmp_path / "absent.yaml", private))
    assert [c.number for c in shown] == ["08000000001"]                      # Wurno's has no verified_on
    assert contact_lines("en", shown, lga="Goronyo") == ["📞 *08000000001*: SEMA desk officer, Goronyo"]
    # the real private file (outside git), when present: role entries only, none verified yet
    real = PRIVATE_CONTACTS[1]
    if real.exists():
        import yaml
        rows = yaml.safe_load(real.read_text(encoding="utf-8"))["contacts"]
        assert len(rows) == 23 and all(r["service"].startswith("SEMA desk officer, ") for r in rows)
        assert not any(r.get("verified_on") for r in rows)
