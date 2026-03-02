# Adaptive Image Format (AIF) — Theme Map Generator
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

"""Theme map generator — produces the delta between light and dark variants."""

from __future__ import annotations

import cv2
import numpy as np

from aif.types import ColorProfile, TransformStrategy


class ThemeMapGenerator:
    """
    Generates the theme map — the delta between the light and dark variant.

    The theme map encodes per-pixel transformations:
    - CLUT mode: Color lookup table (a few hundred bytes)
    - Luminance Map: L* delta only (1 channel, 1/4 resolution)
    - Full LAB Map: L*a*b* delta (3 channels, 1/4 resolution)
    """

    # Default dark-mode target colors (configurable per platform)
    DEFAULT_DARK_PALETTE = {
        "background": "#1A1A2E",
        "surface": "#16213E",
        "text_primary": "#E0E0E0",
        "text_secondary": "#A0A0A0",
        "accent": "#4DA6FF",
        "border": "#2A2A4A",
        "success": "#4ADE80",
        "warning": "#FBBF24",
        "error": "#F87171",
    }

    def __init__(self, dark_palette: dict | None = None):
        self.dark_palette = dark_palette or self.DEFAULT_DARK_PALETTE

    def select_strategy(self, color_profile: ColorProfile) -> TransformStrategy:
        """Select the optimal transformation strategy based on color analysis."""
        if color_profile.palette_complexity == "simple":
            return TransformStrategy.CLUT
        elif color_profile.palette_complexity == "moderate":
            return TransformStrategy.LUMINANCE_MAP
        elif not color_profile.is_light_background:
            return TransformStrategy.NONE
        else:
            return TransformStrategy.FULL_LAB_MAP

    def generate(
        self,
        image: np.ndarray,
        color_profile: ColorProfile,
        strategy: TransformStrategy | None = None,
    ) -> dict:
        """
        Generate a theme map or CLUT for the given image.

        Returns a dict with keys: strategy, clut, theme_map, map_channels,
        map_scale, dark_preview, metadata.
        """
        if strategy is None:
            strategy = self.select_strategy(color_profile)

        if strategy == TransformStrategy.NONE:
            return {
                "strategy": strategy,
                "clut": None,
                "theme_map": None,
                "map_channels": 0,
                "map_scale": 0,
                "dark_preview": image,
                "metadata": {"transform": "none"},
            }

        if strategy == TransformStrategy.CLUT:
            return self._generate_clut(image, color_profile)

        if strategy == TransformStrategy.LUMINANCE_MAP:
            return self._generate_luminance_map(image, color_profile)

        return self._generate_full_lab_map(image, color_profile)

    # ------------------------------------------------------------------
    # CLUT
    # ------------------------------------------------------------------

    def _generate_clut(self, image: np.ndarray, profile: ColorProfile) -> dict:
        """
        CLUT mode: create a color lookup table.
        Ideal for screenshots with few distinct colors. Overhead: < 1 KB.
        """
        clut: dict[str, str] = {}
        for hex_color in profile.palette:
            dark_color = self._map_color_to_dark(hex_color, profile)
            clut[hex_color] = dark_color

        # Explicitly map background and foreground
        clut[profile.dominant_background] = self.dark_palette["background"]
        clut[profile.dominant_foreground] = self.dark_palette["text_primary"]

        dark_preview = self._apply_clut(image, clut)

        return {
            "strategy": TransformStrategy.CLUT,
            "clut": clut,
            "theme_map": None,
            "map_channels": 0,
            "map_scale": 0,
            "dark_preview": dark_preview,
            "metadata": {
                "transform": "clut",
                "clut_size": len(clut),
                "palette_map": ",".join(f"{k}\u2192{v}" for k, v in clut.items()),
            },
        }

    # ------------------------------------------------------------------
    # Luminance Map
    # ------------------------------------------------------------------

    def _generate_luminance_map(
        self,
        image: np.ndarray,
        profile: ColorProfile,
        scale: float = 0.25,
    ) -> dict:
        """
        Luminance-map mode: stores only the L* delta.
        1 channel, 1/4 resolution. Overhead: ~8–15 %.
        """
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        lab = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB).astype(np.float32)

        dark_lab = lab.copy()
        l_channel = dark_lab[:, :, 0]

        # Intelligent L* inversion
        dark_lab[:, :, 0] = np.clip(255 - l_channel * 0.9 + 10, 15, 240)

        # Delta map (offset 128 = no delta)
        l_delta = dark_lab[:, :, 0] - lab[:, :, 0]
        l_delta_encoded = np.clip(l_delta + 128, 0, 255).astype(np.uint8)

        # Scale to 1/4 resolution
        h, w = l_delta_encoded.shape
        theme_map = cv2.resize(
            l_delta_encoded,
            (int(w * scale), int(h * scale)),
            interpolation=cv2.INTER_AREA,
        )

        dark_rgb = cv2.cvtColor(dark_lab.astype(np.uint8), cv2.COLOR_LAB2RGB)
        dark_bgr = cv2.cvtColor(dark_rgb, cv2.COLOR_RGB2BGR)

        return {
            "strategy": TransformStrategy.LUMINANCE_MAP,
            "clut": None,
            "theme_map": theme_map,
            "map_channels": 1,
            "map_scale": scale,
            "dark_preview": dark_bgr,
            "metadata": {
                "transform": "luminance_map",
                "transform_space": "lab",
                "delta_offset": 128,
                "min_l_delta": int(np.min(l_delta)),
                "max_l_delta": int(np.max(l_delta)),
            },
        }

    # ------------------------------------------------------------------
    # Full LAB Map
    # ------------------------------------------------------------------

    def _generate_full_lab_map(
        self,
        image: np.ndarray,
        profile: ColorProfile,
        scale: float = 0.25,
    ) -> dict:
        """
        Full-LAB-map mode: stores L*a*b* delta.
        3 channels, 1/4 resolution. Overhead: ~15–25 %.
        """
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        lab = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB).astype(np.float32)

        dark_lab = lab.copy()
        dark_lab[:, :, 0] = np.clip(255 - dark_lab[:, :, 0] * 0.9 + 10, 15, 240)

        # Slightly desaturate a* and b* for dark mode
        dark_lab[:, :, 1] = dark_lab[:, :, 1] * 0.85 + 128 * 0.15
        dark_lab[:, :, 2] = dark_lab[:, :, 2] * 0.85 + 128 * 0.15

        # Delta map (3 channels, offset 128)
        delta = dark_lab - lab + 128
        delta_encoded = np.clip(delta, 0, 255).astype(np.uint8)

        h, w = delta_encoded.shape[:2]
        theme_map = cv2.resize(
            delta_encoded,
            (int(w * scale), int(h * scale)),
            interpolation=cv2.INTER_AREA,
        )

        dark_rgb = cv2.cvtColor(dark_lab.astype(np.uint8), cv2.COLOR_LAB2RGB)
        dark_bgr = cv2.cvtColor(dark_rgb, cv2.COLOR_RGB2BGR)

        return {
            "strategy": TransformStrategy.FULL_LAB_MAP,
            "clut": None,
            "theme_map": theme_map,
            "map_channels": 3,
            "map_scale": scale,
            "dark_preview": dark_bgr,
            "metadata": {
                "transform": "full_lab_map",
                "transform_space": "lab",
                "delta_offset": 128,
            },
        }

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _map_color_to_dark(self, hex_color: str, profile: ColorProfile) -> str:
        """Map a light-mode color to its dark-mode equivalent using LAB space."""
        r, g, b = (int(hex_color[i : i + 2], 16) for i in (1, 3, 5))

        rgb_pixel = np.array([[[r, g, b]]], dtype=np.uint8)
        lab_pixel = cv2.cvtColor(rgb_pixel, cv2.COLOR_RGB2LAB)[0, 0].astype(float)

        # L* inversion
        lab_pixel[0] = np.clip(255 - lab_pixel[0] * 0.9 + 10, 15, 240)

        # Slight desaturation
        lab_pixel[1] = lab_pixel[1] * 0.85 + 128 * 0.15
        lab_pixel[2] = lab_pixel[2] * 0.85 + 128 * 0.15

        dark_rgb = cv2.cvtColor(
            np.array([[lab_pixel]], dtype=np.uint8), cv2.COLOR_LAB2RGB
        )[0, 0]

        return f"#{dark_rgb[0]:02X}{dark_rgb[1]:02X}{dark_rgb[2]:02X}"

    def _apply_clut(
        self, image: np.ndarray, clut: dict[str, str], tolerance: int = 25
    ) -> np.ndarray:
        """Apply a CLUT to an image."""
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB).copy()
        result = rgb.copy()

        for src_hex, dst_hex in clut.items():
            src_rgb = np.array(
                [int(src_hex[i : i + 2], 16) for i in (1, 3, 5)], dtype=np.int16
            )
            dst_rgb = np.array(
                [int(dst_hex[i : i + 2], 16) for i in (1, 3, 5)], dtype=np.uint8
            )

            diff = np.abs(rgb.astype(np.int16) - src_rgb)
            mask = np.all(diff < tolerance, axis=2)
            result[mask] = dst_rgb

        return cv2.cvtColor(result, cv2.COLOR_RGB2BGR)
