# Adaptive Image Format (AIF) — Pipeline Tests
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

from aif.pipeline import AIFPipeline


class TestAIFPipeline:
    def setup_method(self):
        self.pipeline = AIFPipeline()

    def test_process_returns_tuple(self, white_screenshot_jpeg_bytes):
        result_bytes, result = self.pipeline.process(white_screenshot_jpeg_bytes, "jpeg")
        assert isinstance(result_bytes, bytes)
        assert result.processed is True

    def test_process_jpeg_screenshot(self, white_screenshot_jpeg_bytes):
        _, result = self.pipeline.process(white_screenshot_jpeg_bytes, "jpeg")
        assert result.processed is True
        assert result.content_type in ("screenshot", "diagram", "unknown")
        assert result.processing_time_ms > 0

    def test_process_png_screenshot(self, white_screenshot_png_bytes):
        _, result = self.pipeline.process(white_screenshot_png_bytes, "png")
        assert result.processed is True

    def test_invalid_image_returns_unprocessed(self):
        _, result = self.pipeline.process(b"not an image", "jpeg")
        assert result.processed is False
        assert result.content_type == "unknown"

    def test_result_has_all_fields(self, white_screenshot_jpeg_bytes):
        _, result = self.pipeline.process(white_screenshot_jpeg_bytes, "jpeg")
        assert hasattr(result, "processed")
        assert hasattr(result, "content_type")
        assert hasattr(result, "classification_confidence")
        assert hasattr(result, "source_scheme")
        assert hasattr(result, "invert_safe")
        assert hasattr(result, "transform_strategy")
        assert hasattr(result, "palette_complexity")
        assert hasattr(result, "dominant_background")
        assert hasattr(result, "dominant_foreground")
        assert hasattr(result, "palette_map")
        assert hasattr(result, "theme_map_embedded")
        assert hasattr(result, "size_overhead_bytes")
        assert hasattr(result, "processing_time_ms")

    def test_source_scheme_is_light_for_white_screenshot(self, white_screenshot_png_bytes):
        _, result = self.pipeline.process(white_screenshot_png_bytes, "png")
        if result.content_type != "photo":
            assert result.source_scheme == "light"
