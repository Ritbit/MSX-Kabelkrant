"""Rectangle-enabled 14-wipe integration: hard size, parser and disk gates.

Static tests cannot establish live MSX BASIC parser semantics or image
clipping; a distinct WebMSX test disk is mandatory before promotion.
"""
from pathlib import Path
import sys
import struct
import subprocess
import unittest

ROOT=Path(__file__).resolve().parents[2]
BUILD=ROOT/"z80"/"build"
sys.path.insert(0,str(ROOT/"z80"/"tools"))
from make_rect_wipe_integration import make_rectangle_asm
from make_rect_demo_init import rectangle_init
from msx_basic_ascii import encode_msx_basic,validate_msx_basic
from make_onefile_preview import parse_bload


def disk_get(disk,name):
    return subprocess.check_output(["mcopy","-i",str(disk),"::"+name,"-"],stderr=subprocess.PIPE)


def disk_names(disk):
    out=subprocess.check_output(["mdir","-b","-i",str(disk),"::"],text=True)
    return {x.strip().rsplit("/",1)[-1].upper() for x in out.splitlines() if x.strip()}


class RectangularPrototypeTests(unittest.TestCase):
    def test_generator_preserves_legacy_dispatch(self):
        source=(ROOT/"z80"/"asm"/"basic_text_demo.asm").read_text()
        out=make_rectangle_asm(source)
        self.assertEqual(out.count("WipeCommand:"),1)
        self.assertIn("ld a,(WipeRequested)\n    push hl\n    call WipeSharedRun",out)
        self.assertIn("call WipeRectRun",out)
        self.assertIn("call WipeRectValidate",out)
        self.assertIn("cp 15\n    jp nc,IllegalFunction",out)
        self.assertEqual(out.count("ld ix,FRMQNT\n    call CALBAS"),6)  # 2 TEXT coordinates + 4 rectangle
        self.assertIn("INCLUDE 'wipe_rect_one.asm'",out)
        self.assertNotIn("WipeRectRun",source)

    def test_rectangle_edges_and_exact_coverage(self):
        # Independently validate expected 2-line-stripe segmentation,
        # including an odd-height final one-line stripe.
        for x1,y1,x2,y2 in [(0,50,511,211),(0,8,511,44),(120,90,240,139),
                             (0,0,0,0),(511,211,511,211)]:
            width=x2-x1+1
            y=y1
            rows=[]
            while y<=y2:
                h=min(2,y2-y+1)
                rows.extend(range(y,y+h))
                y+=h
            self.assertEqual(rows,list(range(y1,y2+1)))
            self.assertTrue(1<=width<=512)
            self.assertTrue(0<=x1<=x2<=511)
            self.assertTrue(0<=y1<=y2<=211)

    def test_compiled_payload_fits_safe_page_three_reserve(self):
        start,end,entry,payload=parse_bload((BUILD/"KBLTXTRECT.BIN").read_bytes())
        self.assertEqual((start,entry),(0xC804,0xC806))
        self.assertLess(end,0xD804,"Rectangle extension exceeds reserved 4 KiB")
        original=(BUILD/"KBLTXTWIPE14.BIN").read_bytes()
        self.assertGreater(len(payload),len(original)-7)
        self.assertLessEqual(len(payload)-(len(original)-7),321)
        self.assertIn(b"WIPE\x00",payload)
        self.assertIn(b"TEXT\x00",payload)

    def test_disk_only_replaces_machinecode_and_adds_test(self):
        base=BUILD/"KBLWIPELEAN.DSK"
        rect=BUILD/"KBLWIRECT.DSK"
        self.assertEqual(rect.stat().st_size,737280)
        self.assertEqual(disk_names(rect)-disk_names(base),{"RECTDEMO.BAS"})
        self.assertEqual(disk_names(base)-disk_names(rect),set())
        for name in disk_names(base):
            if name=="RAMDISK.BIN":
                self.assertEqual(disk_get(rect,name),(BUILD/"KBLRAMRECT.BIN").read_bytes())
                self.assertNotEqual(disk_get(rect,name),disk_get(base,name))
            else:
                self.assertEqual(disk_get(rect,name),disk_get(base,name))
        program=encode_msx_basic((ROOT/"z80"/"tests"/"RECTDEMO.BAS").read_bytes())
        validate_msx_basic(program)
        self.assertEqual(disk_get(rect,"RECTDEMO.BAS"),program)
        self.assertIn(b"CALL WIPE(1,0,50,511,211)",program)
        self.assertIn(b"CALL WIPE(1,0,8,511,44)",program)
        self.assertIn(b"CALL WIPE(1,120,90,240,139)",program)

    def test_auto_disk_only_changes_initializer(self):
        base=BUILD/"KBLWIRECT.DSK"
        auto=BUILD/"KBLWIRECTAUTO.DSK"
        self.assertEqual(auto.stat().st_size,737280)
        self.assertEqual(disk_names(auto),disk_names(base))
        for name in disk_names(base):
            if name=="KBLINIT.SYS":
                self.assertEqual(disk_get(auto,name),rectangle_init(disk_get(base,name)))
                self.assertNotEqual(disk_get(auto,name),disk_get(base,name))
            else:
                self.assertEqual(disk_get(auto,name),disk_get(base,name))

if __name__=="__main__":
    unittest.main()
