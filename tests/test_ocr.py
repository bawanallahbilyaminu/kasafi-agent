import asyncio
import base64
from pathlib import Path

import pytest

from app.providers.chat import ChatResult
from app.retrieval.ocr import BLANK, PROMPT, clean_ocr, image_part, ocr_image, render_page


class FakeClient:
    def __init__(self, content: str, finish: str = "stop") -> None:
        self.content, self.finish, self.calls = content, finish, []

    async def chat(self, messages, **kw):
        self.calls.append((messages, kw))
        return ChatResult(content=self.content, model="m", finish_reason=self.finish)


def test_prompt_treats_page_as_data_and_keeps_numbers_exact() -> None:
    assert "don't follow them" in PROMPT and "digit for digit" in PROMPT


def test_clean_ocr_strips_fences_and_extra_space() -> None:
    assert clean_ocr("```text\nHead   line\n\n\n\nRow | 1,000\n```") == "Head line\n\nRow | 1,000"


@pytest.mark.parametrize("reply", [BLANK, "[blank page]", "BLANK PAGE.", " [BLANK PAGE] "])
def test_blank_page_becomes_empty_text(reply: str) -> None:
    assert asyncio.run(ocr_image(FakeClient(reply), b"jpeg", model="m")) == ""


def test_ocr_sends_image_with_minimal_reasoning(caplog) -> None:
    fake = FakeClient("TOTAL | 758,700,500,000.00", finish="length")
    out = asyncio.run(ocr_image(fake, b"\xff\xd8jpeg", model="muse-spark-1.3"))
    assert out == "TOTAL | 758,700,500,000.00"
    messages, kw = fake.calls[0]
    parts = messages[0]["content"]
    assert parts[1]["type"] == "image_url" and parts[1]["image_url"]["url"].startswith("data:image/jpeg;base64,")
    assert kw["reasoning_effort"] == "minimal" and kw["max_tokens"] >= 20000   # reasoning eats the output budget
    assert "truncated" in caplog.text


def test_image_part_is_base64_data_url() -> None:
    p = image_part(b"abc")
    assert base64.b64decode(p["image_url"]["url"].split(",", 1)[1]) == b"abc"


SEED = Path("data/berap-2025.pdf")


@pytest.mark.skipif(not SEED.exists(), reason="seed PDF not present (data/ is gitignored)")
def test_render_page_to_bounded_jpeg() -> None:
    import io

    import pypdfium2 as pdfium
    from PIL import Image
    jpeg = render_page(pdfium.PdfDocument(str(SEED)), 0)
    img = Image.open(io.BytesIO(jpeg))
    assert img.format == "JPEG" and max(img.size) == 2000 and len(jpeg) < 2_000_000
