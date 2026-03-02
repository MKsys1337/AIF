# Adaptive Image Format (AIF) — Core Package
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

"""aif-core — Server-side image processing pipeline for dark/light mode adaptation."""

__version__ = "0.1.0"

from aif.classifier import ImageClassifierHeuristic
from aif.clut import CLUTSerializer
from aif.color_analyzer import ColorAnalyzer
from aif.pipeline import AIFPipeline
from aif.theme_map import ThemeMapGenerator
from aif.types import AIFResult, ColorProfile, ContentType, TransformStrategy
from aif.xmp import XMPEmbedder

__all__ = [
    "AIFPipeline",
    "AIFResult",
    "CLUTSerializer",
    "ColorAnalyzer",
    "ColorProfile",
    "ContentType",
    "ImageClassifierHeuristic",
    "ThemeMapGenerator",
    "TransformStrategy",
    "XMPEmbedder",
]
