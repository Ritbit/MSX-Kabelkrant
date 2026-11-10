"""Regression tests against the exact published one-BLOAD MSX disk image.

Executed after FAT12 packaging, before preview publication. No system ROMs
needed; runtime/editor behaviour is tested separately.
"""
from pathlib import Path
import struct
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
BUILD = ROOT / "z80" / "build"
ONE = BUILD / "KBLONEFILE.DSK"
BASE = BUILD / "stable" / "assets" / "kabelkrant-6.2b.dsk"
sys.path.insert(0, str(ROOT / "z80" / "tools"))
from make_onefile_preview import parse_bload


def read_file(image, name):
    return subprocess.check_output(
        ["mcopy", "-i", str(image), "::" + name, "-"], stderr=subprocess.PIPE
    )


def filenames(image):
    output = subprocess.check_output(
        ["mdir", "-b", "-i", str(image), "::"], text=True
    )
    return [line.strip().rsplit("/", 1)[-1].upper()
            for line in output.splitlines() if line.strip()]


class OnefileDiskTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        for path in (ONE, BASE):
            if not path.is_file():
                raise RuntimeError("Missing built disk: " + str(path))

    def test_fat12_disk_size(self):
        self.assertEqual(ONE.stat().st_size, 737280)

    def test_composite_bload_preserves_original_ramdisk(self):
        combined = read_file(ONE, "RAMDISK.BIN")
        self.assertEqual(combined, (BUILD / "KBLRAMTX.BIN").read_bytes())
        start, end, entry, payload = parse_bload(combined)
        self.assertEqual((start, entry), (0xC000, 0xC000))
        self.assertGreater(end, 0xC806)
        original = (ROOT / "src" / "RAMDISK.BIN").read_bytes()
        _s, _e, _x, old_payload = parse_bload(original)
        self.assertEqual(payload[:len(old_payload)], old_payload)
        self.assertEqual(payload[0x804:], (BUILD / "KBLTXT.BIN").read_bytes()[7:])

    def test_onefile_initializer_is_embedded(self):
        init = read_file(ONE, "KBLINIT.SYS")
        self.assertEqual(init, (BUILD / "onefile" / "KBLINIT.SYS").read_bytes())
        self.assertIn(b"112 CLEAR 2000,&HC7FF", init)
        self.assertIn(b"195 DEFUSR3=&HC806", init)
        self.assertNotIn(b'BLOAD "KBLTXT.BIN"', init)

    def test_onefile_loop_is_embedded(self):
        loop = read_file(ONE, "LOOP.SYS")
        self.assertEqual(loop, (BUILD / "onefile" / "LOOP.SYS").read_bytes())
        self.assertIn(b"190 GOTO 2200", loop)
        self.assertIn(b"CALL TEXT(A$,X,Y,LT,K)", loop)

    def test_unmodified_contents_and_original_fallback(self):
        before, after = set(filenames(BASE)), set(filenames(ONE))
        self.assertIn("RAMDISK.BIN", before)
        self.assertEqual(after - before, {"LOOPBAS.SYS"})
        self.assertEqual(before - after, set())
        self.assertEqual(read_file(ONE, "LOOPBAS.SYS"),
                         read_file(BASE, "LOOP.SYS"))
        changed = {"RAMDISK.BIN", "KBLINIT.SYS", "LOOP.SYS"}
        for name in sorted(before - changed):
            with self.subTest(name=name):
                self.assertEqual(read_file(ONE, name), read_file(BASE, name))


if __name__ == "__main__":
    unittest.main()
