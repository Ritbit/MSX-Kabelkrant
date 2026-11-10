"""Interlaced wipe #11/#12: source geometry, machine-code, disk checks.

Run after assembly and disk packaging. The binary checks are intentionally
based on observable opcodes, not just assembly source selectors.
"""
from pathlib import Path
from struct import unpack_from
import subprocess
import unittest

ROOT=Path(__file__).resolve().parents[2]
BUILD=ROOT/"z80"/"build"
SOURCE=(ROOT/"src"/"LOOP.SYS").read_text()
ASM=(ROOT/"z80"/"asm"/"wipe_interlaced_kernel.asm").read_text()

def binary(n):
    data=(BUILD/f"WIPE{n}.BIN").read_bytes()
    assert data[0]==0xfe
    start,end,entry=unpack_from("<HHH",data,1)
    assert (start,entry)==(0xc804,0xc806)
    assert end==start+len(data)-8
    return data

def disk_read(n,name):
    disk=BUILD/f"KBLWIPE{n}.DSK"
    assert disk.stat().st_size==737280
    return subprocess.check_output(["mcopy","-i",str(disk),f"::{name}","-"],stderr=subprocess.PIPE)

class InterlacedWipes(unittest.TestCase):
    def test_baseline_semantics(self):
        v=next(x for x in SOURCE.splitlines() if x.startswith("3340 "))
        h=next(x for x in SOURCE.splitlines() if x.startswith("3350 "))
        self.assertIn("FOR A = 50 TO 212 STEP 2",v)
        self.assertIn("257-A",v)
        self.assertIn("258-A",v)
        self.assertIn("FOR A = 0 TO 512  STEP 2",h)
        self.assertIn("513-A",h)
        self.assertIn("LINE(A,50)-(A,212),0,B",h)

    def test_vertical_visible_rows(self):
        upper=list(range(50,212,2))
        mirrored=[257-a for a in upper if 257-a >= 50]
        rows={y for start in upper+mirrored for y in (start,start+1)}
        self.assertEqual(rows,set(range(50,212)))
        self.assertEqual((upper[0],upper[-1]),(50,210))
        self.assertEqual(mirrored[0],207)
        self.assertTrue(min(rows)>=50)
        self.assertTrue(max(rows)<=211)

    def test_horizontal_interlace_odd_even_coverage(self):
        left=list(range(0,512,2))
        right=list(range(511,0,-2))
        self.assertEqual(len(left),256)
        self.assertEqual(len(right),256)
        self.assertEqual(set(left).intersection(right),set())
        self.assertEqual(set(left+right),set(range(512)))

    def test_kernel_uses_thin_vdp_fills(self):
        self.assertIn("ld hl,2\n    ld (LmNY),hl",ASM)
        self.assertIn("ld hl,1\n    ld (LmNX),hl",ASM)
        self.assertIn("ld hl,162\n    ld (LmNY),hl",ASM)
        self.assertIn("ld a,080h",ASM)
        self.assertIn("call WipeWaitIdle",ASM)
        self.assertIn("call WipeWaitFrame",ASM)
        self.assertIn("cp 50",ASM)
        self.assertIn("ld a,0                  ; 256 iterations",ASM)
        self.assertIn("WIPE_VERTICAL EQU 1",(ROOT/"z80"/"asm"/"wipe11.asm").read_text())
        self.assertIn("WIPE_VERTICAL EQU 0",(ROOT/"z80"/"asm"/"wipe12.asm").read_text())

    def test_assembled_binaries_have_distinct_axes_and_lengths(self):
        b11,b12=binary(11),binary(12)
        self.assertNotEqual(b11,b12,"interlaced directions compiled identically")
        body11,body12=b11[7:],b12[7:]
        # start near/far: vertical Y=50/207, horizontal X=0/511.
        self.assertIn(b"\x21\x32\x00\x22",body11)
        self.assertIn(b"\x21\xcf\x00\x22",body11)
        self.assertIn(b"\x21\xff\x01\x22",body12)
        # loop count and pacing
        self.assertIn(b"\x3e\x51\x32",body11)  # 81
        self.assertIn(b"\x3e\x00\x32",body12)  # 256 via wrap
        self.assertNotIn(b"\x21\xff\x01\x22",body11)

    def test_fat12_disks_contain_correct_payload(self):
        for n,description in ((11,b"TOP BOTTOM INTERLACED"),
                               (12,b"LEFT RIGHT INTERLACED")):
            with self.subTest(n=n):
                self.assertEqual(disk_read(n,f"WIPE{n}.BIN"),binary(n))
                boot=disk_read(n,"AUTOEXEC.BAS")
                self.assertIn(f'BLOAD "WIPE{n}.BIN",R'.encode(),boot)
                self.assertIn(description,boot)
                other=23-n
                self.assertNotIn(f'BLOAD "WIPE{other}.BIN",R'.encode(),boot)

if __name__=="__main__":
    unittest.main()
