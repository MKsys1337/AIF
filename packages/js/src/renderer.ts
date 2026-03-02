// Adaptive Image Format (AIF) — Client-Side Renderer
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

import { applyCLUTToImageData, parsePaletteMap } from "./clut.js";
import { applyLuminanceInversion } from "./luminance.js";
import type { AIFMetadata, AIFRendererOptions, AppTheme } from "./types.js";

/**
 * AIF Client-Side Renderer.
 *
 * Three rendering modes:
 * 1. **CLUT Remap** — pixel-level color remapping via the PaletteMap
 * 2. **Canvas LAB** — full luminance inversion via OffscreenCanvas
 * 3. **CSS Filter** — fast fallback with `invert(1) hue-rotate(180deg)`
 */
export class AIFRenderer {
  enabled = true;
  preferCanvas: boolean;
  dimPhotos: boolean;
  photoDimLevel: number;

  private darkModeQuery: MediaQueryList | null = null;
  private isDarkMode = false;
  private _appTheme: AppTheme = "auto";

  constructor(options: AIFRendererOptions = {}) {
    this.preferCanvas = options.preferCanvas ?? true;
    this.dimPhotos = options.dimPhotos ?? true;
    this.photoDimLevel = options.photoDimLevel ?? 0.85;

    if (typeof window !== "undefined" && window.matchMedia) {
      this.darkModeQuery = window.matchMedia("(prefers-color-scheme: dark)");
      this.isDarkMode = this.darkModeQuery.matches;
      this.darkModeQuery.addEventListener("change", (e) => {
        this.isDarkMode = e.matches;
        this.reprocessAllImages();
      });
    }
  }

  /** Set the in-app theme (overrides OS preference). */
  setAppTheme(theme: AppTheme): void {
    this._appTheme = theme;
    this.reprocessAllImages();
  }

  get effectiveTheme(): "light" | "dark" {
    if (this._appTheme !== "auto") return this._appTheme;
    return this.isDarkMode ? "dark" : "light";
  }

  /** Process a single `<img>` element, applying the appropriate transformation. */
  async processImage(imgElement: HTMLImageElement): Promise<void> {
    if (!this.enabled || this.effectiveTheme !== "dark") {
      this._removeFilters(imgElement);
      return;
    }

    const meta = this._getAIFMetadata(imgElement);

    if (!meta) {
      if (this.dimPhotos) {
        imgElement.style.filter = `brightness(${this.photoDimLevel})`;
      }
      return;
    }

    switch (meta.contentType) {
      case "photo":
        imgElement.style.filter = `brightness(${this.photoDimLevel})`;
        break;

      case "screenshot":
      case "diagram":
      case "text_post":
      case "icon":
        await this._applyThemeTransformation(imgElement, meta);
        break;

      case "meme":
      case "mixed":
        imgElement.style.filter = "brightness(0.80) contrast(1.05)";
        break;

      default:
        if (this.dimPhotos) {
          imgElement.style.filter = `brightness(${this.photoDimLevel})`;
        }
    }
  }

  /** Reprocess all AIF-annotated images on the page. */
  reprocessAllImages(): void {
    if (typeof document === "undefined") return;
    document.querySelectorAll("img[data-aif-content-type]").forEach((img) => {
      this._removeFilters(img as HTMLImageElement);
      this.processImage(img as HTMLImageElement);
    });
  }

  // ---------------------------------------------------------------
  // Private helpers
  // ---------------------------------------------------------------

  private async _applyThemeTransformation(
    imgElement: HTMLImageElement,
    meta: AIFMetadata
  ): Promise<void> {
    const strategy = meta.transformStrategy || meta.adaptationHint;

    switch (strategy) {
      case "clut":
      case "clut-remap":
        if (meta.paletteMap && this.preferCanvas) {
          await this._applyCLUT(imgElement, meta.paletteMap);
        } else {
          this._applyInvertFilter(imgElement);
        }
        break;

      case "luminance_map":
      case "invert-luminance":
        if (this.preferCanvas) {
          await this._applyLuminanceInversion(imgElement);
        } else {
          this._applyInvertFilter(imgElement);
        }
        break;

      case "dim-only":
        imgElement.style.filter = `brightness(${this.photoDimLevel})`;
        break;

      default:
        this._applyInvertFilter(imgElement);
    }
  }

  /** CSS filter fallback — fast but imprecise. */
  private _applyInvertFilter(imgElement: HTMLImageElement): void {
    imgElement.style.filter = "invert(1) hue-rotate(180deg)";
    imgElement.style.transition = "filter 0.3s ease";
    imgElement.dataset.aifApplied = "css-filter";
  }

  /** Canvas-based CLUT remapping — pixel-accurate. */
  private async _applyCLUT(
    imgElement: HTMLImageElement,
    paletteMapString: string
  ): Promise<void> {
    const clut = parsePaletteMap(paletteMapString);
    if (!clut) {
      this._applyInvertFilter(imgElement);
      return;
    }

    try {
      const canvas = document.createElement("canvas");
      const ctx = canvas.getContext("2d", { willReadFrequently: true });
      if (!ctx) {
        this._applyInvertFilter(imgElement);
        return;
      }

      await this._ensureImageLoaded(imgElement);

      canvas.width = imgElement.naturalWidth;
      canvas.height = imgElement.naturalHeight;
      ctx.drawImage(imgElement, 0, 0);

      const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
      applyCLUTToImageData(imageData.data, clut);
      ctx.putImageData(imageData, 0, 0);

      imgElement.src = canvas.toDataURL("image/png");
      imgElement.dataset.aifApplied = "clut";
    } catch (e) {
      console.warn("[AIF] CLUT application failed, falling back to CSS filter:", e);
      this._applyInvertFilter(imgElement);
    }
  }

  /** Canvas-based luminance inversion in linear RGB space. */
  private async _applyLuminanceInversion(
    imgElement: HTMLImageElement
  ): Promise<void> {
    try {
      const canvas = document.createElement("canvas");
      const ctx = canvas.getContext("2d", { willReadFrequently: true });
      if (!ctx) {
        this._applyInvertFilter(imgElement);
        return;
      }

      await this._ensureImageLoaded(imgElement);

      canvas.width = imgElement.naturalWidth;
      canvas.height = imgElement.naturalHeight;
      ctx.drawImage(imgElement, 0, 0);

      const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
      applyLuminanceInversion(imageData.data);
      ctx.putImageData(imageData, 0, 0);

      imgElement.src = canvas.toDataURL("image/png");
      imgElement.dataset.aifApplied = "luminance-inversion";
    } catch (e) {
      console.warn("[AIF] Luminance inversion failed:", e);
      this._applyInvertFilter(imgElement);
    }
  }

  /**
   * Read AIF metadata from data attributes of an `<img>` element.
   *
   * Expected attributes (set by the server during HTML rendering):
   *   data-aif-content-type="screenshot"
   *   data-aif-source-scheme="light"
   *   data-aif-invert-safe="true"
   *   data-aif-transform-strategy="clut"
   *   data-aif-palette-map="#FFFFFF→#1A1A2E,#333333→#E0E0E0"
   *   data-aif-adaptation-hint="invert-luminance"
   */
  private _getAIFMetadata(imgElement: HTMLImageElement): AIFMetadata | null {
    const contentType = imgElement.dataset.aifContentType;
    if (!contentType) return null;

    return {
      contentType: contentType as AIFMetadata["contentType"],
      sourceScheme:
        (imgElement.dataset.aifSourceScheme as AIFMetadata["sourceScheme"]) ||
        "unknown",
      invertSafe: imgElement.dataset.aifInvertSafe === "true",
      transformStrategy:
        (imgElement.dataset
          .aifTransformStrategy as AIFMetadata["transformStrategy"]) || "none",
      paletteMap: imgElement.dataset.aifPaletteMap || "",
      adaptationHint:
        imgElement.dataset.aifAdaptationHint || "invert-luminance",
    };
  }

  private _ensureImageLoaded(img: HTMLImageElement): Promise<void> {
    return new Promise((resolve, reject) => {
      if (img.complete && img.naturalWidth > 0) {
        resolve();
      } else {
        img.onload = () => resolve();
        img.onerror = reject;
      }
    });
  }

  private _removeFilters(imgElement: HTMLImageElement): void {
    imgElement.style.filter = "";
    delete imgElement.dataset.aifApplied;
  }
}
