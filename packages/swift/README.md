# AIF (Swift)

Swift package for the [Adaptive Image Format (AIF)](../../README.md) specification.

Provides client-side image adaptation for iOS and macOS, automatically transforming images for dark/light mode using CLUT remapping, luminance inversion, or brightness dimming.

## Requirements

- Swift 5.9+
- iOS 16+ / macOS 13+

## Installation

### Swift Package Manager

Add to your `Package.swift`:

```swift
dependencies: [
    .package(url: "https://github.com/MKsys1337/AIF", from: "0.1.0"),
]
```

Or in Xcode: File → Add Package Dependencies → enter the repository URL.

## Quick Start

```swift
import AIF

let metadata = AIFMetadata(
    contentType: .screenshot,
    sourceScheme: .light,
    invertSafe: true,
    paletteMap: ["#FFFFFF": "#1A1A2E", "#333333": "#E0E0E0"],
    transformStrategy: .clut
)

// Using the UIImageView extension
imageView.setAIFImage(originalImage, metadata: metadata)

// Or process manually
let adapted = AIFImageProcessor.shared.adaptImage(originalImage, metadata: metadata)
```

## Components

| Type | Description |
|------|-------------|
| `AIFImageProcessor` | Main processor — selects and applies the appropriate transformation |
| `CLUTProcessor` | Pixel-level color remapping using a palette map |
| `LuminanceInverter` | Luminance inversion in linear RGB space (preserves hues) |
| `UIImageView+AIF` | Convenience extension for seamless UIKit integration |
| `AIFMetadata` | Metadata types, enums, and configuration |

## Testing

```bash
swift test
```

## License

AGPL-3.0-or-later — Copyright (C) 2026 Markus Köplin

See [LICENSE](../../LICENSE) for the full license text. A [commercial license](../../LICENSE-COMMERCIAL.md) is available for proprietary use.
