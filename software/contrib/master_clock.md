# Master Clock and Clock Divider

A master clock and clock divider. Each output sends a +5V trigger/gate at different divisions of the
master clock, or randomly if condigured with a division of zero. Pulse width (gate/trigger duration)
is configurable up to a maximum of 50% of the pulse width of output 1.

All configuration (BPM, Pulse Width, output clock divisions) is automatically saved, then loaded
when the module is restarted.

For wonky/more interesting clock patterns try these:
- Reset to step 1 using a gate into the digital input, or by using an odd value for the maximum
  division
- Vary BPM by sending CV into the analog input
- Set the division to zero for an output, this will cause the output to randomly go from high
  (+5V) to low (0V)

## Inputs & Outputs

- knob_1: (in config mode) Select option to edit
- knob_2: (in config mode) Edit selected option

- knob_1: Screen 2: Adjust BPM. Screen 3: Select output to edit
- knob_2: Screen 2: Adjust Pulse width. Screen 3: Adjust division of selected output

- button_1: Short Press (<500ms): Start/Stop (when using internal clock). Long Press (>500ms):
  Select clock source (Internal/External)
- button_2: Short Press (<500ms): Not used. Long Press (>500ms): Enter config mode

Defaults:
- output_1: clock / 1
- output_2: clock / 2
- output_3: clock / 4
- output_4: clock / 8
- output_5: clock / 16
- output_6: clock / 32

## Getting started

Patch any module that uses gates/triggers to any output! By default the module will run at 100 BPM,
using a 50% pulse width and send gates using the default divisions (1,2,4,8,16,32).

## Configuring / Playing around

Hold button 2 for 2 seconds to enter configuration mode, then use knob 1 (left) to adjust BPM and
knob 2 (right) to adjust pulse width. To exit configuration mode, just press button 2 to move to the
next screen.

Playback may be slightly erraratic when in config mode - this is due to more screen updates hogging
the CPU

### Screen

This screen shows the BPM, Pulse width and configured clock division for each output.
The Pulse width is displayed as `PW:MS`. `PW` is a percentage of the output 1 division and `MS` is
the duration of each pulse in milliseconds

To edit the BPM (internal clock mode only), Pulse Width or the clock division for an output:
- Use knob 1 to select the output you want to edit
- Press and hold button 2 for 2 seconds to enter configuration mode
- Use knob 2 to select the division you want that that output.
- Exit configuration mode by holding button 2 for 2 seconds.

## Selecting a Clock Source

Master clock can generate its own clock, or use an external clock.
Enter clock source configuration mode using a long press on button 1.
Pressing either button 1 or button 2 will configure and save the clock source.

If using an external clock, patch the clock source into the din jack - the clock source should
ideally send a gate/trigger longer than 9ms to avoid issues.

Note that when using an external clock, the reset functionality using the din jack is disabled.

## Randomizing pulses

Selecting a clock division of `/r` will cause pulses to be sent randomly from the configured output.
Note that the 'r' option is at the end (far right) of the division options.

## Known Issues:

- BPM occasionally drifts by 1ms - possibly because asyncio is is truely async
