# Adaptive Image Format (AIF) — Test Fixtures
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

import io

import cv2
import numpy as np
import pytest
from PIL import Image


@pytest.fixture
def white_screenshot() -> np.ndarray:
    """A synthetic 200x400 'screenshot' — mostly white with some dark text-like pixels."""
    img = np.full((400, 200, 3), 255, dtype=np.uint8)  # White background (BGR)
    # Add a dark rectangle to simulate text
    img[50:70, 20:180] = [51, 51, 51]  # Dark gray text
    # Add a blue link
    img[100:110, 20:120] = [204, 102, 0]  # Blue in BGR
    return img


@pytest.fixture
def dark_screenshot() -> np.ndarray:
    """A synthetic 200x400 screenshot with dark background."""
    img = np.full((400, 200, 3), 30, dtype=np.uint8)  # Dark background
    img[50:70, 20:180] = [224, 224, 224]  # Light text
    return img


@pytest.fixture
def colorful_photo() -> np.ndarray:
    """A synthetic 300x300 'photo' with many random colors."""
    rng = np.random.RandomState(42)
    return rng.randint(0, 256, (300, 300, 3), dtype=np.uint8)


@pytest.fixture
def simple_diagram() -> np.ndarray:
    """A synthetic 200x200 diagram — white background with few colored elements."""
    img = np.full((200, 200, 3), 255, dtype=np.uint8)
    # Red bar
    img[20:40, 20:100] = [0, 0, 200]
    # Green bar
    img[50:70, 20:150] = [0, 180, 0]
    # Blue bar
    img[80:100, 20:80] = [200, 0, 0]
    return img


@pytest.fixture
def white_screenshot_jpeg_bytes(white_screenshot) -> bytes:
    """JPEG-encoded bytes of the white screenshot."""
    rgb = cv2.cvtColor(white_screenshot, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(rgb)
    buf = io.BytesIO()
    pil_img.save(buf, "JPEG", quality=95)
    return buf.getvalue()


@pytest.fixture
def white_screenshot_png_bytes(white_screenshot) -> bytes:
    """PNG-encoded bytes of the white screenshot."""
    rgb = cv2.cvtColor(white_screenshot, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(rgb)
    buf = io.BytesIO()
    pil_img.save(buf, "PNG")
    return buf.getvalue()
