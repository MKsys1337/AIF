# Getting Started

This guide walks you through setting up and using the AIF packages.

## Prerequisites

- Python 3.10+ (for the server pipeline)
- Node.js 18+ (for the web renderer)
- Swift 5.9+ / Xcode 15+ (for iOS/macOS)

## Server: Python Pipeline

### Install

```bash
cd packages/python
pip install -e ".[dev]"
```

### Basic Usage

```python
from aif import AIFPipeline

pipeline = AIFPipeline()

# Process an uploaded image
with open("screenshot.png", "rb") as f:
    image_bytes = f.read()

processed_bytes, result = pipeline.process(image_bytes, "png")

print(f"Content type:  {result.content_type}")
print(f"Strategy:      {result.transform_strategy}")
print(f"Source scheme:  {result.source_scheme}")
print(f"Overhead:      {result.size_overhead_bytes} bytes")
```

### Using Individual Modules

```python
import cv2
from aif import ImageClassifierHeuristic, ColorAnalyzer, ThemeMapGenerator

# Classify
classifier = ImageClassifierHeuristic()
image = cv2.imread("screenshot.png")
content_type, confidence = classifier.classify(image)

# Analyze colors
analyzer = ColorAnalyzer()
profile = analyzer.analyze(image)

# Generate theme map
generator = ThemeMapGenerator()
strategy = generator.select_strategy(profile)
result = generator.generate(image, profile, strategy)
```

### Run Tests

```bash
pytest
pytest --cov=aif
```

## Web: JavaScript Renderer

### Install

```bash
cd packages/js
npm install
```

### Basic Usage

```typescript
import { AIFRenderer, observeImages } from "@aif/renderer";

// Create renderer with default options
const renderer = new AIFRenderer();

// Automatically observe all images on the page
observeImages(renderer);
```

### HTML Data Attributes

The server should set these `data-*` attributes on `<img>` elements:

```html
<img
  src="/images/screenshot.avif"
  data-aif-content-type="screenshot"
  data-aif-source-scheme="light"
  data-aif-invert-safe="true"
  data-aif-transform-strategy="clut"
  data-aif-palette-map="#FFFFFF→#1A1A2E,#333333→#E0E0E0"
/>
```

### Run Tests

```bash
npm test
```

## iOS/macOS: Swift Package

### Install

Add to your `Package.swift`:

```swift
dependencies: [
    .package(url: "https://github.com/MKsys1337/AIF", from: "0.1.0"),
]
```

### Basic Usage

```swift
import AIF

let metadata = AIFMetadata(
    contentType: .screenshot,
    sourceScheme: .light,
    invertSafe: true,
    paletteMap: ["#FFFFFF": "#1A1A2E"],
    transformStrategy: .clut
)

imageView.setAIFImage(originalImage, metadata: metadata)
```

### Run Tests

```bash
cd packages/swift
swift test
```

## Next Steps

- Read the [Architecture Overview](architecture.md) for system design details
- Review the [API Specification](../api/openapi.yaml) for endpoint definitions
- Check the [full specification](../spec/AIF-Technische-Spezifikation-v1.0.md) for the complete technical reference
