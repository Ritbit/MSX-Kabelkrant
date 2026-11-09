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

    def test_original_renderer_exact(self):
        lines = set(self.output[:-1].split(b"\r\n"))
        for line in extract_original(self.original):
            self.assertIn(line.encode("ascii"), lines)

    def test_no_z80_binary_or_call_text(self):
        self.assertNotIn(b'KBLTXT.BIN', self.output)
        self.assertNotIn(b'CALL TEXT', self.output)

    def test_ascii_msdos_file(self):
        self.assertTrue(self.output.endswith(b"\r\n\x1a"))
        self.assertNotIn(b"\n\n", self.output)
