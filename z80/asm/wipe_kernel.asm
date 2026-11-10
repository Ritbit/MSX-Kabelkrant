; Kabelkrant V9938 wipe prototype: effect #1 (top -> bottom).
; ISOLATED KERNEL. Not referenced by the working TEXT module or by LOOP.SYS.
; Replaces BASIC lines 3240: FOR A=50 TO 212 STEP 2:
;   LINE(0,A)-(512,A+1),0,BF : NEXT
; In SCREEN 7 the visible area ends at Y=211, so omit A=212.
; Uses one BIOS JIFFY frame between two-scanline bands when IRQs enabled.
;
; WIPE_REVERSE must be defined as numeric 0 (forward) or 1 (reverse)
; by the wrapper before including this file; test actual assembled bytes.
; Requires existing non-reentrant V9938 command queue.
    ORG 0C804h
    dw WipeTopDown         ; MSX BLOAD/R entry is C806 (after two-byte vector)

WipeTopDown:
    push af
    push bc
    push de
    push hl
    ld hl,0
    ld (LmDX),hl
    IF WIPE_REVERSE
    ld hl,210                ; reverse: y=210,208,...,50
    ELSE
    ld hl,50                 ; forward: y=50,52,...,210
    ENDIF
    ld (LmDY),hl
    ld hl,512
    ld (LmNX),hl
    ld hl,2
    ld (LmNY),hl
    xor a
    ld (LmCLR),a
    ld (LmARG),a
    ld a,080h             ; LMMV, logical operation IMP
    ld (LmCMD),a
.next_band:
    call LmmmLaunch      ; wait CE idle then issue one 512x2 fill
    call WipeWaitIdle     ; ensure completed *before* pacing / next band
    call WipeWaitFrame    ; use one 50/60-Hz video tick per band, when IRQs enabled
    ld hl,(LmDY)
    IF WIPE_REVERSE
    ld a,l
    cp 50
    jr z,.done
    dec hl
    dec hl
    ld (LmDY),hl
    jr .next_band
    ELSE
    inc hl
    inc hl
    ld (LmDY),hl
    ld a,h
    or a
    jr nz,.done
    ld a,l
    cp 212               ; visible rows: 50..211 inclusive (81 bands)
    jr c,.next_band
    ENDIF
.done:
    ; Do not return with an outstanding VDP command, since BASIC may
    ; immediately issue a new LINE/COPY.
    call WipeWaitIdle
    pop hl
    pop de
    pop bc
    pop af
    ret

; Wait for status S#2 command-execution (CE) to clear. Preserve IFF2.
WipeWaitIdle:
    push af
    push de
    ld a,i
    jp po,.iff_off
    ld a,1
    jr .iff_saved
.iff_off:
    xor a
.iff_saved:
    ld (WipeSavedIFF),a
.wait:
    di
    ld a,2
    out (VDPCTRL),a
    ld a,08Fh
    out (VDPCTRL),a
    in a,(VDPCTRL)
    ld d,a
    xor a
    out (VDPCTRL),a
    ld a,08Fh
    out (VDPCTRL),a
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
    jr z,.return
    ei
.return:
    pop de
    pop af
    ret

 ; A frame tick is optional: if interrupts are disabled, do not hang.
 ; JIFFY is incremented by the MSX BIOS VBlank interrupt.
JIFFY EQU 0FC9Eh
WipeWaitFrame:
    push af
    push hl
    ld a,i
    jp po,.exit
    ld hl,JIFFY
    ld a,(hl)
.wait:
    cp (hl)
    jr z,.wait
.exit:
    pop hl
    pop af
    ret

WipeSavedIFF: db 0
    INCLUDE 'v9938_lmmm.asm'
