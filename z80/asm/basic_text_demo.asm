; MSX2 Kabelkrant: experimental _TEXT (standalone, not production safe).
; BLOAD from C004 after CLEAR 300,&HBFFF in short test harness.
; Restrictions for initial test: font 2-3, colour 15, X >= 0.
; Sample: CALL TEXT("HELLO",20,90,2,15)
SLTATR EQU 0FCC9h
RAMAD3 EQU 0F344h
PROCNM EQU 0FD89h
VALTYP EQU 0F663h
DACSTR EQU 0F7F8h
CALBAS EQU 00159h
CHRGTR EQU 04666h
FRMEVL EQU 04C64h
FRMQNT EQU 0542Fh
GETBYT EQU 0521Ch
FRESTR EQU 067D0h
ERRHAND EQU 0406Fh
CHPUT EQU 000A2h

    ORG 0C004h
    dw CallHandler
Install:
    ld hl,EmbeddedFonts
    call SetFontBase
    ld a,(RAMAD3)
    and 15
    ld e,a
    rlca
    rlca
    rlca
    rlca
    or e
    and 60
    ld e,a
    ld d,0
    ld hl,SLTATR+3
    add hl,de
    set 5,(hl)
    ret

CallHandler:
    push hl
    ld de,TextName
    call CompareName
    jr z,.text
    ld de,VerName
    call CompareName
    jr z,.ver
    pop hl
    scf
    ret
.text:
    pop hl
    call TextCommand
    or a
    ret
.ver:
    pop hl
    call VersionCommand
    or a
    ret
CompareName:
    ld hl,PROCNM
.loop:
    ld a,(de)
    cp (hl)
    ret nz
    or a
    ret z
    inc de
    inc hl
    jr .loop
TextName: db 'TEXT',0
VerName:  db 'KBLVER',0
VerMsg:   db 'KBL Z80 TEXT TEST 0.1',13,10,0

VersionCommand:
    ld de,VerMsg
.next:
    ld a,(de)
    or a
    ret z
    push de
    call CHPUT
    pop de
    inc de
    jr .next

TextCommand:
    call GetChar
    cp '('
    jp nz,SyntaxError
    inc hl
    ld ix,FRMEVL
    call CALBAS
    ld a,(VALTYP)
    cp 3
    jp nz,TypeError
    push hl
    ld hl,(DACSTR)
    ld a,(hl)
    ld (text_length),a
    inc hl
    ld e,(hl)
    inc hl
    ld d,(hl)
    ex de,hl
    ld de,text_buffer
    ld a,(text_length)
    ld c,a
    ld b,0
    ldir
    ld ix,FRESTR
    call CALBAS
    pop hl

    call ExpectComma
    ld ix,FRMQNT
    call CALBAS
    ld (dest_x),de
    bit 7,d
    jp nz,IllegalFunction
    call ExpectComma
    ld ix,FRMQNT
    call CALBAS
    ld (dest_y),de
    bit 7,d
    jp nz,IllegalFunction
    call ExpectComma
    ld ix,GETBYT
    call CALBAS
    ld (text_font),a
    call ExpectComma
    ld ix,GETBYT
    call CALBAS
    ld (text_colour),a
    call GetChar
    cp ')'
    jp nz,SyntaxError
    inc hl

    push hl
    ld a,(text_colour)
    cp 15
    jp nz,IllegalFunctionPop
    ld a,(text_font)
    cp 2
    jp c,IllegalFunctionPop
    cp 5
    jp nc,IllegalFunctionPop
    call SelectFont
    jp c,IllegalFunctionPop
    call RenderText
    pop hl
    ret

GetChar:
    dec hl
    ld ix,CHRGTR
    jp CALBAS                 ; HL now points to current char; caller consumes it
ExpectComma:
    call GetChar
    cp ','
    jp nz,SyntaxError
    inc hl
    ret
TypeError:
    ld e,13
    jp BasicError
SyntaxError:
    ld e,2
    jp BasicError
IllegalFunctionPop:
    pop hl
IllegalFunction:
    ld e,5
BasicError:
    ld ix,ERRHAND
    jp CALBAS

RenderText:
    ld hl,text_buffer
    ld (text_cursor),hl
    ld a,(text_length)
    ld (text_remaining),a
.next:
    ld a,(text_remaining)
    or a
    ret z
    dec a
    ld (text_remaining),a
    ld hl,(text_cursor)
    ld a,(hl)
    inc hl
    ld (text_cursor),hl
    call GlyphLookup
    jr c,.space
    call GlyphBlit
    jr .advance
.space:
    ld hl,(font_record)
    inc hl
    ld e,(hl)
    ld d,0
    jr .add_width
.advance:
    ld de,(glyph_width)
.add_width:
    ld hl,(dest_x)
    add hl,de
    ld (dest_x),hl
    jr .next

; SCREEN7 page 1 sources use Y=(256 + glyph_y).
GlyphBlit:
    ld hl,(dest_x)
    ld a,h
    cp 2
    ret nc
    ld (LmDX),hl
    ld de,512
    ex de,hl
    or a
    sbc hl,de
    ld de,(glyph_width)
    or a
    sbc hl,de
    jr nc,.width_ok
    ld hl,512
    ld de,(dest_x)
    or a
    sbc hl,de
    ld (LmNX),hl
    jr .width_done
.width_ok:
    ld hl,(glyph_width)
    ld (LmNX),hl
.width_done:
    ld hl,(dest_y)
    ld a,h
    or a
    ret nz
    ld a,l
    cp 212
    ret nc
    ld (LmDY),hl
    ld de,212
    ex de,hl
    or a
    sbc hl,de
    ld a,(glyph_height)
    inc a
    ld e,a
    ld d,0
    or a
    sbc hl,de
    jr nc,.height_ok
    ld hl,212
    ld de,(dest_y)
    or a
    sbc hl,de
    ld (LmNY),hl
    jr .height_done
.height_ok:
    ld h,0
    ld a,(glyph_height)
    inc a
    ld l,a
    ld (LmNY),hl
.height_done:
    ld hl,(glyph_x)
    ld (LmSX),hl
    ld a,(glyph_y)
    ld l,a
    ld h,1
    ld (LmSY),hl
    xor a
    ld (LmCLR),a
    ld (LmARG),a
    ld a,098h
    ld (LmCMD),a
    call LmmmLaunch
    ret

text_length: db 0
text_remaining: db 0
text_colour: db 15
text_font: db 2
text_cursor: dw 0
dest_x: dw 0
dest_y: dw 0
text_buffer: ds 255,0

    INCLUDE 'font_lookup.asm'
    INCLUDE 'v9938_lmmm.asm'
EmbeddedFonts:
    INCBIN '../build/FONTS.DAT'
ModuleEnd:
