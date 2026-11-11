# Headless openMSX regression evidence, ROM-configured Philips NMS 8250.
# Usage: set KBL_CASE=loop or ctest; openmsx -machine Philips_NMS_8250 ...
# All saved screenshots are **evidence**, not proof of runtime correctness.
# The RAMdisk test has an independent proof marker written to a disposable A: disk.

set case [expr {[info exists ::env(KBL_CASE)] ? $::env(KBL_CASE) : "loop"}]
set out [file normalize "z80/build/openmsx-regression"]
file mkdir $out
set throttle off

proc kbl_capture {stamp} {
    global out case
    set png [file join $out "${case}-${stamp}.png"]
    screenshot -raw $png
    set marker [open [file join $out "${case}-${stamp}.done"] w]
    puts $marker "KBL_OPENMSX_CAPTURE:${case}:${stamp}:${png}"
    close $marker
}

proc kbl_done {message} {
    global out case
    set marker [open [file join $out "${case}.done"] w]
    puts $marker $message
    close $marker
}

if {$case eq "loop"} {
    # Sample several pages at many emulator seconds to see both wipes
    # and full screen changes. No screenshot is claimed as a pass alone.
    after time 30  {kbl_capture 030}
    after time 75  {kbl_capture 075}
    after time 120 {kbl_capture 120}
    after time 165 {kbl_capture 165}
    after time 210 {kbl_capture 210; kbl_done "KBL_LOOP_TRACE_DONE"; exit}
} elseif {$case eq "ctest"} {
    # The auto BASIC diagnostic starts after the initializer copied A:->C:.
    # The separate KBLPASS.OK marker in the *emulator's disposable disk*
    # is the machine-checkable proof of the C: round trip.
    after time 25 {kbl_capture 025}
    after time 60 {kbl_capture 060; kbl_done "KBL_CTEST_TRACE_DONE"; exit}
} else {
    error "Unsupported KBL_CASE: $case"
}
