// Adaptive Image Format (AIF) — Renderer Tests
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

import { describe, expect, it, beforeEach } from "vitest";
import { AIFRenderer } from "../src/renderer.js";

describe("AIFRenderer", () => {
  let renderer: AIFRenderer;

  beforeEach(() => {
    renderer = new AIFRenderer();
  });

  it("initializes with default options", () => {
    expect(renderer.preferCanvas).toBe(true);
    expect(renderer.dimPhotos).toBe(true);
    expect(renderer.photoDimLevel).toBe(0.85);
    expect(renderer.enabled).toBe(true);
  });

  it("accepts custom options", () => {
    const custom = new AIFRenderer({
      preferCanvas: false,
      dimPhotos: false,
      photoDimLevel: 0.7,
    });
    expect(custom.preferCanvas).toBe(false);
    expect(custom.dimPhotos).toBe(false);
    expect(custom.photoDimLevel).toBe(0.7);
  });

  it("defaults to light theme when matchMedia is unavailable", () => {
    expect(renderer.effectiveTheme).toBe("light");
  });

  it("allows setting app theme", () => {
    renderer.setAppTheme("dark");
    expect(renderer.effectiveTheme).toBe("dark");
  });

  it("auto theme respects system preference", () => {
    renderer.setAppTheme("auto");
    // Without matchMedia in test env, defaults to light
    expect(renderer.effectiveTheme).toBe("light");
  });
});
