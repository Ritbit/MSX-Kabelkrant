"""Auto-run timing harness must only modify KBLINIT.SYS of benchmark disk."""
import sys
import subprocess
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
BUILD=ROOT/"z80"/"build"
sys.path.insert(0,str(ROOT/"z80"/"tools"))
from msx_basic_ascii import validate_msx_basic
from make_wipe_benchmark import split_program
from make_auto_wipe_benchmark import generate

def read(disk,name):
    return subprocess.check_output(["mcopy","-i",str(disk),f"::{name}","-"],stderr=subprocess.PIPE)

def names(disk):
    result=subprocess.check_output(["mdir","-b","-i",str(disk),"::"],text=True)
    return {line.strip().rsplit("/",1)[-1].upper() for line in result.splitlines() if line.strip()}

class AutoBenchmarkTests(unittest.TestCase):
    def test_startup_uses_original_extension_and_does_not_modify_main(self):
        old=read(BUILD/"KBLWIBENCH.DSK","KBLINIT.SYS")
        new=read(BUILD/"KBLWIAUTO.DSK","KBLINIT.SYS")
        validate_msx_basic(new)
        self.assertEqual(new,generate(old))
        new_lines=split_program(new[:-1].decode("ascii").replace("\r\n","\n"))
        old_lines=split_program(old[:-1].decode("ascii").replace("\r\n","\n"))
        self.assertEqual(new_lines[198],'RUN "A:BENCHW.BAS"')
        self.assertLess(195,198)
        self.assertLess(198,200)
        self.assertEqual(new_lines[195],old_lines[195])
        self.assertEqual({k:v for k,v in new_lines.items() if k!=198},old_lines)

    def test_full_auto_disk_only_modifies_initializer(self):
        old=BUILD/"KBLWIBENCH.DSK"
        new=BUILD/"KBLWIAUTO.DSK"
        self.assertEqual(old.stat().st_size,new.stat().st_size)
        self.assertEqual(old.stat().st_size,737280)
        self.assertEqual(names(old),names(new))
        self.assertIn("BENCHW.BAS",names(new))
        for name in names(old):
            with self.subTest(name=name):
                if name=="KBLINIT.SYS":
                    self.assertNotEqual(read(old,name),read(new,name))
                else:
                    self.assertEqual(read(old,name),read(new,name))

if __name__=="__main__":
    unittest.main()
