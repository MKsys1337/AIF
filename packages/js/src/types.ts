// Adaptive Image Format (AIF) — TypeScript Types
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

export type ContentType =
  | "photo"
  | "screenshot"
  | "diagram"
  | "text_post"
  | "meme"
  | "icon"
  | "mixed"
  | "unknown";

export type TransformStrategy =
  | "clut"
  | "clut-remap"
  | "luminance_map"
  | "invert-luminance"
  | "full_lab_map"
  | "dim-only"
  | "none";

export type ColorScheme = "light" | "dark" | "unknown";

export type AppTheme = "light" | "dark" | "auto";

export interface AIFMetadata {
  contentType: ContentType;
  sourceScheme: ColorScheme;
  invertSafe: boolean;
  transformStrategy: TransformStrategy;
  paletteMap: string;
  adaptationHint: string;
}

export interface AIFRendererOptions {
  /** Use Canvas-based transformations when available. Default: true */
  preferCanvas?: boolean;
  /** Apply brightness dimming to photos. Default: true */
  dimPhotos?: boolean;
  /** Brightness level for photo dimming (0–1). Default: 0.85 */
  photoDimLevel?: number;
}
