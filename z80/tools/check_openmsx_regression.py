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
    patterns=([f"loop-{n:03d}.png" for n in (120,165,210,255)]
              if variant=="loop" else
              [f"long-{n:04d}.png" for n in (120,300,480,660,840,1020,1200,1380)]
              if variant=="long" else ["ctest-120.png","ctest-210.png"])
    frames=[]
    meaningful=[]
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
            min_colours = 2 if variant == "ctest" else 3
            populated = colours is None or len(colours)>=min_colours
            if variant=="ctest" and not populated:
                raise AssertionError(f"Uniform or low-colour screen: {name}")
            meaningful.append(populated)
            frames.append(image.copy())
    results={"case":variant,"frames":patterns,"frame_sizes":[list(im.size) for im in frames]}
    if variant in ("loop","long"):
        # Allow a short instantaneous full-screen wipe, but not a screen that
        # stays blank or repeats for most of the unattended run.
        required=2 if variant=="loop" else 5
        if sum(meaningful)<required:
            raise AssertionError(f"Too few populated newspaper frames: {meaningful}")
        if variant=="long" and any(not any(meaningful[i:i+3]) for i in range(len(meaningful)-2)):
            raise AssertionError("Three consecutive low-colour frames during long run")
        # Compare only a cropped part of the image (avoid the animated clock).
        # A live newspaper must change substantially over many MSX seconds;
        # a blinking cursor/error screen should not be accepted as progress.
        diffs=[]
        from PIL import ImageStat
        for a,b in zip(frames,frames[1:]):
            diff=ImageChops.difference(a,b)
            rms=ImageStat.Stat(diff).mean
            diffs.append(round(sum(rms)/3,3))
        results["populated_frames"]=meaningful
        results["consecutive_mean_rgb_diff"]=diffs
        minimum_diffs=2 if variant=="loop" else 4
        if sum(d>5.0 for d in diffs)<minimum_diffs:
            raise AssertionError(f"No substantial newspaper changes: RGB differences {diffs}")
    return results


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--folder",type=Path,default=Path("z80/build/openmsx-regression"))
    p.add_argument("--case",choices=("loop","long","ctest"),required=True)
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
