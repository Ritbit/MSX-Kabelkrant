"""Wipes #13/#14: BASIC semantics, exact geometry, machine bytes, FAT12.

Run only after SjASMPlus and two test disks have been generated.
Verifies actual embedded data tables and BLOAD entry addresses.
"""
from pathlib import Path
from struct import pack, unpack_from
import subprocess
import unittest

ROOT=Path(__file__).resolve().parents[2]
BUILD=ROOT/"z80"/"build"
BASIC=(ROOT/"src"/"LOOP.SYS").read_text()
ASM13=(ROOT/"z80"/"asm"/"wipe13.asm").read_text()
ASM14=(ROOT/"z80"/"asm"/"wipe14.asm").read_text()


def code(n):
    data=(BUILD/f"WIPE{n}.BIN").read_bytes()
    assert data[0] == 0xFE
    start,end,entry=unpack_from("<HHH",data,1)
    assert (start,entry)==(0xC804,0xC806)
    assert end==start+len(data)-8
    return data[7:]


def disk_read(n,name):
    disk=BUILD/f"KBLWIPE{n}.DSK"
    assert disk.stat().st_size==737280
    return subprocess.check_output(
        ["mcopy","-i",str(disk),f"::{name}","-"],stderr=subprocess.PIPE)


def table13():
    records=[]
    for a in range(0,257,2):
        records.append(tuple(
            n if 0<=n<=511 else 0xFFFF
            for n in (a,512-a,257+a,257-a)
        ))
    return records


def table14():
    records=[]
    for y in range(0,78,2):
        x=2*y
        rects=((x,512-x,y+50,212-y),
               (x+1,511-x,y+50,212-y),
               (182-x,330+x,131-y,131+y),
               (183-x,329+x,131-y,131+y))
        for x0,x1,y0,y1 in rects:
            left=max(0,min(x0,x1))
            right=min(511,max(x0,x1))
            top=max(50,min(y0,y1))
            bottom=min(211,max(y0,y1))
            assert left<=right and top<=bottom
            records.append((left,right,top,bottom,
                            right-left+1,bottom-top+1))
    return records


class LastWipeTests(unittest.TestCase):
    def test_original_basic_shapes(self):
        one=next(x for x in BASIC.splitlines() if x.startswith("3360 "))
        two=next(x for x in BASIC.splitlines() if x.startswith("3370 "))
        self.assertIn("FOR A = 0 TO 256  STEP 2",one)
        self.assertIn("LINE(257+A,50)-(257+A,212),0",one)
        self.assertIn("LINE (257-A,50)-(257-A,212),0",one)
        self.assertIn("FOR Y = 0 TO 77   STEP 2",two)
        self.assertEqual(two.count(",0,B:"),4)
        self.assertNotIn(",0,BF:",two)

    def test_column13_exact_source_and_visible_coverage(self):
        rows=table13()
        self.assertEqual(len(rows),129)
        self.assertEqual(rows[0],(0,0xFFFF,257,257))
        self.assertEqual(rows[-1],(256,256,0xFFFF,1))
        columns={x for row in rows for x in row if x!=0xFFFF}
        self.assertEqual(columns,set(range(512)))
        listing=(ROOT/"z80"/"asm"/"wipe13_columns.asm").read_text()
        lines=[x for x in listing.splitlines() if x.strip().startswith("dw ")]
        self.assertEqual(len(lines),129)
        for line,expected in zip(lines,rows):
            self.assertEqual(tuple(int(x) for x in line.split(";")[0].strip()[3:].split(",")),expected)

    def test_box14_exact_source_and_clipped_rectangles(self):
        rows=table14()
        self.assertEqual(len(rows),156)
        self.assertEqual(rows[0],(0,511,50,211,512,162))
        self.assertTrue(all(0<=l<=r<=511 and 50<=t<=b<=211 and
                            w==r-l+1 and h==b-t+1
                            for l,r,t,b,w,h in rows))
        listing=(ROOT/"z80"/"asm"/"wipe14_boxes.asm").read_text()
        lines=[x for x in listing.splitlines() if x.strip().startswith("dw ")]
        self.assertEqual(len(lines),156)
        for line,expected in zip(lines,rows):
            self.assertEqual(tuple(int(x) for x in line.split(";")[0].strip()[3:].split(",")),expected)

    def test_wipe14_all_four_rectangles_share_exact_centre(self):
        # The old BASIC inner pair was 11.5 pixels above the outer pair.
        # Check all 39 iterations, not only the first or last contours.
        rows=table14()
        for i in range(0,len(rows),4):
            group=rows[i:i+4]
            self.assertEqual(len(group),4)
            for left,right,top,bottom,width,height in group:
                self.assertIn(left+right,(511,512), "horizontal centre must be at X=255.5 or 256")
                # The outermost first pass clips x=512 -> 511; that first
                # record is unavoidably off by one after screen clipping.
                # Outer Y=212 clips to 211 in the first pass only.
                self.assertIn(top+bottom,(261,262), "vertical centre must be near Y=131")
                if i>0 or (left,right) not in ((0,511),(1,511)):
                    self.assertEqual(top+bottom,262, "both moving squares must be centred on Y=131")
            self.assertEqual(group[2][2],group[3][2])
            self.assertEqual(group[2][3],group[3][3])
        self.assertEqual((rows[2][2],rows[2][3]),(131,131))
        self.assertEqual((rows[-2][2],rows[-2][3]),(55,207))

    def test_command_shapes(self):
        self.assertIn("ld hl,1\n    ld (LmNX),hl",ASM13)
        self.assertIn("ld hl,162\n    ld (LmNY),hl",ASM13)
        self.assertIn("ld a,129",ASM13)
        self.assertIn("ld b,4",ASM13)
        self.assertIn("call WipeWaitFrame",ASM13)
        self.assertIn("ld bc,12\n    ldir",ASM14)
        self.assertEqual(ASM14.count("call LmmmLaunch"),5)
        self.assertIn("ld a,39",ASM14)
        self.assertIn("ld a,4",ASM14)
        self.assertIn("call WipeWaitFrame",ASM14)

    def test_wipe14_full_black_final_state(self):
        # Rectangular outlines alone leave untouched pixels. The kernel
        # must finish with a full fill, not merely draw the last outline.
        tail=ASM14.split("FinalFullClear:",1)
        self.assertEqual(len(tail),2,"missing unconditional final clear")
        before,after=tail
        self.assertIn("jr nz,.next_step",before.split(".next_step:",1)[-1])
        instructions=after.split("    pop hl",1)[0]
        required=(
            "ld hl,0\n    ld (LmDX),hl",
            "ld hl,50\n    ld (LmDY),hl",
            "ld hl,512\n    ld (LmNX),hl",
            "ld hl,162\n    ld (LmNY),hl",
            "xor a\n    ld (LmCLR),a",
            "ld (LmARG),a",
            "ld a,080h",
            "ld (LmCMD),a",
            "call LmmmLaunch",
            "call WipeWaitIdle",
        )
        positions=[instructions.index(token) for token in required]
        self.assertEqual(positions,sorted(positions))
        self.assertEqual(ASM14.count("call LmmmLaunch"),5)
        # Both expected dimensions and coordinates must be encoded in
        # the *assembled* machine-code body after the contour loop.
        body=code(14)
        final=body[body.index(b"\x21\x00\x02"):]
        self.assertIn(b"\x21\xa2\x00",final)  # LD HL,162
        self.assertIn(b"\x21\x32\x00",final)  # LD HL,50
        self.assertIn(b"\x3e\x80",final)          # LMMV command

    def test_actual_binaries_embed_tables_and_pointer(self):
        for num,rows in ((13,table13()),(14,table14())):
            with self.subTest(num=num):
                body=code(num)
                packed=b"".join(pack("<"+"H"*len(row),*row) for row in rows)
                self.assertIn(packed,body)
                self.assertEqual(body.count(packed),1)
                addr=0xC804+body.index(packed)
                # The first LD HL in either BLOAD entry points to its
                # table, and the complete table appears only once.
                self.assertIn(pack("<BH",0x21,addr),body[:32])
                self.assertLess(0xC804+len(body),0x10000)
        self.assertNotEqual(code(13),code(14))

    def test_disk_images_have_correct_binary_and_autoexec(self):
        for num,label in ((13,b"FOUR COLUMN INTERLACE"),
                          (14,b"FOUR RECTANGLES")):
            with self.subTest(num=num):
                complete=(BUILD/f"WIPE{num}.BIN").read_bytes()
                self.assertEqual(disk_read(num,f"WIPE{num}.BIN"),complete)
                boot=disk_read(num,"AUTOEXEC.BAS")
                self.assertIn(f'BLOAD "WIPE{num}.BIN",R'.encode(),boot)
                self.assertIn(label,boot)
                other=27-num
                self.assertNotIn(f'BLOAD "WIPE{other}.BIN",R'.encode(),boot)


if __name__=="__main__":
    unittest.main()
