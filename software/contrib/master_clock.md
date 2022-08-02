# EuroPi Master Clock and Clock Divider

Master Clock

author: Nik Ansell (github.com/gamecat69)

date: 2022-08-02

labels: clock, divider

A master clock and clock divider. Each output sends a +5V trigger/gate at different divisions of the master clock.
The pulse width (gate/trigger duration) is configurable using knob 1.
The maximum gate/trigger duration is 50% of the pulse width of output 1.

For wonky/more interesting clock patterns there are two additional functions:
- Reset to step 1 using a gate into the digital input
- Variable BPM using CV into the analog input

Demo video: TBC

digital_in: Reset step count on rising edge
analog_in: Adjust BPM

knob_1: BPM (In screen 2)
knob_2: Pulse width (In screen 2)

button_1: Start / Stop
button_2: Cycle through screens

Defaults:
output_1: clock / 1
output_2: clock / 2
output_3: clock / 4
output_4: clock / 8
output_5: clock / 16
output_6: clock / 32