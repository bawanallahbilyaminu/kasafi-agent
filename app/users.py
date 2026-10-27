"""Per-user state: consent, language, daily limits and the global spend tally.

Privacy: the phone number is never stored. Users are keyed by HMAC-SHA256(number) with a
server secret (KASAFI_HASH_KEY). A plain SHA-256 of a phone number can be reversed by trying
every number. Usage rows are pruned after 30 days, matching the log retention. Everything
for a user is removed by GOGE BAYANAI NA / DELETE MY DATA (app/data_rights.py).

SQLite on a Docker volume for the pilot (KASAFI_STATE_DB). It moves to Postgres with the rest
of the data model.
"""

from __future__ import annotations

import hashlib
import hmac
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

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    user_key    TEXT PRIMARY KEY,
    lang        TEXT,              -- 'ha' | 'en' | NULL (not known yet)
    lang_source TEXT,              -- 'detected' | 'chosen'
    consent_at  TEXT,              -- ISO time the user tapped OK / Na yarda; NULL = not consented
    created_at  TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS usage (
    user_key  TEXT NOT NULL,
    day       TEXT NOT NULL,
    voice     INTEGER NOT NULL DEFAULT 0,
    questions INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (user_key, day)
);
CREATE TABLE IF NOT EXISTS spend (
    day TEXT PRIMARY KEY,
    usd REAL NOT NULL DEFAULT 0
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
        self._lock = threading.Lock()

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

    def delete(self, key: str) -> None:
        with self._lock:
            self._db.execute("DELETE FROM users WHERE user_key=?", (key,))
            self._db.execute("DELETE FROM usage WHERE user_key=?", (key,))

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


@lru_cache
def get_store() -> UserStore:
    return UserStore(get_settings().kasafi_state_db)
