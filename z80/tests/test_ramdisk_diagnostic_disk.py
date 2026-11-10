"""Verify optional C: RAMdisk diagnostic disk is safe and byte-faithful.

This does not test the runtime C: driver: only an actual MSX execution can.
"""
import subprocess
import unittest
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
BUILD=ROOT/"z80"/"build"
sys.path.insert(0,str(ROOT/"z80"/"tools"))
from msx_basic_ascii import encode_msx_basic, validate_msx_basic


def read_file(image,name):
    return subprocess.check_output(["mcopy","-i",str(image),f"::{name}","-"],stderr=subprocess.PIPE)

def names(image):
    x=subprocess.check_output(["mdir","-b","-i",str(image),"::"],text=True)
    return {line.strip().split("/")[-1].upper() for line in x.splitlines() if line.strip()}

class RamdiskDiagnosticDiskTest(unittest.TestCase):
    def test_diagnostic_only_changes_one_disk_file(self):
        old=BUILD/"KBLWIPEINT14.DSK"
        new=BUILD/"KBLCTEST.DSK"
        self.assertEqual(old.stat().st_size,new.stat().st_size)
        self.assertEqual(new.stat().st_size,737280)
        base=names(old)
        self.assertEqual(names(new)-base,{"CTEST.BAS"})
        self.assertEqual(base-names(new),set())
        for filename in base:
            with self.subTest(filename=filename):
                self.assertEqual(read_file(old,filename),read_file(new,filename))

    def test_basic_diagnostic_is_safely_bounded(self):
        source=(ROOT/"z80"/"tests"/"CTEST.BAS").read_bytes()
        expected=encode_msx_basic(source)
        validate_msx_basic(expected)
        self.assertEqual(read_file(BUILD/"KBLCTEST.DSK","CTEST.BAS"),expected)
        self.assertIn(b'F$="C:KBTST26.TMP"',expected)
        self.assertIn(b"PRINT #1,A$",expected)
        self.assertIn(b"LINE INPUT #1,C$",expected)
        self.assertIn(b"KILL F$",expected)
        self.assertNotIn(b"FORMAT",expected)
        self.assertNotIn(b"FILES",expected)
        self.assertNotIn(b"KILL \"C:",expected)

if __name__=="__main__":
    unittest.main()
