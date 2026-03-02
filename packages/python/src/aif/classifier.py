# Adaptive Image Format (AIF) — Image Classifier
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

"""Heuristic and ML-based image content classifier."""

from __future__ import annotations

import cv2
import numpy as np

from aif.types import ContentType


class ImageClassifierHeuristic:
    """
    Rule-based classifier used as a fallback or pre-filter.
    Reduces ML inference load by ~60%.
    """

    # Thresholds (empirically calibrated)
    SCREENSHOT_MAX_COLORS = 64  # Screenshots have few colors
    SCREENSHOT_MIN_EDGE_RATIO = 0.15  # Fraction of sharp edges
    PHOTO_MIN_COLORS = 10000  # Photos have many colors
    PHOTO_MAX_UNIFORM_AREA = 0.20  # Max fraction of uniform areas

    def classify(self, image: np.ndarray) -> tuple[ContentType, float]:
        """
        Classify an image and return (ContentType, confidence).
        A confidence < 0.7 indicates the result should be forwarded to the ML model.
        """
        height, width = image.shape[:2]

        # 1. EXIF check: camera metadata → definitely a photo
        if self._has_camera_exif(image):
            return (ContentType.PHOTO, 0.99)

        # 2. Color counting
        unique_colors = self._count_unique_colors(image, sample_size=50000)

        # 3. Uniformity analysis (large single-color areas)
        uniform_ratio = self._uniform_area_ratio(image, tolerance=5)

        # 4. Edge analysis (sharp UI edges vs. soft photo transitions)
        edge_ratio = self._edge_density(image)

        # 5. Aspect ratio (typical device resolutions)
        is_device_ratio = self._is_device_aspect_ratio(width, height)

        # Decision tree
        if unique_colors < self.SCREENSHOT_MAX_COLORS and uniform_ratio > 0.5:
            return (ContentType.SCREENSHOT, 0.92)

        if unique_colors > self.PHOTO_MIN_COLORS and edge_ratio < 0.05:
            return (ContentType.PHOTO, 0.88)

        if uniform_ratio > 0.6 and edge_ratio > self.SCREENSHOT_MIN_EDGE_RATIO:
            if is_device_ratio:
                return (ContentType.SCREENSHOT, 0.85)
            else:
                return (ContentType.DIAGRAM, 0.75)

        # Uncertain → ML model should decide
        return (ContentType.UNKNOWN, 0.0)

    def _count_unique_colors(self, image: np.ndarray, sample_size: int) -> int:
        """Count distinct colors in a pixel sample."""
        flat = image.reshape(-1, 3)
        if len(flat) > sample_size:
            indices = np.random.choice(len(flat), sample_size, replace=False)
            flat = flat[indices]
        # Quantize to 6-bit per channel (reduces JPEG artifacts)
        quantized = (flat >> 2).astype(np.uint32)
        packed = (quantized[:, 0] << 16) | (quantized[:, 1] << 8) | quantized[:, 2]
        return len(np.unique(packed))

    def _uniform_area_ratio(self, image: np.ndarray, tolerance: int) -> float:
        """
        Compute the fraction of pixels belonging to large uniform areas.
        High values are typical for screenshots (large single-color backgrounds).
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        uniform_mask = np.abs(laplacian) < tolerance
        return np.sum(uniform_mask) / uniform_mask.size

    def _edge_density(self, image: np.ndarray) -> float:
        """Fraction of edge pixels (Canny) relative to total pixels."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        return np.sum(edges > 0) / edges.size

    def _is_device_aspect_ratio(self, width: int, height: int) -> bool:
        """Check for typical device screenshot aspect ratios."""
        ratio = max(width, height) / min(width, height)
        # iPhone: 19.5:9 ≈ 2.17, Android: 20:9 ≈ 2.22, Desktop: 16:9 ≈ 1.78
        device_ratios = [2.17, 2.22, 2.0, 1.78, 1.6, 1.33]
        return any(abs(ratio - dr) < 0.1 for dr in device_ratios)

    def _has_camera_exif(self, image: np.ndarray) -> bool:
        """Check whether EXIF data indicates a camera (Make, Model, FocalLength, etc.)."""
        # Requires Pillow / exifread for real implementation.
        # OpenCV arrays do not carry EXIF — this is a placeholder that returns False
        # so the heuristic falls through to color/edge analysis.
        return False
