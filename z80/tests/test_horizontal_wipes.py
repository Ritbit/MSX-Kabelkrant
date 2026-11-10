"""Wipe #3/#4 regression: original geometry, compiled bytes, packaged disk.

Must run AFTER assembly and disk packaging. A successful assembly is
not proof of direction: verify both binaries and both FAT12 images.
"""
from pathlib import Path
from struct import unpack_from
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[2]
BUILD = ROOT / "z80" / "build"
ASM = (ROOT / "z80" / "asm" / "wipe_horizontal_kernel.asm").read_text()
BASIC = (ROOT / "src" / "LOOP.SYS").read_text()


def load_bin(n):
    data = (BUILD / f"WIPE{n}.BIN").read_bytes()
    assert data[0] == 0xFE
    start, end, entry = unpack_from("<HHH", data, 1)
    assert (start, entry) == (0xC804, 0xC806)
    assert end == start + len(data) - 8
    return data


def disk_file(n, name):
    disk = BUILD / f"KBLWIPE{n}.DSK"
    assert disk.stat().st_size == 737280
    return subprocess.check_output(
        ["mcopy", "-i", str(disk), "::" + name, "-"], stderr=subprocess.PIPE
    )


class HorizontalWipeTests(unittest.TestCase):
    def test_reference_basic_direction(self):
        l3 = next(x for x in BASIC.splitlines() if x.startswith("3260 "))
        l4 = next(x for x in BASIC.splitlines() if x.startswith("3270 "))
        self.assertIn("FOR A = 0 TO 512  STEP 2", l3)
        self.assertIn("FOR A = 512 TO 0  STEP-2", l4)
        self.assertIn("LINE(A,50)-(A+1,212),0,BF", l3)
        self.assertIn("LINE(A,50)-(A+1,212),0,BF", l4)

    def test_exact_visible_pixel_geometry(self):
        forward = list(range(0, 512, 2))
        reverse = list(range(510, -1, -2))
        self.assertEqual(len(forward), 256)
        self.assertEqual(reverse, forward[::-1])
        self.assertEqual(forward[0], 0)
        self.assertEqual(forward[-1], 510)
        self.assertEqual({x for start in forward for x in (start, start+1)},
                         set(range(512)))
        self.assertIn("ld hl,50\n    ld (LmDY),hl", ASM)
        self.assertIn("ld hl,2\n    ld (LmNX),hl", ASM)
        self.assertIn("ld hl,162\n    ld (LmNY),hl", ASM)
        self.assertIn("ld a,080h", ASM)
        self.assertIn("call HorizontalWaitIdle", ASM)
        self.assertIn("call HorizontalWaitFrame", ASM)
        self.assertIn("ld a,4\n    ld (WipePaceCounter),a", ASM)
        self.assertIn("IF WIPE_RIGHT_TO_LEFT", ASM)
        self.assertIn("WIPE_RIGHT_TO_LEFT EQU 0",
                      (ROOT/"z80"/"asm"/"wipe_lr.asm").read_text())
        self.assertIn("WIPE_RIGHT_TO_LEFT EQU 1",
                      (ROOT/"z80"/"asm"/"wipe_rl.asm").read_text())

    def test_actual_machine_code_has_opposite_x_start(self):
        lr, rl = load_bin(3), load_bin(4)
        self.assertNotEqual(lr, rl, "reverse build compiled identically")
        # LD HL,firstX ; LD (LmDX),HL; LD HL,50
        self.assertIn(b"\x21\x00\x00\x22", lr[7:])
        self.assertIn(b"\x21\xfe\x01\x22", rl[7:])
        self.assertNotIn(b"\x21\xfe\x01\x22", lr[7:])
        # Guard against accidentally compiling both with same wrapper.
        self.assertEqual(rl[7:15], lr[7:15])  # vector and register prologue

    def test_disk_embeds_its_own_correct_binary_and_demo(self):
        for n, label in ((3, b"LEFT TO RIGHT"), (4, b"RIGHT TO LEFT")):
            with self.subTest(wipe=n):
                self.assertEqual(disk_file(n, f"WIPE{n}.BIN"), load_bin(n))
                boot = disk_file(n, "AUTOEXEC.BAS")
                self.assertIn(f'BLOAD "WIPE{n}.BIN",R'.encode(), boot)
                self.assertIn(label, boot)
                self.assertNotIn(f'BLOAD "WIPE{7-n}.BIN",R'.encode(), boot)
        self.assertNotEqual(disk_file(3, "AUTOEXEC.BAS"),
                            disk_file(4, "AUTOEXEC.BAS"))


if __name__ == "__main__":
    unittest.main()
