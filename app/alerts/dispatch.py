"""Deciding and sending alerts: the limits, the kasafi_hazard_alert template's values, and the dry run.

For each trigger candidate (app/alerts/triggers.py) with subscribers for its hazard and LGA:
- a key already sent (or dry-run sent, or skipped for want of an approved template) is never sent again;
- at most one alert per hazard per LGA per Lagos day;
- quiet hours 22:00-06:00 hold back everything but official warnings (the candidate waits for 06:00);
- the global daily cap (KASAFI_ALERTS_DAILY_CAP, template messages a day, all users): 0 sends nothing live; the
  dry run applies it only when set;
- each recipient gets the template in their language when Meta has approved it (KASAFI_ALERT_TEMPLATE_LANGS);
  otherwise that send is skipped and logged.
In the dry run (KASAFI_ALERTS_DRY_RUN, on by default) nothing reaches users: each alert is logged with its values
for /admin/alerts. Every decision is in alert_log, by hazard and LGA, with no user keys.
"""

from __future__ import annotations

import logging
import re
from collections import Counter
from collections.abc import Awaitable, Callable
from datetime import datetime, timedelta, timezone

from app.alerts.triggers import Candidate, all_candidates
from app.sources.lga_names import name_of

log = logging.getLogger(__name__)
LAGOS = timezone(timedelta(hours=1))
TEMPLATE = "kasafi_hazard_alert"
QUIET = (22, 6)                       # 22:00-06:00 Lagos
VALUE_CHARS = 300
DONE = {"sent", "dry_run", "no_template"}
HAZARD_NAMES = {"en": {"heat": "heat", "dust": "harmattan dust", "flood": "flood", "outbreak": "disease outbreak"},
                "ha": {"heat": "zafin rana", "dust": "ƙurar hunturu", "flood": "ambaliya",
                       "outbreak": "ɓarkewar cuta"}}
# (user key, language, the four values) -> delivered; None: no way to reach a user key yet (see docs)
SendFn = Callable[[str, str, list[str]], Awaitable[bool]]


def clean(value: str) -> str:
    """A template value: one line, no closing full stop (the template supplies it), at most VALUE_CHARS."""
    v = " ".join((value or "").split())[:VALUE_CHARS].strip()
    return re.sub(r"[.\s]+$", "", v)


def values(c: Candidate, lang: str) -> list[str]:
    """{{1}} hazard, {{2}} LGA, {{3}} what and when with the figure, {{4}} source and time."""
    names = HAZARD_NAMES.get(lang, HAZARD_NAMES["en"])
    return [clean(v) for v in (names[c.hazard], name_of(c.lga_pcode) or c.lga_pcode, c.what[lang], c.source[lang])]


def quiet(now: datetime) -> bool:
    h = now.astimezone(LAGOS).hour
    return h >= QUIET[0] or h < QUIET[1]


def approved_langs(settings) -> set[str]:
    return {x.strip() for x in (settings.kasafi_alert_template_langs or "").split(",") if x.strip()}


async def dispatch(candidates: list[Candidate], store, settings, now: datetime | None = None,
                   send: SendFn | None = None) -> Counter:
    """Apply the limits to each candidate and send (or, in the dry run, log) it. Returns the count per status."""
    now = now or datetime.now(timezone.utc)
    day = now.astimezone(LAGOS).date().isoformat()
    dry, cap, approved = settings.kasafi_alerts_dry_run, settings.kasafi_alerts_daily_cap, approved_langs(settings)
    out: Counter = Counter()

    def once(c: Candidate, status: str, seen: set[str], n: int, **kw) -> None:
        if status not in seen:                     # a held-back alert is logged once, not every round
            store.log_alert(c.hazard, c.lga_pcode, c.key, c.official, status, n, now=now, **kw)
        out[status] += 1

    for c in candidates:
        seen = store.alert_statuses(c.key)
        if seen & DONE:
            continue
        subs = store.subscribers(c.lga_pcode, c.hazard)
        if not subs or store.alerted_today(c.hazard, c.lga_pcode, day):
            continue
        langs = Counter(lang for _, lang in subs)
        message = {lang: values(c, lang) for lang in langs}
        if quiet(now) and not c.official:
            once(c, "quiet", seen, len(subs), langs=dict(langs), message=message, note="held until 06:00")
            continue
        ready = [(k, lang) for k, lang in subs if lang in approved]
        skipped = {lang: n for lang, n in langs.items() if lang not in approved}
        note = (f"skipped, template not approved: {', '.join(f'{lang} ({n})' for lang, n in skipped.items())}"
                if skipped else "")
        if skipped:
            log.info("alert %s: %d send(s) skipped, template language not approved: %s", c.key,
                     sum(skipped.values()), ", ".join(skipped))
        if not ready:
            once(c, "no_template", seen, 0, langs=dict(langs), message=message, note=note)
            continue
        limit = cap if (cap > 0 or not dry) else None
        if limit is not None and store.alerts_sent(day) + len(ready) > limit:
            once(c, "capped", seen, len(ready), langs=dict(langs), message=message,
                 note=f"daily cap {cap} (KASAFI_ALERTS_DAILY_CAP)")
            continue
        if dry:
            store.log_alert(c.hazard, c.lga_pcode, c.key, c.official, "dry_run", len(ready), dict(langs), message,
                            note, now=now)
            out["dry_run"] += 1
            continue
        if send is None:
            once(c, "no_recipient", seen, len(ready), langs=dict(langs), message=message,
                 note="no recipient address for a user key: live sending isn't set up")
            continue
        delivered = sum([await send(k, lang, message[lang]) for k, lang in ready])
        store.log_alert(c.hazard, c.lga_pcode, c.key, c.official, "sent", delivered, dict(langs), message,
                        note, now=now)
        out["sent"] += 1
    return out


def run(conn, store, settings, now: datetime | None = None) -> Counter:
    """One round, from the hazard fetch loop: the triggers, then the dispatch (dry run unless switched off)."""
    import asyncio
    return asyncio.run(dispatch(all_candidates(conn, now), store, settings, now))
