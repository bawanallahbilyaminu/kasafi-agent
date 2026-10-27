"""Data-subject requests (NDPA 2023): deletion via WhatsApp command.

docs/site/data-deletion.md promises that GOGE BAYANAI NA / DELETE MY DATA
deletes everything linked to the sender's number. Keep this in sync with that page.
"""

from __future__ import annotations

import logging
import re

from app.config import Settings, get_settings
from app.users import UserStore, get_store, user_key
from app.whatsapp.client import mask_phone

log = logging.getLogger(__name__)

DELETE_COMMANDS = {"goge bayanai na", "goge bayanaina", "goge bayanai", "delete my data"}
DELETED_REPLY = (
    "An goge duk bayananka daga Kasafi: saƙonninka, rubutun saƙon murya, amsoshinmu da zaɓinka na harshe.\n\n"
    "Your Kasafi data has been deleted."
)


def is_delete_command(text: str) -> bool:
    return " ".join(re.sub(r"[^\w\s]", " ", text).lower().split()) in DELETE_COMMANDS


def delete_user_data(phone: str, *, store: UserStore | None = None, settings: Settings | None = None) -> None:
    """Delete everything stored for this number: consent, language and usage counts.

    Messages, transcripts and replies aren't stored yet. When conversation storage lands,
    delete them here too.
    """
    settings = settings or get_settings()
    (store or get_store()).delete(user_key(phone, settings))
    log.info("data deletion completed for %s", mask_phone(phone))
