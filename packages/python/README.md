# aif-core

Server-side image processing pipeline for the [Adaptive Image Format (AIF)](../../README.md) specification.

Classifies uploaded images, analyzes their color profiles, and generates theme-adaptation metadata (CLUT or Theme Map) for automatic dark/light mode rendering.

## Installation

```bash
pip install aif-core
```

Or for development:

```bash
cd packages/python
pip install -e ".[dev]"
```

## Quick Start

```python
from aif import AIFPipeline

pipeline = AIFPipeline()

with open("screenshot.png", "rb") as f:
    image_bytes = f.read()

processed_bytes, result = pipeline.process(image_bytes, "png")

print(result.content_type)        # "screenshot"
print(result.transform_strategy)  # "clut"
print(result.source_scheme)       # "light"
```

## Modules

| Module | Description |
|--------|-------------|
| `aif.classifier` | Heuristic image classifier (screenshot vs. photo vs. diagram) |
| `aif.color_analyzer` | Color palette extraction and background detection |
| `aif.theme_map` | Theme map / CLUT generation for dark mode adaptation |
| `aif.clut` | Compact binary CLUT serialization |
| `aif.xmp` | XMP metadata embedding for JPEG and PNG |
| `aif.pipeline` | Full orchestration pipeline |
| `aif.types` | Shared types, enums, and dataclasses |

## Testing

```bash
pytest
pytest --cov=aif
```

## License

AGPL-3.0-or-later — Copyright (C) 2026 Markus Köplin

See [LICENSE](../../LICENSE) for the full license text. A [commercial license](../../LICENSE-COMMERCIAL.md) is available for proprietary use.
