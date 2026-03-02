# AIF Web Demo

Minimal HTML demo showing the AIF renderer in action.

## Usage

Open `index.html` in a browser. Toggle between light/dark mode using:

- The buttons in the demo
- Your operating system's appearance settings

## What it demonstrates

- **Screenshot images** get `invert(1) hue-rotate(180deg)` in dark mode (CSS filter fallback)
- **Photo images** get `brightness(0.85)` dimming only
- **Images without AIF metadata** get universal dimming

This demo uses an inline minimal renderer. In production, use the full `@aif/renderer` package for Canvas-based CLUT remapping and luminance inversion.
