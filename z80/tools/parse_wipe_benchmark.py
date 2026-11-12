#!/usr/bin/env python3
"""Validate real MSX BASIC/Z80 benchmark output from an emulator-mutated DSK."""
import csv
import json
import argparse
from pathlib import Path

p=argparse.ArgumentParser()
p.add_argument("results",type=Path)
p.add_argument("--json",dest="json_path",type=Path,required=True)
args=p.parse_args()
with args.results.open(newline="",encoding="ascii",errors="replace") as f:
    rows=list(csv.reader(f))
if not rows or [s.strip() for s in rows[0]] != ["effect","basic_jiffies","z80_jiffies"]:
    raise SystemExit(f"Missing or malformed emulated benchmark header: {rows[:1]!r}")
samples=[]
for row in rows[1:15]:
    if len(row)!=3:
        raise SystemExit(f"Invalid sample row {row}")
    effect,b,z=[int(v.strip()) for v in row]
    if effect!=len(samples)+1 or b<=0 or z<=0:
        raise SystemExit(f"Missing effect or invalid measured jiffies: {row}")
    samples.append(dict(effect=effect,basic_jiffies=b,z80_jiffies=z,
                        speedup=round(b/z,3),z80_vs_basic=round(z/b,3)))
if len(samples)!=14:
    raise SystemExit(f"Expected 14 effects, received {len(samples)}")
free=[row for row in rows[15:] if len(row)==2 and row[0].strip()=="FRE0"]
if len(free)!=1:
    raise SystemExit("Missing FRE(0) record from MSX BASIC")
fre=float(free[0][1].strip())
if not 0<fre<65536:
    raise SystemExit(f"Invalid FRE(0) measurement: {fre}")
results=dict(platform="Philips NMS 8250 / openMSX",unit="MSX TIME jiffies",
             free_basic_bytes_before_benchmark=fre,
             effects=samples,mean_speedup=round(sum(v["speedup"] for v in samples)/14,3),
             all_z80_faster=all(v["speedup"]>1 for v in samples))
args.json_path.parent.mkdir(parents=True,exist_ok=True)
args.json_path.write_text(json.dumps(results,indent=2)+"\n")
print("PASS: real machine benchmark contains 14 paired BASIC/Z80 effects")
print(f"FRE(0) before benchmark: {fre:g} bytes")
print("effect BASIC Z80 speedup")
for s in samples: print(f"{s['effect']:>2} {s['basic_jiffies']:>5} {s['z80_jiffies']:>5} {s['speedup']:.2f}x")
print(f"Mean per-effect speedup: {results['mean_speedup']:.2f}x")
