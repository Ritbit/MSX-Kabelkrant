"""Structure and preservation checks for the *unproven* one-BLOAD preview."""
import sys
import unittest
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "z80" / "tools"))
from make_onefile_preview import combine, parse_bload, RAM_START, RAM_END, TEXT_START, TEXT_ENTRY
from make_full_z80_test import transform

def bload(start, entry, payload):
    return b"\xfe" + struct.pack("<HHH", start, start + len(payload) - 1, entry) + payload


class OnefilePreviewTests(unittest.TestCase):
    def test_real_historical_ramdisk_layout(self):
        start, end, entry, payload = parse_bload((ROOT/"src"/"RAMDISK.BIN").read_bytes())
        self.assertEqual((start, end, entry), (0xC000, 0xC7EF, 0xC000))
        self.assertEqual(len(payload), 0x7F0)

    def test_composite_preserves_original_installer_and_address(self):
        raw = bytes([i & 0xff for i in range(0x7F0)])
        text = bytes([0xC3, 0x10, 0xC8, 0xC9, 0x00])
        merged = combine(bload(RAM_START, RAM_START, raw),
                         bload(TEXT_START, TEXT_ENTRY, text))
        start, end, entry, body = parse_bload(merged)
        self.assertEqual((start, entry), (RAM_START, RAM_START))
        self.assertEqual(end, TEXT_START + len(text) - 1)
        self.assertEqual(body[:len(raw)], raw)
        self.assertEqual(body[len(raw):TEXT_START-RAM_START], bytes(0x14))
        self.assertEqual(body[TEXT_START-RAM_START:], text)

    def test_wrong_layout_fails_closed(self):
        with self.assertRaises(ValueError):
            combine(bload(0xC001, 0xC001, bytes(0x7EF)),
                    bload(TEXT_START, TEXT_ENTRY, b"x"))
        with self.assertRaises(ValueError):
            combine(bload(RAM_START, RAM_START, bytes(0x7F0)),
                    bload(0xC7F0, 0xC7F2, b"x"))

    def test_onefile_initializer_only_changes_install_step(self):
        init = (ROOT/"src"/"KBLINIT.SYS").read_text()
        loop = (ROOT/"src"/"LOOP.SYS").read_text()
        normal_init, normal_loop, normal_count = transform(init, loop)
        single_init, single_loop, single_count = transform(init, loop, one_file=True)
        self.assertEqual(normal_loop, single_loop)
        self.assertEqual(normal_count, single_count)
        self.assertEqual(
            [line for line in single_init.splitlines() if not line.startswith(('112 ', '188 ', '193 '))],
            normal_init.replace('195 BLOAD "KBLTXT.BIN",R',
                                '195 DEFUSR3=&HC806: A=USR3(0)').splitlines())
        for checkpoint, code in [(112, "E1"), (188, "E2"), (193, "E3")]:
            line = next(line for line in single_init.splitlines() if line.startswith(f"{checkpoint} "))
            self.assertIn("PEEK(&HC806)<>33", line)
            self.assertIn(f"ONEFILE ERROR {code}", line)
        self.assertNotIn('BLOAD "KBLTXT.BIN"', single_init)


if __name__ == "__main__":
    unittest.main()
