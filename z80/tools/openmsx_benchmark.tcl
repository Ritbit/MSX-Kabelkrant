# Headless NMS8250: auto-run existing BASIC/Z80 14-wipe benchmark.
# The guest BASIC writes BENCHRES.CSV to a disposable A: test image.
# Screenshots are diagnostics; do not interpret an unverified image as data.
set throttle off
set out [file normalize "z80/build/openmsx-benchmark"]
file mkdir $out
proc bench_capture {stamp} {
    global out
    screenshot -raw [file join $out "bench-$stamp.png"]
}
foreach stamp {240 480 720} {
    after time $stamp [list bench_capture $stamp]
}
after time 745 {
    global out
    set f [open [file join $out "benchmark.done"] w]
    puts $f "KBL_BENCH_EMULATED_745_SECONDS"
    close $f
    exit
}
