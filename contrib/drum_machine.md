# Drum Sequencer

author: Nik Ansell (github.com/gamecat69)

date: 2022-02-05

labels: sequencer, triggers, drums, randomness

A drum sequencer inspired by Grids from Mutable Instruments that contains pre-loaded drum patterns that can be smoothly morphed from one to another. Triggers are sent from outputs 1 - 3, randomized stepped CV patterns are sent from outputs 4 - 6.
Send a clock to the digital input to start the sequence.

Demo video: TBC

The following sections provide instructions for creating a simple 3 drum pattern with a kick, snare and hi-hat, then using random CV patterns to control the sound of each drum patter. You can of course connect outputs 1 - 3 to any module which expects triggers and outputs 4 - 6 to any module expecting a control voltage.

## Basic Usage
1. Connect a clock input to the Digital input
2. Connect a Bass Drum to output 1, Snare to output 2 and Hi-hat to output 3
3. Start your clock - the selected pattern will output triggers on outputs 1 -3
4. Select different patterns using knob 2 (right-hand)

## Adding randomness
1. When button 1 is pressed a random trigger pattern is sent from output 1. Toggle this feature on and off by pressing button 1 again.
2. When knob 1 (left-hand) is turned up this increases the randomness of outputs 1 -3
3. Randomness can also be controlled by sending CV to the analogue input

## Using random CV from outputs 4 - 6

Outputs 4 - 6 provide a random pattern of stepped CV which is sync'd with the inbound clock.
Press button 1 to generate a new pattern for all 3 outputs.
Example usage for these CV outputs, (this will depend on the inputs your drum module has):
- Snare Decay
- Hi-Hat decay (simulate an open hi-hat)
- Hi-Hat pitch
- Velocity
- Kick decay
- Kick accent

## Controls

- digital_in: clock in
- analog_in: randomness CV

- knob_1: randomness
- knob_2: select pre-loaded drum pattern

- button_1: toggle randomized hi-hats on / off
- button_2: generate a new random cv pattern for outputs 4 - 6

- output_1: trigger 1 / Bass Drum
- output_2: trigger 2 / Snare Drum
- output_3: trigger 3 / Hi-Hat
- output_4: randomly generated CV (cycled by pushing button 2)
- output_5: randomly generated CV (cycled by pushing button 2)
- output_6: randomly generated CV (cycled by pushing button 2)