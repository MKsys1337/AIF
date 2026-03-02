# Adaptive Image Format (AIF) — CLUT Serializer
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

"""Compact CLUT serialization format for XMP embedding."""

from __future__ import annotations

import base64
import struct


class CLUTSerializer:
    """
    Serialize a CLUT into a compact binary format.

    Format:
        Header (4 bytes):
            - Magic:     0xCF (1 byte)
            - Version:   0x01 (1 byte)
            - Count:     uint16 (number of entries)
        Per entry (7 bytes):
            - Source:    RGB (3 bytes)
            - Tolerance: uint8 (1 byte)
            - Target:    RGB (3 bytes)

    Total size: 4 + N * 7 bytes.
    For N=16 colors: 4 + 112 = 116 bytes.
    """

    MAGIC = 0xCF
    VERSION = 0x01

    @staticmethod
    def serialize(clut: dict[str, str], tolerances: dict[str, int] | None = None) -> bytes:
        """
        Serialize a CLUT to binary format.

        Args:
            clut: Mapping of hex colors, e.g. {"#FFFFFF": "#1A1A2E", ...}
            tolerances: Optional per-color tolerances, e.g. {"#FFFFFF": 20, ...}
        """
        entries = list(clut.items())
        header = struct.pack("!BBH", CLUTSerializer.MAGIC, CLUTSerializer.VERSION, len(entries))
        body = b""
        for src_hex, dst_hex in entries:
            src = bytes(int(src_hex[i : i + 2], 16) for i in (1, 3, 5))
            dst = bytes(int(dst_hex[i : i + 2], 16) for i in (1, 3, 5))
            tol = (tolerances or {}).get(src_hex, 25)
            body += src + struct.pack("B", tol) + dst

        return header + body

    @staticmethod
    def deserialize(data: bytes) -> dict[str, dict]:
        """Deserialize a binary CLUT back into a dictionary."""
        magic, version, count = struct.unpack("!BBH", data[:4])
        if magic != CLUTSerializer.MAGIC:
            raise ValueError(f"Invalid CLUT magic byte: 0x{magic:02X}")
        if version != CLUTSerializer.VERSION:
            raise ValueError(f"Unsupported CLUT version: {version}")

        clut: dict[str, dict] = {}
        offset = 4
        for _ in range(count):
            src = data[offset : offset + 3]
            tol = data[offset + 3]
            dst = data[offset + 4 : offset + 7]
            src_hex = f"#{src[0]:02X}{src[1]:02X}{src[2]:02X}"
            dst_hex = f"#{dst[0]:02X}{dst[1]:02X}{dst[2]:02X}"
            clut[src_hex] = {"target": dst_hex, "tolerance": tol}
            offset += 7

        return clut

    @staticmethod
    def to_base64(clut: dict[str, str]) -> str:
        """Base64-encoded CLUT for XMP embedding."""
        return base64.b64encode(CLUTSerializer.serialize(clut)).decode("ascii")

    @staticmethod
    def to_palette_map_string(clut: dict[str, str]) -> str:
        """
        Human-readable palette map for the XMP aif:PaletteMap field.
        Example: "#FFFFFF→#1A1A2E,#333333→#E0E0E0"
        """
        return ",".join(f"{src}\u2192{dst}" for src, dst in clut.items())
