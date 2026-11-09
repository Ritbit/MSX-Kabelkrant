import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from msx_basic_ascii import encode_msx_basic, validate_msx_basic

class MsxBasicTests(unittest.TestCase):
    def test_converts_lf_to_crlf_and_eof(self):
        out = encode_msx_basic(b'10 PRINT "OK"\n20 END\n')
        self.assertEqual(out, b'10 PRINT "OK"\r\n20 END\r\n\x1a')
        validate_msx_basic(out)

    def test_line_length_rejected(self):
        with self.assertRaises(ValueError):
            encode_msx_basic(b'10 REM ' + b'x'*240 + b'\n')

    def test_duplicate_number_rejected(self):
        with self.assertRaises(ValueError):
            encode_msx_basic(b'10 PRINT 1\n10 PRINT 2\n')

    def test_actual_demo_source(self):
        source = Path(__file__).resolve().parents[1] / 'asm' / 'ASMTEXT.BAS'
        output = encode_msx_basic(source.read_bytes())
        validate_msx_basic(output)
        self.assertEqual(output.count(b'\r\n'), len(source.read_text().splitlines()))
        self.assertLessEqual(max(len(l) for l in output[:-1].split(b'\r\n')), 240)

if __name__ == "__main__":
    unittest.main()
