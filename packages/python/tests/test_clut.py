# Adaptive Image Format (AIF) — CLUT Serializer Tests
# Copyright (C) 2026 Markus Köplin
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

import pytest

from aif.clut import CLUTSerializer


class TestCLUTSerializer:
    SAMPLE_CLUT = {
        "#FFFFFF": "#1A1A2E",
        "#333333": "#E0E0E0",
        "#0066CC": "#4DA6FF",
    }

    def test_serialize_header(self):
        data = CLUTSerializer.serialize(self.SAMPLE_CLUT)
        assert data[0] == 0xCF  # Magic
        assert data[1] == 0x01  # Version
        # Count = 3 (big-endian uint16)
        assert data[2] == 0x00
        assert data[3] == 0x03

    def test_serialize_size(self):
        data = CLUTSerializer.serialize(self.SAMPLE_CLUT)
        expected_size = 4 + len(self.SAMPLE_CLUT) * 7
        assert len(data) == expected_size

    def test_roundtrip(self):
        data = CLUTSerializer.serialize(self.SAMPLE_CLUT)
        deserialized = CLUTSerializer.deserialize(data)
        for src_hex, dst_hex in self.SAMPLE_CLUT.items():
            assert src_hex in deserialized
            assert deserialized[src_hex]["target"] == dst_hex
            assert deserialized[src_hex]["tolerance"] == 25  # default

    def test_custom_tolerance(self):
        tolerances = {"#FFFFFF": 10, "#333333": 30, "#0066CC": 15}
        data = CLUTSerializer.serialize(self.SAMPLE_CLUT, tolerances)
        deserialized = CLUTSerializer.deserialize(data)
        assert deserialized["#FFFFFF"]["tolerance"] == 10
        assert deserialized["#333333"]["tolerance"] == 30
        assert deserialized["#0066CC"]["tolerance"] == 15

    def test_to_base64_is_string(self):
        result = CLUTSerializer.to_base64(self.SAMPLE_CLUT)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_to_palette_map_string(self):
        result = CLUTSerializer.to_palette_map_string(self.SAMPLE_CLUT)
        assert "\u2192" in result  # → character
        assert "#FFFFFF" in result
        assert "#1A1A2E" in result
        pairs = result.split(",")
        assert len(pairs) == 3

    def test_empty_clut(self):
        data = CLUTSerializer.serialize({})
        assert len(data) == 4
        deserialized = CLUTSerializer.deserialize(data)
        assert deserialized == {}

    def test_invalid_magic_raises(self):
        data = b"\x00\x01\x00\x00"
        with pytest.raises(ValueError, match="Invalid CLUT magic"):
            CLUTSerializer.deserialize(data)

    def test_invalid_version_raises(self):
        data = b"\xCF\x99\x00\x00"
        with pytest.raises(ValueError, match="Unsupported CLUT version"):
            CLUTSerializer.deserialize(data)
