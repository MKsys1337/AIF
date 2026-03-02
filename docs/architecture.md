# Architecture

This document provides a high-level overview of the Adaptive Image Format (AIF) system architecture.

## System Overview

AIF is a three-layer system:

```
┌─────────────────────────────────────────────────────────────┐
│                     UPLOAD PIPELINE (Server)                │
│                                                             │
│  Ingest → Classifier → Color Analyzer → Theme Map → Embed  │
│                                                             │
│  Packages: aif-core (Python)                                │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                     STORAGE / CDN                           │
│                                                             │
│  Original image + AIF metadata (XMP / AVIF container)      │
│  Delivered with AIF-* HTTP response headers                 │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                     CLIENT RENDERING                        │
│                                                             │
│  Web: @aif/renderer (JS/TS)                                 │
│  iOS/macOS: AIF (Swift)                                     │
│                                                             │
│  Fallback cascade:                                          │
│  CLUT Remap → Luminance Inversion → CSS Filter → Dim       │
└─────────────────────────────────────────────────────────────┘
```

## Server Pipeline

The upload pipeline processes every image upload through these stages:

1. **Ingest** — Decode the uploaded image (JPEG, PNG, WebP)
2. **Classify** — Determine the content type (screenshot, photo, diagram, etc.) using heuristics and/or ML (MobileNetV3-Small)
3. **Color Analyze** — Extract the color palette, detect background color, compute luminance histogram
4. **Strategy Selection** — Choose the optimal transformation strategy based on palette complexity:
   - **CLUT** for simple palettes (< 64 colors) — overhead < 1 KB
   - **Luminance Map** for moderate complexity — overhead 8–15%
   - **Full LAB Map** for complex images — overhead 15–25%
   - **None** for photos or already-dark images
5. **Generate** — Create the CLUT or theme map
6. **Embed** — Write AIF metadata as XMP into the image file

## Content Type Taxonomy

| Type | Code | Transformable? | Default Strategy |
|------|------|----------------|------------------|
| `PHOTO` | 0x01 | No | Brightness dim |
| `SCREENSHOT` | 0x02 | Yes | CLUT / Theme Map |
| `DIAGRAM` | 0x03 | Yes | CLUT / Theme Map |
| `TEXT_POST` | 0x04 | Yes | CLUT / Theme Map |
| `MEME` | 0x05 | Partially | Selective |
| `ICON` | 0x06 | Yes | CLUT |
| `MIXED` | 0x07 | Partially | Conservative dim |
| `UNKNOWN` | 0xFF | Fallback | Brightness dim |

## Client Rendering

Clients read AIF metadata from `data-*` attributes (web) or API response headers and apply the appropriate transformation:

1. **CLUT Remap** — pixel-accurate color replacement via Canvas / Core Graphics
2. **Luminance Inversion** — inverts perceived brightness while preserving color hues
3. **CSS Filter Fallback** — `invert(1) hue-rotate(180deg)` for low-power devices
4. **Brightness Dim** — universal `brightness(0.85)` for photos and unknown content

## Transport

AIF metadata is transported via:

- **XMP** — embedded in JPEG/PNG/WebP (namespace: `https://mkhub.de/ns/aif/1.0/`)
- **AVIF container** — `thmb` box + auxiliary item
- **HTTP headers** — `AIF-Content-Type`, `AIF-Palette-Map`, `AIF-Transform-Strategy`, etc.

See the [full specification](../spec/AIF-Technische-Spezifikation-v1.0.md) for details.
