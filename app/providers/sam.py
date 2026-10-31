"""Segment Anything Model 3.1 on the Meta Model API (dev.meta.ai/docs/sam/segmenting.md).

One streaming Responses API call on `sam-3.1` carries a prompt and an image. The prompt is either a short
noun phrase ("table") or box/point prompts in SAM's token grammar:
    <0f>1<|box;x1=..;y1=..;x2=..;y2=..;w=<image width>;h=<image height>|>
The output streams as `response.output_text.delta` events: one line per frame, one record per object:
    <0f>1<|box;x1=..;y1=..;x2=..;y2=..;w=..;h=..|><|mask;...|>
We only need the boxes. Zero matches is a normal, empty result.
"""

from __future__ import annotations

import base64
import json
import re
from dataclasses import dataclass

import httpx

from app.config import Settings

_BOX = re.compile(r"(\d+)<\|box;x1=(\d+);y1=(\d+);x2=(\d+);y2=(\d+);w=(\d+);h=(\d+)")


class SamError(RuntimeError):
    pass


@dataclass(frozen=True)
class Box:
    obj: int
    x1: int
    y1: int
    x2: int
    y2: int

    @property
    def area(self) -> int:
        return max(0, self.x2 - self.x1) * max(0, self.y2 - self.y1)


def box_prompt(x1: int, y1: int, x2: int, y2: int, w: int, h: int, obj: int = 1) -> str:
    """A box prompt in image pixels; x2/y2 inclusive, w/h the image's own size."""
    x1, y1 = max(0, min(x1, w - 1)), max(0, min(y1, h - 1))
    x2, y2 = max(x1, min(x2, w - 1)), max(y1, min(y2, h - 1))
    return f"<0f>{obj}<|box;x1={x1};y1={y1};x2={x2};y2={y2};w={w};h={h}|>"


def parse_boxes(text: str) -> list[Box]:
    return [Box(int(m[0]), int(m[1]), int(m[2]), int(m[3]), int(m[4])) for m in _BOX.findall(text)]


_MASK = re.compile(r"<\|mask;x=\d+;y=\d+(?:;c=[0-9.]+)?;data=(\d+),(\d+),([!~][^|]*)\|>")


@dataclass(frozen=True)
class Segment:
    box: Box
    mask: object | None          # a numpy bool array (rows x columns) covering the box (its own size), or None
    confidence: float | None = None

    def on_frame(self, w: int, h: int):
        """The mask placed on the full image (w x h), as a bool array, or None."""
        import numpy as np
        if self.mask is None:
            return None
        full = np.zeros((h, w), dtype=bool)
        mh, mw = self.mask.shape
        y1, x1 = max(0, self.box.y1), max(0, self.box.x1)
        part = self.mask[: max(0, min(mh, h - y1)), : max(0, min(mw, w - x1))]
        full[y1:y1 + part.shape[0], x1:x1 + part.shape[1]] = part
        return full


def parse_segments(text: str) -> list[Segment]:
    """Every record's box with its mask decoded (Meta's own parser package, meta_sam_parser): a mask is a
    row-major raster of the box's height x width (seen on the wire, Oct 31 2026: a box x1=371..573, y1=250..493
    came with a 244 x 203 mask), placed on the image with Segment.on_frame."""
    import numpy as np
    from meta_sam_parser import InvalidSegmentationMaskError, SegmentationMask, decode_mask_to_raster
    out = []
    masks = _MASK.findall(text)
    for i, box in enumerate(parse_boxes(text)):
        mask = None
        if i < len(masks):
            h, w, payload = int(masks[i][0]), int(masks[i][1]), masks[i][2]
            try:
                raw = decode_mask_to_raster(SegmentationMask("one_bit" if payload[0] == "!" else "lossless",
                                                             payload, w, h))
                mask = np.frombuffer(raw, dtype="uint8").reshape(h, w).astype(bool)
            except (InvalidSegmentationMaskError, ValueError):
                mask = None
        out.append(Segment(box, mask))
    return out


def point_prompt(x: int, y: int, w: int, h: int, obj: int = 1) -> str:
    """A positive point prompt in image pixels (the plot outline: 'the field at this pin')."""
    return f"<0f>{obj}<|point;x={max(0, min(x, w - 1))};y={max(0, min(y, h - 1))};w={w};h={h}|>"


async def segment(jpeg: bytes, prompt: str, *, settings: Settings, timeout: float = 20.0,
                  transport: httpx.AsyncBaseTransport | None = None) -> list[Box]:
    return parse_boxes(await raw_output(jpeg, prompt, settings=settings, timeout=timeout, transport=transport))


async def segment_masks(jpeg: bytes, prompt: str, *, settings: Settings, timeout: float = 20.0,
                        transport: httpx.AsyncBaseTransport | None = None) -> list[Segment]:
    return parse_segments(await raw_output(jpeg, prompt, settings=settings, timeout=timeout, transport=transport))


async def raw_output(jpeg: bytes, prompt: str, *, settings: Settings, timeout: float = 20.0,
                     transport: httpx.AsyncBaseTransport | None = None) -> str:
    """One SAM 3.1 call's streamed output text (the records: boxes and masks)."""
    if settings.meta_api_key is None:
        raise SamError("META_API_KEY is not set")
    body = {"model": settings.sam_model, "stream": True, "input": [{"type": "message", "role": "user", "content": [
        {"type": "input_text", "text": prompt},
        {"type": "input_image", "image_url": "data:image/jpeg;base64," + base64.b64encode(jpeg).decode("ascii")}]}]}
    parts: list[str] = []
    async with httpx.AsyncClient(timeout=timeout, transport=transport) as http:
        async with http.stream("POST", settings.meta_base_url.rstrip("/") + "/responses", json=body,
                               headers={"Authorization": f"Bearer {settings.meta_api_key.get_secret_value()}"}) as resp:
            if resp.status_code != 200:
                raise SamError(f"HTTP {resp.status_code}")
            async for line in resp.aiter_lines():
                if not line.startswith("data: "):
                    continue
                try:
                    event = json.loads(line[6:])
                except ValueError:
                    continue
                kind = event.get("type")
                if kind == "response.output_text.delta":
                    parts.append(str(event.get("delta", "")))
                elif kind in ("error", "response.failed"):
                    raise SamError(f"{kind}")
                elif kind == "response.completed":
                    break
    return "".join(parts)
