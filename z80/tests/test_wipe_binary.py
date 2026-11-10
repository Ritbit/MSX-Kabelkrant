"""Verify the *actual assembled binaries* for wipe #1 and #2 are opposite.

This test runs after SjASMPlus, not just against assembly source.
"""
import unittest
from pathlib import Path
from struct import unpack_from

BUILD = Path(__file__).resolve().parents[1] / "build"

class WipeBinaryTests(unittest.TestCase):
    def test_direction_encoded_in_actual_machine_code(self):
        down = (BUILD / "WIPE1.BIN").read_bytes()
        up = (BUILD / "WIPE2.BIN").read_bytes()
        self.assertNotEqual(down, up, "both wipe binaries are identical")
        self.assertEqual(down[0], 0xFE)
        self.assertEqual(up[0], 0xFE)
        self.assertEqual(unpack_from("<HHH", down, 1)[0::2], (0xC804, 0xC806))
        self.assertEqual(unpack_from("<HHH", up, 1)[0::2], (0xC804, 0xC806))
        # On entry: DW pointer; PUSH AF/BC/DE/HL; LD HL,0 / LD(nn),HL;
        # and then LD HL, first-Y. Assert which immediate Y each disk loads.
        # Look for byte sequence LD HL,Y ; LD (LmDY),HL ; LD HL,512.
        body_down, body_up = down[7:], up[7:]
        self.assertIn(b"\x21\x32\x00\x22", body_down, "wipe1 missing start Y=50")
        self.assertIn(b"\x21\xd2\x00\x22", body_up, "wipe2 missing start Y=210")
        self.assertNotIn(b"\x21\xd2\x00\x22", body_down, "wipe1 unexpectedly reverse")
        self.assertNotIn(b"\x21\x32\x00\x22", body_up, "wipe2 unexpectedly forward")

if __name__ == "__main__":
    unittest.main()
