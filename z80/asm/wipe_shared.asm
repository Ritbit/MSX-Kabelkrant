; Shared experimental wipe core for CALL WIPE(1..8).
; Included in generated TEXT assembly BEFORE EmbeddedFonts.
; Reuses the existing TEXT V9938 LmmmLaunch/Lm* parameters (no duplicate VDP).
; Fixed drawing region SCREEN 7 X0..511 Y50..211. No title changes.
;
; Input A = 1..8. Caller has validated BASIC syntax/range.
; Modes 1,2: vertical single bands; 3,4: horizontal single bands;
; 5,7: vertical paired edges; 6,8: horizontal paired edges.
;
; Unverified when embedded in the full newspaper: isolated patterns
; had prior WebMSX visual acceptance; do not promote without new test.

WipeSharedRun:
    push af
    push bc
    push de
    push hl
    ld (WipeMode),a
    ld b,a
    ld a,4
    ld (WipePace),a
    ld a,b
    cp 3
    jr c,.vertical
    cp 5
    jr c,.horizontal
    cp 6
    jr z,.horizontal
    cp 8
    jr z,.horizontal
.vertical:
    ld hl,0
    ld (LmDX),hl
    ld hl,512
    ld (LmNX),hl
    ld hl,2
    ld (LmNY),hl
    ld a,1
    ld (WipePace),a
    ld a,b
    cp 5
    jr z,.v5
    cp 7
    jr z,.v7
    ld hl,50
    ld de,210
    ld a,81
    ld (WipeRemaining),a
    ld a,b
    cp 2
    jr nz,.setpos
    ex de,hl
    jr .setpos
.v5:
    ld hl,50
    ld de,210
    ld a,41
    ld (WipeRemaining),a
    jr .setpos
.v7:
    ld hl,130
    ld de,130
    ld a,41
    ld (WipeRemaining),a
    jr .setpos
.horizontal:
    ld hl,50
    ld (LmDY),hl
    ld hl,2
    ld (LmNX),hl
    ld hl,162
    ld (LmNY),hl
    ld a,b
    cp 6
    jr z,.h6
    cp 8
    jr z,.h8
    ld hl,0
    ld de,510
    xor a                   ; 256 iterations, 8-bit wrap
    ld (WipeRemaining),a
    ld a,b
    cp 4
    jr nz,.setpos
    ex de,hl
    jr .setpos
.h6:
    ld hl,0
    ld de,510
    ld a,128
    ld (WipeRemaining),a
    ld a,2
    ld (WipePace),a
    jr .setpos
.h8:
    ld hl,254
    ld de,256
    ld a,128
    ld (WipeRemaining),a
    ld a,2
    ld (WipePace),a
.setpos:
    ld (WipeNear),hl
    ld (WipeFar),de
    xor a
    ld (LmCLR),a
    ld (LmARG),a
    ld a,080h
    ld (LmCMD),a
    ld a,(WipePace)
    ld (WipePaceLeft),a
.next:
    ld hl,(WipeNear)
    call WipeSetCoordinate
    call LmmmLaunch
    ld a,(WipeMode)
    cp 5
    jr c,.completed
    ld hl,(WipeFar)
    call WipeSetCoordinate
    call LmmmLaunch
.completed:
    call WipeSharedIdle
    ld hl,WipePaceLeft
    dec (hl)
    jr nz,.advance
    ld a,(WipePace)
    ld (hl),a
    call WipeSharedFrame
.advance:
    ld hl,WipeRemaining
    dec (hl)
    jr z,.done
    ; Modes 2,4,7,8 descend on the near edge; the other modes ascend.
    ld a,(WipeMode)
    cp 2
    jr z,.near_down
    cp 4
    jr z,.near_down
    cp 7
    jr z,.near_down
    cp 8
    jr z,.near_down
    ld hl,(WipeNear)
    inc hl
    inc hl
    ld (WipeNear),hl
    ld hl,(WipeFar)
    dec hl
    dec hl
    ld (WipeFar),hl
    jr .next
.near_down:
    ld hl,(WipeNear)
    dec hl
    dec hl
    ld (WipeNear),hl
    ld hl,(WipeFar)
    inc hl
    inc hl
    ld (WipeFar),hl
    jr .next
.done:
    pop hl
    pop de
    pop bc
    pop af
    ret

; HL contains coordinate. Vertical modes 1,2,5,7 write DY.
; Horizontal modes 3,4,6,8 write DX.
WipeSetCoordinate:
    push af
    ld a,(WipeMode)
    cp 3
    jr c,.y
    cp 5
    jr c,.x
    cp 6
    jr z,.x
    cp 8
    jr z,.x
.y:
    ld (LmDY),hl
    pop af
    ret
.x:
    ld (LmDX),hl
    pop af
    ret

; Ensure last VDP command has completed before BASIC starts next action.
; Shared launch routine already handles interrupt preservation; reuse
; its CE polling policy here, with status-select restored to 0.
WipeSharedIdle:
    push af
    push de
    ld a,i
    jp po,.iff_off
    ld a,1
    jr .iff_saved
.iff_off:
    xor a
.iff_saved:
    ld (WipeIFF),a
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
    jr z,.idle
    ld a,(WipeIFF)
    or a
    jr z,.wait
    ei
    jr .wait
.idle:
    ld a,(WipeIFF)
    or a
    jr z,.ret
    ei
.ret:
    pop de
    pop af
    ret

; BIOS JIFFY is incremented by interrupts, but do not spin if IFF2 off.
WipeSharedFrame:
    push af
    push hl
    ld a,i
    jp po,.ret
    ld hl,0FC9Eh
    ld a,(hl)
.wait:
    cp (hl)
    jr z,.wait
.ret:
    pop hl
    pop af
    ret

WipeMode:      db 0
WipeRemaining: db 0
WipeNear:      dw 0
WipeFar:       dw 0
WipePace:      db 0
WipePaceLeft:  db 0
WipeIFF:       db 0
