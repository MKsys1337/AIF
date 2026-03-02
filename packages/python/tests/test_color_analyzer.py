# Adaptive Image Format (AIF) — Color Analyzer Tests
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


class TestColorAnalyzer:
    def setup_method(self):
        self.analyzer = ColorAnalyzer()

    def test_white_background_detected(self, white_screenshot):
        profile = self.analyzer.analyze(white_screenshot)
        # Dominant background should be close to white
        bg = profile.dominant_background
        r, g, b = (int(bg[i : i + 2], 16) for i in (1, 3, 5))
        assert r > 200 and g > 200 and b > 200

    def test_is_light_background(self, white_screenshot):
        profile = self.analyzer.analyze(white_screenshot)
        assert profile.is_light_background is True

    def test_dark_background_detected(self, dark_screenshot):
        profile = self.analyzer.analyze(dark_screenshot)
        assert profile.is_light_background is False

    def test_palette_has_colors(self, white_screenshot):
        profile = self.analyzer.analyze(white_screenshot, max_palette_size=8)
        assert len(profile.palette) > 0
        assert len(profile.palette) <= 8

    def test_background_coverage_high_for_screenshot(self, white_screenshot):
        profile = self.analyzer.analyze(white_screenshot)
        assert profile.background_coverage > 0.5

    def test_palette_complexity_simple_for_few_colors(self):
        """An image with very few colors should have 'simple' complexity."""
        img = np.full((100, 100, 3), 255, dtype=np.uint8)
        img[10:20, 10:20] = [0, 0, 0]
        profile = self.analyzer.analyze(img)
        assert profile.palette_complexity == "simple"

    def test_luminance_histogram_has_256_bins(self, white_screenshot):
        profile = self.analyzer.analyze(white_screenshot)
        assert len(profile.luminance_histogram) == 256

    def test_hex_format(self, white_screenshot):
        profile = self.analyzer.analyze(white_screenshot)
        assert profile.dominant_background.startswith("#")
        assert len(profile.dominant_background) == 7
        for color in profile.palette:
            assert color.startswith("#")
            assert len(color) == 7
