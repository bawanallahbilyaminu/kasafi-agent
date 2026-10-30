"""Medical-emergency safety net: runs before anything else replies.

Kasafi gives no medical advice (CLAUDE.md rule 5). When a message describes an
emergency, it must not get a read-back or an "answer coming soon"; it gets an
immediate referral. This is a deliberately simple keyword check on the transcript
and its English translation, kept until the full guardrail classifier exists.

It avoids "gaggawa" and "emergency" on purpose: budget questions about emergency
care (e.g. EmONC, "kulawar gaggawa") are in scope and must not trigger it.
"""

import re
from dataclasses import dataclass
from pathlib import Path

import yaml

CONTACTS_PATH = Path(__file__).resolve().parents[2] / "data" / "emergency_contacts.yaml"


@dataclass(frozen=True)
class Contact:
    number: str
    service: str
    service_ha: str
    area: str
    verified_on: str


def verified_contacts(path: Path = CONTACTS_PATH) -> list[Contact]:
    """The emergency numbers confirmed to work from Sokoto (data/emergency_contacts.yaml, verified_on set). An entry
    without verified_on is never shown; a missing or broken file means none."""
    try:
        rows = (yaml.safe_load(path.read_text(encoding="utf-8")) or {}).get("contacts") or []
    except (OSError, yaml.YAMLError):
        return []
    return [Contact(str(r["number"]).strip(), str(r.get("service") or ""), str(r.get("service_ha") or r.get("service")
                                                                                 or ""),
                    str(r.get("area") or "state-wide"), str(r["verified_on"]))
            for r in rows if isinstance(r, dict) and r.get("number") and r.get("verified_on")]


def emergency_reply(contacts: list[Contact] | None = None) -> str:
    """Go to the nearest facility now, and the verified numbers only (none shown until one is verified)."""
    contacts = verified_contacts() if contacts is None else contacts
    ha = "\n".join(f"📞 *{c.number}*: {c.service_ha}" + ("" if c.area == "state-wide" else f" ({c.area})")
                   for c in contacts)
    en = "\n".join(f"📞 *{c.number}*: {c.service}" + ("" if c.area == "state-wide" else f" ({c.area})")
                   for c in contacts)
    return ("⚠️ Wannan na iya zama gaggawar lafiya. Kasafi ba ya ba da shawarar magani.\n\n"
            "Don Allah ku je asibiti ko cibiyar lafiya mafi kusa *nan take*." + (f"\n{ha}" if ha else "") + "\n\n"
            "This may be a medical emergency. Kasafi cannot give medical advice.\n\n"
            "Please go to the nearest health facility *now*." + (f"\n{en}" if en else ""))


EMERGENCY_REPLY = emergency_reply()

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
