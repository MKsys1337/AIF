// Adaptive Image Format (AIF) — CLUT Tests
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

import { describe, expect, it } from "vitest";
import { applyCLUTToImageData, hexToRgb, parsePaletteMap } from "../src/clut.js";

describe("hexToRgb", () => {
  it("converts white", () => {
    expect(hexToRgb("#FFFFFF")).toEqual([255, 255, 255]);
  });

  it("converts black", () => {
    expect(hexToRgb("#000000")).toEqual([0, 0, 0]);
  });

  it("handles lowercase", () => {
    expect(hexToRgb("#ff8800")).toEqual([255, 136, 0]);
  });

  it("handles without hash", () => {
    expect(hexToRgb("1A1A2E")).toEqual([26, 26, 46]);
  });
});

describe("parsePaletteMap", () => {
  it("returns null for empty string", () => {
    expect(parsePaletteMap("")).toBeNull();
  });

  it("parses a single mapping", () => {
    const map = parsePaletteMap("#FFFFFF→#1A1A2E");
    expect(map).not.toBeNull();
    expect(map!.size).toBe(1);
  });

  it("parses multiple mappings", () => {
    const map = parsePaletteMap("#FFFFFF→#1A1A2E,#333333→#E0E0E0,#0066CC→#4DA6FF");
    expect(map).not.toBeNull();
    expect(map!.size).toBe(3);
  });
});

describe("applyCLUTToImageData", () => {
  it("replaces matching colors", () => {
    // 1 pixel: white (255,255,255)
    const data = new Uint8ClampedArray([255, 255, 255, 255]);
    const clut = new Map<[number, number, number], [number, number, number]>();
    clut.set([255, 255, 255], [26, 26, 46]);

    applyCLUTToImageData(data, clut);

    expect(data[0]).toBe(26);
    expect(data[1]).toBe(26);
    expect(data[2]).toBe(46);
    expect(data[3]).toBe(255); // alpha unchanged
  });

  it("does not replace non-matching colors", () => {
    const data = new Uint8ClampedArray([100, 100, 100, 255]);
    const clut = new Map<[number, number, number], [number, number, number]>();
    clut.set([255, 255, 255], [0, 0, 0]);

    applyCLUTToImageData(data, clut);

    expect(data[0]).toBe(100);
    expect(data[1]).toBe(100);
    expect(data[2]).toBe(100);
  });

  it("respects tolerance", () => {
    // Pixel is (250, 250, 250) — within tolerance=25 of (255,255,255)
    const data = new Uint8ClampedArray([250, 250, 250, 255]);
    const clut = new Map<[number, number, number], [number, number, number]>();
    clut.set([255, 255, 255], [26, 26, 46]);

    applyCLUTToImageData(data, clut, 25);

    expect(data[0]).toBe(26);
    expect(data[1]).toBe(26);
    expect(data[2]).toBe(46);
  });
});
