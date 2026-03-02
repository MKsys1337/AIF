// Adaptive Image Format (AIF) — Metadata Types
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

import Foundation

/// Classification of image content for adaptive rendering decisions.
public enum ContentType: String, Sendable {
    case photo
    case screenshot
    case diagram
    case textPost = "text_post"
    case meme
    case icon
    case mixed
    case unknown
}

/// Strategy used to generate the dark-mode adaptation.
public enum TransformStrategy: String, Sendable {
    case clut
    case luminanceMap = "luminance_map"
    case fullLabMap = "full_lab_map"
    case none
}

/// Color scheme of the source image.
public enum ColorScheme: String, Sendable {
    case light
    case dark
    case unknown
}

/// AIF metadata associated with an image.
public struct AIFMetadata: Sendable {
    /// The classified content type of the image.
    public let contentType: ContentType

    /// The color scheme of the original image.
    public let sourceScheme: ColorScheme

    /// Whether luminance inversion can be safely applied.
    public let invertSafe: Bool

    /// Mapping of source hex colors to dark-mode target hex colors.
    public let paletteMap: [String: String]

    /// The recommended transformation strategy.
    public let transformStrategy: TransformStrategy

    public init(
        contentType: ContentType,
        sourceScheme: ColorScheme,
        invertSafe: Bool,
        paletteMap: [String: String],
        transformStrategy: TransformStrategy
    ) {
        self.contentType = contentType
        self.sourceScheme = sourceScheme
        self.invertSafe = invertSafe
        self.paletteMap = paletteMap
        self.transformStrategy = transformStrategy
    }
}
