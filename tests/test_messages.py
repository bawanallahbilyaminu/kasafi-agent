"""Style rules for every fixed user-facing message: Hausa hooked letters and paragraph spacing."""

import re

import pytest

from app.data_rights import DELETED_REPLY
from app.guardrails.emergency import EMERGENCY_REPLY
from app.whatsapp.messages import NOT_IN_PILOT, TEXTS, first_contact_notice

# Common words that must carry their hooked letter, as plain-ASCII (wrong) forms.
UNHOOKED = ["karbi", "sakon", "sako", "sakonka", "sakonninka", "kudi", "kudin", "kananan", "karamar", "rika",
            "fada", "hakuri", "bude", "zabi", "zabinka", "dan takara", "kasa da", "da ke kasa", "gyara ta"]


def _all_messages() -> list[str]:
    out = [v.format(n=20, minutes=3, text="x", transcript="x", question="x", value="x") for d in TEXTS.values() for v in d.values()]
    for lang, src in [("ha", "detected"), ("en", "detected"), ("ha", "chosen"), ("en", "chosen"), (None, None)]:
        out.extend(first_contact_notice(lang, src))
    return out + [DELETED_REPLY, EMERGENCY_REPLY, NOT_IN_PILOT]


@pytest.mark.parametrize("msg", _all_messages())
def test_no_unhooked_hausa_spellings(msg: str) -> None:
    lowered = msg.lower()
    for word in UNHOOKED:
        assert not re.search(rf"\b{word}\b", lowered), f"unhooked {word!r} in: {msg[:60]}"


@pytest.mark.parametrize("msg", _all_messages())
def test_paragraphs_are_separated_by_blank_lines(msg: str) -> None:
    # Any line break must be part of a blank line (two newlines), never a lone one.
    assert not re.search(r"(?<!\n)\n(?!\n)", msg), f"single line break in: {msg[:60]!r}"
