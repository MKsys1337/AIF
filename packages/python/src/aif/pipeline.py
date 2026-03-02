# Adaptive Image Format (AIF) — Processing Pipeline
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

"""Full AIF upload pipeline — classifies, analyzes, and embeds theme metadata."""

from __future__ import annotations

import io
import time

import cv2
import numpy as np
from PIL import Image
from PIL.PngImagePlugin import PngInfo

from aif.classifier import ImageClassifierHeuristic
from aif.clut import CLUTSerializer
from aif.color_analyzer import ColorAnalyzer
from aif.theme_map import ThemeMapGenerator
from aif.types import AIFResult, ContentType, TransformStrategy
from aif.xmp import XMPEmbedder


class AIFPipeline:
    """
    Full AIF processing pipeline.
    Called after the existing image upload step.
    """

    def __init__(
        self,
        classifier: ImageClassifierHeuristic | None = None,
        color_analyzer: ColorAnalyzer | None = None,
        theme_map_gen: ThemeMapGenerator | None = None,
        clut_serializer: CLUTSerializer | None = None,
    ):
        self.classifier = classifier or ImageClassifierHeuristic()
        self.color_analyzer = color_analyzer or ColorAnalyzer()
        self.theme_map_gen = theme_map_gen or ThemeMapGenerator()
        self.clut_serializer = clut_serializer or CLUTSerializer()
        self.xmp_embedder = XMPEmbedder()

    def process(
        self, image_bytes: bytes, original_format: str = "jpeg"
    ) -> tuple[bytes, AIFResult]:
        """
        Process an uploaded image through the full AIF pipeline.

        Args:
            image_bytes: Raw bytes of the uploaded image.
            original_format: One of 'jpeg', 'png', 'webp', etc.

        Returns:
            (processed_image_bytes, aif_result)
        """
        start_time = time.monotonic()

        # 1. Decode image
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if image is None:
            return image_bytes, AIFResult(
                processed=False,
                content_type="unknown",
                classification_confidence=0,
                source_scheme="unknown",
                invert_safe=False,
                transform_strategy="none",
                palette_complexity="unknown",
                dominant_background="#000000",
                dominant_foreground="#000000",
                palette_map="",
                theme_map_embedded=False,
                size_overhead_bytes=0,
                processing_time_ms=0,
            )

        # 2. Classification
        content_type, confidence = self.classifier.classify(image)

        # 3. If photo → minimal processing
        if content_type == ContentType.PHOTO:
            elapsed = (time.monotonic() - start_time) * 1000
            return image_bytes, AIFResult(
                processed=True,
                content_type="photo",
                classification_confidence=confidence,
                source_scheme="unknown",
                invert_safe=False,
                transform_strategy="none",
                palette_complexity="complex",
                dominant_background="#000000",
                dominant_foreground="#FFFFFF",
                palette_map="",
                theme_map_embedded=False,
                size_overhead_bytes=0,
                processing_time_ms=elapsed,
            )

        # 4. Color analysis
        color_profile = self.color_analyzer.analyze(image)

        # 5. Determine source scheme
        source_scheme = "light" if color_profile.is_light_background else "dark"

        # 6. If already dark → no transformation needed
        if source_scheme == "dark":
            elapsed = (time.monotonic() - start_time) * 1000
            return image_bytes, AIFResult(
                processed=True,
                content_type=self._content_type_to_string(content_type),
                classification_confidence=confidence,
                source_scheme="dark",
                invert_safe=False,
                transform_strategy="none",
                palette_complexity=color_profile.palette_complexity,
                dominant_background=color_profile.dominant_background,
                dominant_foreground=color_profile.dominant_foreground,
                palette_map="",
                theme_map_embedded=False,
                size_overhead_bytes=0,
                processing_time_ms=elapsed,
            )

        # 7. Generate theme map / CLUT
        strategy = self.theme_map_gen.select_strategy(color_profile)
        theme_result = self.theme_map_gen.generate(image, color_profile, strategy)

        # 8. Build XMP metadata
        xmp_metadata = {
            "Version": "1.0",
            "SourceScheme": source_scheme,
            "ContentType": self._content_type_to_string(content_type),
            "ClassificationConfidence": str(int(confidence * 100)),
            "InvertSafe": "true",
            "TransformStrategy": strategy.value,
            "DominantBackground": color_profile.dominant_background,
            "DominantForeground": color_profile.dominant_foreground,
            "BackgroundCoverage": f"{color_profile.background_coverage:.2f}",
            "PaletteComplexity": color_profile.palette_complexity,
            "AdaptationHint": (
                "clut-remap" if strategy == TransformStrategy.CLUT else "invert-luminance"
            ),
        }

        # Add CLUT mapping if applicable
        palette_map_string = ""
        if theme_result["clut"]:
            palette_map_string = CLUTSerializer.to_palette_map_string(theme_result["clut"])
            xmp_metadata["PaletteMap"] = palette_map_string
            xmp_metadata["PaletteMapBinary"] = CLUTSerializer.to_base64(theme_result["clut"])

        # 9. Embed XMP into image
        pil_image = Image.open(io.BytesIO(image_bytes))
        output_buffer = io.BytesIO()

        xmp_string = self.xmp_embedder._build_xmp_string(xmp_metadata)

        if original_format in ("jpeg", "jpg"):
            pil_image.save(
                output_buffer, "JPEG", quality=90, xmp=xmp_string.encode("utf-8")
            )
        elif original_format == "png":
            pnginfo = PngInfo()
            pnginfo.add_text("XML:com.adobe.xmp", xmp_string)
            pil_image.save(output_buffer, "PNG", pnginfo=pnginfo)
        else:
            pil_image.save(
                output_buffer, "JPEG", quality=90, xmp=xmp_string.encode("utf-8")
            )

        processed_bytes = output_buffer.getvalue()
        size_overhead = len(processed_bytes) - len(image_bytes)

        elapsed = (time.monotonic() - start_time) * 1000

        return processed_bytes, AIFResult(
            processed=True,
            content_type=self._content_type_to_string(content_type),
            classification_confidence=confidence,
            source_scheme=source_scheme,
            invert_safe=True,
            transform_strategy=strategy.value,
            palette_complexity=color_profile.palette_complexity,
            dominant_background=color_profile.dominant_background,
            dominant_foreground=color_profile.dominant_foreground,
            palette_map=palette_map_string,
            theme_map_embedded=False,
            size_overhead_bytes=max(0, size_overhead),
            processing_time_ms=elapsed,
        )

    @staticmethod
    def _content_type_to_string(ct: ContentType) -> str:
        mapping = {
            ContentType.PHOTO: "photo",
            ContentType.SCREENSHOT: "screenshot",
            ContentType.DIAGRAM: "diagram",
            ContentType.TEXT_POST: "text_post",
            ContentType.MEME: "meme",
            ContentType.ICON: "icon",
            ContentType.MIXED: "mixed",
            ContentType.UNKNOWN: "unknown",
        }
        return mapping.get(ct, "unknown")
