# Adaptive Image Format (AIF) — Theme Map Tests
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

import numpy as np

from aif.color_analyzer import ColorAnalyzer
from aif.theme_map import ThemeMapGenerator
from aif.types import ColorProfile, TransformStrategy


class TestThemeMapGenerator:
    def setup_method(self):
        self.generator = ThemeMapGenerator()
        self.analyzer = ColorAnalyzer()

    def test_select_strategy_simple_palette(self):
        profile = ColorProfile(
            dominant_background="#FFFFFF",
            dominant_foreground="#333333",
            palette=["#FFFFFF", "#333333"],
            unique_color_count=10,
            background_coverage=0.8,
            is_light_background=True,
            luminance_histogram=[0] * 256,
            palette_complexity="simple",
        )
        assert self.generator.select_strategy(profile) == TransformStrategy.CLUT

    def test_select_strategy_moderate_palette(self):
        profile = ColorProfile(
            dominant_background="#FFFFFF",
            dominant_foreground="#333333",
            palette=["#FFFFFF", "#333333"],
            unique_color_count=100,
            background_coverage=0.5,
            is_light_background=True,
            luminance_histogram=[0] * 256,
            palette_complexity="moderate",
        )
        assert self.generator.select_strategy(profile) == TransformStrategy.LUMINANCE_MAP

    def test_select_strategy_dark_background(self):
        profile = ColorProfile(
            dominant_background="#1A1A2E",
            dominant_foreground="#E0E0E0",
            palette=["#1A1A2E", "#E0E0E0"],
            unique_color_count=500,
            background_coverage=0.6,
            is_light_background=False,
            luminance_histogram=[0] * 256,
            palette_complexity="complex",
        )
        assert self.generator.select_strategy(profile) == TransformStrategy.NONE

    def test_generate_clut_result_structure(self, white_screenshot):
        profile = self.analyzer.analyze(white_screenshot)
        # Force simple complexity to get CLUT
        profile = ColorProfile(
            **{**profile.__dict__, "palette_complexity": "simple"}
        )
        result = self.generator.generate(white_screenshot, profile, TransformStrategy.CLUT)
        assert result["strategy"] == TransformStrategy.CLUT
        assert result["clut"] is not None
        assert isinstance(result["clut"], dict)
        assert result["dark_preview"] is not None

    def test_generate_luminance_map_shape(self, white_screenshot):
        profile = self.analyzer.analyze(white_screenshot)
        result = self.generator.generate(
            white_screenshot, profile, TransformStrategy.LUMINANCE_MAP
        )
        assert result["strategy"] == TransformStrategy.LUMINANCE_MAP
        assert result["theme_map"] is not None
        assert result["map_channels"] == 1
        assert result["map_scale"] == 0.25
        # Verify quarter-resolution
        h, w = white_screenshot.shape[:2]
        assert result["theme_map"].shape == (h // 4, w // 4)

    def test_generate_full_lab_map_shape(self, white_screenshot):
        profile = self.analyzer.analyze(white_screenshot)
        result = self.generator.generate(
            white_screenshot, profile, TransformStrategy.FULL_LAB_MAP
        )
        assert result["strategy"] == TransformStrategy.FULL_LAB_MAP
        assert result["theme_map"] is not None
        assert result["map_channels"] == 3

    def test_generate_none_returns_original(self, white_screenshot):
        profile = self.analyzer.analyze(white_screenshot)
        result = self.generator.generate(white_screenshot, profile, TransformStrategy.NONE)
        assert result["strategy"] == TransformStrategy.NONE
        assert result["clut"] is None
        assert result["theme_map"] is None
        np.testing.assert_array_equal(result["dark_preview"], white_screenshot)
