; Experimental rectangular wipe #1, compiled only with WIPE_RECT=1.
; CALL WIPE(1,x1,y1,x2,y2), inclusive, SCREEN7 X=0..511 Y=0..211.
; Invalid/out-of-screen coordinates are rejected *before* VDP command.
; In-bounds only in stage 1, full clipping across screen added later.
; Existing CALL WIPE(n) remains unchanged in generated bridge.
;
; Input coordinates are signed 16-bit MSX BASIC FRMQNT values in Rect*.
; Returns carry on invalid bounds, clear on valid bounds.
WipeRectValidate:
    ld hl,(RectX2)
    ld a,h
    cp 2
    jr nc,.bad
    ld de,(RectX1)
    or a
    sbc hl,de
    jr c,.bad
    inc hl
    ld (RectWidth),hl
    ld hl,(RectY2)
    ld a,h
    or a
    jr nz,.bad
    ld a,l
    cp 212
    jr nc,.bad
    ld de,(RectY1)
    or a
    sbc hl,de
    jr c,.bad
    or a
    ret
.bad:
    scf
    ret

; Paint horizontal 1- or 2-pixel strips, waiting for each VDP command.
; The final strip is exactly 1px when the rectangle height is odd.
; IRQ/BIOS JIFFY pacing follows the shared wipe wait helper.
WipeRectRun:
    push af
    push bc
    push de
    push hl
    ld hl,(RectX1)
    ld (LmDX),hl
    ld hl,(RectY1)
    ld (LmDY),hl
    ld hl,(RectWidth)
    ld (LmNX),hl
    xor a
    ld (LmCLR),a
    ld (LmARG),a
    ld a,080h
    ld (LmCMD),a
.loop:
    ld hl,(RectY2)
    ld de,(LmDY)
    or a
    sbc hl,de
    inc hl
    ld a,l
    cp 2
    jr c,.last
    ld hl,2
    jr .size
.last:
    ld hl,1
.size:
    ld (LmNY),hl
    call LmmmLaunch
    call WipeSharedIdle
    call WipeSharedFrame
    ld hl,(LmNY)
    ld de,(LmDY)
    add hl,de
    ld (LmDY),hl
    ld de,(RectY2)
    or a
    sbc hl,de
    jr c,.loop
    jr z,.loop
    pop hl
    pop de
    pop bc
    pop af
    ret

RectX1:   dw 0
RectY1:   dw 0
RectX2:   dw 0
RectY2:   dw 0
RectWidth: dw 0
