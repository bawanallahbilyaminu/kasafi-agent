"""Medical-emergency safety net: runs before anything else replies.

Kasafi gives no medical advice (CLAUDE.md rule 5). When a message describes an
emergency, it must not get a read-back or an "answer coming soon"; it gets an
immediate referral. This is a deliberately simple keyword check on the transcript
and its English translation, kept until the full guardrail classifier exists.

It avoids "gaggawa" and "emergency" on purpose: budget questions about emergency
care (e.g. EmONC, "kulawar gaggawa") are in scope and must not trigger it.
"""

import re

EMERGENCY_REPLY = (
    "⚠️ Wannan na iya zama gaggawar lafiya. Kasafi ba ya ba da shawarar magani.\n"
    "Don Allah ku je asibiti ko cibiyar lafiya mafi kusa *nan take*, ko ku kira *112*.\n\n"
    "This may be a medical emergency. Kasafi cannot give medical advice. "
    "Please go to the nearest health facility *now*, or call *112*."
)

_PATTERNS = [
    # Hausa
    r"\bzubar da jini\b", r"\bjini na\s+zuba\b", r"\bta\s+suma\b", r"\bya\s+suma\b", r"\bsuman\b",
    r"\bba\s+(?:ya|ta)\s+numfashi\b", r"\bfarfadiya\b", r"\bɓari\b", r"\bbari\s+ciki\b",
    # English
    r"\bbleed(?:ing|s)?\b", r"\bunconscious\b", r"\bfainted\b", r"\bnot breathing\b",
    r"\bconvuls(?:ion|ing)s?\b", r"\bseizures?\b", r"\bmiscarri(?:age|ed)\b", r"\boverdose\b",
]
_RE = re.compile("|".join(_PATTERNS), re.IGNORECASE)


def is_medical_emergency(*texts: str) -> bool:
    return any(t and _RE.search(t) for t in texts)
