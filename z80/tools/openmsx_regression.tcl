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
    # The 30s/75s frames captured boot/intro rather than newspaper pages.
    after time 120 {kbl_capture 120}
    after time 165 {kbl_capture 165}
    after time 210 {kbl_capture 210}
    after time 255 {kbl_capture 255; kbl_done "KBL_LOOP_TRACE_DONE"; exit}
} elseif {$case eq "long"} {
    # Unattended running: sample over >20 minutes of emulated time.
    # Each frame is evidence; intermittent uniform wipes are legitimate.
    foreach stamp {120 300 480 660 840 1020 1200 1380} {
        # A pair 2 simulated seconds apart separates transient full-screen
        # wipes from sustained blank/frozen display states.
        after time $stamp [list kbl_capture [format "%04d" $stamp]]
        after time [expr {$stamp + 2}] [list kbl_capture [format "%04d" [expr {$stamp + 2}]]]
        after time [expr {$stamp + 12}] [list kbl_capture [format "%04d" [expr {$stamp + 12}]]]
    }
    # Last 1380s sample also schedules a +12s frame at 1392s.
    after time 1395 {kbl_done "KBL_LONG_TRACE_DONE"; exit}
} elseif {$case eq "ctest"} {
    # The auto BASIC diagnostic starts after the initializer copied A:->C:.
    # The separate KBLPASS.OK marker in the *emulator's disposable disk*
    # is the machine-checkable proof of the C: round trip.
    # Boot still blank at 25s and displaying the intro at 60s.
    after time 120 {kbl_capture 120}
    after time 210 {kbl_capture 210; kbl_done "KBL_CTEST_TRACE_DONE"; exit}
} else {
    error "Unsupported KBL_CASE: $case"
}
