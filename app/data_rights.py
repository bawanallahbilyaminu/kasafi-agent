"""Data-subject requests (NDPA 2023): deletion via WhatsApp command.

The /data-deletion page promises that GOGE BAYANAI / DELETE MY DATA deletes
everything linked to the sender's number. Keep this in sync with that page.
"""

import logging
import re

from app.whatsapp.client import mask_phone

log = logging.getLogger(__name__)

DELETE_COMMANDS = {"goge bayanai", "goge bayanaina", "delete my data"}
DELETED_REPLY = (
    "An goge duk bayananka daga Kasafi: saƙonninka, rubutun saƙon murya da amsoshinmu.\n"
    "Your Kasafi data has been deleted."
)


def is_delete_command(text: str) -> bool:
    return " ".join(re.sub(r"[^\w\s]", " ", text).lower().split()) in DELETE_COMMANDS


def delete_user_data(phone: str) -> None:
    # Echo stage: nothing is stored per user yet. When conversation storage lands,
    # delete messages, transcripts, replies and evidence images for `phone` here.
    log.info("data deletion completed for %s", mask_phone(phone))
