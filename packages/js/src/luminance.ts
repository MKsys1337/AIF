// Adaptive Image Format (AIF) — Luminance Inversion (Canvas)
// Copyright (C) 2026 Markus Köplin
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU Affero General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
// GNU Affero General Public License for more details.
//
// You should have received a copy of the GNU Affero General Public License
// along with this program. If not, see <https://www.gnu.org/licenses/>.

/**
 * Apply luminance inversion to pixel data in-place.
 *
 * This inverts the perceived brightness while preserving chrominance,
 * producing a much better result than CSS `invert(1) hue-rotate(180deg)`.
 *
 * Algorithm:
 * 1. Convert sRGB → linear RGB
 * 2. Compute relative luminance (BT.709)
 * 3. Invert luminance, scale RGB channels accordingly
 * 4. Convert linear RGB → sRGB
 *
 * @param data - RGBA pixel data from a CanvasRenderingContext2D.
 */
export function applyLuminanceInversion(data: Uint8ClampedArray): void {
  for (let i = 0; i < data.length; i += 4) {
    let r = data[i] / 255;
    let g = data[i + 1] / 255;
    let b = data[i + 2] / 255;

    // sRGB → linear
    r = srgbToLinear(r);
    g = srgbToLinear(g);
    b = srgbToLinear(b);

    // Relative luminance (BT.709)
    const L = 0.2126 * r + 0.7152 * g + 0.0722 * b;

    // Invert luminance, preserve chrominance
    const targetL = 1.0 - L;
    let scale = L > 0.001 ? targetL / L : 1.0;
    scale = Math.min(scale, 10.0); // Clamp for numerical stability

    r = Math.min(r * scale, 1.0);
    g = Math.min(g * scale, 1.0);
    b = Math.min(b * scale, 1.0);

    // Linear → sRGB
    r = linearToSrgb(r);
    g = linearToSrgb(g);
    b = linearToSrgb(b);

    data[i] = Math.round(r * 255);
    data[i + 1] = Math.round(g * 255);
    data[i + 2] = Math.round(b * 255);
  }
}

/** Convert a single sRGB channel value to linear. */
export function srgbToLinear(c: number): number {
  return c <= 0.04045 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
}

/** Convert a single linear channel value to sRGB. */
export function linearToSrgb(c: number): number {
  return c <= 0.0031308
    ? c * 12.92
    : 1.055 * Math.pow(c, 1 / 2.4) - 0.055;
}
