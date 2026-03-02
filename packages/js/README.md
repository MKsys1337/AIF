# @aif/renderer

Client-side renderer for the [Adaptive Image Format (AIF)](../../README.md) specification.

Automatically adapts images to dark/light mode in the browser using CLUT remapping, luminance inversion, or CSS filter fallbacks.

## Installation

```bash
npm install @aif/renderer
```

## Quick Start

```typescript
import { AIFRenderer, observeImages } from "@aif/renderer";

const renderer = new AIFRenderer();

// Automatically process all current and future <img> elements
observeImages(renderer);
```

### HTML Integration

The renderer reads AIF metadata from `data-*` attributes on `<img>` elements:

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

## API

### `AIFRenderer`

| Method | Description |
|--------|-------------|
| `processImage(img)` | Process a single `<img>` element |
| `reprocessAllImages()` | Reprocess all AIF-annotated images on the page |
| `setAppTheme(theme)` | Set the in-app theme: `'light'`, `'dark'`, or `'auto'` |

### `observeImages(renderer, root?)`

Start a `MutationObserver` that automatically processes new images added to the DOM.

### Low-Level Utilities

| Function | Description |
|----------|-------------|
| `parsePaletteMap(str)` | Parse a `PaletteMap` string into a Map |
| `applyCLUTToImageData(data, clut)` | Apply CLUT to raw pixel data |
| `applyLuminanceInversion(data)` | Invert luminance of raw pixel data |

## Testing

```bash
npm test
```

## License

AGPL-3.0-or-later — Copyright (C) 2026 Markus Köplin

See [LICENSE](../../LICENSE) for the full license text. A [commercial license](../../LICENSE-COMMERCIAL.md) is available for proprietary use.
