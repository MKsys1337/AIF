// Adaptive Image Format (AIF) — Luminance Inverter
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

/// Inverts the luminance of an image while preserving chrominance.
///
/// This produces significantly better results than a naive `invert()` filter,
/// as color hues are maintained while only the perceived brightness is flipped.
public enum LuminanceInverter {
    /// Invert the luminance of an image.
    ///
    /// Converts to YCbCr-like space, inverts the Y (luminance) channel,
    /// and converts back — keeping color hues intact.
    ///
    /// - Parameter image: The source `UIImage`.
    /// - Returns: The luminance-inverted image, or the original if processing fails.
    public static func invert(_ image: UIImage) -> UIImage {
        guard let cgImage = image.cgImage else { return image }

        let width = cgImage.width
        let height = cgImage.height
        let bytesPerPixel = 4
        let bytesPerRow = bytesPerPixel * width

        var pixelData = [UInt8](repeating: 0, count: height * bytesPerRow)
        let colorSpace = CGColorSpaceCreateDeviceRGB()

        guard let context = CGContext(
            data: &pixelData,
            width: width,
            height: height,
            bitsPerComponent: 8,
            bytesPerRow: bytesPerRow,
            space: colorSpace,
            bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue
        ) else { return image }

        context.draw(cgImage, in: CGRect(x: 0, y: 0, width: width, height: height))

        for i in stride(from: 0, to: pixelData.count, by: 4) {
            var r = Double(pixelData[i]) / 255.0
            var g = Double(pixelData[i + 1]) / 255.0
            var b = Double(pixelData[i + 2]) / 255.0

            // sRGB → linear
            r = srgbToLinear(r)
            g = srgbToLinear(g)
            b = srgbToLinear(b)

            // Relative luminance (BT.709)
            let luminance = 0.2126 * r + 0.7152 * g + 0.0722 * b

            // Invert luminance, preserve chrominance
            let targetL = 1.0 - luminance
            var scale = luminance > 0.001 ? targetL / luminance : 1.0
            scale = min(scale, 10.0)

            r = min(r * scale, 1.0)
            g = min(g * scale, 1.0)
            b = min(b * scale, 1.0)

            // Linear → sRGB
            r = linearToSrgb(r)
            g = linearToSrgb(g)
            b = linearToSrgb(b)

            pixelData[i] = UInt8(clamping: Int(r * 255.0 + 0.5))
            pixelData[i + 1] = UInt8(clamping: Int(g * 255.0 + 0.5))
            pixelData[i + 2] = UInt8(clamping: Int(b * 255.0 + 0.5))
        }

        guard let outputCGImage = context.makeImage() else { return image }
        return UIImage(
            cgImage: outputCGImage,
            scale: image.scale,
            orientation: image.imageOrientation
        )
    }

    // MARK: - Color Space Conversion

    static func srgbToLinear(_ c: Double) -> Double {
        c <= 0.04045 ? c / 12.92 : pow((c + 0.055) / 1.055, 2.4)
    }

    static func linearToSrgb(_ c: Double) -> Double {
        c <= 0.0031308 ? c * 12.92 : 1.055 * pow(c, 1.0 / 2.4) - 0.055
    }
}
#endif
