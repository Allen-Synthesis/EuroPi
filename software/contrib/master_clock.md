# EuroPi Master Clock and Clock Divider

'''
Master Clock
author: Nik Ansell (github.com/gamecat69)
date: 2022-08-02
labels: clock, divider

A master clock and clock divider. Each output sends a +5V trigger/gate at different divisions of the master clock, or randomly if condigured with a division of zero.
Pulse width (gate/trigger duration) is configurable up to a maximum of 50% of the pulse width of output 1.

All configuration (BPM, Pulse Width, output clock divisions) is automatically saved, then loaded when the module is restarted.

For wonky/more interesting clock patterns try these:
- Reset to step 1 using a gate into the digital input, or by using an odd value for the maximum division
- Vary BPM by sending CV into the analog input
- Set the division to zero for an output, this will cause the output to randomly go from high (+5V) to low (0V)

Demo video: TBC

digital_in: (optional) Reset step count on rising edge
analog_in: (optional) Adjust BPM

knob_1: Screen 2: Adjust BPM. Screen 3: Select output to edit 
knob_2: Screen 2: Adjust Pulse width. Screen 3: Adjust division of selected output 

button_1: Start / Stop
button_2: Short Press (<500ms): Cycle through screens. Long Press (>500ms): Enter config mode

Defaults:
output_1: clock / 1
output_2: clock / 2
output_3: clock / 4
output_4: clock / 8
output_5: clock / 16
output_6: clock / 32

Known Issues:
- If playback is restarted while screen 2 is in config mode, playback will be slightly irratic, especially when moving knobs
- BPM occasionally drifts by 1ms - possibly because asyncio is is truely async

# Getting started

Patch any module that uses gates/triggers to any output! By default the module will run at 100 BPM, using a 50% pulse width and send gates using the default divisions (1,2,4,8,16,32).

# Configuring / Playing around

Use button 2 (right button) to cycle through screens 1 - 3. A description of each screen is shown below.
Hold button 2 for 2 seconds to enter configuration mode when in screen 2 or 3.
Configuration mode will exit when changing screens to avoid accidentally changing any values on the next screen.
Also note that playback will stop when in config mode.
Each screen has a small indicator on the bottom right to show the screen you are on.

## Screen 1
- Top: Number of completed cycles since playback was last started, follewed by the current step in the cycle
- Bottom: Instruction to use B1 to toggle start/stop

## Screen 2
- BPM
- Pulse Width (PW) as a percentage of the output 1 division and also as milliseconds

Hold button 2 for 2 seconds to enter configuration mode, then use knob 1 (left) to adjust BPM and knob 2 (right) to adjust pulse width. To exit configuration mode, just press button 2 to move to the next screen.

## Screen 3:

This screen shows the configured clock division for each output.
To edit a clock division for an output:
- Use knob 1 to select the output you want to edit
- Press and hold button 2 for 2 seconds to enter configuration mode
- Use knob 2 to select the division you want that that output. Setting a division to zero will produce random fluctuations between 0V and +5V.
- Exit configuration mode by pressing button 2 to move to the next screen