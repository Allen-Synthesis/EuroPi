# Consequencer

author: Nik Ansell (github.com/gamecat69)

date: 2022-02-05

labels: sequencer, triggers, drums, randomness

A drum and CV sequencer inspired by Grids from Mutable Instruments.
Consequencer is pre-loaded with drum patterns that can be smoothly morphed between.
Triggers are sent from outputs 1 - 3, randomized stepped CV patterns are sent from outputs 4 - 6.
Send a clock to the digital input to start the sequence.
Pattern changes and randomness is introduced as a consequence of both manual and CV-control input.

Demo video: TBC

The following sections provide instructions for creating a simple 3 drum pattern with a kick, snare and hi-hat, then using random CV patterns to control the sound of each drum patter. You can of course connect outputs 1 - 3 to any module which expects triggers and outputs 4 - 6 to any module expecting a control voltage.

Credits:
- Some drum patterns were recreated from here: https://docs.google.com/spreadsheets/d/19_3BxUMy3uy1Gb0V8Wc-TcG7q16Amfn6e8QVw4-HuD0/edit#gid=0

## Basic Usage
1. Connect a clock input to the Digital input
2. Connect a Bass Drum to output 1, Snare to output 2 and Hi-hat to output 3
3. Start your clock - a pattern will output triggers on outputs 1 -3
4. Select different patterns using knob 2 (right-hand knob)

## Adding randomness
1. Pressing button 1 (left-hand button) toggles on/off the real-time generation of a random trigger pattern to output 1.
2. Adjusting knob 1 (left-hand knob) increases or reduces the randomness of the patterns sent to outputs 1 -3
3. Randomness can also be controlled by sending CV to the analogue input if analogInputMode is set to 1 in the script.

## Using random CV from outputs 4 - 6

Outputs 4 - 6 provide a random pattern of stepped CV which is sync'd with the inbound clock.
Press button 2 to generate a new pattern for all 3 outputs.
Example usage for these CV outputs, (this will depend on the inputs your drum module has):
- Snare Decay
- Hi-Hat decay (simulate an open hi-hat)
- Hi-Hat pitch
- Velocity
- Kick decay
- Kick accent

## Controlling a pattern using CV

Send a control voltage into the analogue input to select or cycle through the patterns.
A fixed voltage will select a single pattern and varying voltage (e.g. an envelope or LFO) will cycle through patterns.

There is also an interesting bug caused by small amount of noise in the Europi which causes the drum pattern to flicker between two patterns, which creates additional pattern variation. You can find these sweet spots manually using knob 2 or, by pushing fixed CV values into the analogue input.

## Controls

- digital_in: clock in
- analog_in: pattern / randomness CV

- knob_1: randomness
- knob_2: select pre-loaded drum pattern

- button_1: Short Press: toggle randomized hi-hats on / off. Long Press: Play previous CV Pattern
- button_2: Short PressL Generate a new random cv pattern for outputs 4 - 6. Long Press: Cycle through analogue input modes

- output_1: trigger 1 e.g. Bass Drum
- output_2: trigger 2 e.g Snare Drum
- output_3: trigger 3 e.g Hi-Hat
- output_4: randomly generated CV (cycled by pushing button 2)
- output_5: randomly generated CV (cycled by pushing button 2)
- output_6: randomly generated CV (cycled by pushing button 2)