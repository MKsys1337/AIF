# Adaptive Image Format (AIF) — XMP Embedder Tests
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

from pathlib import Path

from PIL import Image

from aif.xmp import XMPEmbedder


class TestXMPEmbedder:
    SAMPLE_METADATA = {
        "Version": "1.0",
        "ContentType": "screenshot",
        "SourceScheme": "light",
        "InvertSafe": "true",
    }

    def setup_method(self):
        self.embedder = XMPEmbedder()

    def test_build_xmp_string_contains_namespace(self):
        xmp = self.embedder._build_xmp_string(self.SAMPLE_METADATA)
        assert XMPEmbedder.AIF_NS in xmp

    def test_build_xmp_string_contains_all_fields(self):
        xmp = self.embedder._build_xmp_string(self.SAMPLE_METADATA)
        for key, value in self.SAMPLE_METADATA.items():
            assert f'aif:{key}="{value}"' in xmp

    def test_build_xmp_string_is_valid_xml_structure(self):
        xmp = self.embedder._build_xmp_string(self.SAMPLE_METADATA)
        assert xmp.startswith("<?xpacket")
        assert xmp.endswith('<?xpacket end="w"?>')
        assert "<x:xmpmeta" in xmp
        assert "<rdf:RDF" in xmp

    def test_embed_in_jpeg(self, tmp_path):
        # Create a test JPEG
        img = Image.new("RGB", (50, 50), "white")
        input_path = str(tmp_path / "test.jpg")
        output_path = str(tmp_path / "output.jpg")
        img.save(input_path, "JPEG")

        self.embedder.embed_in_jpeg(input_path, self.SAMPLE_METADATA, output_path)

        # Verify output exists and is a valid JPEG
        assert Path(output_path).exists()
        out_img = Image.open(output_path)
        assert out_img.format == "JPEG"

    def test_embed_in_png(self, tmp_path):
        # Create a test PNG
        img = Image.new("RGB", (50, 50), "white")
        input_path = str(tmp_path / "test.png")
        output_path = str(tmp_path / "output.png")
        img.save(input_path, "PNG")

        self.embedder.embed_in_png(input_path, self.SAMPLE_METADATA, output_path)

        # Verify output exists and is a valid PNG
        assert Path(output_path).exists()
        out_img = Image.open(output_path)
        assert out_img.format == "PNG"

    def test_embedded_png_contains_xmp(self, tmp_path):
        img = Image.new("RGB", (50, 50), "white")
        input_path = str(tmp_path / "test.png")
        output_path = str(tmp_path / "output.png")
        img.save(input_path, "PNG")

        self.embedder.embed_in_png(input_path, self.SAMPLE_METADATA, output_path)

        # Read back and check for XMP in PNG metadata
        out_img = Image.open(output_path)
        xmp_data = out_img.info.get("XML:com.adobe.xmp", "")
        assert "mkhub.de/ns/aif" in xmp_data
