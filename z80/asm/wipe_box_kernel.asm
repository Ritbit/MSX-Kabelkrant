; Kabelkrant wipe #9/#10: two-pixel rectangular outlines.
; BASIC source lines 3320 and 3330 use LINE(...),0,B (not BF).
; Four thin V9938 LMMV rectangles emulate a 2px outline: top/bottom
; horizontal bands and left/right vertical bands; centre stays unfilled.
; x=0,2,...254; y=floor(x*75/256); coordinates are in rect table.
; #9 outer -> inner, #10 inner -> outer. Numeric RECT_REVERSE 0/1.
; The original final x=256 degenerates to zero width, so omitted.
; Standalone BLOAD/R; no modification to the working newspaper.

    ORG 0C804h
    dw WipeBox
JIFFY EQU 0FC9Eh

WipeBox:
    push af
    push bc
    push de
    push hl
    IF RECT_REVERSE
    ld hl,RectTable+12*127
    ELSE
    ld hl,RectTable
    ENDIF
    ld (TablePtr),hl
    ld a,128
    ld (WipeRemaining),a
    ld a,2
    ld (WipePaceCounter),a
    xor a
    ld (LmCLR),a
    ld (LmARG),a
    ld a,080h             ; V9938 LMMV, IMP (black)
    ld (LmCMD),a

.next_box:
    ld hl,(TablePtr)
    ld de,FrameLeft
    ld bc,12
    ldir                  ; BC=12 always, never zero

    ; Horizontal top (two scanlines), full box width.
    ld hl,(FrameLeft)
    ld (LmDX),hl
    ld hl,(FrameTop)
    ld (LmDY),hl
    ld hl,(FrameWidth)
    ld (LmNX),hl
    ld hl,2
    ld (LmNY),hl
    call LmmmLaunch

    ; Horizontal bottom (two scanlines).
    ld hl,(FrameBottom)
    ld (LmDY),hl
    call LmmmLaunch

    ; Vertical left, two-pixel column, full box height.
    ld hl,(FrameTop)
    ld (LmDY),hl
    ld hl,(FrameHeight)
    ld (LmNY),hl
    ld hl,2
    ld (LmNX),hl
    call LmmmLaunch

    ; Vertical right, preserving an unfilled interior.
    ld hl,(FrameRight)
    ld (LmDX),hl
    call LmmmLaunch
    call WipeWaitIdle

    ld hl,WipePaceCounter
    dec (hl)
    jr nz,.advance
    ld (hl),2
    call WipeWaitFrame
.advance:
    ld a,(WipeRemaining)
    dec a
    ld (WipeRemaining),a
    jr z,.finished

    ld hl,(TablePtr)
    ld de,12
    IF RECT_REVERSE
    or a
    sbc hl,de
    ELSE
    add hl,de
    ENDIF
    ld (TablePtr),hl
    jr .next_box

.finished:
    pop hl
    pop de
    pop bc
    pop af
    ret

TablePtr:        dw 0
WipeRemaining:   db 0
WipePaceCounter: db 0
FrameLeft:       dw 0
FrameRight:      dw 0
FrameTop:        dw 0
FrameBottom:     dw 0
FrameWidth:      dw 0
FrameHeight:     dw 0

; Poll V9938 status S#2 command-execution bit (CE=bit0).
; Restore original interrupt state before returning.
WipeWaitIdle:
    push af
    push de
    ld a,i
    jp po,.off
    ld a,1
    jr .saved
.off:
    xor a
.saved:
    ld (WipeSavedIFF),a
.wait:
    di
    ld a,2
    out (099h),a
    ld a,08Fh
    out (099h),a
    in a,(099h)
    ld d,a
    xor a
    out (099h),a
    ld a,08Fh
    out (099h),a
    ld a,d
    and 1
    jr z,.done
    ld a,(WipeSavedIFF)
    or a
    jr z,.wait
    ei
    jr .wait
.done:
    ld a,(WipeSavedIFF)
    or a
    jr z,.restore
    ei
.restore:
    pop de
    pop af
    ret

WipeWaitFrame:
    push af
    push hl
    ld a,i
    jp po,.done
    ld hl,JIFFY
    ld a,(hl)
.wait:
    cp (hl)
    jr z,.wait
.done:
    pop hl
    pop af
    ret

WipeNear:        dw 0
WipeFar:         dw 0
WipeRemaining:   db 0
WipePaceCounter: db 0
WipeSavedIFF:    db 0
    INCLUDE 'v9938_lmmm.asm'\n    INCLUDE 'wipe_rect_table.asm'

