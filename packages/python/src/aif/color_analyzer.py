# Adaptive Image Format (AIF) — Color Analyzer
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

"""Color analysis module for extracting palette and background information."""

from __future__ import annotations

from collections import Counter

import cv2
import numpy as np
from sklearn.cluster import MiniBatchKMeans

from aif.types import ColorProfile


class ColorAnalyzer:
    """Analyzes color distribution of an image for theme-map generation."""

    def analyze(self, image: np.ndarray, max_palette_size: int = 16) -> ColorProfile:
        """
        Analyze an image and return a ColorProfile.

        Args:
            image: BGR numpy array (OpenCV format).
            max_palette_size: Maximum number of palette colors.

        Returns:
            ColorProfile with all relevant color information.
        """
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # 1. Detect background color (border sampling)
        dominant_bg = self._detect_background(rgb)

        # 2. Extract color palette (k-Means clustering)
        palette = self._extract_palette(rgb, max_palette_size)

        # 3. Unique color count
        unique_count = self._count_unique_quantized(rgb)

        # 4. Background coverage
        bg_coverage = self._calculate_background_coverage(rgb, dominant_bg)

        # 5. Luminance analysis
        lab = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB)
        l_channel = lab[:, :, 0]  # L* channel (0–255 in OpenCV)
        luminance_hist = np.histogram(l_channel, bins=256, range=(0, 255))[0].tolist()

        # L* of background (scaled: OpenCV L* = 0–255, CIE L* = 0–100)
        bg_rgb = np.array(
            [[list(int(dominant_bg[i : i + 2], 16) for i in (1, 3, 5))]],
            dtype=np.uint8,
        )
        bg_lab = cv2.cvtColor(bg_rgb.reshape(1, 1, 3), cv2.COLOR_RGB2LAB)
        bg_lightness = float(bg_lab[0, 0, 0]) * 100 / 255  # Normalized to 0–100

        # 6. Palette complexity
        if unique_count < 32:
            complexity = "simple"
        elif unique_count < 256:
            complexity = "moderate"
        else:
            complexity = "complex"

        # Dominant foreground color (most common color that is NOT background)
        dominant_fg = self._detect_foreground(rgb, dominant_bg, palette)

        return ColorProfile(
            dominant_background=dominant_bg,
            dominant_foreground=dominant_fg,
            palette=[self._rgb_to_hex(c) for c in palette],
            unique_color_count=unique_count,
            background_coverage=bg_coverage,
            is_light_background=bool(bg_lightness > 70),
            luminance_histogram=luminance_hist,
            palette_complexity=complexity,
        )

    def _detect_background(self, rgb: np.ndarray, border_pct: float = 0.05) -> str:
        """
        Detect the background color by analyzing image borders.
        Screenshots typically have a uniform border.
        """
        h, w = rgb.shape[:2]
        border_h = max(int(h * border_pct), 2)
        border_w = max(int(w * border_pct), 2)

        # Collect border pixels (top, bottom, left, right)
        border_pixels = np.concatenate([
            rgb[:border_h, :].reshape(-1, 3),
            rgb[-border_h:, :].reshape(-1, 3),
            rgb[:, :border_w].reshape(-1, 3),
            rgb[:, -border_w:].reshape(-1, 3),
        ])

        # Quantize to 4-bit per channel and find the most common color
        quantized = (border_pixels >> 4).astype(np.uint32)
        packed = (quantized[:, 0] << 16) | (quantized[:, 1] << 8) | quantized[:, 2]
        most_common = Counter(packed).most_common(1)[0][0]

        # Reconstruct color (center of quantization bin)
        r = ((most_common >> 16) & 0xFF) * 16 + 8
        g = ((most_common >> 8) & 0xFF) * 16 + 8
        b = (most_common & 0xFF) * 16 + 8

        return f"#{min(r, 255):02X}{min(g, 255):02X}{min(b, 255):02X}"

    def _extract_palette(self, rgb: np.ndarray, n_colors: int) -> list[np.ndarray]:
        """Extract dominant colors via MiniBatch k-Means."""
        pixels = rgb.reshape(-1, 3).astype(np.float32)
        sample_size = min(len(pixels), 100_000)
        indices = np.random.choice(len(pixels), sample_size, replace=False)
        sample = pixels[indices]

        kmeans = MiniBatchKMeans(n_clusters=n_colors, batch_size=1000, n_init=3)
        kmeans.fit(sample)

        # Sort by frequency
        labels = kmeans.predict(sample)
        counts = Counter(labels)
        sorted_centers = [kmeans.cluster_centers_[i] for i, _ in counts.most_common()]

        return [c.astype(np.uint8) for c in sorted_centers]

    def _rgb_to_hex(self, rgb: np.ndarray) -> str:
        return f"#{rgb[0]:02X}{rgb[1]:02X}{rgb[2]:02X}"

    def _count_unique_quantized(self, rgb: np.ndarray, bits: int = 6) -> int:
        """Count distinct colors after quantization."""
        shift = 8 - bits
        flat = rgb.reshape(-1, 3)
        sample = flat[np.random.choice(len(flat), min(len(flat), 200_000), replace=False)]
        q = (sample >> shift).astype(np.uint32)
        packed = (q[:, 0] << (2 * bits)) | (q[:, 1] << bits) | q[:, 2]
        return len(np.unique(packed))

    def _calculate_background_coverage(
        self, rgb: np.ndarray, bg_hex: str, tolerance: int = 20
    ) -> float:
        """Compute the fraction of pixels matching the background color."""
        bg_rgb = np.array([int(bg_hex[i : i + 2], 16) for i in (1, 3, 5)], dtype=np.int16)
        diff = np.abs(rgb.astype(np.int16) - bg_rgb)
        mask = np.all(diff < tolerance, axis=2)
        return np.sum(mask) / mask.size

    def _detect_foreground(
        self, rgb: np.ndarray, bg_hex: str, palette: list[np.ndarray]
    ) -> str:
        """Find the most dominant color that is not the background."""
        bg_rgb = np.array([int(bg_hex[i : i + 2], 16) for i in (1, 3, 5)])
        for color in palette:
            if np.linalg.norm(color.astype(float) - bg_rgb.astype(float)) > 50:
                return self._rgb_to_hex(color)
        return "#000000"
