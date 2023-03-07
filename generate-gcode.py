#!/usr/bin/env python3
from math import ceil
from math import pi

#---- Configuration (there's no CLI, etc) -------------------------------------

# Constant acceleration we must achieve.
a = 4000.0  # mm/s/s

# Duration of test time spent at each frequency.
duration = 5.0 # s

# Table of discrete frequencies at which we want to test.
freqs = [float(x) for x in range (1, 30)]

#---- Static GCode ------------------------------------------------------------

# Static GCode to emit at the start of the file.
static_gcode_start = (
''';==================================
;==== X1C Vibration Test GCode ====
;==================================

;==== initialize machine parameters ====
M73 P0 R1                        ; progress: 0%, remaining 1 minute
M201 X20000 Y20000 Z500 E5000    ; move limits
M203 X500 Y500 Z20 E30           ; max feedrate
M204 P20000 R5000 T20000         ; starting accel
M205 X9.00 Y9.00 Z3.00 E2.50     ; jerk, etc

;===== reset machine status ====
G91                              ; relative positioning
M17 Z0.4                         ; lower the z-motor current
G0 Z12                           ; lower the hotbed
G0 Z-6
G90                              ; absolute positioning
M17 X1.2 Y1.2 Z0.75              ; reset motor current to default
M960 S5 P1                       ; turn on logo lamp
M220 S100                        ; reset feedrate
M221 S100                        ; reset flowrate
M73.2 R1.0                       ; reset left time magnitude
M1002 set_gcode_claim_speed_level : 5
M221 X0 Y0 Z0                    ; turn off soft endstop
G29.1 Z0.0                       ; clear z-trim value first

;==== home x ====
G91                              ; relative positioning
G0 Z10 F1200                     ; move z down
G90                              ; absolute positioning
G28 X                            ; home x

;==== home z with low precision ====
G0 X135 Y253 F20000              ; move to exposed steel surface edge
G28 Z P0                         ; home z with low precision
G29.2 S0                         ; turn off ABL
G0 Z5 F20000                     ; move to z5

;==== init move ====
G0 X128 Y128 F20000              ; move to center of plate
M975 S0                          ; turn off vibration supression
''')

# Static GCode to emit at the end of the file.
static_gcode_end = (
''';==== footer; complete everything ====
M975 S1                          ; turn on vibration supression
M400                             ; wait for buffer to clear
''')

#---- Single frequency --------------------------------------------------------

def emit_freq(f):
    v = a / (2 * pi * f)         # velocity (mm/s)
    r = v / (2 * pi * f)         # radius (mm)
    vv = v * 60.0                # velocity (mm/min)
    n = int(ceil(f * duration))  # number of cycles

    print(f';==== frequency test {f} Hz ====')
    print(f'; velocity: {v} (mm/s)')
    print(f'; radius:   {r} (mm)')
    print(f'; cycles:   {n}')

    x0 = 128.0 + r
    y0 = 128.0
    x1 = 128.0 - r
    y1 = 128.0

    print(f'G0 X{x0} Y{y0} F600  ; move to start radius of circle')
    for i in range(0, n):
        print(f'G3 I-{r} J0 X{x1} Y{y1} F{vv}  ; first arc of circle')
        print(f'G3 I+{r} J0 X{x0} Y{y0} F{vv}  ; second arc of circle')

    print('')

#---- Full GCode --------------------------------------------------------------

def main():
    print(static_gcode_start)
    for f in freqs:
        emit_freq(f)
    print(static_gcode_end)

#---- Main --------------------------------------------------------------------

if __name__ == '__main__':
    main()
