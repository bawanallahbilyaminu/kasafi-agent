"""Exact locations a user types or says are never stored (follow-up review, finding 3). One redactor, applied at
the shared boundaries: every text the user store writes (conversation turns, saved working and quotes, pending
questions and options), every trace and failure record (app/agent/trace.py), every log record (a record factory,
installed on import), and the question and follow-up history sent to the models.

What counts as an exact location:
- a decimal latitude/longitude pair with 4 or more decimals ('13.0589127, 5.1673341', '13.0589 5.1673'), or with
  3 or more when labelled ('lat 13.058 lon 5.167', 'latitude: 13.058');
- degrees-minutes(-seconds) ('13°03'32"N 5°10'02"E', '13° 3.5' N');
- Open Location Codes (plus codes: '7FG9+X2', '7FG9X2V5+7C').
Budget figures ('70,000,000.00'), percentages and statistics with two or three decimals ('MPI 0.409, 0.239')
survive. A WhatsApp pin is never text: its point stays in memory only (app/geo/location.py).
"""

from __future__ import annotations

import logging
import re

MARK = "[location removed]"

_PAIR = re.compile(r"(?<!\d)(?<!\d[.,])-?\d{1,3}\.\d{4,}\s*[,;/ ]\s*-?\d{1,3}\.\d{4,}(?!\d)(?!\.\d)")
_LABELLED = re.compile(r"(?i)\b(?:lat(?:itude)?|lon(?:gitude)?|lng|long)\s*[:=]?\s*-?\d{1,3}\.\d{3,}"
                       r"(?:\s*[,;/ ]?\s*(?:(?:lat(?:itude)?|lon(?:gitude)?|lng|long)\s*[:=]?\s*)?-?\d{1,3}\.\d{3,})?")
_DMS = re.compile(r"\d{1,3}\s*°\s*\d{1,2}(?:\.\d+)?\s*['′’]\s*(?:\d{1,2}(?:\.\d+)?\s*[\"″”]\s*)?[NSEW]?"
                  r"(?:\s*[,;/ ]?\s*\d{1,3}\s*°\s*\d{1,2}(?:\.\d+)?\s*['′’]\s*(?:\d{1,2}(?:\.\d+)?\s*[\"″”]\s*)?[NSEW]?)?"
                  r"|\d{1,3}(?:\.\d+)?\s*°\s*[NSEW](?:\s*[,;/ ]?\s*\d{1,3}(?:\.\d+)?\s*°\s*[NSEW])?")
_PLUS = re.compile(r"(?<![A-Za-z0-9+])[23456789CFGHJMPQRVWX]{4,8}\+[23456789CFGHJMPQRVWX]{2,3}(?![A-Za-z0-9])",
                   re.IGNORECASE)


def strip_location(text):
    """The text with every exact location replaced by MARK; anything that isn't a str is returned as it is."""
    if not isinstance(text, str) or not text:
        return text
    text = _LABELLED.sub(MARK, text)
    text = _DMS.sub(MARK, text)
    text = _PAIR.sub(MARK, text)
    return _PLUS.sub(MARK, text)


def has_location(text: str) -> bool:
    return strip_location(text) != text


# --- a name the user gives about themselves (5 Nov 2026) -----------------------------------------------------------
# "My name is …", "Sunana …", "I am Musa Bello, Director of …": Kasafi doesn't ask who anyone is and doesn't keep it.
# The name is removed before the message is saved to the follow-up history or an answer trace; the question itself
# stays. Only the name goes: a job or an office named without a person isn't personal data.
NAME_MARK = "[name removed]"
_HONORIFIC = r"(?:Alhaji|Alh\.?|Hajiya|Haj\.?|Malam|Mallam|Mal\.?|Dr\.?|Engr\.?|Prof\.?|Mr\.?|Mrs\.?|Ms\.?|Barr\.?|Hon\.?|Sir|Chief)"
_PERSON = rf"(?:{_HONORIFIC}\s+)?[A-Z][\w'’-]+(?:\s+(?:{_HONORIFIC}\s+)?[A-Z][\w'’-]+){{0,3}}"
_SAYS_NAME = re.compile(rf"((?i:\b(?:my\s+names?\s+(?:is|are)|i\s+am\s+called|they\s+call\s+me|sunana|sunan\s*na|"
                        rf"ana\s+kira\s*na))\s+)({_PERSON})")
_INTRODUCES = re.compile(rf"((?i:\b(?:i\s+am|i['’]m|this\s+is|ni\s+ne|ni\s+ce))\s+)({_PERSON})"
                         rf"(?=\s*(?:,|\bfrom\b|\bdaga\b|\bof\s+the\b|\bna\s+ma))")


def strip_identity(text):
    """The text with a name the user gave for themselves replaced by NAME_MARK; anything that isn't a str is
    returned as it is."""
    if not isinstance(text, str) or not text:
        return text
    text = _SAYS_NAME.sub(lambda m: m.group(1) + NAME_MARK, text)
    return _INTRODUCES.sub(lambda m: m.group(1) + NAME_MARK, text)


_old_factory = logging.getLogRecordFactory()


def _factory(*args, **kwargs):
    record = _old_factory(*args, **kwargs)
    try:
        if record.args:
            record.args = tuple(strip_location(a) for a in record.args) if isinstance(record.args, tuple) else record.args
        record.msg = strip_location(record.msg)
    except Exception:              # noqa: BLE001 - a log line is never lost to the redactor
        pass
    return record


if getattr(logging.getLogRecordFactory(), "__name__", "") != "_factory":
    logging.setLogRecordFactory(_factory)
