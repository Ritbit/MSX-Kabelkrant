# openMSX automated screenshot capture for the standalone Z80 text demo.
# Use with: openmsx -machine Philips_NMS_8250 -diska z80/build/KBLASM.DSK -script z80/tools/openmsx_smoke.tcl
# Allow the NMS8250 disk boot and demo to finish before capture.
set throttle off
after time 120 {
    set path [file normalize "z80/build/openmsx-smoke.png"]
    screenshot -raw $path
    set marker [open [file normalize "z80/build/openmsx-smoke.done"] w]
    puts $marker "OPENMSX_SMOKE_SCREENSHOT: $path"
    close $marker
    exit
}
