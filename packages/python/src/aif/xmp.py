# Adaptive Image Format (AIF) — XMP Embedder
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

"""XMP metadata embedding for JPEG and PNG images."""

from __future__ import annotations

from PIL import Image
from PIL.PngImagePlugin import PngInfo


class XMPEmbedder:
    """Embeds AIF XMP metadata into existing images."""

    AIF_NS = "https://mkhub.de/ns/aif/1.0/"

    def embed_in_jpeg(self, image_path: str, aif_metadata: dict, output_path: str) -> None:
        """Embed XMP into JPEG via APP1 marker."""
        xmp_string = self._build_xmp_string(aif_metadata)
        img = Image.open(image_path)
        img.save(output_path, "JPEG", xmp=xmp_string.encode("utf-8"))

    def embed_in_png(self, image_path: str, aif_metadata: dict, output_path: str) -> None:
        """Embed XMP into PNG via iTXt chunk."""
        xmp_string = self._build_xmp_string(aif_metadata)
        img = Image.open(image_path)
        pnginfo = PngInfo()
        pnginfo.add_text("XML:com.adobe.xmp", xmp_string)
        img.save(output_path, "PNG", pnginfo=pnginfo)

    def _build_xmp_string(self, meta: dict) -> str:
        """Build the complete XMP string with AIF namespace."""
        pairs = "\n      ".join(f'aif:{k}="{v}"' for k, v in meta.items())
        return (
            '<?xpacket begin="\ufeff" id="W5M0MpCehiHzreSzNTczkc9d"?>\n'
            '<x:xmpmeta xmlns:x="adobe:ns:meta/">\n'
            '  <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">\n'
            "    <rdf:Description\n"
            '      rdf:about=""\n'
            f'      xmlns:aif="{self.AIF_NS}"\n'
            f"      {pairs}\n"
            "    />\n"
            "  </rdf:RDF>\n"
            "</x:xmpmeta>\n"
            '<?xpacket end="w"?>'
        )
