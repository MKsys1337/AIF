// Adaptive Image Format (AIF) — CLUT Parsing and Canvas Application
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
 * Parse a palette map string into a Map of source→target RGB tuples.
 *
 * @param mapString - Format: "#FFFFFF→#1A1A2E,#333333→#E0E0E0"
 * @returns Map of [r,g,b] source to [r,g,b] target, or null on invalid input.
 */
export function parsePaletteMap(
  mapString: string
): Map<[number, number, number], [number, number, number]> | null {
  if (!mapString) return null;
  const map = new Map<[number, number, number], [number, number, number]>();
  for (const pair of mapString.split(",")) {
    const [src, dst] = pair.split("→");
    if (src && dst) {
      map.set(hexToRgb(src.trim()), hexToRgb(dst.trim()));
    }
  }
  return map.size > 0 ? map : null;
}

/**
 * Convert a hex color string to an RGB tuple.
 */
export function hexToRgb(hex: string): [number, number, number] {
  const h = hex.replace("#", "");
  return [
    parseInt(h.slice(0, 2), 16),
    parseInt(h.slice(2, 4), 16),
    parseInt(h.slice(4, 6), 16),
  ];
}

/**
 * Apply a CLUT to image data in-place.
 *
 * @param data - RGBA pixel data from a CanvasRenderingContext2D.
 * @param clut - Parsed palette map.
 * @param tolerance - Color matching tolerance per channel (default: 25).
 */
export function applyCLUTToImageData(
  data: Uint8ClampedArray,
  clut: Map<[number, number, number], [number, number, number]>,
  tolerance: number = 25
): void {
  for (let i = 0; i < data.length; i += 4) {
    const r = data[i];
    const g = data[i + 1];
    const b = data[i + 2];

    for (const [src, dst] of clut) {
      if (
        Math.abs(r - src[0]) < tolerance &&
        Math.abs(g - src[1]) < tolerance &&
        Math.abs(b - src[2]) < tolerance
      ) {
        data[i] = dst[0];
        data[i + 1] = dst[1];
        data[i + 2] = dst[2];
        break;
      }
    }
  }
}
