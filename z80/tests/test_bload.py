import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from make_bload import convert
class BloadTests(unittest.TestCase):
    def test_header(self):
        import struct
        d=convert(b"hello")
        self.assertEqual(d[:7],b"\xfe"+struct.pack("<HHH",0xC004,0xC008,0xC006))
        self.assertEqual(d[7:],b"hello")
    def test_reject_overflow(self):
        with self.assertRaises(ValueError):
            convert(b"x"*12300)
if __name__ == "__main__":
    unittest.main()
