// Adaptive Image Format (AIF) — Image Processor
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

#if canImport(UIKit)
import UIKit
import CoreImage

/// Processes images for dark/light mode adaptation based on AIF metadata.
public final class AIFImageProcessor: Sendable {
    public static let shared = AIFImageProcessor()

    public init() {}

    /// Adapt an image for the current interface style.
    ///
    /// - Parameters:
    ///   - image: The source `UIImage`.
    ///   - metadata: AIF metadata describing the image content and transformation.
    /// - Returns: The adapted image, or the original if no transformation is needed.
    public func adaptImage(_ image: UIImage, metadata: AIFMetadata) -> UIImage {
        let isDark = UITraitCollection.current.userInterfaceStyle == .dark

        guard isDark, metadata.sourceScheme == .light else {
            return image
        }

        switch metadata.contentType {
        case .photo:
            return applyBrightnessDim(image, factor: 0.85)

        case .screenshot, .diagram, .textPost, .icon:
            if metadata.transformStrategy == .clut, !metadata.paletteMap.isEmpty {
                return CLUTProcessor.apply(to: image, paletteMap: metadata.paletteMap)
            } else if metadata.invertSafe {
                return LuminanceInverter.invert(image)
            } else {
                return applyBrightnessDim(image, factor: 0.80)
            }

        case .meme, .mixed:
            return applyBrightnessDim(image, factor: 0.80)

        case .unknown:
            return applyBrightnessDim(image, factor: 0.85)
        }
    }

    /// Apply brightness dimming via Core Image.
    public func applyBrightnessDim(_ image: UIImage, factor: CGFloat) -> UIImage {
        guard let ciImage = CIImage(image: image) else { return image }

        guard let filter = CIFilter(name: "CIColorControls") else { return image }
        filter.setValue(ciImage, forKey: kCIInputImageKey)
        filter.setValue(factor - 1.0, forKey: kCIInputBrightnessKey)
        filter.setValue(1.05, forKey: kCIInputContrastKey)

        guard let output = filter.outputImage else { return image }
        let context = CIContext()
        guard let cgImage = context.createCGImage(output, from: output.extent) else {
            return image
        }
        return UIImage(cgImage: cgImage, scale: image.scale, orientation: image.imageOrientation)
    }
}
#endif
