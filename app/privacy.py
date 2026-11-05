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

import contextvars
import logging
import re

MARK ="[location removed]"

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
# after words that can only introduce a name, the first word counts in any letter case ('my name is musa'), then
# any capitalised words that follow ('musa Bello'); small words that follow such a phrase without being a name
# ('my name is not important', 'call me when …') are left alone
_SMALL = (r"(?!(?:not|the|a|an|on|in|at|is|it|if|when|back|later|now|here|there|and|or|but|for|to|ba|ne|ce|da|"
          r"kuma|idan)\b)")
_PERSON_ANY = (rf"(?:(?i:{_HONORIFIC})\s+)?{_SMALL}[^\W\d_][\w'’-]+"
               rf"(?:\s+(?:{_HONORIFIC}\s+)?[A-Z][\w'’-]+){{0,3}}")
_SAYS_NAME = re.compile(rf"((?i:\b(?:my\s+names?\s+(?:is|are)|i\s+am\s+called|they\s+call\s+me|"
                        rf"(?:you\s+can\s+|you\s+may\s+|please\s+|just\s+)?call\s+me|sunana|sunan\s*na|"
                        rf"ana\s+kira\s*na|(?:ku\s+|ka\s+|ki\s+)?kira\s+ni))\s+)({_PERSON_ANY})")
# the name first: 'Musa ne sunana', 'Aisha ce sunana', 'Musa is my name'
_NAME_FIRST = re.compile(rf"(?<![\w'’-])({_PERSON_ANY})(\s+(?i:ne\s+sunana|ce\s+sunana|shi\s+ne\s+sunana|is\s+my\s+name)\b)")
_INTRODUCES = re.compile(rf"((?i:\b(?:i\s+am|i['’]m|this\s+is|ni\s+ne|ni\s+ce))\s+)({_PERSON})"
                         rf"(?=\s*(?:,|\bfrom\b|\bdaga\b|\bof\s+the\b|\bna\s+ma))")
# … and alone at the end of a sentence: 'Ni ne Musa.', 'I am Musa' (never after 'this is': that names anything)
_INTRODUCES_END = re.compile(rf"((?i:\b(?:i\s+am|i['’]m|ni\s+ne|ni\s+ce))\s+)({_PERSON})(?=\s*(?:[.!?]|$))")


# the name held for the user whose message is being handled (set by the conversation handler for its own task and
# the threads and tasks it starts): every storage boundary below strips it, whichever route wrote the text
_speaker: contextvars.ContextVar[str] = contextvars.ContextVar("kasafi_stated_name", default="")


def speaking(name: str) -> None:
    _speaker.set(name or "")


def strip_speaker(text):
    """The text without the name held for the user being answered (a reply that greeted them by it)."""
    return strip_name(text, _speaker.get())


def strip_identity(text):
    """The text with a name the user gave for themselves replaced by NAME_MARK (as they state it, and anywhere
    else while it is held in memory); anything that isn't a str is returned as it is."""
    if not isinstance(text, str) or not text:
        return text
    text = _SAYS_NAME.sub(lambda m: m.group(1) + NAME_MARK, text)
    text = _NAME_FIRST.sub(lambda m: NAME_MARK + m.group(2), text)
    text = _INTRODUCES.sub(lambda m: m.group(1) + NAME_MARK, text)
    return strip_speaker(_INTRODUCES_END.sub(lambda m: m.group(1) + NAME_MARK, text))


# 'I am Nigerian, …', 'This is Kasafi, right?', 'I am Director of the …': a capitalised word that isn't a person's
# name. Such words are still removed from what is stored (harmless); they are never used to address the user.
_NOT_A_NAME = {"kasafi", "nigerian", "hausa", "fulani", "sokoto", "director", "permanent", "secretary",
               "commissioner", "chairman", "chairperson", "officer", "teacher", "farmer", "student", "doctor",
               "nurse", "journalist", "staff", "resident", "citizen", "sorry", "happy", "glad", "sure", "new",
               "worried", "interested", "here", "back", "fine", "okay", "manomi", "malami", "dalibi", "likita"}


def given_name(raw, message: str = "") -> str:
    """A name as Kasafi may use it, or '': one to four words of letters, not a role, a people or a place word, not
    a title alone; written with capitals ('musa bello' -> 'Musa Bello'). With `message`, every word of it must be
    in that message (a reading can't bring a name from elsewhere)."""
    name = " ".join(str(raw or "").split())[:60].strip(" .,;:!?\"'“”")
    words = name.split()
    if not words or len(words) > 4 or not all(re.fullmatch(r"[^\W\d_][\w'’.-]*", w) for w in words):
        return ""
    low = [w.strip(".").lower() for w in words]
    if any(w in _NOT_A_NAME or w in ("none", "null", "unknown", "user") for w in low) or \
            all(re.fullmatch(_HONORIFIC, w, re.I) for w in words):
        return ""
    if message and not all(re.search(rf"(?i)(?<![\w'’-]){re.escape(w.strip('.'))}", message) for w in words):
        return ""
    return " ".join(w if any(c.isupper() for c in w) else w[:1].upper() + w[1:] for w in words)


def stated_name(text) -> str:
    """The name a user states for themselves in this message, by its wording alone ('My name is Musa Bello' ->
    'Musa Bello'), else ''. The conversation-understanding step finds the name when it runs (any form, any letter
    case: app/agent/understand.py `user_name`); this is what decides when that step doesn't run or fails. Only what
    the user writes or says: never the WhatsApp profile name."""
    if not isinstance(text, str) or not text:
        return ""
    if m := _SAYS_NAME.search(text) or _INTRODUCES.search(text) or _INTRODUCES_END.search(text):
        return given_name(m.group(2))
    m = _NAME_FIRST.search(text)
    return given_name(m.group(1)) if m else ""


def strip_name(text, name: str):
    """The text with a remembered name (whole, and each of its words of three letters or more) replaced by
    NAME_MARK: what is written to disk (the follow-up history, a trace) never carries it."""
    if not isinstance(text, str) or not text or not name:
        return text
    out = re.sub(rf"(?i)\b{re.escape(name)}\b", NAME_MARK, text)
    for part in name.split():
        if len(part.strip(".")) >= 3 and not re.fullmatch(_HONORIFIC, part):
            out = re.sub(rf"(?i)\b{re.escape(part)}\b", NAME_MARK, out)
    mark = re.escape(NAME_MARK)
    return re.sub(rf"{mark}(?:\s+{mark})+", NAME_MARK, out)          # 'Musa Bello' -> one mark, not two


NAME_TTL_S = 60 * 60          # a stated name is held for an hour after the user's last message, in memory only


class NameMemory:
    """User key -> (the name the user stated, the time of their last message). Held in the server's memory for
    NAME_TTL_S after their last message, as the location is for 30 minutes (app/geo/location.py), so a greeting or
    a thank-you can use it; never written to the database, a trace, a log or a backup; gone on DELETE MY DATA."""

    def __init__(self, ttl_s: float = NAME_TTL_S) -> None:
        import threading
        self.ttl_s, self._names, self._lock = ttl_s, {}, threading.Lock()

    def remember(self, key: str, name: str) -> None:
        import time
        if key and name:
            with self._lock:
                self._names[key] = (name[:60], time.time())

    def touch(self, key: str) -> None:
        """A new message from the user: the hour starts again (when a name is still held)."""
        import time
        with self._lock:
            held = self._names.get(key)
            if held and time.time() - held[1] <= self.ttl_s:
                self._names[key] = (held[0], time.time())
            elif held:
                self._names.pop(key, None)

    def recall(self, key: str) -> str:
        import time
        with self._lock:
            held = self._names.get(key)
            if held and time.time() - held[1] <= self.ttl_s:
                return held[0]
            self._names.pop(key, None)
            return ""

    def forget(self, key: str) -> None:
        with self._lock:
            self._names.pop(key, None)


names = NameMemory()


_old_factory = logging.getLogRecordFactory()


def _factory(*args, **kwargs):
    record = _old_factory(*args, **kwargs)
    try:
        if record.args:
            record.args = tuple(strip_identity(strip_location(a)) for a in record.args) \
                if isinstance(record.args, tuple) else record.args
        record.msg = strip_identity(strip_location(record.msg))
    except Exception:              # noqa: BLE001 - a log line is never lost to the redactor
        pass
    return record


if getattr(logging.getLogRecordFactory(), "__name__", "") != "_factory":
    logging.setLogRecordFactory(_factory)
