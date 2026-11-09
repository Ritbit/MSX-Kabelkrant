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
        init = (ROOT / "src/KBLINIT.SYS").read_text(encoding="ascii")
        loop = (ROOT / "src/LOOP.SYS").read_text(encoding="ascii")
        cls.original_init = init
        cls.original_loop = loop
        cls.init, cls.loop, cls.calls = transform(init, loop)

    def test_only_seven_calls_and_keep_reference(self):
        self.assertEqual(self.calls, 7)
        self.assertEqual(self.loop.count("CALL TEXT(A$,X,Y,LT,K)"), 7)
        self.assertIn("2500 '", self.loop)
        self.assertIn("2690 ", self.loop)

    def test_load_after_clear_in_normal_init(self):
        self.assertIn('190 SETPAGE 0,1: CLS: BLOAD "KRANT3.SC7",S: SETPAGE 0,0: CLEAR 2000,&HC7FF',self.init)
        self.assertIn('195 BLOAD "KBLTXT.BIN",R',self.init)
        self.assertLess(self.init.index("190 SETPAGE"),self.init.index("195 BLOAD"))
        self.assertLess(self.init.index("195 BLOAD"),self.init.index("210 RESTORE"))

    def test_all_non_text_code_preserved(self):
        original = self.original_loop.splitlines()
        patched = self.loop.splitlines()
        self.assertEqual(len(original), len(patched))
        for a, b in zip(original, patched):
            if "GOSUB 2500" in a:
                self.assertEqual(b,a.replace("GOSUB 2500","CALL TEXT(A$,X,Y,LT,K)"))
            else:
                self.assertEqual(a,b)
        self.assertIn("RUN \"LOOP.SYS\"",self.init)
        self.assertIn("DEFUSR=AD:DEFUSR2=AD+11: DEFUSR1=AD+25",self.init)

    def test_encoded_msx_text_is_safe(self):
        self.assertTrue(encode_msx_basic(self.loop.encode("ascii")).endswith(b"\r\n\x1a"))


if __name__ == "__main__":
    unittest.main()
