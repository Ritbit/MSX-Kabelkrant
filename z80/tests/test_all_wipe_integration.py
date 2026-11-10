"""Final combined 14-effect ALPHA contract: compiled code + FAT12 + geometry.

This is not a screen-pixel emulator test. Keep standalone visual
acceptance separate from verification of the new resident assembly.
"""
import unittest
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[2]
BUILD=ROOT/"z80"/"build"
sys.path.insert(0,str(ROOT/"z80"/"tools"))
from make_wipe_integration import make_asm,make_loop
from make_onefile_preview import parse_bload

class AllWipesShared(unittest.TestCase):
    def test_full_generator_dispatches_1_through_14(self):
        base=(ROOT/"z80"/"asm"/"basic_text_demo.asm").read_text()
        full=make_asm(base,full=True)
        self.assertIn("WIPE_EXTRA EQU 1",full)
        self.assertIn("WIPE_FULL EQU 1",full)
        self.assertIn("cp 15\n    jp nc,IllegalFunction",full)
        self.assertIn("INCLUDE 'wipe_shared.asm'",full)
        basic=(ROOT/"src"/"LOOP.SYS").read_text()
        altered=make_loop(basic,full=True)
        self.assertIn("3140 IF A>=1 AND A<=14 THEN CALL WIPE(A):GOTO 3380",altered)
        self.assertIn("3141 ON A GOTO 3240,3250",altered)
        for n in range(3240,3380,10):
            self.assertIn(f"{n} ",altered)
        self.assertNotIn("CALL WIPE",basic)

    def test_last_two_effects_are_procedural_and_bounded(self):
        src=(ROOT/"z80"/"asm"/"wipe_shared_final.asm").read_text()
        self.assertIn("WipeIntegrated13:",src)
        self.assertIn("WipeIntegrated14:",src)
        self.assertIn("ld hl,257",src)
        self.assertIn("ld hl,512",src)
        self.assertIn("ld hl,162",src)
        self.assertIn("ld a,39",src)
        self.assertIn("ld a,129",src)
        self.assertIn("call ExtraDrawRect",src)
        self.assertIn("call ExtraInitBlack\n    call LmmmLaunch\n    call WipeSharedIdle",src)
        self.assertIn("WipeExtraRun:",(ROOT/"z80"/"asm"/"wipe_shared_extra.asm").read_text())

    def test_complete_compiled_text_wipe_payload_fits(self):
        full=(BUILD/"KBLTXTWIPE14.BIN").read_bytes()
        start,end,entry,payload=parse_bload(full)
        self.assertEqual((start,entry),(0xC804,0xC806))
        self.assertLess(end,0xD804)
        self.assertIn(b"TEXT\x00",payload)
        self.assertIn(b"WIPE\x00",payload)
        self.assertIn(b"KBLVER\x00",payload)
        prior=(BUILD/"KBLTXTWIPE12.BIN").read_bytes()
        self.assertNotEqual(full,prior)
        self.assertGreater(len(full),len(prior))

    def test_only_opted_in_files_differ_from_legacy_onefile(self):
        preview=BUILD/"KBLWIPEINT14.DSK"
        baseline=BUILD/"KBLONEFILE.DSK"
        def names(disk):
            raw=subprocess.check_output(["mdir","-b","-i",str(disk),"::"],text=True)
            return {line.strip().rsplit("/",1)[-1].upper()
                    for line in raw.splitlines() if line.strip()}
        def read(disk,name):
            return subprocess.check_output(["mcopy","-i",str(disk),f"::{name}","-"],
                                           stderr=subprocess.PIPE)
        old,new=names(baseline),names(preview)
        self.assertEqual(old,new)
        changed={"RAMDISK.BIN","LOOP.SYS"}
        for name in sorted(old-changed):
            with self.subTest(file=name):
                self.assertEqual(read(preview,name),read(baseline,name))
        for name in changed:
            self.assertNotEqual(read(preview,name),read(baseline,name))

    def test_disk_embeds_correct_combined_code(self):
        disk=BUILD/"KBLWIPEINT14.DSK"
        self.assertEqual(disk.stat().st_size,737280)
        def read(name):
            return subprocess.check_output(["mcopy","-i",str(disk),"::"+name,"-"],stderr=subprocess.PIPE)
        code=(BUILD/"KBLRAMWIPE14.BIN").read_bytes()
        self.assertEqual(read("RAMDISK.BIN"),code)
        self.assertEqual(read("LOOP.SYS"),(BUILD/"wipe_integration14"/"LOOP.SYS").read_bytes())
        self.assertEqual(read("KBLINIT.SYS"),(BUILD/"onefile"/"KBLINIT.SYS").read_bytes())
        cs,ce,cx,cp=parse_bload(code)
        ts,te,tx,tp=parse_bload((BUILD/"KBLTXTWIPE14.BIN").read_bytes())
        rs,re,rx,rp=parse_bload((ROOT/"src"/"RAMDISK.BIN").read_bytes())
        self.assertEqual((cs,cx),(0xC000,0xC000))
        self.assertEqual(cp[:len(rp)],rp)
        self.assertEqual(cp[ts-cs:],tp)
        self.assertEqual(ce,te)

if __name__=="__main__":
    unittest.main()
