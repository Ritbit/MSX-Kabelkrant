"""Wipes 7/8: source, coverage, assembled BLOAD bytes and disk payloads."""
from pathlib import Path
from struct import unpack_from
import subprocess
import unittest

ROOT=Path(__file__).resolve().parents[2]
BUILD=ROOT/"z80"/"build"
SOURCE=(ROOT/"src"/"LOOP.SYS").read_text()
ASM=(ROOT/"z80"/"asm"/"wipe_outward_kernel.asm").read_text()

def binary(n):
    b=(BUILD/f"WIPE{n}.BIN").read_bytes()
    assert b[0]==0xFE
    start,end,entry=unpack_from("<HHH",b,1)
    assert (start,entry)==(0xC804,0xC806)
    assert end==start+len(b)-8
    return b

def disk_read(n,name):
    disk=BUILD/f"KBLWIPE{n}.DSK"
    assert disk.stat().st_size==737280
    return subprocess.check_output(["mcopy","-i",str(disk),f"::{name}","-"],stderr=subprocess.PIPE)

class OutwardTests(unittest.TestCase):
    def test_basic_semantics(self):
        a=next(x for x in SOURCE.splitlines() if x.startswith("3300 "))
        b=next(x for x in SOURCE.splitlines() if x.startswith("3310 "))
        self.assertIn("FOR A = 80 TO 0   STEP-2",a)
        self.assertIn("FOR A = 256 TO 0  STEP-2",b)

    def test_vertical_covers_full_visible_region_without_touching_title(self):
        near=[130-2*i for i in range(41)]
        far=[130+2*i for i in range(41)]
        self.assertEqual((near[0],far[0]),(130,130))
        self.assertEqual((near[-1],far[-1]),(50,210))
        pixels={y for v in near+far for y in (v,v+1)}
        self.assertEqual(pixels,set(range(50,212)))
        self.assertNotIn(49,pixels)

    def test_horizontal_covers_all_columns(self):
        near=[254-2*i for i in range(128)]
        far=[256+2*i for i in range(128)]
        self.assertEqual((near[0],far[0]),(254,256))
        self.assertEqual((near[-1],far[-1]),(0,510))
        pixels={x for v in near+far for x in (v,v+1)}
        self.assertEqual(pixels,set(range(512)))

    def test_command_contract(self):
        self.assertIn("call LmmmLaunch",ASM)
        self.assertIn("call WipeWaitIdle",ASM)
        self.assertIn("call WipeWaitFrame",ASM)
        self.assertIn("ld a,080h",ASM)
        self.assertIn("ld a,41",ASM)
        self.assertIn("ld a,128",ASM)
        self.assertIn("WIPE_FROM_SIDES EQU 0",(ROOT/"z80"/"asm"/"wipe_tb_outward.asm").read_text())
        self.assertIn("WIPE_FROM_SIDES EQU 1",(ROOT/"z80"/"asm"/"wipe_lr_outward.asm").read_text())

    def test_compiled_directions_and_counts(self):
        b7,b8=binary(7),binary(8)
        self.assertNotEqual(b7,b8)
        # LD HL,130 / LD (WipeNear),HL ; far 130
        self.assertIn(b"\x21\x82\x00\x22",b7[7:])
        # LD HL,254 and LD HL,256 for X sides
        self.assertIn(b"\x21\xfe\x00\x22",b8[7:])
        self.assertIn(b"\x21\x00\x01\x22",b8[7:])
        self.assertIn(b"\x3e\x29\x32",b7[7:]) # 41 pairs
        self.assertIn(b"\x3e\x80\x32",b8[7:]) # 128 pairs
        # Do not globally exclude LD A,80h: BOTH variants use 80h for LMMV.

    def test_exact_disk_contents(self):
        for n,label in ((7,b"CENTRE TO TOP BOTTOM"),(8,b"CENTRE TO LEFT RIGHT")):
            with self.subTest(n=n):
                self.assertEqual(disk_read(n,f"WIPE{n}.BIN"),binary(n))
                boot=disk_read(n,"AUTOEXEC.BAS")
                self.assertIn(f'BLOAD "WIPE{n}.BIN",R'.encode(),boot)
                self.assertIn(label,boot)
                self.assertNotIn(f'BLOAD "WIPE{15-n}.BIN",R'.encode(),boot)

if __name__=="__main__":
    unittest.main()
