# Adaptive Image Format (AIF) — Core Types
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

"""Core types for the AIF pipeline: enums, dataclasses, and type definitions."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ContentType(Enum):
    """Classification of image content for adaptive rendering decisions."""

    PHOTO = 0x01  # Camera photo — not a transformation candidate
    SCREENSHOT = 0x02  # UI screenshot — primary transformation candidate
    DIAGRAM = 0x03  # Charts, graphs, infographics
    TEXT_POST = 0x04  # Screenshot of a post from another platform
    MEME = 0x05  # Text overlay on an image
    ICON = 0x06  # Logo, icon, vector-like graphic
    MIXED = 0x07  # Mixed content
    UNKNOWN = 0xFF  # Unclassifiable


class TransformStrategy(Enum):
    """Strategy used to generate the dark-mode adaptation."""

    CLUT = "clut"  # Color Lookup Table (< 64 colors)
    LUMINANCE_MAP = "luminance_map"  # L* channel transformation only
    FULL_LAB_MAP = "full_lab_map"  # Full L*a*b* transformation
    NONE = "none"  # No transformation (photos, already-dark images)


@dataclass
class ColorProfile:
    """Result of color analysis for an image."""

    dominant_background: str  # Hex color, e.g. "#FFFFFF"
    dominant_foreground: str  # Hex color, e.g. "#333333"
    palette: list[str]  # Top-N colors as hex strings
    unique_color_count: int  # Number of distinct colors
    background_coverage: float  # 0.0–1.0, fraction covered by background color
    is_light_background: bool  # True if L* > 70 in LAB color space
    luminance_histogram: list[int]  # 256 bins, L* distribution
    palette_complexity: str  # "simple" (<32), "moderate" (32–256), "complex" (>256)


@dataclass
class AIFResult:
    """Result of the full AIF processing pipeline."""

    processed: bool
    content_type: str
    classification_confidence: float
    source_scheme: str
    invert_safe: bool
    transform_strategy: str
    palette_complexity: str
    dominant_background: str
    dominant_foreground: str
    palette_map: str
    theme_map_embedded: bool
    size_overhead_bytes: int
    processing_time_ms: float
