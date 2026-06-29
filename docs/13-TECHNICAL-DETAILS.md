# Technical Details

## Keyboard/input-buffer bootstrap

The boot process uses a BASIC-level hand-off around the binary `BLOAD` of the RAM disk. This is a classic practical MSX BASIC trick: prepare what BASIC should execute next, run the binary installer, then continue automatically.

## Embedded machine code

`KBLINIT.SYS` embeds a small Z80 helper in DATA statements and registers it as USR routines. This is used for string operations that would be slower or clumsier in BASIC.

## Hidden page scratch rendering

The text renderer uses a hidden VRAM page/scratch area to render proportional text before copying it into the final visible position. This allows width-dependent positioning without a separate full pre-render pass.

## Interrupt management

The display loop uses `INTERVAL` for clock updates, but disables it around sensitive rendering sections to avoid corrupting intermediate graphics operations.
