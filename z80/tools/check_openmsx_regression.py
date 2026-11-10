#!/usr/bin/env python3
"""Validate screenshot evidence from an actually ROM-booted NMS8250 run.

Reject blank screens and loops with no changing newspaper body.
This is not a substitute for editor/keypad, fonts, or C: proof tests.
"""
from PIL import Image, ImageChops
from pathlib import Path
import argparse
import json


def inspect(folder: Path, variant: str):
    patterns=([f"loop-{n:03d}.png" for n in (30,75,120,165,210)]
              if variant=="loop" else ["ctest-025.png","ctest-060.png"])
    frames=[]
    for name in patterns:
        p=folder/name
        if not p.is_file() or p.stat().st_size<1024:
            raise AssertionError(f"Missing emulator screenshot: {p}")
        with Image.open(p) as im:
            im.load()
            rgb=im.convert("RGB")
            if rgb.width<256 or rgb.height<192:
                raise AssertionError(f"Unrealistic screenshot shape: {name} {rgb.size}")
            # Snapshot emulator output includes borders on some renderers,
            # so use a central crop and do not assume 512x212 exactly.
            image=rgb.crop((rgb.width//10,rgb.height//4,
                            9*rgb.width//10,9*rgb.height//10))
            colours=image.getcolors(maxcolors=1_000_000)
            if colours is not None and len(colours)<3:
                raise AssertionError(f"Uniform or low-colour screen: {name}")
            frames.append(image.copy())
    results={"case":variant,"frames":patterns,"frame_sizes":[list(im.size) for im in frames]}
    if variant=="loop":
        # Compare only a cropped part of the image (avoid the animated clock).
        # A live newspaper must change substantially over many MSX seconds;
        # a blinking cursor/error screen should not be accepted as progress.
        diffs=[]
        from PIL import ImageStat
        for a,b in zip(frames,frames[1:]):
            diff=ImageChops.difference(a,b)
            rms=ImageStat.Stat(diff).mean
            diffs.append(round(sum(rms)/3,3))
        results["consecutive_mean_rgb_diff"]=diffs
        if sum(d>5.0 for d in diffs)<2:
            raise AssertionError(f"No substantial newspaper changes: RGB differences {diffs}")
    return results


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--folder",type=Path,default=Path("z80/build/openmsx-regression"))
    p.add_argument("--case",choices=("loop","ctest"),required=True)
    p.add_argument("--output",type=Path)
    a=p.parse_args()
    result=inspect(a.folder,a.case)
    print(json.dumps(result,sort_keys=True,indent=2))
    if a.output:
        a.output.parent.mkdir(parents=True,exist_ok=True)
        a.output.write_text(json.dumps(result,indent=2)+"\n")
    print(f"PASS: {a.case} emulator screenshot evidence ({len(result['frames'])} frames)")


if __name__=="__main__":
    main()
