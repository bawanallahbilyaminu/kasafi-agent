"""Clarification options, deduplicated (2 Nov 2026).

"I can read your question two ways: Education / EDUCATION" offered the same thing twice: two readings picked the
same sector printed in two tables. Options are one option when their titles are the same name (letter case, accents,
punctuation and spacing aside) or they name the same entity (the same budget code). One option left: no question,
the answer is given.
"""

from __future__ import annotations

import re
import unicodedata


def norm(text: str) -> str:
    """'EDUCATION', 'Education ', 'Éducation' -> 'education'."""
    t = unicodedata.normalize("NFKD", text or "")
    t = "".join(ch for ch in t if not unicodedata.combining(ch))
    return re.sub(r"[^a-z0-9]+", " ", t.casefold()).strip()


def dedupe(options: list[dict], keys: list[str] | None = None) -> list[dict]:
    """The options with duplicates removed, first kept. `keys`: one meaning key per option (an entity's code), when
    known; two options with the same non-empty key are one."""
    out, seen_titles, seen_keys = [], set(), set()
    for i, o in enumerate(options or []):
        t = norm(str(o.get("title") or ""))
        k = (keys[i] if keys and i < len(keys) else "") or ""
        if t in seen_titles or (k and k in seen_keys):
            continue
        seen_titles.add(t)
        if k:
            seen_keys.add(k)
        out.append(o)
    return out
