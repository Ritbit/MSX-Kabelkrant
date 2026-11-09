import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from make_combined_rom import combine, extension_source, COPY_PATTERN, ROM_OFFSET, ORG

ROOT = Path(__file__).resolve().parents[2]


class CombinedRomTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old = (ROOT / 'src/RAMDISK.BIN').read_bytes()

    def test_original_installer_and_rom_shape(self):
        payload = self.old[7:]
        self.assertEqual(payload.count(COPY_PATTERN), 1)
        self.assertEqual(payload[ROM_OFFSET:ROM_OFFSET + 6], b'ABA\x40\0\0')
        self.assertEqual(0x4000 + len(payload) - ROM_OFFSET, ORG)

    def test_only_copy_length_and_call_vector_change(self):
        mock_extension = bytes([0xc9] * 12)
        out = combine(self.old, mock_extension)
        self.assertEqual(out[:7], b'\xfe\x00\xc0' +
                         (0xc000 + len(out) - 8).to_bytes(2, 'little') +
                         b'\x00\xc0')
        original = bytearray(self.old[7:])
        updated = bytearray(out[7:7 + len(original)])
        ix = original.index(COPY_PATTERN)
        # Restore only explicitly patched bytes; everything else matches.
        updated[ix+4:ix+6] = original[ix+4:ix+6]
        updated[ROM_OFFSET+4:ROM_OFFSET+6] = original[ROM_OFFSET+4:ROM_OFFSET+6]
        self.assertEqual(updated, original)
        self.assertEqual(out[-len(mock_extension):], mock_extension)
        self.assertEqual(int.from_bytes(out[7+ix+4:7+ix+6], 'little'),
                         0x6f5 + len(mock_extension))
        self.assertEqual(int.from_bytes(out[7+ROM_OFFSET+4:7+ROM_OFFSET+6], 'little'),
                         ORG)

    def test_combined_asm_has_existing_text_handler(self):
        text = (ROOT / 'z80/asm/basic_text_demo.asm').read_text()
        asm = extension_source(text)
        self.assertIn('    ORG 046F5h', asm)
        self.assertIn("CallHandler:\n    push hl\n    ld hl,EmbeddedFonts", asm)
        self.assertIn("INCLUDE 'v9938_lmmm.asm'", asm)

    def test_overlarge_extension_rejected(self):
        with self.assertRaises(ValueError):
            combine(self.old, bytes(0x6000))


if __name__ == '__main__':
    unittest.main()
