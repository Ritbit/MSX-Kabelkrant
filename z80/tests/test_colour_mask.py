"""Regression: colour-mask path must preserve outline palette index 1.

The released BASIC renderer applies LINE(...),K,BF,AND to the whole
glyph, followed by TPSET.  Keep these semantics when optimizing Z80.
"""
import unittest
from pathlib import Path

ASM = (Path(__file__).resolve().parents[1] / "asm" / "basic_text_demo.asm").read_text()
START = ASM.index("GlyphBlitColoured:\n")
END = ASM.index("ColourOutputX: dw 0", START)
PATH = ASM[START:END]


class ColourMaskTests(unittest.TestCase):
    def test_palette_bitwise_mask_matches_basic(self):
        for pixel, expected in [(0, 0), (1, 1), (13, 13), (14, 12), (15, 13)]:
            self.assertEqual(pixel & 13, expected)
        # Palette 1 is the dark outline, not transparent.
        self.assertEqual(1 & 13, 1)
        self.assertEqual(15 & 13, 13)
        self.assertEqual(0 & 13, 0)

    def test_only_one_and_mask_and_one_transparent_copy(self):
        self.assertIn("ld a,(text_colour)\n    ld (LmCLR),a", PATH)
        self.assertEqual(PATH.count("ld a,081h"), 1)  # LMMV AND K
        self.assertEqual(PATH.count("ld a,090h"), 1)  # LMMM IMP
        self.assertEqual(PATH.count("ld a,098h"), 1)  # LMMM TIMP
        self.assertNotIn("ld a,14\n", PATH)
        self.assertNotIn("ld a,09Ch", PATH)  # TNOT drops original outline
        self.assertNotIn("ld a,09Ah", PATH)  # TOR no longer necessary

    def test_empty_string_never_enters_ldir(self):
        # Z80 LDIR with BC=0 copies a full 64KiB: input can be empty.
        source = ASM
        start = source.index("    ld a,(text_length)\n    ld c,a\n    ld b,0")
        end = source.index("    ld ix,FRESTR", start)
        copy = source[start:end]
        self.assertIn("    or a\n    jr z,.text_copied\n    ldir\n.text_copied:", copy)
        self.assertEqual(copy.count("    ldir"), 1)

    def test_mask_is_applied_before_transparent_copy(self):
        self.assertLess(PATH.index("ld a,090h"), PATH.index("ld a,081h"))
        self.assertLess(PATH.index("ld a,081h"), PATH.index("ld a,098h"))
        self.assertIn("ld hl,256+190", PATH)  # page-1 scratch safely below font


if __name__ == "__main__":
    unittest.main()
