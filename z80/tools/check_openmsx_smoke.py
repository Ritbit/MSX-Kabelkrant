#!/usr/bin/env python3
"""Sanity-check a headless openMSX screenshot.

This is deliberately a SMOKE test (not pixel-equivalence or a guarantee
that all CALLs executed). See BUILD-AND-TEST.md for manual validation.
"""
import argparse
from pathlib import Path
from PIL import Image


def check(path: Path) -> None:
    if not path.is_file() or path.stat().st_size < 1000:
        raise ValueError("Missing or implausibly small openMSX screenshot")
    with Image.open(path) as image:
        image.load()
        width, height = image.size
        if width < 256 or height < 192:
            raise ValueError(f"Unexpected screenshot resolution: {width}x{height}")
        rgb = image.convert("RGB")
        # Distinguish a populated screen from a uniform boot/error background.
        colours = rgb.getcolors(maxcolors=1_000_000)
        if colours is not None and len(colours) < 3:
            raise ValueError("Screenshot has fewer than three colours")
        print(f"OpenMSX smoke screenshot: {width}x{height}, "
              f"{len(colours) if colours is not None else '>1000000'} unique colours")
    print("PASS: screenshot exists and is non-uniform")
    print("NOTE: This does NOT prove CALL TEXT succeeded or fonts match BASIC.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("image", type=Path)
    args = parser.parse_args()
    check(args.image)
