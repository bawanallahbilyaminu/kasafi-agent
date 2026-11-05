"""Maintenance that must run whatever optional features are on (follow-up review, §5.1): the daily SQLite backup of
the user store had lived inside the hazard fetch loop, which only starts with KASAFI_HAZARD_FETCH=true and a
database, so a backup folder alone did nothing. Its own thread now, started at boot whenever KASAFI_BACKUP_DIR is
set."""

from __future__ import annotations

import logging
import threading
import time
from datetime import datetime, timezone

log = logging.getLogger(__name__)

CHECK_EVERY_S = 600
SWEEP_EVERY_S = 60
_backup_day: list[str] = []
_started: list[threading.Thread] = []
_swept: list[threading.Thread] = []


def daily_store_backup(settings, today: str | None = None) -> bool:
    """One consistent sqlite copy of the user store a day into KASAFI_BACKUP_DIR (external review, finding 19);
    False when none is due or no folder is set."""
    if not settings.kasafi_backup_dir:
        return False
    day = today or datetime.now(timezone.utc).date().isoformat()
    if _backup_day and _backup_day[-1] == day:
        return False
    from app.users import get_store
    path = get_store().backup_to(settings.kasafi_backup_dir)
    _backup_day[:] = [day]
    log.info("store backup written: %s", path.name)
    return True


def sweep_held() -> dict[str, int]:
    """Deletes what is held in memory for a limited time once its time is up (5 Nov 2026): a name the user stated
    (1 hour after their last message), a location, plot shape or waiting question (30 minutes), a first message kept
    before consent (30 minutes). Reads check the time too, but only for the user who writes: without this, the data
    of a user who never came back stayed in memory, unusable but not deleted. Returns how many of each went."""
    from app.geo.location import memory
    from app.privacy import names
    from app.whatsapp.conversation import sweep_first_messages
    return {"names": names.sweep(), "locations": memory.sweep(), "first_messages": sweep_first_messages()}


def start_held_sweep(every_s: float = SWEEP_EVERY_S) -> threading.Thread:
    """The sweep in its own daemon thread, whatever else is switched on. Started once per process."""
    if _swept and _swept[0].is_alive():
        return _swept[0]

    def loop() -> None:
        while True:
            try:
                sweep_held()
            except Exception as e:      # noqa: BLE001 - the loop must outlive any one failure
                log.warning("held-data sweep failed: %s", type(e).__name__)
            time.sleep(every_s)
    th = threading.Thread(target=loop, name="held-data-sweep", daemon=True)
    th.start()
    _swept[:] = [th]
    log.info("held-data sweep started (every %.0f s)", every_s)
    return th


def start_maintenance(settings, every_s: float = CHECK_EVERY_S) -> threading.Thread | None:
    """The maintenance loop in its own daemon thread: the daily backup, checked every `every_s`. None when there is
    nothing to maintain (no backup folder). Started once per process."""
    if not settings.kasafi_backup_dir:
        log.info("maintenance: no KASAFI_BACKUP_DIR, no daily store backup")
        return None
    if _started and _started[0].is_alive():
        return _started[0]

    def loop() -> None:
        while True:
            try:
                daily_store_backup(settings)
            except Exception as e:      # noqa: BLE001 - the loop must outlive any one failure
                log.warning("store backup failed: %s", type(e).__name__)
            time.sleep(every_s)
    th = threading.Thread(target=loop, name="maintenance", daemon=True)
    th.start()
    _started[:] = [th]
    log.info("maintenance scheduler started (daily store backup)")
    return th
