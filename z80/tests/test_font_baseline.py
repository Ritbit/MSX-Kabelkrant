import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from make_font_baseline import make_program, extract_original

class OriginalBasicFontBaseline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = (Path(__file__).resolve().parents[2] / "src" / "LOOP.SYS").read_text(encoding="latin-1")
        cls.output = make_program(cls.original)

    def test_all_four_fonts_called(self):
        for font in range(1, 5):
            self.assertIn(f"LT={font}:".encode(), self.output)

    def test_renderer_from_production_source_exact(self):
        lines = set(self.output[:-1].split(b"\r\n"))
        for line in extract_original(self.original):
            self.assertIn(line.encode("ascii"), lines)
        self.assertIn(b"IF NOT BT THEN COPY(", self.output)
        self.assertIn(b"IF BT THEN COPY(", self.output)

    def test_uses_four_font_atlas_and_preserves_font_four(self):
        self.assertIn(b'BLOAD "KRANT3.SC7",S', self.output)
        self.assertIn(b"IF BT THEN INTERVAL OFF:SETPAGE 0,1:LINE(0,190)", self.output)
        self.assertIn(b"DATA 43,83,96,107,124,142,16", self.output)
        self.assertIn(b"DATA 52,96,00,051,066,000,14", self.output)

    def test_font2_coordinate_fix(self):
        self.assertIn(b"65 X(2,20)=158", self.output)
        self.assertIn("1135 X(2,20)=158", self.original)

    def test_colour_and_alignment_baseline(self):
        out = make_program(self.original, colour=True)
        self.assertIn(b"K=13", out)
        self.assertIn(b"X=-505", out)
        self.assertIn(b"IF K<>15 THEN", out)
        self.assertTrue(out.endswith(b"\r\n\x1a"))

    def test_no_z80_binary_or_call_text(self):
        self.assertNotIn(b'KBLTXT.BIN', self.output)
        self.assertNotIn(b'CALL TEXT', self.output)

    def test_ascii_msdos_file(self):
        self.assertTrue(self.output.endswith(b"\r\n\x1a"))
        self.assertNotIn(b"\n\n", self.output)
