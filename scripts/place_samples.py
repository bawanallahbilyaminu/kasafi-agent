"""Place history samples for the private test pins (data/private/place_pins.yaml, outside git): the plot outline
drawn on the chip for every pin, and for the pins named with --answers the full farmer answer in Hausa and
English with the chart and the map, saved under data/samples/place/ (committed: no coordinates are printed on an
image or in a file name; the LGA only).

Usage: uv run python scripts/place_samples.py [--answers wurno,kwalkwalawa,goronyo] [--fresh] [--outlines-only]
"""

from __future__ import annotations

import argparse
import asyncio
import io
import logging
import os
import re
import sys
import time
from datetime import date
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.stdout.reconfigure(encoding="utf-8")

import psycopg  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

from app.config import get_settings  # noqa: E402
from app.place import answer as A  # noqa: E402
from app.place import images as I  # noqa: E402
from app.place import outline as O  # noqa: E402
from app.place.history import cell_id  # noqa: E402
from app.sources.lga_names import pcode  # noqa: E402

OUT = ROOT / "data/samples/place"


def slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")[:40]


def lga_of(pin: dict) -> str:
    m = re.search(r"\(([^()]+?)\s+LGA\)", pin.get("notes", ""))
    return m.group(1) if m else ""


def outline_image(chip: O.Chip, o: O.Outline, lon: float, lat: float, label: str) -> bytes:
    img = Image.open(io.BytesIO(chip.png())).convert("RGB")
    d = ImageDraw.Draw(img)
    scale = img.width / chip.rgb.shape[1]
    ring = [((x - chip.transform.c) / chip.transform.a * scale, (y - chip.transform.f) / chip.transform.e * scale)
            for x, y in o.geometry["coordinates"][0]]
    d.line(ring + [ring[0]], fill=(255, 213, 0), width=4 if o.is_plot else 2)
    px, py = O.pin_pixel(chip, lon, lat)
    d.ellipse([px - 7, py - 7, px + 7, py + 7], fill=(214, 45, 32), outline=(255, 255, 255), width=2)
    d.rectangle([0, img.height - 34, img.width, img.height], fill=(255, 255, 255))
    d.text((8, img.height - 28), f"{label} · Sentinel-2 {chip.day} · outline: {o.method} "
                                 f"{o.area_ha} ha{(' (' + o.note + ')') if o.note else ''}", fill=(31, 31, 29))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85)
    return buf.getvalue()


async def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--answers", default="wurno,kwalkwalawa,goronyo_dam")
    ap.add_argument("--fresh", action="store_true", help="clear the pins' caches first (a first request)")
    ap.add_argument("--outlines-only", action="store_true")
    ap.add_argument("--file", default=str(ROOT / "data/private/place_pins.yaml"))
    a = ap.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s: %(message)s")
    for noisy in ("httpx", "httpcore", "rasterio", "matplotlib", "PIL"):
        logging.getLogger(noisy).setLevel(logging.WARNING)
    pins = yaml.safe_load(open(a.file, encoding="utf-8"))
    pins = pins if isinstance(pins, list) else pins.get("pins", [])
    OUT.mkdir(parents=True, exist_ok=True)
    settings = get_settings()
    today = date.today()
    want = [w.strip() for w in a.answers.split(",") if w.strip()]
    with psycopg.connect(settings.db_url()) as conn:
        for p in pins:
            lat, lon, name = float(p["lat"]), float(p["lon"]), p["name"]
            s, lga = slug(name), lga_of(p)
            cell = cell_id(lat, lon)
            if a.fresh:
                conn.execute("DELETE FROM plot_outline_cache WHERE cell = %s", (cell,))
                conn.execute("DELETE FROM sat_cache WHERE cell = %s", (cell,))
                conn.commit()
            t0 = time.perf_counter()
            chip = O.true_colour(lon, lat, today)
            o = await O.plot_outline(conn, settings, lat, lon, today=today, chip=chip)
            print(f"\n=== {name} ({lga} LGA): outline {o.method} {o.area_ha} ha {o.note} "
                  f"[{time.perf_counter() - t0:.1f}s{', cached' if o.from_cache else ''}]")
            if chip is not None:
                (OUT / f"outline_{s}.jpg").write_bytes(outline_image(chip, o, lon, lat, f"{lga} LGA"))
            if a.outlines_only or not any(w in s for w in want):
                continue
            place = {"lat": lat, "lon": lon, "lga": lga, "lga_pcode": pcode(lga) or ""}
            for lang in ("ha", "en"):
                q = "Yaya tarihin wannan gona a hotunan tauraron ɗan adam? Ruwa ya taɓa rufe ta?" if lang == "ha" else \
                    "What is the history of this farm in the satellite images? Was it ever under water?"
                t1 = time.perf_counter()
                pa = await A.place_answer(conn, settings, q, "", lang, place, today,
                                          notify=lambda m: print("  [progress]", m) or asyncio.sleep(0))
                print(f"\n--- {lang} answer ({time.perf_counter() - t1:.1f}s; {pa.timing}) ---\n{pa.text}\n")
                print(f"--- {lang} show working ---\n{pa.working}\n")
                for spec in pa.specs:
                    t2 = time.perf_counter()
                    img = I.draw_place(conn, {**spec, "water": True}, lang, today)
                    if img is None:
                        print("  image failed:", spec["kind"])
                        continue
                    path = OUT / f"{spec['kind']}_{s}_{lang}.jpg"
                    path.write_bytes(img.jpeg)
                    print(f"  {path.name}: {len(img.jpeg) // 1024} KB in {time.perf_counter() - t2:.1f}s — {img.caption}")


if __name__ == "__main__":
    asyncio.run(main())
    sys.stdout.flush()
    os._exit(0)
