"""Text shown to users is shortened at a word, never in the middle of one (5 Nov 2026: 'public schools with pre-primary
classes (subset of the public Pre-Primary and Pr: 14')."""

from __future__ import annotations

import re


def shorten(text: str, most: int, mark: str = "…", hard: bool = False) -> str:
    """At most `most` characters, cut at a word, with `mark` to show that something went. A bracket the cut leaves open
    goes whole (an aside, so no mark). A first word longer than `most` is kept whole, since a label over its limit reads
    better than half a word; with `hard` (WhatsApp refuses a longer button title) it is cut, as nothing else can fit."""
    t = re.sub(r"\s+", " ", text or "").strip()
    if len(t) <= most:
        return t
    room = most - len(mark)
    cut = t[:room + 1].rsplit(" ", 1)[0] if " " in t[:room + 1] else ""
    if not cut:
        first = t.split(" ", 1)[0]
        if hard:
            return first[:room] + mark
        return first if first == t else first + mark
    aside = cut.count("(") > cut.count(")")
    if aside:
        before = cut[:cut.rfind("(")].rstrip(" ,;:-")
        if before:
            return before
    return cut.rstrip(" ,;:-(") + mark


def button_title(text: str) -> str:
    """A WhatsApp button's title: at most 20 characters."""
    return shorten(text, 20, hard=True)
