; Wipe #14, original LOOP.SYS line 3370.
; Four single-pixel rectangle outlines for Y=0..76 STEP 2.
; Their clipped geometry is in wipe14_boxes.asm (39 x 4 records).
; Each rectangle is drawn using four 1-pixel V9938 LMMV/IMP strips.
; We retain BASIC's sequence; clipping excludes x=512, y=212 and title.
; ISOLATED preview binary, no changes to live newspaper.
    ORG 0C804h
    dw WipeFourBoxes
JIFFY EQU 0FC9Eh

WipeFourBoxes:
    push af
    push bc
    push de
    push hl
    ld hl,FourBoxTable
    ld (TablePtr),hl
    ld a,39
    ld (RemainingSteps),a
    xor a
    ld (LmCLR),a
    ld (LmARG),a
    ld a,080h              ; V9938 LMMV, IMP, black
    ld (LmCMD),a

.next_step:
    ld a,4
    ld (RemainingBoxes),a

.next_box:
    ld hl,(TablePtr)
    ld de,FrameLeft
    ld bc,12
    ldir                   ; always copy 12 bytes, never BC=0
    ld (TablePtr),hl

    ; Top edge: width pixels, height one.
    ld hl,(FrameLeft)
    ld (LmDX),hl
    ld hl,(FrameTop)
    ld (LmDY),hl
    ld hl,(FrameWidth)
    ld (LmNX),hl
    ld hl,1
    ld (LmNY),hl
    call LmmmLaunch

    ; Bottom edge: width pixels, height one.
    ld hl,(FrameBottom)
    ld (LmDY),hl
    call LmmmLaunch

    ; Left edge: one pixel, height pixels.
    ld hl,(FrameTop)
    ld (LmDY),hl
    ld hl,(FrameHeight)
    ld (LmNY),hl
    ld hl,1
    ld (LmNX),hl
    call LmmmLaunch

    ; Right edge: one pixel, full height.
    ld hl,(FrameRight)
    ld (LmDX),hl
    call LmmmLaunch
    call WipeWaitIdle

    ld a,(RemainingBoxes)
    dec a
    ld (RemainingBoxes),a
    jr nz,.next_box

    ; One frame after all four outlines, approximately 39 frames.
    call WipeWaitFrame
    ld a,(RemainingSteps)
    dec a
    ld (RemainingSteps),a
    jr nz,.next_step

    pop hl
    pop de
    pop bc
    pop af
    ret

TablePtr:        dw 0
RemainingSteps:  db 0
RemainingBoxes:  db 0
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


WipeSavedIFF:    db 0
    INCLUDE 'v9938_lmmm.asm'
    INCLUDE 'wipe14_boxes.asm'
