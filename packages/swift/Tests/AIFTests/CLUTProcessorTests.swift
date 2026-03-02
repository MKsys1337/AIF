// Adaptive Image Format (AIF) — CLUTProcessor Tests
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

import Testing
@testable import AIF

#if canImport(UIKit)
@Suite("CLUTProcessor")
struct CLUTProcessorTests {
    @Test("hexToRGB parses valid hex colors")
    func hexToRGBValid() {
        let white = CLUTProcessor.hexToRGB("#FFFFFF")
        #expect(white == [255, 255, 255])

        let black = CLUTProcessor.hexToRGB("#000000")
        #expect(black == [0, 0, 0])

        let color = CLUTProcessor.hexToRGB("#1A2B3C")
        #expect(color == [0x1A, 0x2B, 0x3C])
    }

    @Test("hexToRGB handles missing hash")
    func hexToRGBNoHash() {
        let result = CLUTProcessor.hexToRGB("FF8800")
        #expect(result == [255, 136, 0])
    }

    @Test("hexToRGB returns nil for invalid input")
    func hexToRGBInvalid() {
        #expect(CLUTProcessor.hexToRGB("ZZZ") == nil)
        #expect(CLUTProcessor.hexToRGB("#GG0000") == nil)
        #expect(CLUTProcessor.hexToRGB("") == nil)
    }
}
#endif
