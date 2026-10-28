"""Sending evidence images: upload + image message, after the text, under a timeout, switchable per user."""

import asyncio
import json

import httpx
import pytest
from pydantic import SecretStr

from app.agent.answer import Answer, Evidence
from app.config import Settings
from app.evidence import crops
from app.evidence.crops import CropRequest, send_evidence
from app.guardrails.scope import Verdict
from app.whatsapp.client import WhatsAppClient
from app.whatsapp.conversation import handle
from tests.helpers import make_settings
from tests.test_conversation_answers import consented, text


def test_send_image_uploads_then_sends_with_caption() -> None:
    seen = []

    def handler(req: httpx.Request) -> httpx.Response:
        seen.append((req.method, req.url.path))
        if req.url.path.endswith("/media"):
            body = req.content
            assert b'name="messaging_product"' in body and b"whatsapp" in body and b"image/jpeg" in body
            return httpx.Response(200, json={"id": "media-9"})
        sent = json.loads(req.content)
        assert sent["type"] == "image" and sent["image"] == {"id": "media-9", "caption": "cap"} and sent["to"] == "234"
        return httpx.Response(200, json={"messages": [{"id": "wamid"}]})

    async def go():
        c = WhatsAppClient(Settings(_env_file=None, whatsapp_token=SecretStr("t"), whatsapp_phone_number_id="111"),
                           transport=httpx.MockTransport(handler))
        try:
            await c.send_image("234", b"\xff\xd8jpeg", "cap")
        finally:
            await c.aclose()
    asyncio.run(go())
    assert seen == [("POST", "/v26.0/111/media"), ("POST", "/v26.0/111/messages")]


class FakeWA:
    def __init__(self, fail: bool = False):
        self.images, self.fail = [], fail

    async def send_image(self, to, jpeg, caption=""):
        if self.fail:
            raise httpx.ConnectError("down")
        self.images.append((to, jpeg, caption))


REQS = [CropRequest(1, "a", "Doc A", 11, "1,000.00", "2025 Approved Budget"), CropRequest(2, "b", "Doc B", 17, "2,000.00"),
        CropRequest(3, "c", "Doc C", 3, "3,000.00")]


def run_send(monkeypatch, wa, *, delay=0.0, settings=None):
    async def fake_crop(req, settings):
        await asyncio.sleep(delay)
        return f"jpeg-{req.doc_id}".encode() if req.doc_id != "b-none" else None
    monkeypatch.setattr(crops, "make_crop", fake_crop)
    return asyncio.run(send_evidence(wa, "234", REQS, "ha", settings or make_settings()))


def test_one_image_per_message_best_first_at_most_two(monkeypatch) -> None:
    wa = FakeWA()
    assert run_send(monkeypatch, wa) == 2
    assert [j for _, j, _ in wa.images] == [b"jpeg-a", b"jpeg-b"]
    assert wa.images[0][2] == "2025 Approved Budget: 1,000.00\n[1] Doc A, shafi 11"


def test_a_slow_crop_is_dropped_at_the_timeout(monkeypatch) -> None:
    wa = FakeWA()
    assert run_send(monkeypatch, wa, delay=0.2, settings=make_settings(kasafi_crop_timeout_s=0.3)) == 1


def test_a_failing_send_never_raises(monkeypatch) -> None:
    assert run_send(monkeypatch, FakeWA(fail=True)) == 0


# --- the conversation attaches crops to an answer, unless images are off --------------------------

EV = Evidence(1, "budget-2025-approved", "Sokoto State Government 2025 Approved Budget", 2025, 11, "text",
              "017200000000 Ministry for Religious Affairs | 2025 Approved Budget: 11,255,447,389.16")


def run(store, msg):
    async def fake_answer(question, lang, **kw):
        return Answer("An ware ₦11.26 biliyan [1]", True, True, [EV], exact="An ware 11,255,447,389.16 [1]")

    async def no_guard(texts, *, settings):
        return Verdict("ok", "none")
    return asyncio.run(handle(msg, None, store=store, settings=make_settings(), guard_fn=no_guard, answer_fn=fake_answer))


def test_answer_carries_its_crops_and_images_off_removes_them() -> None:
    store = consented("ha")
    outs = run(store, text("Nawa aka ware wa Ma'aikatar Addini a 2025?"))
    assert [c.figure for c in outs[0].crops] == ["11,255,447,389.16"] and outs[0].lang == "ha"
    run(store, text("kashe hotuna"))
    outs = run(store, text("Nawa aka ware wa Ma'aikatar Addini a 2025?"))
    assert outs[0].crops is None


def test_switched_off_server_wide() -> None:
    store = consented("en")

    async def fake_answer(question, lang, **kw):
        return Answer("x [1]", True, True, [EV], exact="11,255,447,389.16 [1]")

    async def no_guard(texts, *, settings):
        return Verdict("ok", "none")
    outs = asyncio.run(handle(text("How much for religious affairs in 2025?"), None, store=store,
                              settings=make_settings(kasafi_evidence_images=False), guard_fn=no_guard,
                              answer_fn=fake_answer))
    assert outs[0].crops is None
