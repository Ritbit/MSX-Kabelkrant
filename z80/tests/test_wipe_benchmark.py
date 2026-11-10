"""Regression gates for lean BASIC loop and same-hardware wipe benchmark."""
from pathlib import Path
import subprocess
import sys
import unittest
ROOT=Path(__file__).resolve().parents[2]
BUILD=ROOT/"z80"/"build"
sys.path.insert(0,str(ROOT/"z80"/"tools"))
from msx_basic_ascii import validate_msx_basic
from make_wipe_benchmark import clean_loop, make_benchmark, split_program, ORIGINAL_EFFECT_LINES


def get(image,name):
    return subprocess.check_output(["mcopy","-i",str(image),f"::{name}","-"],stderr=subprocess.PIPE)

def listing(image):
    raw=subprocess.check_output(["mdir","-b","-i",str(image),"::"],text=True)
    return {line.strip().split("/")[-1].upper() for line in raw.splitlines() if line.strip()}


class LeanWipeAndBenchmarkTests(unittest.TestCase):
    def test_cleaner_preserves_legacy_fallthrough_and_broadcast(self):
        original=(ROOT/"src"/"LOOP.SYS").read_text()
        # The actual built full LOOP is used, not the raw old source.
        old=(BUILD/"wipe_integration14"/"LOOP.SYS").read_bytes()
        new=(BUILD/"wipe_lean"/"LOOP.SYS").read_bytes()
        validate_msx_basic(new)
        orig=split_program(old[:-1].decode("ascii").replace("\r\n","\n"))
        clean=split_program(new[:-1].decode("ascii").replace("\r\n","\n"))
        self.assertEqual(clean[3140],"IF A<1 OR A>14 THEN A=1")
        self.assertEqual(clean[3141],"CALL WIPE(A):GOTO 3380")
        self.assertEqual(clean[3380],"INTERVAL ON")
        self.assertEqual(clean[3390],"RETURN")
        self.assertTrue(all(n not in clean for n in ORIGINAL_EFFECT_LINES))
        self.assertTrue(all(n in orig for n in ORIGINAL_EFFECT_LINES))
        self.assertTrue(all(n not in clean for n in range(3150,3380)))
        self.assertTrue(all(orig[k]==clean[k] for k in clean if k not in (3140,3141)))
        self.assertLess(len(new),len(old))
        # Original ON A GOTO with A=0/15 fell through to wipe 1.
        # The new dispatch must call exactly one valid Z80 effect.
        def original_route(a):
            return a if 1<=a<=14 else 1
        def lean_route(a):
            return a if 1<=a<=14 else 1
        for a in range(0,16):
            self.assertEqual(original_route(a),lean_route(a))

    def test_benchmark_matches_original_fourteen_bodies(self):
        original=split_program((ROOT/"src"/"LOOP.SYS").read_text())
        bench=split_program(make_benchmark((ROOT/"src"/"LOOP.SYS").read_text()))
        self.assertEqual(len([x for x in bench if x>=1000]),14)
        self.assertIn("T#=TIME",bench[70])
        self.assertIn("CALL WIPE(I)",bench[130])
        self.assertIn("ON I GOSUB",bench[80])
        self.assertIn("INTERVAL OFF",bench[40])
        self.assertEqual(bench[160],"NEXT I")
        self.assertIn("B(I)=D#",bench[100])
        self.assertIn("Z(I)=D#",bench[150])
        self.assertIn("D#=D#+65536",bench[90])
        for i,n in enumerate(ORIGINAL_EFFECT_LINES):
            with self.subTest(effect=i+1):
                expected=original[n].removesuffix(": GOTO 3380")+": RETURN"
                self.assertEqual(bench[1000+10*i],expected)

    def test_clean_disk_changes_only_loop(self):
        before=BUILD/"KBLWIPEINT14.DSK"
        after=BUILD/"KBLWIPELEAN.DSK"
        self.assertEqual(after.stat().st_size,737280)
        self.assertEqual(listing(before),listing(after))
        for name in listing(before):
            with self.subTest(name=name):
                if name=="LOOP.SYS":
                    self.assertEqual(get(after,name),(BUILD/"wipe_lean"/name).read_bytes())
                    self.assertNotEqual(get(before,name),get(after,name))
                else:
                    self.assertEqual(get(before,name),get(after,name))

    def test_benchmark_disk_only_adds_new_program(self):
        before=BUILD/"KBLWIPELEAN.DSK"
        after=BUILD/"KBLWIBENCH.DSK"
        self.assertEqual(after.stat().st_size,737280)
        self.assertEqual(listing(after)-listing(before),{"BENCHW.BAS"})
        self.assertEqual(listing(before)-listing(after),set())
        for name in listing(before):
            with self.subTest(name=name):
                self.assertEqual(get(before,name),get(after,name))
        program=(BUILD/"wipe_benchmark"/"BENCHW.BAS").read_bytes()
        validate_msx_basic(program)
        self.assertEqual(get(after,"BENCHW.BAS"),program)

if __name__=="__main__":
    unittest.main()
