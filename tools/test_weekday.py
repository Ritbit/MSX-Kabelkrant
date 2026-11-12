#!/usr/bin/env python3
"""Regression for original Kabelkrant LOOP.SYS weekday code (1990..2089).

MSX BASIC relational TRUE is -1, not Python True/+1.
Run: python3 tools/test_weekday.py
"""
from datetime import date, timedelta
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
MONTH_OFFSETS = (1, 4, 4, 0, 2, 5, 0, 3, 6, 1, 4, 6)
WEEKDAYS = ("zaterdag", "zondag", "maandag", "dinsdag",
            "woensdag", "donderdag", "vrijdag")
EXPECTED = (
    r'1330 DG=((Y\12+Y MOD 12+(Y MOD 12)\4+C(M)'
    r'+(Y MOD 4=0 AND M<3 AND Y>0)+D'
    r'+(LEFT$(JA$,2)="20")'
    r'+(Y=0 AND M<3 AND LEFT$(JA$,2)="20")) MOD 7)'
)


def msx_weekday(year: int, month: int, day: int) -> int:
    """Independent Python simulation of the checked MSX BASIC expression."""
    y = year % 100
    leap_janfeb = -1 if (y != 0 and y % 4 == 0 and month < 3) else 0
    century2000 = -1 if year >= 2000 else 0
    leap_2000_janfeb = -1 if year == 2000 and month < 3 else 0
    return ((y // 12 + y % 12 + (y % 12) // 4
             + MONTH_OFFSETS[month - 1] + leap_janfeb + day
             + century2000 + leap_2000_janfeb) % 7)


class KabelkrantWeekdayTests(unittest.TestCase):
    def test_source_uses_validated_formula(self):
        src = (ROOT / "src" / "LOOP.SYS").read_text(
            encoding="utf-8", errors="replace")
        lines = src.splitlines()
        self.assertIn(EXPECTED, lines)
        self.assertIn(
            '1290 IF VAL(RIGHT$(D$,2))<90 THEN JA$="20"+RIGHT$(D$,2) ELSE JA$="19"+RIGHT$(D$,2)',
            lines,
            "Date pivot changed: re-check the supported year range",
        )
        self.assertIn("1090 DATA " + ",".join(map(str, MONTH_OFFSETS)), lines)
        self.assertIn("1360 WK=((DG+5)MOD 7)+1", lines)

    def test_all_dates_supported_by_1990_2089_pivot(self):
        d = date(1990, 1, 1)
        last = date(2089, 12, 31)
        count = 0
        while d <= last:
            expected = (d.weekday() + 2) % 7  # BASIC: 0 = Saturday
            with self.subTest(date=str(d)):
                self.assertEqual(
                    msx_weekday(d.year, d.month, d.day), expected,
                    f"{d}: expected {WEEKDAYS[expected]}",
                )
            count += 1
            d += timedelta(days=1)
        self.assertEqual(count, 36525)

    def test_edge_cases_and_week_number_mapping(self):
        cases = {
            (1999, 12, 31): 6,    # Friday
            (2000, 1, 1): 0,      # Saturday
            (2000, 2, 29): 3,     # Tuesday; year 2000 is leap
            (2000, 3, 1): 4,      # Wednesday
            (2024, 2, 29): 5,     # Thursday
            (2026, 11, 12): 5,    # Thursday
            (2026, 11, 13): 6,    # Friday, not Saturday
            (2088, 2, 29): 1,     # Sunday
        }
        for ymd, dg in cases.items():
            with self.subTest(date=ymd):
                self.assertEqual(msx_weekday(*ymd), dg)
                # Original DG=0 Sat -> WK=6, DG=6 Fri -> WK=5.
                self.assertEqual(((dg + 5) % 7) + 1,
                                 date(*ymd).weekday() + 1)


if __name__ == "__main__":
    unittest.main()
