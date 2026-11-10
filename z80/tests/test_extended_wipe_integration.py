"""Compiled and packaged shared WIPE(1..12) regression gates."""
import unittest
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[2]
BUILD=ROOT/"z80"/"build"
sys.path.insert(0,str(ROOT/"z80"/"tools"))
from make_onefile_preview import parse_bload
from make_wipe_integration import make_asm,make_loop

class ExtendedWipeTests(unittest.TestCase):
    def test_compact_coordinate_table_is_exact(self):
        src=(ROOT/"z80"/"asm"/"wipe_compact_table.asm").read_text()
        rows=[x for x in src.splitlines() if x.strip().startswith("db ")]
        self.assertEqual(len(rows),128)
        for i,line in enumerate(rows):
            x,y=[int(t) for t in line.split(";")[0].strip()[3:].split(",")]
            self.assertEqual((x,y),(i*2,(i*75)//128))
        self.assertEqual((x,y),(254,74))

    def test_extra_dispatch_has_four_modes(self):
        src=(ROOT/"z80"/"asm"/"wipe_shared_extra.asm").read_text()
        self.assertIn("cp 11\n    jp nc,WipeExtraInterlace",src)
        self.assertIn("cp 10",src)
        self.assertIn("ld hl,207",src)
        self.assertIn("ld hl,511",src)
        self.assertIn("call ExtraDrawBox",src)
        self.assertIn("call WipeSharedIdle",src)
        self.assertIn("call WipeSharedFrame",src)
        self.assertIn("INCLUDE 'wipe_compact_table.asm'",src)

    def test_generated_two_alphas_differ_in_range(self):
        bas=(ROOT/"src"/"LOOP.SYS").read_text()
        old=make_loop(bas)
        new=make_loop(bas,extra=True)
        self.assertIn("A<=8 THEN CALL WIPE(A)",old)
        self.assertIn("A<=12 THEN CALL WIPE(A)",new)
        asm=(ROOT/"z80"/"asm"/"basic_text_demo.asm").read_text()
        a=make_asm(asm)
        b=make_asm(asm,extra=True)
        self.assertIn("WIPE_EXTRA EQU 0",a)
        self.assertIn("WIPE_EXTRA EQU 1",b)
        self.assertIn("cp 13\n    jp nc,IllegalFunction",b)
        self.assertNotIn("cp 13\n    jp nc,IllegalFunction",a)

    def test_compiled_extended_text_stays_within_c804_d803(self):
        a=(BUILD/"KBLTXTWIPE.BIN").read_bytes()
        b=(BUILD/"KBLTXTWIPE12.BIN").read_bytes()
        sa,ea,ia,pa=parse_bload(a)
        sb,eb,ib,pb=parse_bload(b)
        self.assertEqual((sa,ia,sb,ib),(0xc804,0xc806,0xc804,0xc806))
        self.assertNotEqual(pa,pb)
        self.assertGreater(len(pb),len(pa))
        self.assertLess(eb,0xd804)
        self.assertIn(b"WIPE\x00",pb)
        self.assertIn(bytes([0,0,2,0]),pb) # box table begins 0,0; 2,0

    def test_published_test_disk_matches_actual_compiled_extension(self):
        disk=BUILD/"KBLWIPEINT12.DSK"
        self.assertEqual(disk.stat().st_size,737280)
        def read(name):
            return subprocess.check_output(["mcopy","-i",str(disk),"::"+name,"-"],stderr=subprocess.PIPE)
        combined=(BUILD/"KBLRAMWIPE12.BIN").read_bytes()
        self.assertEqual(read("RAMDISK.BIN"),combined)
        self.assertEqual(read("LOOP.SYS"),(BUILD/"wipe_integration12"/"LOOP.SYS").read_bytes())
        cs,ce,cx,cp=parse_bload(combined)
        ts,te,tx,tp=parse_bload((BUILD/"KBLTXTWIPE12.BIN").read_bytes())
        rs,re,rx,rp=parse_bload((ROOT/"src"/"RAMDISK.BIN").read_bytes())
        self.assertEqual((cs,cx),(0xc000,0xc000))
        self.assertEqual(cp[:len(rp)],rp)
        self.assertEqual(cp[ts-cs:],tp)
        self.assertEqual(ce,te)

if __name__=="__main__":
    unittest.main()
