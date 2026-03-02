// Adaptive Image Format (AIF) — CLUT Processor
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

/// Applies a Color Lookup Table (CLUT) transformation to an image.
public enum CLUTProcessor {
    /// Apply a palette map to an image, remapping colors pixel by pixel.
    ///
    /// - Parameters:
    ///   - image: The source `UIImage`.
    ///   - paletteMap: Mapping of source hex colors to target hex colors.
    ///   - tolerance: Per-channel color matching tolerance (default: 25).
    /// - Returns: The remapped image, or the original if processing fails.
    public static func apply(
        to image: UIImage,
        paletteMap: [String: String],
        tolerance: UInt8 = 25
    ) -> UIImage {
        guard let cgImage = image.cgImage else { return image }

        let width = cgImage.width
        let height = cgImage.height
        let bytesPerPixel = 4
        let bytesPerRow = bytesPerPixel * width
        let bitsPerComponent = 8

        var pixelData = [UInt8](repeating: 0, count: height * bytesPerRow)
        let colorSpace = CGColorSpaceCreateDeviceRGB()

        guard let context = CGContext(
            data: &pixelData,
            width: width,
            height: height,
            bitsPerComponent: bitsPerComponent,
            bytesPerRow: bytesPerRow,
            space: colorSpace,
            bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue
        ) else { return image }

        context.draw(cgImage, in: CGRect(x: 0, y: 0, width: width, height: height))

        let mappings: [([UInt8], [UInt8])] = paletteMap.compactMap { src, dst in
            guard let srcRGB = hexToRGB(src), let dstRGB = hexToRGB(dst) else { return nil }
            return (srcRGB, dstRGB)
        }

        for i in stride(from: 0, to: pixelData.count, by: 4) {
            let r = pixelData[i]
            let g = pixelData[i + 1]
            let b = pixelData[i + 2]

            for (src, dst) in mappings {
                if abs(Int(r) - Int(src[0])) < Int(tolerance),
                   abs(Int(g) - Int(src[1])) < Int(tolerance),
                   abs(Int(b) - Int(src[2])) < Int(tolerance)
                {
                    pixelData[i] = dst[0]
                    pixelData[i + 1] = dst[1]
                    pixelData[i + 2] = dst[2]
                    break
                }
            }
        }

        guard let outputCGImage = context.makeImage() else { return image }
        return UIImage(
            cgImage: outputCGImage,
            scale: image.scale,
            orientation: image.imageOrientation
        )
    }

    /// Convert a hex color string (e.g. "#FF8800") to an RGB byte array.
    static func hexToRGB(_ hex: String) -> [UInt8]? {
        let h = hex.replacingOccurrences(of: "#", with: "")
        guard h.count == 6, let val = UInt32(h, radix: 16) else { return nil }
        return [
            UInt8((val >> 16) & 0xFF),
            UInt8((val >> 8) & 0xFF),
            UInt8(val & 0xFF),
        ]
    }
}
#endif
