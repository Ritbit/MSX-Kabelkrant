import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from ramdisk_layout import validate_ramdisk, first_overlap, FORMER_TEXT_ENTRY

ROOT = Path(__file__).resolve().parents[2]

class RAMdiskLayoutTests(unittest.TestCase):
    def test_historical_driver_zero_fill(self):
        validate_ramdisk((ROOT / "src/RAMDISK.BIN").read_bytes())

    def test_combined_handler_is_erased(self):
        self.assertEqual(first_overlap(FORMER_TEXT_ENTRY, 0x800), FORMER_TEXT_ENTRY)
        self.assertIsNone(first_overlap(0x400A, 3))
        self.assertIsNone(first_overlap(0xE004, 2048))

    def test_reject_invalid_extension(self):
        with self.assertRaises(ValueError):
            first_overlap(FORMER_TEXT_ENTRY, 0)
