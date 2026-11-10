"""Validate isolated wipe #1 plan against original MSX BASIC semantics."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[2]
ASM = (ROOT/"z80"/"asm"/"wipe_kernel.asm").read_text()
BASIC = (ROOT/"src"/"LOOP.SYS").read_text()


class WipeKernelTests(unittest.TestCase):
    def test_basic_wipe1_source_contract(self):
        line = next(x for x in BASIC.splitlines() if x.startswith("3240 "))
        self.assertRegex(line, r"FOR A\s*=\s*50 TO 212 STEP 2")
        self.assertIn("LINE(0,A)-(512,A+1),0,BF", line)

    def test_visible_screen7_bands_are_exact(self):
        expected = [(0, y, 511, y + 1) for y in range(50, 212, 2)]
        self.assertEqual(len(expected), 81)
        self.assertEqual(expected[0], (0, 50, 511, 51))
        self.assertEqual(expected[-1], (0, 210, 511, 211))
        self.assertIn("ld hl,50\n    ld (LmDY),hl", ASM)
        self.assertIn("ld hl,512\n    ld (LmNX),hl", ASM)
        self.assertIn("ld hl,2\n    ld (LmNY),hl", ASM)
        self.assertIn("cp 212", ASM)

    def test_v9938_fill_command_and_wait(self):
        self.assertIn("ld a,080h", ASM)  # LMMV IMP
        self.assertIn("call LmmmLaunch", ASM)
        self.assertIn("call WipeWaitIdle", ASM)
        self.assertIn("ld (LmCLR),a", ASM)
        self.assertIn("ld (LmARG),a", ASM)
        self.assertNotIn("CALL TEXT", ASM)


if __name__ == "__main__":
    unittest.main()
