# Harmonically Related LFOs

Six harmonically related sine/saw/square wave LFOs

- `din``: Reset all LFOs
- `ain`: Added to master rate
- `k1`: Master rate
- `k2`: Adjusts the master clock division of the currently selected LFO (or the maximum voltage
  for noise)
- `b1`, short press: Change mode of current LFO between sine/saw/square/off/random/noise
- `b1`, long press (> 0.5sec): Toggles between displaying all LFOs or just the currently selected
  one
- `b2`: Select the next LFO
- `cv1`-`cv6`: LFO outputs

## Editing/understanding the program

There is a list named ```divisions``` which controls the relationship of each LFO to the master
clock, in terms of its division. You could change them to all be evenly divisible, for example
`[1, 2, 4, 8, 16, 32]`, or to be very 'unrelated', for example
`[1.24, 5.27, 9.46, 13.45, 17.23, 23.54]`. The last example would only come back into sync after
2,472,424,774,707 cycles, which is approximately 78400 years at one second per cycle.

The default example uses all prime numbers (except 1 if you want to be technical), and will only
sync up around 15,015 cycles. You can change any of these values during operation of the program by
using knob 2, and button 2 to change which LFO you have selected. The maximum division is controlled
by the MAX_HARMONIC variable at the top of the script.

Both the division and mode (wave shape) of each LFO are saved to a file, so will be retained after
shut down. For this reason there isn't much point in changing the values of the LFO divisions in
code, as they will be overwritten and saved as soon as you use knob 2 to alter them.

The state of ```viewAllWaveforms``` is also saved to the same file. Therefore, you can set it and
forget it to your preferred view, or toggle as desired. Either way, the previous state will be
recalled on power up.

There is also a variable named ```MAX_VOLTAGE```, which is likely only going to be 10 or 5
depending on which you prefer in your system, and what modules you are controlling. This is
inherited by the `MAX_OUTPUT_VOLTAGE` set in `europi.py`, but you can override it if you use this
script for something specific.
