"""Opt-in shared WIPE(1..8) integration gate for actual compiled/disk files."""
from pathlib import Path
import sys
import unittest
import subprocess

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"z80"/"tools"))
from make_onefile_preview import parse_bload
from make_wipe_integration import make_asm, make_loop

BUILD=ROOT/"z80"/"build"
SRC=ROOT/"z80"/"asm"/"basic_text_demo.asm"

class SharedWipeIntegrationTests(unittest.TestCase):
    def test_generation_preserves_original(self):
        text=SRC.read_text()
        out=make_asm(text)
        self.assertEqual(out.count("WipeName: db 'WIPE',0"),1)
        self.assertEqual(out.count("call WipeSharedRun"),1)
        self.assertEqual(out.count("INCLUDE 'wipe_shared.asm'"),1)
        self.assertEqual(text.count("WipeName"),0)
        basic=(ROOT/"src"/"LOOP.SYS").read_text()
        changed=make_loop(basic)
        self.assertIn("3140 IF A>=1 AND A<=8 THEN CALL WIPE(A):GOTO 3380",changed)
        self.assertIn("3141 ON A GOTO 3240,3250,3260",changed)
        self.assertEqual(changed.count("CALL WIPE(A)"),1)
        with self.assertRaises(ValueError):
            make_loop(changed)

    def test_compiled_extension_is_within_reserved_memory(self):
        raw=(BUILD/"KBLTXTWIPE.BIN").read_bytes()
        start,end,entry,payload=parse_bload(raw)
        self.assertEqual((start,entry),(0xC804,0xC806))
        self.assertLess(end,0xD804)
        # First word is the BASIC extension entry vector; opcode of\n        # Install (LD HL,handler) begins at C806, not C804.\n        import struct\n        vector=struct.unpack_from("<H",payload,0)[0]\n        self.assertGreaterEqual(vector,0xC806)\n        self.assertLessEqual(vector,end)\n        self.assertEqual(payload[2:3],b"\x21")
        self.assertIn(b"WIPE\x00",payload)
        self.assertIn(b"TEXT\x00",payload)
        self.assertIn(b"KBLVER\x00",payload)
        self.assertLessEqual(len(payload),4096)

    def test_disk_image_has_exact_combined_loader(self):
        disk=BUILD/"KBLWIPEINT.DSK"
        self.assertEqual(disk.stat().st_size,737280)
        def file(name):
            return subprocess.check_output(["mcopy","-i",str(disk),"::"+name,"-"],stderr=subprocess.PIPE)
        combined=(BUILD/"KBLRAMWIPE.BIN").read_bytes()
        self.assertEqual(file("RAMDISK.BIN"),combined)
        self.assertEqual(file("LOOP.SYS"),(BUILD/"wipe_integration"/"LOOP.SYS").read_bytes())
        self.assertEqual(file("KBLINIT.SYS"),(BUILD/"onefile"/"KBLINIT.SYS").read_bytes())
        self.assertEqual(file("LOOPBAS.SYS"),(ROOT/"z80"/"build"/"onefile"/"LOOPBAS.SYS").read_bytes())
        cstart,cend,centry,cpayload=parse_bload(combined)
        tstart,tend,tentry,tpayload=parse_bload((BUILD/"KBLTXTWIPE.BIN").read_bytes())
        rstart,rend,rentry,rpayload=parse_bload((ROOT/"src"/"RAMDISK.BIN").read_bytes())
        self.assertEqual((cstart,centry),(0xC000,0xC000))
        self.assertEqual(cpayload[:len(rpayload)],rpayload)
        self.assertEqual(cpayload[tstart-cstart:],tpayload)
        self.assertEqual(cend,tend)

if __name__=="__main__":
    unittest.main()
