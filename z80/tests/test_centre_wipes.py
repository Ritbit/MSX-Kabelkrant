"""Wipes 5/6: test independent geometry plus actual machine-code and FAT12.

This test runs after both demo disks have been assembled and populated.
Do not publish on static-source checks alone (regression from wipe #2).
"""
import subprocess
import unittest
from pathlib import Path
from struct import unpack_from

ROOT = Path(__file__).resolve().parents[2]
BUILD = ROOT / "z80" / "build"
ASM = (ROOT / "z80" / "asm" / "wipe_centre_kernel.asm").read_text()
BASIC = (ROOT / "src" / "LOOP.SYS").read_text()


def read_binary(n):
    data = (BUILD / f"WIPE{n}.BIN").read_bytes()
    assert data[0] == 0xFE
    start, end, entry = unpack_from("<HHH", data, 1)
    assert (start, entry) == (0xC804, 0xC806)
    assert end == start + len(data) - 8
    return data


def disk_read(n, name):
    disk = BUILD / f"KBLWIPE{n}.DSK"
    assert disk.stat().st_size == 737280
    return subprocess.check_output(
        ["mcopy", "-i", str(disk), f"::{name}", "-"], stderr=subprocess.PIPE
    )


class CentreWipesTests(unittest.TestCase):
    def test_original_basic_reference(self):
        top_bottom = next(x for x in BASIC.splitlines() if x.startswith("3280 "))
        left_right = next(x for x in BASIC.splitlines() if x.startswith("3290 "))
        self.assertIn("FOR A = 0 TO 80   STEP 2", top_bottom)
        self.assertIn("LINE(0,A+50)-(512,A+51),0,BF", top_bottom)
        self.assertIn("LINE(0,211-A)-(512,212-A),0,BF", top_bottom)
        self.assertIn("FOR A = 0 TO 256  STEP 2", left_right)
        self.assertIn("LINE(A,50)-(A+1,212),0,BF", left_right)
        self.assertIn("LINE(512-A,50)-(511-A,212),0,BF", left_right)

    def test_top_bottom_visible_coverage(self):
        near = [50+2*i for i in range(41)]
        far = [210-2*i for i in range(41)]
        self.assertEqual((near[0],far[0]), (50,210))
        self.assertEqual((near[-1],far[-1]), (130,130))
        visible = {v for y in near+far for v in (y,y+1)}
        self.assertEqual(visible, set(range(50,212)))

    def test_left_right_visible_coverage(self):
        near = [2*i for i in range(128)]
        far = [510-2*i for i in range(128)]
        self.assertEqual((near[0],far[0]), (0,510))
        self.assertEqual((near[-1],far[-1]), (254,256))
        visible = {v for x in near+far for v in (x,x+1)}
        self.assertEqual(visible, set(range(512)))
        self.assertEqual(set(near).intersection(far), set())

    def test_command_shape_and_pacing(self):
        self.assertIn("IF WIPE_FROM_SIDES", ASM)
        self.assertIn("ld a,080h", ASM)
        self.assertIn("ld hl,512\n    ld (LmNX),hl", ASM)
        self.assertIn("ld hl,162\n    ld (LmNY),hl", ASM)
        self.assertIn("call WipeWaitIdle", ASM)
        self.assertIn("call WipeWaitFrame", ASM)
        self.assertIn("ld a,41", ASM)
        self.assertIn("ld a,128", ASM)
        self.assertIn("WIPE_FROM_SIDES EQU 0",
                      (ROOT/"z80"/"asm"/"wipe_tb_centre.asm").read_text())
        self.assertIn("WIPE_FROM_SIDES EQU 1",
                      (ROOT/"z80"/"asm"/"wipe_lr_centre.asm").read_text())

    def test_compiled_binary_axes_and_counts_are_different(self):
        five = read_binary(5)
        six = read_binary(6)
        self.assertNotEqual(five, six, "both wipes compiled to same image")
        body5, body6 = five[7:], six[7:]
        # LD HL,210; LD (WipeFar),HL; and LD HL,510 respectively.
        self.assertIn(b"\x21\xd2\x00\x22", body5)
        self.assertIn(b"\x21\xfe\x01\x22", body6)
        self.assertNotIn(b"\x21\xfe\x01\x22", body5)
        self.assertNotIn(b"\x21\xd2\x00\x22", body6)
        # 41 versus 128 near/far pairs (LD A,n ; LD (nn),A).
        self.assertIn(b"\x3e\x29\x32", body5)
        self.assertIn(b"\x3e\x80\x32", body6)

    def test_disk_contains_correct_payload_only(self):
        for n, description in ((5,b"TOP BOTTOM TO CENTRE"),
                               (6,b"LEFT RIGHT TO CENTRE")):
            with self.subTest(n=n):
                self.assertEqual(disk_read(n, f"WIPE{n}.BIN"),
                                 read_binary(n))
                boot = disk_read(n, "AUTOEXEC.BAS")
                self.assertIn(f'BLOAD "WIPE{n}.BIN",R'.encode(), boot)
                self.assertIn(description, boot)
                other = 11-n
                self.assertNotIn(f'BLOAD "WIPE{other}.BIN",R'.encode(), boot)
        self.assertNotEqual(disk_read(5,"AUTOEXEC.BAS"),
                            disk_read(6,"AUTOEXEC.BAS"))


if __name__ == "__main__":
    unittest.main()
