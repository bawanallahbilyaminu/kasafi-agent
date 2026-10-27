import json
from pathlib import Path

import pytest
from pydantic import SecretStr

from app.config import Settings
from app.language import detect_language
from app.users import UserStore, user_key

QUESTIONS = json.loads(Path("evals/questions.json").read_text(encoding="utf-8"))["questions"]


def test_user_key_is_keyed_hash_not_plain_sha() -> None:
    import hashlib
    s1 = Settings(_env_file=None, kasafi_hash_key=SecretStr("k1"))
    s2 = Settings(_env_file=None, kasafi_hash_key=SecretStr("k2"))
    k = user_key("+234 000 000 0001", s1)
    assert k == user_key("2340000000001", s1)                 # formatting doesn't matter
    assert k != user_key("2340000000001", s2)                 # depends on the secret
    assert k != hashlib.sha256(b"2340000000001").hexdigest()  # not reversible by brute force without the key
    assert "2340000000001" not in k


def test_user_key_requires_a_secret() -> None:
    with pytest.raises(RuntimeError, match="KASAFI_HASH_KEY"):
        user_key("2340000000001", Settings(_env_file=None))


def test_store_consent_language_usage_spend_and_delete() -> None:
    st = UserStore(":memory:")
    assert st.get("u") is None
    u = st.create("u", "en")
    assert (u.lang, u.lang_source, u.consented) == ("en", "detected", False)
    st.set_lang("u", "ha"); st.give_consent("u")
    u = st.get("u")
    assert (u.lang, u.lang_source, u.consented) == ("ha", "chosen", True)
    st.count("u", "voice"); st.count("u", "voice"); st.count("u", "questions")
    assert st.usage("u") == (2, 1)
    st.add_spend(0.5); st.add_spend(0.25)
    assert st.spent_today() == pytest.approx(0.75)
    st.delete("u")
    assert st.get("u") is None and st.usage("u") == (0, 0)


@pytest.mark.parametrize("q", QUESTIONS, ids=[q["id"] for q in QUESTIONS])
def test_detects_language_of_every_eval_question(q: dict) -> None:
    expected = "en" if q["id"] == "12" else "ha"   # 09 is mixed, dominant Hausa
    assert detect_language(q["text_ha"]) == expected


@pytest.mark.parametrize("text, expected", [
    ("Sannu", "ha"), ("Hello", "en"), ("Barka da yamma", "ha"),
    ("How much was the 2026 health budget?", "en"),
    ("OK", None), ("2026", None), ("👍", None),
])
def test_detect_short_and_unclear(text: str, expected: str | None) -> None:
    assert detect_language(text) == expected
