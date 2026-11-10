"""Validate the *built* full MSX2 alpha disk, not just its source generator.

Uses mtools to inspect the FAT12 disk as shipped. No MSX ROMs required.
"""
from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess
import struct
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
BUILD = ROOT / "z80" / "build"
IMAGE = BUILD / "KBLZ80TEST.DSK"
BASELINE = BUILD / "stable" / "assets" / "kabelkrant-6.2b.dsk"


def disk_file(image: Path, name: str) -> bytes:
    # mcopy -n sends the exact FAT file bytes to stdout without LF conversion.
    return subprocess.check_output(
        ["mcopy", "-i", str(image), f"::{name}", "-"],
        stderr=subprocess.PIPE,
    )


class FullDiskImageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not IMAGE.is_file() or not BASELINE.is_file():
            raise RuntimeError("Build the full preview and checkout main baseline first")
        cls.image = IMAGE
        cls.baseline = BASELINE

    def test_disk_geometry(self):
        self.assertEqual(self.image.stat().st_size, 737280)

    def test_text_binary_load_address(self):
        data = disk_file(self.image, "KBLTXT.BIN")
        self.assertGreater(len(data), 7)
        self.assertEqual(data[0], 0xFE)
        load, end, entry = struct.unpack_from("<HHH", data, 1)
        self.assertEqual(load, 0xC804)
        self.assertEqual(entry, 0xC806)
        self.assertEqual(end - load + 1, len(data) - 7)
        self.assertLessEqual(end, 0xD803)
        self.assertEqual(data, (BUILD / "KBLTXT.BIN").read_bytes())

    def test_generated_loop_matches_disk_and_has_safe_cycle(self):
        loop = disk_file(self.image, "LOOP.SYS")
        self.assertEqual(loop, (BUILD / "full" / "LOOP.SYS").read_bytes())
        self.assertIn(b"190 GOTO 2200", loop)
        self.assertNotIn(b"190 GOSUB 2200", loop)
        self.assertIn(b"3880 GOTO 140", loop)
        self.assertIn(b"CALL TEXT(A$,X,Y,LT,K)", loop)
        self.assertNotIn(b"GOSUB 2500", loop)

    def test_original_basic_fallback_is_preserved(self):
        original = disk_file(self.baseline, "LOOP.SYS")
        self.assertEqual(disk_file(self.image, "LOOPBAS.SYS"), original)

    def test_generated_initializer_matches_disk(self):
        init = disk_file(self.image, "KBLINIT.SYS")
        self.assertEqual(init, (BUILD / "full" / "KBLINIT.SYS").read_bytes())
        self.assertIn(b'BLOAD "KBLTXT.BIN",R', init)
        self.assertIn(b"CLEAR 2000,&HC7FF", init)

    def test_other_files_are_identical_to_stable_release(self):
        lines = subprocess.check_output(
            ["mdir", "-b", "-i", str(self.baseline), "::"],
            text=True,
        ).splitlines()
        files = [line.rsplit("/", 1)[-1] for line in lines if line.strip()]
        self.assertGreaterEqual(len(files), 25)
        replaced = {"LOOP.SYS", "KBLINIT.SYS"}
        for name in files:
            if name.upper() in replaced:
                continue
            with self.subTest(file=name):
                self.assertEqual(
                    disk_file(self.image, name),
                    disk_file(self.baseline, name),
                )


if __name__ == "__main__":
    unittest.main()
