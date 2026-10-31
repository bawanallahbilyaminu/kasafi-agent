"""Per-user state: consent, language, daily limits and the global spend tally.

Privacy: the phone number is never stored. Users are keyed by HMAC-SHA256(number) with a
server secret (KASAFI_HASH_KEY). A plain SHA-256 of a phone number can be reversed by trying
every number. Usage rows are pruned after 30 days, matching the log retention. A read-back
question waiting for confirmation is kept for at most KASAFI_PENDING_TTL_MINUTES. The last few
turns (question, answer, cited documents) are kept for follow-ups such as "check again", and
deleted after 90 days (the conversation retention in the privacy policy). Everything
for a user is removed by GOGE BAYANAI NA / DELETE MY DATA (app/data_rights.py).

SQLite on a Docker volume for the pilot (KASAFI_STATE_DB). It moves to Postgres with the rest
of the data model.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
import sqlite3
import threading
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from functools import lru_cache
from pathlib import Path

from app.config import Settings, get_settings

log = logging.getLogger(__name__)
LAGOS = timezone(timedelta(hours=1))  # Nigeria has no DST; "per day" means a Lagos calendar day
USAGE_RETENTION_DAYS = 30
TURN_RETENTION_DAYS = 90
TURNS_KEPT = 5
TURN_ANSWER_CHARS = 1500
WORKING_CHARS = 3500        # the rows and arithmetic behind an answer, sent on "nuna lissafi" / "show working"

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    user_key    TEXT PRIMARY KEY,
    lang        TEXT,              -- 'ha' | 'en' | NULL (not known yet)
    lang_source TEXT,              -- 'detected' | 'chosen'
    consent_at  TEXT,              -- ISO time the user tapped OK / Na yarda; NULL = not consented
    created_at  TEXT NOT NULL,
    pending_question TEXT,         -- read-back awaiting Eh / A'a / a correction (short-lived)
    pending_english  TEXT,
    pending_at       TEXT,
    pending_options  TEXT,         -- JSON {"replace": ..., "add": ...} while asking which one was meant
    pending_calc     TEXT,         -- JSON calculation offered ("Reply Eh to calculate"), until the next message
    images_off       INTEGER,      -- 1 = no evidence images with answers ("images off"); NULL/0 = send them
    pending_clarify  TEXT,         -- JSON options while Kasafi asks which reading of a question was meant
    last_lga         TEXT,         -- the LGA (P-code) of the user's last location; never coordinates (90 days)
    last_lga_at      TEXT,
    location_notice_at TEXT        -- when the one-line location notice was shown (once)
);
CREATE TABLE IF NOT EXISTS usage (
    user_key  TEXT NOT NULL,
    day       TEXT NOT NULL,
    voice     INTEGER NOT NULL DEFAULT 0,
    questions INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (user_key, day)
);
CREATE TABLE IF NOT EXISTS turns (
    user_key  TEXT NOT NULL,
    at        TEXT NOT NULL,       -- ISO time
    lang      TEXT,
    question  TEXT NOT NULL,
    answer    TEXT NOT NULL,
    sources   TEXT                 -- JSON [{"doc_id", "title", "page", "series", "edition"}]
);
CREATE INDEX IF NOT EXISTS turns_user_idx ON turns (user_key, at);
CREATE TABLE IF NOT EXISTS spend (
    day TEXT PRIMARY KEY,
    usd REAL NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS api_calls (  -- per-day call counts for priced APIs (e.g. SAM 3.1), to watch spending
    day  TEXT NOT NULL,
    name TEXT NOT NULL,
    n    INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (day, name)
);
CREATE TABLE IF NOT EXISTS alert_subs (  -- hazard alerts a user signed up for (app/alerts): nothing else is kept
    user_key   TEXT PRIMARY KEY,
    lgas       TEXT NOT NULL,      -- JSON list of LGA P-codes
    hazards    TEXT NOT NULL,      -- JSON list: heat | dust | flood | outbreak
    lang       TEXT NOT NULL,      -- the alert template's language: 'ha' | 'en'
    created_at TEXT NOT NULL,
    number_enc TEXT,               -- the WhatsApp number, encrypted (app/alerts/recipients.py), to send alerts to
    last_contact_at TEXT           -- the user's last message: 90 days without one deletes the subscription
);
CREATE TABLE IF NOT EXISTS alert_log (   -- each alert decided, per hazard and LGA (no user keys), for the admin page
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    at         TEXT NOT NULL,      -- ISO time (UTC)
    day        TEXT NOT NULL,      -- the Lagos day, for 'one per hazard per LGA per day'
    hazard     TEXT NOT NULL,
    lga_pcode  TEXT NOT NULL,
    key        TEXT NOT NULL,      -- what fired: adv:<id>, heat:<lga>:<day>, ncdc:<disease>:<year>-<week> ...
    official   INTEGER NOT NULL,   -- 1: an official warning (sent in quiet hours too)
    status     TEXT NOT NULL,      -- dry_run | sent | quiet | capped | no_template | no_recipient
    recipients INTEGER NOT NULL,
    langs      TEXT,               -- JSON {"ha": 3, "en": 1}: recipients by language
    message    TEXT,               -- JSON {"ha": [v1, v2, v3, v4], ...}: the template's variables
    note       TEXT
);
CREATE INDEX IF NOT EXISTS alert_log_day_idx ON alert_log (day, hazard, lga_pcode);
"""
ALERT_LOG_DAYS = 90


@dataclass
class User:
    key: str
    lang: str | None
    lang_source: str | None
    consent_at: str | None

    @property
    def consented(self) -> bool:
        return self.consent_at is not None


def today() -> str:
    return datetime.now(LAGOS).date().isoformat()


def user_key(phone: str, settings: Settings) -> str:
    secret = settings.kasafi_hash_key or settings.whatsapp_app_secret
    key = secret.get_secret_value() if secret is not None else ""
    if not key:
        raise RuntimeError("KASAFI_HASH_KEY (or WHATSAPP_APP_SECRET) must be set to key user IDs")
    digits = "".join(ch for ch in phone if ch.isdigit())
    return hmac.new(key.encode(), digits.encode(), hashlib.sha256).hexdigest()


class UserStore:
    def __init__(self, path: str) -> None:
        if path != ":memory:":
            Path(path).parent.mkdir(parents=True, exist_ok=True)
        self._db = sqlite3.connect(path, check_same_thread=False, isolation_level=None)
        self._db.execute("PRAGMA journal_mode=WAL" if path != ":memory:" else "PRAGMA journal_mode=MEMORY")
        self._db.executescript(SCHEMA)
        self._migrate()
        self._lock = threading.Lock()

    def _migrate(self) -> None:
        """Add columns introduced after the first deploy (the server DB already exists)."""
        have = {row[1] for row in self._db.execute("PRAGMA table_info(users)")}
        for col in ("pending_question", "pending_english", "pending_at", "pending_options", "pending_calc"):
            if col not in have:
                self._db.execute(f"ALTER TABLE users ADD COLUMN {col} TEXT")
        if "images_off" not in have:
            self._db.execute("ALTER TABLE users ADD COLUMN images_off INTEGER")
        if "pending_clarify" not in have:
            self._db.execute("ALTER TABLE users ADD COLUMN pending_clarify TEXT")
        for col in ("last_lga", "last_lga_at", "location_notice_at"):      # location: the LGA only (hazard step 1)
            if col not in have:
                self._db.execute(f"ALTER TABLE users ADD COLUMN {col} TEXT")
        if "pending_alert" not in have:          # an alert sign-up waiting for the user's explicit OK (step 6)
            self._db.execute("ALTER TABLE users ADD COLUMN pending_alert TEXT")
        sub_cols = {row[1] for row in self._db.execute("PRAGMA table_info(alert_subs)")}
        for col in ("number_enc", "last_contact_at"):      # live alerts need an address (subscribers only)
            if col not in sub_cols:
                self._db.execute(f"ALTER TABLE alert_subs ADD COLUMN {col} TEXT")
        turn_cols = {row[1] for row in self._db.execute("PRAGMA table_info(turns)")}
        if "working" not in turn_cols:
            self._db.execute("ALTER TABLE turns ADD COLUMN working TEXT")     # "nuna lissafi" / "show working"
        if "quotes" not in turn_cols:
            self._db.execute("ALTER TABLE turns ADD COLUMN quotes TEXT")      # "quotes" / "nuna rubutun"

    def _exec(self, sql: str, args: tuple = ()) -> sqlite3.Cursor:
        with self._lock:
            return self._db.execute(sql, args)

    # users
    def get(self, key: str) -> User | None:
        row = self._exec("SELECT user_key, lang, lang_source, consent_at FROM users WHERE user_key=?", (key,)).fetchone()
        return User(*row) if row else None

    def create(self, key: str, lang: str | None) -> User:
        now = datetime.now(timezone.utc).isoformat()
        self._exec("INSERT OR IGNORE INTO users (user_key, lang, lang_source, created_at) VALUES (?,?,?,?)",
                   (key, lang, "detected" if lang else None, now))
        return self.get(key)  # type: ignore[return-value]

    def set_lang(self, key: str, lang: str) -> None:
        self._exec("UPDATE users SET lang=?, lang_source='chosen' WHERE user_key=?", (lang, key))

    def give_consent(self, key: str) -> None:
        self._exec("UPDATE users SET consent_at=? WHERE user_key=? AND consent_at IS NULL",
                   (datetime.now(timezone.utc).isoformat(), key))

    # pending read-back
    def set_pending(self, key: str, question: str, english: str) -> None:
        self._exec("UPDATE users SET pending_question=?, pending_english=?, pending_at=? WHERE user_key=?",
                   (question, english, datetime.now(timezone.utc).isoformat(), key))

    def get_pending(self, key: str, ttl_minutes: int) -> tuple[str, str] | None:
        row = self._exec("SELECT pending_question, pending_english, pending_at FROM users WHERE user_key=?",
                         (key,)).fetchone()
        if not row or not row[0]:
            return None
        if datetime.now(timezone.utc) - datetime.fromisoformat(row[2]) > timedelta(minutes=ttl_minutes):
            self.clear_pending(key)
            return None
        return row[0], row[1] or ""

    def set_pending_options(self, key: str, options: dict[str, str]) -> None:
        self._exec("UPDATE users SET pending_options=? WHERE user_key=?", (json.dumps(options, ensure_ascii=False), key))

    def get_pending_options(self, key: str) -> dict[str, str] | None:
        row = self._exec("SELECT pending_options FROM users WHERE user_key=?", (key,)).fetchone()
        return json.loads(row[0]) if row and row[0] else None

    def clear_pending_options(self, key: str) -> None:
        self._exec("UPDATE users SET pending_options=NULL WHERE user_key=?", (key,))

    # evidence images ("images off" / "kashe hotuna")
    def images_on(self, key: str) -> bool:
        row = self._exec("SELECT images_off FROM users WHERE user_key=?", (key,)).fetchone()
        return not (row and row[0])

    def set_images(self, key: str, on: bool) -> None:
        self._exec("UPDATE users SET images_off=? WHERE user_key=?", (0 if on else 1, key))

    def set_pending_clarify(self, key: str, options: list[dict] | None) -> None:
        self._exec("UPDATE users SET pending_clarify=? WHERE user_key=?",
                   (json.dumps(options, ensure_ascii=False) if options else None, key))

    def get_pending_clarify(self, key: str) -> list[dict] | None:
        row = self._exec("SELECT pending_clarify FROM users WHERE user_key=?", (key,)).fetchone()
        return json.loads(row[0]) if row and row[0] else None

    def set_pending_calc(self, key: str, calc: dict | None) -> None:
        self._exec("UPDATE users SET pending_calc=? WHERE user_key=?",
                   (json.dumps(calc, ensure_ascii=False) if calc else None, key))

    def get_pending_calc(self, key: str) -> dict | None:
        row = self._exec("SELECT pending_calc FROM users WHERE user_key=?", (key,)).fetchone()
        return json.loads(row[0]) if row and row[0] else None

    # location: only the LGA is kept (its P-code), for 90 days; coordinates never reach this store
    def set_last_lga(self, key: str, lga_pcode: str) -> None:
        self._exec("UPDATE users SET last_lga=?, last_lga_at=? WHERE user_key=?",
                   (lga_pcode, datetime.now(timezone.utc).isoformat(), key))

    def get_last_lga(self, key: str) -> str | None:
        row = self._exec("SELECT last_lga, last_lga_at FROM users WHERE user_key=?", (key,)).fetchone()
        if not row or not row[0] or not row[1]:
            return None
        if datetime.now(timezone.utc) - datetime.fromisoformat(row[1]) > timedelta(days=TURN_RETENTION_DAYS):
            self._exec("UPDATE users SET last_lga=NULL, last_lga_at=NULL WHERE user_key=?", (key,))
            return None
        return row[0]

    def location_notice_due(self, key: str) -> bool:
        """True once: the first time the user shares or asks with a location (the one-line notice)."""
        row = self._exec("SELECT location_notice_at FROM users WHERE user_key=?", (key,)).fetchone()
        if row and row[0]:
            return False
        self._exec("UPDATE users SET location_notice_at=? WHERE user_key=?",
                   (datetime.now(timezone.utc).isoformat(), key))
        return True

    def clear_pending(self, key: str) -> None:
        self._exec("UPDATE users SET pending_question=NULL, pending_english=NULL, pending_at=NULL, "
                   "pending_options=NULL WHERE user_key=?",
                   (key,))

    def delete(self, key: str) -> None:
        with self._lock:
            self._db.execute("DELETE FROM users WHERE user_key=?", (key,))
            self._db.execute("DELETE FROM usage WHERE user_key=?", (key,))
            self._db.execute("DELETE FROM turns WHERE user_key=?", (key,))
            self._db.execute("DELETE FROM alert_subs WHERE user_key=?", (key,))

    # hazard alerts (app/alerts): the subscription is the user key, LGAs, hazards, language and created_at only
    def set_pending_alert(self, key: str, pending: dict | None) -> None:
        self._exec("UPDATE users SET pending_alert=? WHERE user_key=?",
                   (json.dumps(pending, ensure_ascii=False) if pending else None, key))

    def get_pending_alert(self, key: str) -> dict | None:
        row = self._exec("SELECT pending_alert FROM users WHERE user_key=?", (key,)).fetchone()
        return json.loads(row[0]) if row and row[0] else None

    def subscribe(self, key: str, lgas: list[str], hazards: list[str], lang: str, number_enc: str | None = None
                  ) -> dict:
        """Add LGAs and hazards to the user's alerts (a second sign-up adds to the first); the language is the
        latest chosen, and the encrypted number the latest given. Returns the subscription as stored."""
        have = self.subscription(key) or {"lgas": [], "hazards": []}
        lgas = sorted(set(have["lgas"]) | set(lgas))
        hazards = [h for h in ("heat", "dust", "flood", "outbreak") if h in set(have["hazards"]) | set(hazards)]
        now = datetime.now(timezone.utc).isoformat()
        self._exec("INSERT INTO alert_subs (user_key, lgas, hazards, lang, created_at, number_enc, last_contact_at) "
                   "VALUES (?,?,?,?,?,?,?) ON CONFLICT(user_key) DO UPDATE SET lgas=excluded.lgas, "
                   "hazards=excluded.hazards, lang=excluded.lang, last_contact_at=excluded.last_contact_at, "
                   "number_enc=coalesce(excluded.number_enc, alert_subs.number_enc)",
                   (key, json.dumps(lgas), json.dumps(hazards), lang, now, number_enc, now))
        return {"lgas": lgas, "hazards": hazards, "lang": lang}

    def alert_number(self, key: str) -> str | None:
        """The subscriber's encrypted number (app/alerts/recipients.decrypt), or None."""
        row = self._exec("SELECT number_enc FROM alert_subs WHERE user_key=?", (key,)).fetchone()
        return row[0] if row else None

    def touch_alert_contact(self, key: str) -> None:
        """A message from the user: their subscription (if any) is active for another 90 days."""
        self._exec("UPDATE alert_subs SET last_contact_at=? WHERE user_key=?",
                   (datetime.now(timezone.utc).isoformat(), key))

    def prune_alert_subs(self, days: int = 90, now: datetime | None = None) -> int:
        """Delete subscriptions (and so their encrypted numbers) with no message from the user for `days` days."""
        cutoff = ((now or datetime.now(timezone.utc)) - timedelta(days=days)).isoformat()
        return self._exec("DELETE FROM alert_subs WHERE coalesce(last_contact_at, created_at) < ?", (cutoff,)).rowcount

    def subscription(self, key: str) -> dict | None:
        row = self._exec("SELECT lgas, hazards, lang FROM alert_subs WHERE user_key=?", (key,)).fetchone()
        return {"lgas": json.loads(row[0]), "hazards": json.loads(row[1]), "lang": row[2]} if row else None

    def unsubscribe(self, key: str) -> bool:
        """STOP / DAINA: the subscription is deleted (not flagged). True when there was one."""
        return self._exec("DELETE FROM alert_subs WHERE user_key=?", (key,)).rowcount > 0

    def subscribers(self, lga_pcode: str, hazard: str) -> list[tuple[str, str]]:
        """(user key, language) of everyone signed up for this hazard in this LGA."""
        rows = self._exec("SELECT user_key, lgas, hazards, lang FROM alert_subs").fetchall()
        return [(k, lang) for k, lgas, hazards, lang in rows
                if lga_pcode in json.loads(lgas) and hazard in json.loads(hazards)]

    def log_alert(self, hazard: str, lga_pcode: str, key: str, official: bool, status: str, recipients: int,
                  langs: dict | None = None, message: dict | None = None, note: str = "",
                  now: datetime | None = None) -> None:
        now = now or datetime.now(timezone.utc)
        self._exec("INSERT INTO alert_log (at, day, hazard, lga_pcode, key, official, status, recipients, langs, "
                   "message, note) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                   (now.isoformat(), now.astimezone(LAGOS).date().isoformat(), hazard, lga_pcode, key, int(official),
                    status, recipients, json.dumps(langs or {}), json.dumps(message or {}, ensure_ascii=False), note))
        self._exec("DELETE FROM alert_log WHERE at < ?", ((now - timedelta(days=ALERT_LOG_DAYS)).isoformat(),))

    def alert_statuses(self, key: str) -> set[str]:
        """The statuses logged for what fired (`key`): a key already sent (or dry-run sent) is not sent again."""
        return {r[0] for r in self._exec("SELECT status FROM alert_log WHERE key=?", (key,)).fetchall()}

    def alerted_today(self, hazard: str, lga_pcode: str, day: str) -> bool:
        """At most one alert per hazard per LGA per (Lagos) day: sent, or sent in the dry run."""
        return self._exec("SELECT 1 FROM alert_log WHERE day=? AND hazard=? AND lga_pcode=? AND status IN "
                          "('sent', 'dry_run') LIMIT 1", (day, hazard, lga_pcode)).fetchone() is not None

    def alerts_sent(self, day: str) -> int:
        """Template messages sent (or dry-run sent) on a Lagos day, for the global daily cap."""
        row = self._exec("SELECT coalesce(sum(recipients), 0) FROM alert_log WHERE day=? AND status IN "
                         "('sent', 'dry_run')", (day,)).fetchone()
        return int(row[0])

    def alert_log(self, limit: int = 200) -> list[dict]:
        cols = ("at", "day", "hazard", "lga_pcode", "key", "official", "status", "recipients", "langs", "message",
                "note")
        rows = self._exec(f"SELECT {', '.join(cols)} FROM alert_log ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
        return [{**dict(zip(cols, r)), "langs": json.loads(r[8] or "{}"), "message": json.loads(r[9] or "{}")}
                for r in rows]

    def subscription_counts(self) -> dict[str, int]:
        """How many people are signed up, per hazard (the admin page; no keys shown)."""
        out: dict[str, int] = {}
        for (hazards,) in self._exec("SELECT hazards FROM alert_subs").fetchall():
            for h in json.loads(hazards):
                out[h] = out.get(h, 0) + 1
        return out

    # conversation context for follow-ups
    def add_turn(self, key: str, lang: str, question: str, answer: str, sources: list[dict] | None = None,
                 working: str = "", quotes: str = "") -> None:
        now = datetime.now(timezone.utc)
        with self._lock:
            self._db.execute("INSERT INTO turns (user_key, at, lang, question, answer, sources, working, quotes) "
                             "VALUES (?,?,?,?,?,?,?,?)",
                             (key, now.isoformat(), lang, question[:1000], answer[:TURN_ANSWER_CHARS],
                              json.dumps(sources or [], ensure_ascii=False), working[:WORKING_CHARS] or None,
                              quotes[:WORKING_CHARS] or None))
            # keep only the last few turns per user, and nothing older than the retention period
            self._db.execute("DELETE FROM turns WHERE user_key=? AND at NOT IN (SELECT at FROM turns WHERE user_key=? "
                             "ORDER BY at DESC LIMIT ?)", (key, key, TURNS_KEPT))
            self._db.execute("DELETE FROM turns WHERE at < ?",
                             ((now - timedelta(days=TURN_RETENTION_DAYS)).isoformat(),))

    def recent_turns(self, key: str) -> list[dict]:
        """Oldest first, at most TURNS_KEPT, within the retention period."""
        cutoff = (datetime.now(timezone.utc) - timedelta(days=TURN_RETENTION_DAYS)).isoformat()
        rows = self._exec("SELECT at, lang, question, answer, sources, working, quotes FROM turns WHERE user_key=? "
                          "AND at >= ? ORDER BY at DESC LIMIT ?", (key, cutoff, TURNS_KEPT)).fetchall()
        return [{"at": r[0], "lang": r[1], "question": r[2], "answer": r[3], "sources": json.loads(r[4] or "[]"),
                 "working": r[5] or "", "quotes": r[6] or ""} for r in reversed(rows)]

    # limits
    def usage(self, key: str, day: str | None = None) -> tuple[int, int]:
        row = self._exec("SELECT voice, questions FROM usage WHERE user_key=? AND day=?", (key, day or today())).fetchone()
        return (row[0], row[1]) if row else (0, 0)

    def count(self, key: str, kind: str) -> None:
        assert kind in ("voice", "questions")
        day = today()
        self._exec(f"INSERT INTO usage (user_key, day, {kind}) VALUES (?,?,1) "
                   f"ON CONFLICT(user_key, day) DO UPDATE SET {kind}={kind}+1", (key, day))
        cutoff = (datetime.now(LAGOS).date() - timedelta(days=USAGE_RETENTION_DAYS)).isoformat()
        self._exec("DELETE FROM usage WHERE day < ?", (cutoff,))

    def spent_today(self) -> float:
        row = self._exec("SELECT usd FROM spend WHERE day=?", (today(),)).fetchone()
        return row[0] if row else 0.0

    def add_spend(self, usd: float) -> None:
        self._exec("INSERT INTO spend (day, usd) VALUES (?,?) ON CONFLICT(day) DO UPDATE SET usd=usd+excluded.usd",
                   (today(), usd))

    def count_api_call(self, name: str, usd: float = 0.0) -> int:
        """Count one call to a priced API today (and add its cost to the daily spend); returns today's count."""
        day = today()
        self._exec("INSERT INTO api_calls (day, name, n) VALUES (?,?,1) ON CONFLICT(day, name) DO UPDATE SET n=n+1",
                   (day, name))
        if usd:
            self.add_spend(usd)
        return self._exec("SELECT n FROM api_calls WHERE day=? AND name=?", (day, name)).fetchone()[0]


@lru_cache
def get_store() -> UserStore:
    return UserStore(get_settings().kasafi_state_db)
