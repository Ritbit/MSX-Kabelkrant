import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from convert_fonts import convert, decode_number

class FontConversionTests(unittest.TestCase):
    def test_mbf_numbers(self):
        self.assertEqual(decode_number(bytes.fromhex('4140000000000000')), 4)
        self.assertEqual(decode_number(bytes.fromhex('c110000000000000')), -1)

    def test_original_xdat(self):
        source = Path(__file__).resolve().parents[2] / 'src/X.DAT'
        result = convert(source.read_bytes())
        self.assertTrue(result.startswith(b'KBF1\x01\x04\0\0'))
        self.assertEqual(len(result), 838)
        pos, lengths = 8, []
        for font_id in range(1, 5):
            self.assertEqual(result[pos], font_id)
            count = int.from_bytes(result[pos+9:pos+11], 'little')
            lengths.append(count)
            pos += 11 + 2 * count
        self.assertEqual(lengths, [98, 99, 98, 98])
        self.assertEqual(pos, len(result))

if __name__ == '__main__':
    unittest.main()
