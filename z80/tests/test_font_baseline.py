import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from make_font_baseline import make_program, extract_original, REFERENCE_OVERRIDES

class OriginalBasicFontBaseline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = (Path(__file__).resolve().parents[2] / "src" / "LOOP.SYS").read_text(encoding="latin-1")
        cls.output = make_program(cls.original)

    def test_all_four_fonts_called(self):
        for font in range(1, 5):
            self.assertIn(f"LT={font}:".encode(), self.output)

    def test_original_renderer_with_only_documented_changes(self):
        lines = set(self.output[:-1].split(b"\r\n"))
        for line in extract_original(self.original):
            self.assertIn(line.encode("ascii"), lines)
        self.assertEqual(set(REFERENCE_OVERRIDES), {2530, 2540, 2550, 2675, 2830})

    def test_uses_four_font_atlas_and_preserves_font_four(self):
        self.assertIn(b'BLOAD "KRANT3.SC7",S', self.output)
        self.assertIn(b'IF LT=1 THEN LINE(0,164)', self.output)
        self.assertIn(b'DATA 43,83,96,107,124,142,16', self.output)

    def test_no_z80_binary_or_call_text(self):
        self.assertNotIn(b'KBLTXT.BIN', self.output)
        self.assertNotIn(b'CALL TEXT', self.output)

    def test_ascii_msdos_file(self):
        self.assertTrue(self.output.endswith(b"\r\n\x1a"))
        self.assertNotIn(b"\n\n", self.output)
