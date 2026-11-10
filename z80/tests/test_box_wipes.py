"""Geometry, assembled direction, FAT12 packaging for rectangle outlines #9/10."""
from pathlib import Path
from struct import unpack_from
import subprocess
import unittest

ROOT=Path(__file__).resolve().parents[2]
BUILD=ROOT/"z80"/"build"
TABLE=(ROOT/"z80"/"asm"/"wipe_rect_table.asm").read_text()
KERNEL=(ROOT/"z80"/"asm"/"wipe_box_kernel.asm").read_text()
BASIC=(ROOT/"src"/"LOOP.SYS").read_text()

def binfile(n):
    data=(BUILD/f"WIPE{n}.BIN").read_bytes()
    assert data[0]==0xfe
    start,end,entry=unpack_from("<HHH",data,1)
    assert (start,entry)==(0xc804,0xc806)
    assert end==start+len(data)-8
    return data

def diskfile(n,name):
    disk=BUILD/f"KBLWIPE{n}.DSK"
    assert disk.stat().st_size==737280
    return subprocess.check_output(["mcopy","-i",str(disk),f"::{name}","-"],stderr=subprocess.PIPE)

class BoxWipes(unittest.TestCase):
    def test_original_basic_outlines_not_filled(self):
        nine=next(x for x in BASIC.splitlines() if x.startswith("3320 "))
        ten=next(x for x in BASIC.splitlines() if x.startswith("3330 "))
        self.assertIn("FOR A = 0 TO 256  STEP 2",nine)
        self.assertIn("FOR A = 256 TO 0  STEP-2",ten)
        for line in (nine,ten):
            self.assertEqual(line.count(",0,B:"),2)
            self.assertNotIn(",0,BF",line)

    def test_table_records_and_screen7_bounds(self):
        rows=[line for line in TABLE.splitlines() if line.strip().startswith("dw ")]
        self.assertEqual(len(rows),128)
        for i,line in enumerate(rows):
            fields=line.split(";")[0].strip()[3:].split(",")
            x,right,top,bottom,width,height=map(int,fields)
            y=(x*75)//256
            self.assertEqual((x,right,top,bottom,width,height),
                             (2*i,510-2*i,50+y,210-y,512-4*i,162-2*y))
            self.assertGreaterEqual(top,50)
            self.assertLessEqual(bottom+1,211)
            self.assertGreaterEqual(width,4)
            self.assertGreaterEqual(height,14)

    def test_kernel_draws_four_thin_strips(self):
        self.assertEqual(KERNEL.count("call LmmmLaunch"),4)
        self.assertIn("ld a,080h",KERNEL)
        self.assertIn("ld bc,12\n    ldir",KERNEL)
        self.assertIn("ld hl,(FrameRight)",KERNEL)
        self.assertIn("ld hl,(FrameBottom)",KERNEL)
        self.assertIn("ld hl,(FrameHeight)",KERNEL)
        self.assertIn("call WipeWaitIdle",KERNEL)
        self.assertIn("call WipeWaitFrame",KERNEL)

    def test_machine_code_directions_and_bload_entry(self):
        b9,b10=binfile(9),binfile(10)
        self.assertNotEqual(b9,b10)
        # The two build variants start with different table pointers;
        # assert the exact address via the embedded table at the binary tail
        # and the first initialized table-pointer LD HL,nn.
        def table_location(data):
            blob=data[7:]
            row=bytes([0,0,254,1,50,0,210,0,0,2,162,0])
            off=blob.find(row)
            self.assertGreater(off,0)
            self.assertEqual(blob.count(row),1)
            return 0xc804+off
        addr9=table_location(b9)
        addr10=table_location(b10)
        self.assertEqual(addr9,addr10)
        # After vector (2 bytes), PUSH AF/BC/DE/HL (4 bytes):
        # LD HL, table_first/table_last (3 bytes).
        self.assertEqual(b9[7+6],0x21)
        self.assertEqual(b10[7+6],0x21)
        self.assertEqual(unpack_from("<H",b9,7+7)[0],addr9)
        self.assertEqual(unpack_from("<H",b10,7+7)[0],addr10+12*127)

    def test_disk_contains_correct_binary(self):
        for n,label in ((9,b"OUTSIDE TO CENTRE"),(10,b"CENTRE TO OUTSIDE")):
            with self.subTest(n=n):
                self.assertEqual(diskfile(n,f"WIPE{n}.BIN"),binfile(n))
                boot=diskfile(n,"AUTOEXEC.BAS")
                self.assertIn(f'BLOAD "WIPE{n}.BIN",R'.encode(),boot)
                self.assertIn(label,boot)
        self.assertNotEqual(diskfile(9,"AUTOEXEC.BAS"),diskfile(10,"AUTOEXEC.BAS"))

if __name__=="__main__":
    unittest.main()
