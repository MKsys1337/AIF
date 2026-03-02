# Adaptive Image Format (AIF) — Classifier Tests
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

from aif.classifier import ImageClassifierHeuristic
from aif.types import ContentType


class TestImageClassifierHeuristic:
    def setup_method(self):
        self.classifier = ImageClassifierHeuristic()

    def test_white_screenshot_classified_as_screenshot(self, white_screenshot):
        content_type, confidence = self.classifier.classify(white_screenshot)
        assert content_type == ContentType.SCREENSHOT
        assert confidence > 0.7

    def test_colorful_photo_not_classified_as_screenshot(self, colorful_photo):
        content_type, confidence = self.classifier.classify(colorful_photo)
        # A random/colorful image should NOT be classified as a screenshot
        assert content_type != ContentType.SCREENSHOT
        assert content_type != ContentType.DIAGRAM

    def test_simple_diagram_has_high_confidence(self, simple_diagram):
        content_type, confidence = self.classifier.classify(simple_diagram)
        # Should be classified as either SCREENSHOT or DIAGRAM
        assert content_type in (ContentType.SCREENSHOT, ContentType.DIAGRAM)
        assert confidence > 0.5

    def test_uniform_white_image(self):
        """A fully white image should be classified as a screenshot."""
        img = np.full((100, 100, 3), 255, dtype=np.uint8)
        content_type, confidence = self.classifier.classify(img)
        assert content_type == ContentType.SCREENSHOT
        assert confidence > 0.8

    def test_count_unique_colors_few(self):
        """An image with very few colors should have a low unique count."""
        img = np.full((100, 100, 3), 128, dtype=np.uint8)
        count = self.classifier._count_unique_colors(img, sample_size=10000)
        assert count < 10

    def test_edge_density_smooth_image(self):
        """A completely smooth image should have near-zero edge density."""
        img = np.full((100, 100, 3), 128, dtype=np.uint8)
        density = self.classifier._edge_density(img)
        assert density < 0.01

    def test_device_aspect_ratio_iphone(self):
        assert self.classifier._is_device_aspect_ratio(1170, 2532)  # iPhone 13

    def test_device_aspect_ratio_desktop(self):
        assert self.classifier._is_device_aspect_ratio(1920, 1080)  # 16:9
