import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from make_full_z80_test import transform
from msx_basic_ascii import encode_msx_basic

ROOT = Path(__file__).resolve().parents[2]


class FullZ80DiskTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init = (ROOT / "src/KBLINIT.SYS").read_text(encoding="utf-8")
        loop = (ROOT / "src/LOOP.SYS").read_text(encoding="utf-8")
        cls.original_loop = loop
        cls.init, cls.loop, cls.calls = transform(init, loop)

    def test_all_seven_calls(self):
        self.assertEqual(self.calls, 7)
        self.assertEqual(self.loop.count("CALL TEXT(A$,X,Y,LT,K)"), 7)
        self.assertNotIn("GOSUB 2500", self.loop)

    def test_memory_and_original_usr_compatibility(self):
        self.assertIn('190 SETPAGE 0,1: CLS: BLOAD "KRANT3.SC7",S: SETPAGE 0,0: CLEAR 2000,&HC7FF', self.init)
        self.assertIn('195 BLOAD "KBLTXT.BIN",R', self.init)
        self.assertIn("105 CLEAR 1000,&HC7FF", self.loop)
        self.assertIn("DEFUSR=AD:DEFUSR2=AD+11: DEFUSR1=AD+25", self.init)

    def test_remove_only_unused_font_code_and_arrays(self):
        expected = []
        for line in self.original_loop.splitlines():
            if not line.strip():
                continue
            n = int(line.split()[0])
            if 2500 <= n <= 2890 or n in (1135, 1140):
                continue
            if n == 1050:
                line = '1050 DIM XK(60),YK(60)'
            elif n == 1130:
                line = '1130 COPY "XK.dat" TO XK: COPY "YK.DAT" TO YK'
            elif n == 190:
                line = line.replace('GOSUB 2200', 'GOTO 2200')
            elif n == 105:
                line = line.replace("CLEAR 1000:", "CLEAR 1000,&HC7FF:")
            line = line.replace("GOSUB 2500", "CALL TEXT(A$,X,Y,LT,K)")
            expected.append(line.replace("\u2014", "-"))
        self.assertEqual(self.loop.splitlines(), expected)
        self.assertNotIn("X(4,110)", self.loop)
        self.assertNotIn("2530 ", self.loop)
        self.assertIn("RUN \"LOOP.SYS\"", self.init)

    def test_page_cycle_does_not_leak_gosub_stack(self):
        # Page-loop exit is GOTO 140, not RETURN. It must enter via GOTO.
        self.assertIn('190 GOTO 2200', self.loop)
        self.assertNotIn('190 GOSUB 2200', self.loop)
        self.assertIn('3880 GOTO 140', self.loop)

    def test_exported_msx_ascii(self):
        self.assertTrue(encode_msx_basic(self.loop.encode("ascii")).endswith(b"\r\n\x1a"))


if __name__ == "__main__":
    unittest.main()
