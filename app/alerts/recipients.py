"""How a live alert reaches a subscriber: their WhatsApp number, kept encrypted, and only for people signed up.

Everyone else stays hash-only (users are keyed by HMAC(number), which can't be turned back into a number). A
subscriber's number is encrypted with Fernet (AES-128-CBC with HMAC-SHA256) under KASAFI_ALERTS_NUMBER_KEY and
stored with the subscription (alert_subs.number_enc). It is decrypted only to send a kasafi_hazard_alert, and is
deleted with the subscription on STOP / DAINA, DELETE MY DATA, or 90 days without a message from the user. Numbers
are never logged, never sent to a model, never shown on the admin page.

Generate the key once with:
    python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
"""

from __future__ import annotations

import logging

from cryptography.fernet import Fernet, InvalidToken

log = logging.getLogger(__name__)
INACTIVE_DAYS = 90


def _fernet(settings) -> Fernet | None:
    key = getattr(settings, "kasafi_alerts_number_key", None)
    if key is None or not key.get_secret_value():
        return None
    try:
        return Fernet(key.get_secret_value().encode())
    except (ValueError, TypeError):
        log.warning("KASAFI_ALERTS_NUMBER_KEY is not a valid Fernet key")
        return None


def encrypt(number: str, settings) -> str | None:
    """The number encrypted for storage, or None when no key is set (the subscription is kept without one)."""
    f = _fernet(settings)
    digits = "".join(ch for ch in number or "" if ch.isdigit())
    if f is None or not digits:
        return None
    return f.encrypt(digits.encode()).decode()


def decrypt(token: str | None, settings) -> str | None:
    """The number to send to, or None (no token, no key, or a token from another key)."""
    f = _fernet(settings)
    if f is None or not token:
        return None
    try:
        return f.decrypt(token.encode()).decode()
    except InvalidToken:
        log.warning("an alert number could not be decrypted (key changed?)")
        return None


def live_sender(store, settings, client):
    """The send function for dispatch: decrypts the subscriber's number and sends the template; False when there
    is no number or the send fails (the reason is logged without the number)."""
    from app.alerts.dispatch import TEMPLATE

    async def send(user_key: str, lang: str, values: list[str]) -> bool:
        number = decrypt(store.alert_number(user_key), settings)
        if number is None:
            return False
        try:
            await client.send_template(number, TEMPLATE, lang, values)
            return True
        except Exception as e:       # noqa: BLE001 - one failed send never stops the others
            log.warning("alert send failed: %s", type(e).__name__)
            return False
    return send
