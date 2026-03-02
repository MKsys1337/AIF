#!/usr/bin/env python3
# Adaptive Image Format (AIF) — Showcase Image Generator
# Copyright (C) 2026 Markus Köplin
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

"""Generate synthetic test images and process them through the AIF pipeline.

Creates light-mode originals (screenshot, diagram, photo-like gradient),
runs each through the AIF pipeline, and saves both variants to docs/images/.
"""

from __future__ import annotations

import io
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# Ensure aif package is importable
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "packages" / "python" / "src"))

from aif import AIFPipeline, ColorAnalyzer, ThemeMapGenerator  # noqa: E402

OUTPUT_DIR = PROJECT_ROOT / "docs" / "images"


# ---------------------------------------------------------------------------
# Image generators
# ---------------------------------------------------------------------------


def _get_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Try to load a reasonable system font, fall back to default."""
    font_paths = [
        "/System/Library/Fonts/SFCompact.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/TTF/DejaVuSans.ttf",
    ]
    for fp in font_paths:
        if Path(fp).exists():
            try:
                return ImageFont.truetype(fp, size)
            except Exception:
                continue
    return ImageFont.load_default()


def generate_screenshot(width: int = 390, height: int = 844) -> Image.Image:
    """Generate a synthetic iOS-style screenshot (light mode)."""
    img = Image.new("RGB", (width, height), "#FFFFFF")
    draw = ImageDraw.Draw(img)

    font_sm = _get_font(13)
    font_md = _get_font(17)
    font_lg = _get_font(22)

    # --- Status bar ---
    draw.rectangle([(0, 0), (width, 44)], fill="#F8F8F8")
    draw.text((20, 14), "9:41", fill="#333333", font=font_sm)
    draw.text((width - 70, 14), "100%", fill="#333333", font=font_sm)

    # Separator
    draw.line([(0, 44), (width, 44)], fill="#D1D1D6", width=1)

    # --- Navigation title ---
    draw.text((20, 58), "Settings", fill="#000000", font=font_lg)

    # --- List cells ---
    y = 100
    cells = [
        ("Wi-Fi", "Connected", "#0066CC"),
        ("Bluetooth", "On", "#0066CC"),
        ("Notifications", "", "#333333"),
        ("Display & Brightness", "", "#333333"),
        ("General", "", "#333333"),
        ("Privacy & Security", "", "#333333"),
    ]
    for label, detail, color in cells:
        # Cell background (light gray)
        draw.rectangle([(15, y), (width - 15, y + 48)], fill="#F5F5F5")
        draw.text((30, y + 14), label, fill="#333333", font=font_md)
        if detail:
            draw.text((width - 110, y + 14), detail, fill=color, font=font_md)
        # Chevron indicator
        draw.text((width - 35, y + 14), ">", fill="#C7C7CC", font=font_md)
        y += 56

    # --- Another section ---
    y += 20
    draw.text((20, y), "Account", fill="#666666", font=font_sm)
    y += 28
    for label in ["Apple ID", "iCloud", "Media & Purchases"]:
        draw.rectangle([(15, y), (width - 15, y + 48)], fill="#F5F5F5")
        draw.text((30, y + 14), label, fill="#0066CC", font=font_md)
        draw.text((width - 35, y + 14), ">", fill="#C7C7CC", font=font_md)
        y += 56

    # --- Tab bar ---
    bar_y = height - 80
    draw.rectangle([(0, bar_y), (width, height)], fill="#F8F8F8")
    draw.line([(0, bar_y), (width, bar_y)], fill="#D1D1D6", width=1)
    tab_labels = ["Home", "Search", "Settings"]
    tab_w = width // len(tab_labels)
    for i, tab in enumerate(tab_labels):
        tx = i * tab_w + tab_w // 2 - 20
        c = "#0066CC" if tab == "Settings" else "#999999"
        draw.text((tx, bar_y + 16), tab, fill=c, font=font_sm)

    return img


def generate_diagram(width: int = 600, height: int = 400) -> Image.Image:
    """Generate a synthetic bar chart (light mode)."""
    img = Image.new("RGB", (width, height), "#FFFFFF")
    draw = ImageDraw.Draw(img)

    font_sm = _get_font(13)
    font_md = _get_font(16)
    font_lg = _get_font(20)

    # Title
    draw.text((width // 2 - 100, 20), "Quarterly Revenue", fill="#333333", font=font_lg)

    # Chart area
    left, right, top, bottom = 80, width - 40, 70, height - 60

    # Y-axis
    draw.line([(left, top), (left, bottom)], fill="#333333", width=2)
    # X-axis
    draw.line([(left, bottom), (right, bottom)], fill="#333333", width=2)

    # Grid lines
    for i in range(5):
        gy = bottom - int((bottom - top) * i / 4)
        draw.line([(left, gy), (right, gy)], fill="#E0E0E0", width=1)
        draw.text((20, gy - 8), f"${i * 25}k", fill="#666666", font=font_sm)

    # Bars
    bars = [
        ("Q1", 0.6, "#E74C3C"),   # Red
        ("Q2", 0.75, "#27AE60"),   # Green
        ("Q3", 0.85, "#3498DB"),   # Blue
        ("Q4", 0.95, "#F39C12"),   # Orange
    ]
    bar_count = len(bars)
    available_w = right - left - 40
    bar_w = available_w // (bar_count * 2)
    gap = bar_w

    for i, (label, pct, color) in enumerate(bars):
        bx = left + 20 + i * (bar_w + gap)
        bar_h = int((bottom - top) * pct)
        by = bottom - bar_h
        draw.rectangle([(bx, by), (bx + bar_w, bottom)], fill=color)
        draw.text(
            (bx + bar_w // 2 - 8, bottom + 10), label, fill="#333333", font=font_md
        )

    return img


def generate_photo(width: int = 400, height: int = 300) -> Image.Image:
    """Generate a colorful gradient image simulating a landscape photo."""
    arr = np.zeros((height, width, 3), dtype=np.uint8)

    for y in range(height):
        t = y / height
        if t < 0.5:
            # Sky: blue gradient
            s = t / 0.5
            r = int(100 + 55 * s)
            g = int(150 + 50 * s)
            b = int(230 - 30 * s)
        else:
            # Ground: green-to-brown gradient
            s = (t - 0.5) / 0.5
            r = int(80 + 100 * s)
            g = int(160 - 60 * s)
            b = int(60 + 20 * s)
        arr[y, :] = [r, g, b]

    # Add a warm "sun" glow in the upper-right
    cy, cx, radius = 60, width - 80, 50
    yy, xx = np.ogrid[:height, :width]
    dist = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
    sun_mask = np.clip(1 - dist / radius, 0, 1)
    arr[:, :, 0] = np.clip(arr[:, :, 0] + (sun_mask * 100).astype(np.uint8), 0, 255)
    arr[:, :, 1] = np.clip(arr[:, :, 1] + (sun_mask * 80).astype(np.uint8), 0, 255)

    return Image.fromarray(arr)


# ---------------------------------------------------------------------------
# Pipeline processing
# ---------------------------------------------------------------------------


def image_to_bytes(img: Image.Image, fmt: str = "png") -> bytes:
    buf = io.BytesIO()
    img.save(buf, format=fmt.upper())
    return buf.getvalue()


def dark_preview_from_pipeline(
    img: Image.Image,
) -> tuple[Image.Image, str, str, int]:
    """Run image through AIF pipeline and return (dark_preview, content_type, strategy, overhead).

    For photos (strategy=none), applies brightness(0.85) as the spec mandates.
    """
    img_bytes = image_to_bytes(img, "png")

    pipeline = AIFPipeline()
    processed_bytes, result = pipeline.process(img_bytes, "png")

    if result.transform_strategy == "none":
        # Photo fallback: apply brightness 0.85
        arr = np.array(img).astype(np.float32) * 0.85
        dark_pil = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
        return (
            dark_pil,
            result.content_type,
            result.transform_strategy,
            result.size_overhead_bytes,
        )

    # Re-run the intermediate steps to get the dark_preview numpy array
    nparr = np.frombuffer(img_bytes, np.uint8)
    bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    analyzer = ColorAnalyzer()
    color_profile = analyzer.analyze(bgr)

    theme_gen = ThemeMapGenerator()
    theme_result = theme_gen.generate(bgr, color_profile)

    dark_bgr = theme_result["dark_preview"]
    dark_rgb = cv2.cvtColor(dark_bgr, cv2.COLOR_BGR2RGB)
    dark_pil = Image.fromarray(dark_rgb)

    return (
        dark_pil,
        result.content_type,
        result.transform_strategy,
        result.size_overhead_bytes,
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    generators = {
        "screenshot": generate_screenshot,
        "diagram": generate_diagram,
        "photo": generate_photo,
    }

    print("AIF Showcase Generator")
    print("=" * 50)

    for name, gen_fn in generators.items():
        light_img = gen_fn()
        light_path = OUTPUT_DIR / f"{name}-light.png"
        light_img.save(light_path)

        dark_img, content_type, strategy, overhead = dark_preview_from_pipeline(
            light_img
        )
        dark_path = OUTPUT_DIR / f"{name}-dark.png"
        dark_img.save(dark_path)

        print(f"\n{name.upper()}")
        print(f"  Content type : {content_type}")
        print(f"  Strategy     : {strategy}")
        print(f"  XMP overhead : {overhead} bytes")
        print(f"  Light        : {light_path.relative_to(PROJECT_ROOT)}")
        print(f"  Dark         : {dark_path.relative_to(PROJECT_ROOT)}")

    print(f"\nDone — {len(generators) * 2} images written to {OUTPUT_DIR.relative_to(PROJECT_ROOT)}/")


if __name__ == "__main__":
    main()
