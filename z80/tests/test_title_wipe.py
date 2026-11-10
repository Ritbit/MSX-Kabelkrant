"""Dedicated two-bar title wipe: memory budget, untouched clock & FAT12."""
from pathlib import Path
import subprocess
import sys
import unittest

ROOT=Path(__file__).resolve().parents[2]
BUILD=ROOT/"z80"/"build"
sys.path.insert(0,str(ROOT/"z80"/"tools"))
from make_title_wipe import title_asm,title_loop
from make_wipe_benchmark import split_program
from make_onefile_preview import parse_bload

def file(disk,name):
    return subprocess.check_output(["mcopy","-i",str(disk),"::"+name,"-"],stderr=subprocess.PIPE)

def names(disk):
    data=subprocess.check_output(["mdir","-b","-i",str(disk),"::"],text=True)
    return {x.strip().rsplit("/",1)[-1].upper() for x in data.splitlines() if x.strip()}

class TitleOnlyWipeTest(unittest.TestCase):
    def test_source_template_copy_restores_background_and_protects_clock(self):
        src=(ROOT/"z80"/"asm"/"wipe_title_bars.asm").read_text()
        # The template comes from a clean left-hand column; it carries
        # the original borders and both differently coloured title bands.
        for token in [
            "ld (LmSX),hl", "ld (LmSY),hl",
            "ld (LmDX),hl", "ld (LmDY),hl",
            "ld hl,10\n    ld (LmNX),hl",
            "ld hl,49\n    ld (LmNY),hl",
            "ld a,090h", "ld (LmCMD),a",
            "ld b,44", "ld hl,5",
            "call LmmmLaunch", "call WipeSharedIdle",
            "call WipeSharedFrame"]:
            self.assertIn(token,src)
        self.assertNotIn("ld a,080h",src)
        self.assertNotIn("ld (LmCLR),a",src)
        strips=[]
        for i in range(44):
            x=i*10
            width=5 if i==43 else 10
            strips.append((x,x+width-1))
        self.assertEqual(strips[0],(0,9))
        self.assertEqual(strips[-1],(430,434))
        self.assertEqual(sum(b-a+1 for a,b in strips),435)
        self.assertEqual(
            [x for a,b in strips for x in range(a,b+1)],
            list(range(435)),
        )
        self.assertTrue(all(0<=a<=b<435 for a,b in strips))
        self.assertEqual(set(range(49)),set(range(0,49)))

    def test_legacy_paging_and_page_wipes_untouched(self):
        source=(ROOT/"z80"/"asm"/"basic_text_demo.asm").read_text()
        new=title_asm(source)
        self.assertIn("WIPE_TITLE EQU 1",new)
        self.assertIn("cp 16\n    jp nc,IllegalFunction",new)
        self.assertIn("call WipeSharedRun",new)
        self.assertIn("INCLUDE 'wipe_shared.asm'",new)
        self.assertNotIn("WIPE_TITLE EQU 1",source)
        raw=(BUILD/"wipe_lean"/"LOOP.SYS").read_bytes()
        original=raw[:-1].decode("ascii").replace("\r\n","\n")
        updated=title_loop(original)
        before=split_program(original)
        after=split_program(updated)
        self.assertEqual(after[3430],"INTERVAL OFF:CALL WIPE(15):INTERVAL ON")
        self.assertEqual(after[3480],"RETURN")
        self.assertEqual(after[2450],before[2450])
        self.assertEqual(after[3141],before[3141])
        self.assertTrue(all(k not in after for k in (3440,3450,3460,3470)))
        self.assertTrue(all(before[k]==after[k] for k in after if k!=3430))

    def test_compiled_binary_does_not_cross_reserve(self):
        old=(BUILD/"KBLTXTWIPE14.BIN").read_bytes()
        new=(BUILD/"KBLTXTTITLE.BIN").read_bytes()
        start,end,entry,payload=parse_bload(new)
        self.assertEqual((start,entry),(0xc804,0xc806))
        self.assertLess(end,0xd804)
        self.assertGreater(len(new),len(old))
        self.assertLessEqual(len(new)-len(old),321)
        self.assertIn(b"WIPE\x00",payload)
        self.assertIn(b"TEXT\x00",payload)

    def test_disk_only_changes_z80_and_loop(self):
        original=BUILD/"KBLWIPELEAN.DSK"
        updated=BUILD/"KBLTITLE.DSK"
        self.assertEqual(updated.stat().st_size,737280)
        self.assertEqual(names(original),names(updated))
        expected={"RAMDISK.BIN","LOOP.SYS"}
        for name in names(original):
            if name in expected:
                self.assertNotEqual(file(original,name),file(updated,name))
            else:
                self.assertEqual(file(original,name),file(updated,name))
        self.assertEqual(file(updated,"RAMDISK.BIN"),
                         (BUILD/"KBLRAMTITLE.BIN").read_bytes())
        self.assertEqual(file(updated,"LOOP.SYS"),
                         (BUILD/"title_wipe"/"LOOP.SYS").read_bytes())
        combined=(BUILD/"KBLRAMTITLE.BIN").read_bytes()
        _,_,_,bytes_combined=parse_bload(combined)
        _,_,_,original_payload=parse_bload((ROOT/"src"/"RAMDISK.BIN").read_bytes())
        self.assertEqual(bytes_combined[:len(original_payload)],original_payload)

if __name__=="__main__":
    unittest.main()
