; Kabelkrant MSX2 - KBF1 font lookup kernel (prototype)
; Caller provides KBF1 data pointer. No BASIC ABI or VDP accesses.
; SetFontBase: HL = KBF1 buffer
; SelectFont: A = font number, CY clear on success
; GlyphLookup: A = ASCII character, results in glyph_* variables
; KBF1 record: ID, height, limits[3], y[3], reserved, count DW, coords[] DW

SetFontBase:
    ld (font_base),hl
    ret

SelectFont:
    cp 1
    jr c,.bad
    cp 5
    jr nc,.bad
    ld (target_id),a
    ld hl,(font_base)
    ld de,8
    add hl,de
    ld b,4
.scan:
    ld a,(hl)
    ld c,a
    ld a,(target_id)
    cp c
    jr z,.found
    push bc
    ld de,9
    add hl,de
    ld e,(hl)
    inc hl
    ld d,(hl)
    inc hl
    sla e
    rl d
    add hl,de
    pop bc
    djnz .scan
.bad:
    scf
    ret
.found:
    ld (font_record),hl
    or a
    ret

GlyphLookup:
    ld (glyph_char),a
    xor a
    ld (glyph_valid),a
    ld a,(glyph_char)
    sub 33
    jr c,.fail
    ld b,a
    ld hl,(font_record)
    ld de,2
    add hl,de
    cp (hl)
    jr c,.row0
    inc hl
    cp (hl)
    jr c,.row1
    inc hl
    ld c,(hl)
    ld a,c
    or a
    jr z,.fail
    ld a,b
    cp c
    jr nc,.fail
    inc b
    inc b
    ld c,7
    jr .row_ready
.row0:
    ld c,5
    jr .row_ready
.row1:
    inc b
    ld c,6
.row_ready:
    ld hl,(font_record)
    ld e,c
    ld d,0
    add hl,de
    ld a,(hl)
    ld (glyph_y),a
    ld hl,(font_record)
    inc hl
    ld a,(hl)
    ld (glyph_height),a
    ld hl,(font_record)
    ld de,11
    add hl,de
    ld e,b
    ld d,0
    sla e
    rl d
    add hl,de
    ld e,(hl)
    inc hl
    ld d,(hl)
    ld (glyph_x),de
    inc hl
    ld c,(hl)
    inc hl
    ld b,(hl)
    ld h,b
    ld l,c
    or a
    sbc hl,de
    bit 7,h
    jr nz,.fail
    ld a,h
    or l
    jr z,.fail
    ld (glyph_width),hl
    ld a,1
    ld (glyph_valid),a
    or a
    ret
.fail:
    scf
    ret

font_base:      dw 0
font_record:    dw 0
target_id:      db 0
glyph_char:     db 0
glyph_x:        dw 0
glyph_y:        db 0
glyph_height:   db 0
glyph_width:    dw 0
glyph_valid:    db 0
