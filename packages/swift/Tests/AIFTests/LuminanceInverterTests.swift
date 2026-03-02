// Adaptive Image Format (AIF) — LuminanceInverter Tests
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
@Suite("LuminanceInverter")
struct LuminanceInverterTests {
    @Test("srgbToLinear converts 0 to 0")
    func srgbToLinearZero() {
        #expect(LuminanceInverter.srgbToLinear(0) == 0)
    }

    @Test("srgbToLinear converts 1 to 1")
    func srgbToLinearOne() {
        #expect(abs(LuminanceInverter.srgbToLinear(1.0) - 1.0) < 1e-10)
    }

    @Test("linearToSrgb converts 0 to 0")
    func linearToSrgbZero() {
        #expect(LuminanceInverter.linearToSrgb(0) == 0)
    }

    @Test("linearToSrgb converts 1 to 1")
    func linearToSrgbOne() {
        #expect(abs(LuminanceInverter.linearToSrgb(1.0) - 1.0) < 1e-10)
    }

    @Test("srgbToLinear and linearToSrgb are inverse functions")
    func roundTrip() {
        let values = [0.0, 0.1, 0.25, 0.5, 0.75, 1.0]
        for val in values {
            let roundTripped = LuminanceInverter.linearToSrgb(LuminanceInverter.srgbToLinear(val))
            #expect(abs(roundTripped - val) < 1e-10)
        }
    }
}
#endif
