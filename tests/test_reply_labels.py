"""Pattern p8 (evals/patterns): a row's internal level label ('ministry total including its agencies') echoed by
the model never reaches the reply, from any path; the working keeps it."""

from __future__ import annotations

from app.agent.answer import plain_level_words


def test_internal_level_labels_become_plain_words_in_any_reply() -> None:
    text = ("• 2026 approved budget (personnel) for Government House (ministry total including its agencies): ₦444.25 million\n"
            "• 2026 approved budget (total) for Government House: ₦18.53 billion")
    out = plain_level_words(text, "en")
    assert "ministry total including" not in out and "its agencies included" in out
    assert "one agency or unit" not in plain_level_words("This is the one agency or unit line.", "en")
    ha = plain_level_words("Wannan shi ne ministry total including its agencies.", "ha")
    assert "jimillar ma'aikatar" in ha and "ministry total" not in ha
