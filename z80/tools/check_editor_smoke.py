#!/usr/bin/env python3
"""Conservative visual checks for disposable interactive menu/editor regression.
A: file content is checked separately in CI. Pixel comparison is smoke evidence
only; it is not optical recognition of individual menu labels.
"""
from pathlib import Path
from PIL import Image, ImageChops, ImageStat

folder = Path("z80/build/openmsx-editor")
names = ["main", "textmenu", "editor", "escape", "returnmenu",
         "save", "saved", "mainagain", "resumed", "resumed2"]
frames = {}
for name in names:
    p = folder / (name + ".png")
    if not p.is_file() or p.stat().st_size < 1000:
        raise AssertionError(f"Screenshot missing or too small: {p}")
    with Image.open(p) as img:
        frames[name] = img.convert("RGB")
    if frames[name].width < 256 or frames[name].height < 192:
        raise AssertionError(f"Unexpected frame dimensions at {name}")
def difference(a, b):
    if frames[a].size != frames[b].size:
        raise AssertionError(f"Unexpected resolution change {a} -> {b}")
    diff = ImageChops.difference(frames[a], frames[b])
    return sum(ImageStat.Stat(diff).mean) / 3
# At least one operator screen should differ substantially from the live
# pages and two broadcast snapshots should show live updates.
if max(difference("editor", "resumed"), difference("textmenu", "resumed")) < 4:
    raise AssertionError("Operator screens not distinct from broadcast screen")
if difference("resumed", "resumed2") < 3:
    raise AssertionError("No convincing post-editor newspaper screen changes")
print("PASS: distinct operator screens and changing newspaper after return")
print("NOTE: the independent saved A: TXT proof is necessary for full acceptance")
