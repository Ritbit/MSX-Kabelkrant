"""Validate original MSX X.DAT coverage for ASCII 33..127.

Uses precisely the same KBF1 records as the Z80 renderer. Font 3's last
character (127) is missing a final width boundary in the original file;
the runtime must treat that glyph as a space, not issue a negative-width
VDP command. This is source-data coverage, not a pixel-correctness test.
"""
import sys
import struct
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from convert_fonts import convert

LIMITS = {1: (52, 96, 0), 2: (56, 96, 0), 3: (43, 83, 96), 4: (49, 96, 0)}


def offset_for(font, ascii_code):
    i = ascii_code - 33
    l1, l2, l3 = LIMITS[font]
    if i < l1:
        return i
    if i < l2:
        return i + 1
    if l3 and i < l3:
        return i + 2
    return None


class AsciiCoverage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        raw = (Path(__file__).resolve().parents[2] / 'src' / 'X.DAT').read_bytes()
        data = convert(raw)
        cls.coords = {}
        pos = 8
        for font in range(1, 5):
            count = struct.unpack_from('<H', data, pos + 9)[0]
            cls.coords[font] = struct.unpack_from('<' + 'h'*count, data, pos + 11)
            pos += 11 + count*2

    def test_all_printable_ascii_mappings_are_bounded(self):
        for font, values in self.coords.items():
            for code in range(33, 128):
                i = offset_for(font, code)
                if i is None:
                    continue
                self.assertLess(i+1, len(values), (font, code))
                w = values[i+1] - values[i]
                if font == 3 and code == 127:
                    # The original data ends here: x[96]=132; x[97]=-1.
                    # The Z80 lookup deliberately rejects negative widths.
                    self.assertLess(w, 0)
                    continue
                self.assertTrue(0 < w <= 18, (font, code, i, w))

    def test_four_font_ascii_coverage(self):
        for font, values in self.coords.items():
            supported = sum(1 for code in range(33,128)
                            if (lambda i: i is not None and 0 < values[i+1]-values[i] <= 18)(offset_for(font,code)))
            self.assertEqual(supported, 94 if font == 3 else 95)

    def test_original_font2_typo_corrected(self):
        self.assertEqual(self.coords[2][19:22], (148, 158, 166))


if __name__ == '__main__':
    unittest.main()
