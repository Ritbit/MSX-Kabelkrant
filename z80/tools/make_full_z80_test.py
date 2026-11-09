#!/usr/bin/env python3
"""Generate a full Kabelkrant Z80 TEXT integration test from the BASIC sources.

This changes only the generated test disk's KBLINIT.SYS and LOOP.SYS.
It keeps the original RAMDISK.BIN and the rest of Kabelkrant unchanged.
The historical BASIC renderer is saved separately as LOOPBAS.SYS.
"""
from pathlib import Path
import argparse
import re
from msx_basic_ascii import encode_msx_basic, validate_msx_basic

TEXT_CALL = 'CALL TEXT(A$,X,Y,LT,K)'
INITIALIZER = '190 SETPAGE 0,1: CLS: BLOAD "KRANT3.SC7",S: SETPAGE 0,0: CLEAR 2000,&HC7FF'



def split_long_data_lines(source: str, max_len: int = 210) -> str:
    """Split overlong original DATA statements on free line numbers.

    This preserves the sequential READ byte stream for the USR routines;
    only output BASIC line boundaries change.
    """
    lines = source.splitlines()
    result = []
    for i,line in enumerate(lines):
        if len(line) <= max_len:
            result.append(line)
            continue
        match = re.fullmatch(r'(\d+)\s+DATA\s+(.+)',line)
        if not match:
            raise ValueError(f'Non-DATA BASIC line too long: {line[:50]}')
        n = int(match.group(1))
        next_n = int(lines[i+1].split()[0]) if i+1 < len(lines) else 65530
        pieces = match.group(2).split(',')
        start_n = n
        cur = []
        for value in pieces:
            candidate = ','.join(cur+[value])
            if len(f'{start_n} DATA {candidate}') > max_len and cur:
                result.append(f'{start_n} DATA '+','.join(cur))
                start_n += 1
                cur = []
            cur.append(value)
        if cur:
            result.append(f'{start_n} DATA '+','.join(cur))
        if start_n >= next_n:
            raise ValueError(f'No free BASIC numbers after line {n}')
    return '\n'.join(result)+'\n'


def transform(init: str, loop: str) -> tuple[str, str, int]:
    lines=init.splitlines()
    i=next((i for i,line in enumerate(lines) if line.startswith('190 ')),None)
    if i is None or 'CLEAR 2000' not in lines[i]:
        raise ValueError('Unexpected KBLINIT.SYS memory setup')
    lines[i]=INITIALIZER
    # Reserve memory before loading the machine code.
    lines.insert(i+1,'195 BLOAD "KBLTXT.BIN",R')
    init=split_long_data_lines('\n'.join(lines)+'\n')

    # The Z80 engine embeds the font coordinates: X(4,110) in BASIC
    # would waste ~4.4 KiB and trigger ERR 7 at the DIM in line 1050.
    # Keep the original LOOP.SYS as LOOPBAS.SYS on the test disk.
    changed=0
    result=[]
    for line in loop.splitlines():
        if not line.strip():
            continue
        match=re.match(r'^(\d+)\s',line)
        if not match:
            raise ValueError('Unnumbered BASIC line')
        n=int(match.group(1))
        if 2500 <= n <= 2890 or n in (1135,1140):
            continue
        if n == 1050:
            line='1050 DIM XK(60),YK(60)'
        elif n == 1130:
            line='1130 COPY "XK.dat" TO XK: COPY "YK.DAT" TO YK'
        new=line.replace('GOSUB 2500',TEXT_CALL)
        changed+=new!=line
        result.append(new)
    if changed != 7:
        raise ValueError(f'Expected seven text CALL sites, found {changed}')
    loop='\n'.join(result)+'\n'
    # LOOP.SYS executes CLEAR again at startup; keep the Z80 RAM reservation.
    if '105 CLEAR 1000: DEFINTA-Z: DEFDBL X,Y' not in loop:
        raise ValueError('Unexpected LOOP.SYS CLEAR statement')
    loop=loop.replace('105 CLEAR 1000: DEFINTA-Z: DEFDBL X,Y',
                      '105 CLEAR 1000,&HC7FF: DEFINTA-Z: DEFDBL X,Y')
    # The original Git source contains Unicode em dashes in two REM comments.
    # MSX Disk BASIC ASCII only permits 7-bit text; normalize comments here.
    loop=loop.replace('\u2014','-')
    if '2500 ' in loop or '2690 ' in loop or 'GOSUB 2500' in loop or 'X(4,110)' in loop:
        raise ValueError('Unused BASIC font renderer or array was retained')
    for item in [init,loop]:
        buf=encode_msx_basic(item.encode('ascii'))
        validate_msx_basic(buf)
    return init,loop,changed


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--root',type=Path,default=Path('.'))
    p.add_argument('--output',type=Path,default=Path('z80/build'))
    args=p.parse_args()
    init=(args.root/'src/KBLINIT.SYS').read_text(encoding='utf-8')
    loop=(args.root/'src/LOOP.SYS').read_text(encoding='utf-8')
    init,loop,count=transform(init,loop)
    args.output.mkdir(parents=True,exist_ok=True)
    for name,value in [('KBLINIT.SYS',init),('LOOP.SYS',loop)]:
        (args.output/name).write_bytes(encode_msx_basic(value.encode('ascii')))
    print(f'Full Kabelkrant Z80 experiment: {count} CALL TEXT sites, RAMdisk unchanged')


if __name__=='__main__':
    main()
