// Adaptive Image Format (AIF) — Luminance Tests
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
import {
  applyLuminanceInversion,
  linearToSrgb,
  srgbToLinear,
} from "../src/luminance.js";

describe("srgbToLinear", () => {
  it("converts 0 to 0", () => {
    expect(srgbToLinear(0)).toBeCloseTo(0, 5);
  });

  it("converts 1 to 1", () => {
    expect(srgbToLinear(1)).toBeCloseTo(1, 5);
  });

  it("converts low values linearly", () => {
    // Below threshold 0.04045, sRGB is linear
    expect(srgbToLinear(0.01)).toBeCloseTo(0.01 / 12.92, 5);
  });

  it("converts mid values non-linearly", () => {
    const result = srgbToLinear(0.5);
    expect(result).toBeGreaterThan(0);
    expect(result).toBeLessThan(0.5);
  });
});

describe("linearToSrgb", () => {
  it("converts 0 to 0", () => {
    expect(linearToSrgb(0)).toBeCloseTo(0, 5);
  });

  it("converts 1 to 1", () => {
    expect(linearToSrgb(1)).toBeCloseTo(1, 5);
  });

  it("is the inverse of srgbToLinear", () => {
    for (const val of [0, 0.1, 0.25, 0.5, 0.75, 1.0]) {
      expect(linearToSrgb(srgbToLinear(val))).toBeCloseTo(val, 5);
    }
  });
});

describe("applyLuminanceInversion", () => {
  it("inverts white to near-black", () => {
    const data = new Uint8ClampedArray([255, 255, 255, 255]);
    applyLuminanceInversion(data);
    // White should become very dark
    expect(data[0]).toBeLessThan(10);
    expect(data[1]).toBeLessThan(10);
    expect(data[2]).toBeLessThan(10);
    expect(data[3]).toBe(255); // alpha unchanged
  });

  it("keeps pure black unchanged (zero luminance cannot be scaled)", () => {
    const data = new Uint8ClampedArray([0, 0, 0, 255]);
    applyLuminanceInversion(data);
    // Pure black has L=0 → scale=1.0 → stays black (0*1=0)
    // This is mathematically expected; near-black values do get inverted
    expect(data[0]).toBe(0);
    expect(data[1]).toBe(0);
    expect(data[2]).toBe(0);
  });

  it("inverts near-black to brighter value", () => {
    const data = new Uint8ClampedArray([10, 10, 10, 255]);
    applyLuminanceInversion(data);
    // Scale is clamped to 10x, so dark values get noticeably brighter
    // but not fully white due to the clamp
    expect(data[0]).toBeGreaterThan(10);
    expect(data[1]).toBeGreaterThan(10);
    expect(data[2]).toBeGreaterThan(10);
  });

  it("preserves alpha channel", () => {
    const data = new Uint8ClampedArray([128, 128, 128, 100]);
    applyLuminanceInversion(data);
    expect(data[3]).toBe(100);
  });

  it("handles multiple pixels", () => {
    const data = new Uint8ClampedArray([
      255, 255, 255, 255, // white
      128, 128, 128, 255, // mid-gray
    ]);
    applyLuminanceInversion(data);
    // First pixel (was white) should be dark
    expect(data[0]).toBeLessThan(10);
    // Second pixel (was mid-gray) should be different from 128
    // Inversion: mid-gray inverts around the middle
    expect(data[4]).not.toBe(128);
  });
});
