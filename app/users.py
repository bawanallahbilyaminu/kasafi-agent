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
    pending_clarify  TEXT          -- JSON options while Kasafi asks which reading of a question was meant
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
"""


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
        if "working" not in {row[1] for row in self._db.execute("PRAGMA table_info(turns)")}:
            self._db.execute("ALTER TABLE turns ADD COLUMN working TEXT")     # "nuna lissafi" / "show working"

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

    def clear_pending(self, key: str) -> None:
        self._exec("UPDATE users SET pending_question=NULL, pending_english=NULL, pending_at=NULL, "
                   "pending_options=NULL WHERE user_key=?",
                   (key,))

    def delete(self, key: str) -> None:
        with self._lock:
            self._db.execute("DELETE FROM users WHERE user_key=?", (key,))
            self._db.execute("DELETE FROM usage WHERE user_key=?", (key,))
            self._db.execute("DELETE FROM turns WHERE user_key=?", (key,))

    # conversation context for follow-ups
    def add_turn(self, key: str, lang: str, question: str, answer: str, sources: list[dict] | None = None,
                 working: str = "") -> None:
        now = datetime.now(timezone.utc)
        with self._lock:
            self._db.execute("INSERT INTO turns (user_key, at, lang, question, answer, sources, working) "
                             "VALUES (?,?,?,?,?,?,?)",
                             (key, now.isoformat(), lang, question[:1000], answer[:TURN_ANSWER_CHARS],
                              json.dumps(sources or [], ensure_ascii=False), working[:WORKING_CHARS] or None))
            # keep only the last few turns per user, and nothing older than the retention period
            self._db.execute("DELETE FROM turns WHERE user_key=? AND at NOT IN (SELECT at FROM turns WHERE user_key=? "
                             "ORDER BY at DESC LIMIT ?)", (key, key, TURNS_KEPT))
            self._db.execute("DELETE FROM turns WHERE at < ?",
                             ((now - timedelta(days=TURN_RETENTION_DAYS)).isoformat(),))

    def recent_turns(self, key: str) -> list[dict]:
        """Oldest first, at most TURNS_KEPT, within the retention period."""
        cutoff = (datetime.now(timezone.utc) - timedelta(days=TURN_RETENTION_DAYS)).isoformat()
        rows = self._exec("SELECT at, lang, question, answer, sources, working FROM turns WHERE user_key=? AND "
                          "at >= ? ORDER BY at DESC LIMIT ?", (key, cutoff, TURNS_KEPT)).fetchall()
        return [{"at": r[0], "lang": r[1], "question": r[2], "answer": r[3], "sources": json.loads(r[4] or "[]"),
                 "working": r[5] or ""} for r in reversed(rows)]

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
