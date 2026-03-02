// Adaptive Image Format (AIF) — AIFImageProcessor Tests
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

@Suite("AIFMetadata")
struct AIFMetadataTests {
    @Test("Content type raw values match spec")
    func contentTypeRawValues() {
        #expect(ContentType.photo.rawValue == "photo")
        #expect(ContentType.screenshot.rawValue == "screenshot")
        #expect(ContentType.diagram.rawValue == "diagram")
        #expect(ContentType.textPost.rawValue == "text_post")
        #expect(ContentType.meme.rawValue == "meme")
        #expect(ContentType.icon.rawValue == "icon")
        #expect(ContentType.mixed.rawValue == "mixed")
        #expect(ContentType.unknown.rawValue == "unknown")
    }

    @Test("Transform strategy raw values match spec")
    func transformStrategyRawValues() {
        #expect(TransformStrategy.clut.rawValue == "clut")
        #expect(TransformStrategy.luminanceMap.rawValue == "luminance_map")
        #expect(TransformStrategy.fullLabMap.rawValue == "full_lab_map")
        #expect(TransformStrategy.none.rawValue == "none")
    }

    @Test("Metadata initializer sets all properties")
    func metadataInit() {
        let metadata = AIFMetadata(
            contentType: .screenshot,
            sourceScheme: .light,
            invertSafe: true,
            paletteMap: ["#FFFFFF": "#1A1A2E"],
            transformStrategy: .clut
        )

        #expect(metadata.contentType == .screenshot)
        #expect(metadata.sourceScheme == .light)
        #expect(metadata.invertSafe == true)
        #expect(metadata.paletteMap.count == 1)
        #expect(metadata.transformStrategy == .clut)
    }

    @Test("Content type can be initialized from raw value")
    func contentTypeFromRaw() {
        #expect(ContentType(rawValue: "screenshot") == .screenshot)
        #expect(ContentType(rawValue: "invalid") == nil)
    }
}
