import hashlib
import hmac
import json

import pytest
from fastapi.testclient import TestClient
from pydantic import SecretStr

from app.config import Settings
from app.main import app
from app.whatsapp import webhook

SECRET = "test-app-secret"
VERIFY = "test-verify-token"


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch):
    s = Settings(_env_file=None, whatsapp_app_secret=SecretStr(SECRET), whatsapp_verify_token=SecretStr(VERIFY))
    monkeypatch.setattr(webhook, "get_settings", lambda: s)
    monkeypatch.setattr(webhook, "seen_ids", webhook._SeenIds())
    sent: list = []

    async def fake_reply(messages):
        sent.extend(messages)

    monkeypatch.setattr(webhook, "_reply", fake_reply)
    c = TestClient(app)
    c.sent = sent
    return c


def _payload(msg_id: str = "wamid.1", kind: str = "text") -> dict:
    msg = {"from": "0000000000", "id": msg_id, "type": kind}
    if kind == "text":
        msg["text"] = {"body": "Sannu"}
    return {"object": "whatsapp_business_account", "entry": [{"changes": [
        {"field": "messages", "value": {"messages": [msg]}}]}]}


def _post(client, payload: dict, secret: str = SECRET):
    body = json.dumps(payload).encode()
    sig = "sha256=" + hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    return client.post("/webhook", content=body,
                       headers={"x-hub-signature-256": sig, "content-type": "application/json"})


def test_verify_handshake(client) -> None:
    ok = client.get("/webhook", params={"hub.mode": "subscribe", "hub.verify_token": VERIFY, "hub.challenge": "42"})
    assert (ok.status_code, ok.text) == (200, "42")
    bad = client.get("/webhook", params={"hub.mode": "subscribe", "hub.verify_token": "nope", "hub.challenge": "42"})
    assert bad.status_code == 403


def test_signed_message_is_echoed_once(client) -> None:
    assert _post(client, _payload()).status_code == 200
    assert _post(client, _payload()).status_code == 200  # Meta retry: same id
    assert [m["id"] for m in client.sent] == ["wamid.1"]


def test_bad_signature_rejected(client) -> None:
    assert _post(client, _payload(), secret="wrong").status_code == 401
    assert client.sent == []


def test_status_updates_are_acknowledged_without_reply(client) -> None:
    status_only = {"entry": [{"changes": [{"field": "messages", "value": {"statuses": [{"id": "x"}]}}]}]}
    assert _post(client, status_only).status_code == 200
    assert client.sent == []


def test_echo_text_by_type() -> None:
    assert "Sannu" in webhook.echo_reply({"type": "text", "text": {"body": "Sannu"}})
    assert webhook.echo_reply({"type": "audio"}) == webhook.ECHO_VOICE
    assert webhook.echo_reply({"type": "sticker"}) == webhook.ECHO_OTHER


def test_empty_secrets_count_as_unconfigured(monkeypatch: pytest.MonkeyPatch) -> None:
    # An empty key would let anyone forge a valid HMAC, so empty must mean "reject".
    s = Settings(_env_file=None, whatsapp_app_secret=SecretStr(""), whatsapp_verify_token=SecretStr(""))
    monkeypatch.setattr(webhook, "get_settings", lambda: s)
    c = TestClient(app)
    assert c.get("/webhook", params={"hub.mode": "subscribe", "hub.verify_token": "", "hub.challenge": "1"}).status_code == 503
    assert _post(c, _payload(), secret="").status_code == 503


def test_access_log_redacts_query_string() -> None:
    import logging

    from app.main import _RedactQuery

    rec = logging.LogRecord("uvicorn.access", logging.INFO, "", 0, '%s - "%s %s HTTP/%s" %d',
                            ("1.2.3.4", "GET", "/webhook?hub.verify_token=secret", "1.1", 200), None)
    _RedactQuery().filter(rec)
    assert "secret" not in rec.getMessage() and "/webhook?[redacted]" in rec.getMessage()
