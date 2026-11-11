"""Prove the C: test disk changes only the test program and startup hook.

The final runtime pass condition is a marker written by the *emulated*
MSX after successful RAMdisk read, compare and deletion. Static CI
merely verifies the setup; never label this runtime-verified without ROMs.
"""
from pathlib import Path
import subprocess
import sys
import unittest

ROOT=Path(__file__).resolve().parents[2]
BUILD=ROOT/"z80"/"build"
sys.path.insert(0,str(ROOT/"z80"/"tools"))
from make_auto_ramdisk_test import generate as auto_init
from make_ramdisk_proof import generate as proof_basic
from msx_basic_ascii import validate_msx_basic
from make_wipe_benchmark import split_program


def disk_get(disk,filename):
    return subprocess.check_output(["mcopy","-i",str(disk),f"::{filename}","-"],stderr=subprocess.PIPE)


def files_on_disk(disk):
    raw=subprocess.check_output(["mdir","-b","-i",str(disk),"::"],text=True)
    return {line.strip().rsplit("/",1)[-1].upper() for line in raw.splitlines() if line.strip()}


class AutoRAMdiskProofTests(unittest.TestCase):
    def test_initializer_hooks_after_ramdisk_copy(self):
        src=(BUILD/"onefile"/"KBLINIT.SYS").read_bytes()
        aut=auto_init(src)
        validate_msx_basic(aut)
        lines=split_program(aut[:-1].decode("ascii").replace("\r\n","\n"))
        self.assertEqual(lines[235],'RUN "A:CTEST.BAS"')
        self.assertIn('COPY "A:"+PR$ TO "C:"',lines[230])
        self.assertEqual(lines[240],'RUN "LOOP.SYS"')
        self.assertIn("DEFUSR3=&HC806",lines[195])

    def test_proof_marker_only_after_all_c_roundtrips(self):
        src=(ROOT/"z80"/"tests"/"CTEST.BAS").read_text()
        assembled=proof_basic(src)
        validate_msx_basic(assembled)
        lines=split_program(assembled[:-1].decode("ascii").replace("\r\n","\n"))
        self.assertEqual(lines[90],'OPEN F$ FOR OUTPUT AS #1')
        self.assertEqual(lines[140],'OPEN F$ FOR INPUT AS #1')
        self.assertEqual(lines[180],'IF C$<>A$ THEN 8000')
        self.assertEqual(lines[190],'IF D$<>B$ THEN 8000')
        self.assertEqual(lines[210],"KILL F$")
        self.assertEqual(lines[212],'OPEN "A:KBLPASS.OK" FOR OUTPUT AS #1')
        self.assertEqual(lines[214],'PRINT #1,"PASS C: RW DELETE"')
        self.assertEqual(lines[216],"CLOSE #1")
        self.assertEqual(lines[220],'PRINT "PASS: WRITE/READ/DELETE ON C:"')

    def test_testimage_modifies_only_initialization_and_diagnostic(self):
        previous=BUILD/"KBLTITLECOPY.DSK"
        new=BUILD/"KBLCTESTAUTO.DSK"
        self.assertEqual(previous.stat().st_size,737280)
        self.assertEqual(new.stat().st_size,737280)
        self.assertEqual(files_on_disk(new)-files_on_disk(previous),{"CTEST.BAS"})
        self.assertEqual(files_on_disk(previous)-files_on_disk(new),set())
        self.assertNotIn("KBLPASS.OK",files_on_disk(new))
        for filename in files_on_disk(previous):
            with self.subTest(filename=filename):
                if filename=="KBLINIT.SYS":
                    self.assertEqual(disk_get(new,filename),
                                     auto_init(disk_get(previous,filename)))
                else:
                    self.assertEqual(disk_get(new,filename),
                                     disk_get(previous,filename))
        expected=(BUILD/"ramdisk_auto"/"CTEST.BAS").read_bytes()
        self.assertEqual(disk_get(new,"CTEST.BAS"),expected)

if __name__=="__main__":
    unittest.main()
