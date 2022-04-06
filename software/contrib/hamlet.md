# EuroPi Hamlet - Sequencing Drums and Two Voices

author: Sean Bechhofer (github.com/seanbechhofer)

date: 2022-04-03

labels: sequencer, gates, triggers, drums, randomness

**TB or not TB?** Hamlet is a drum and voice sequencer based on
Nik Ansell's Consequencer, which is itself inspired by Grids from
Mutable Instruments. It includes features inspired by O_C's TB3PO,
adding two tracks of CV and gates. Density of notes played on the CV
tracks can be adjusted. 

The app provides two gates for drum patterns and a pair of channels
giving gate/CV to drive voices. 

Use outputs 1/2 for drum gates. Pairs 3/4 and 5/6 provide gate/CV for
melody lines. Send a clock to the digital input to start the sequence.

Credits:
- The Europi hardware and firmware was designed by Allen Synthesis:
https://github.com/Allen-Synthesis/EuroPi
- Hamlet is based on the Consequencer by Nik Ansell (github.com/gamecat69)

# Controls

- digital_in: Clock in
- analog_in: Mode 1: Randomness, Mode 2: Selects gate pattern, Mode 3: Selects voice patterns

- knob_1: Adjust sparsity
- knob_2: Select pre-loaded gate pattern

- button_1: Short Press: Select previous voice pattern for tracks 1 and 2.. Long
  Press: Not used
- button_2: Short Press: Select next voice patterns for tracks 1
  and 2. Creates a new pattern if we're at the last. Long Press: Cycle
  through analogue input modes

- output_1: gate 1 e.g Kick Drum
- output_2: gate 2 e.g Hi-Hat
- output_3: track 1 gate
- output_4: track 1 randomly generated stepped CV 
- output_5: track 2 gate
- output_6: track 2 randomly generated stepped CV

# Getting Started

The following sections provide instructions for creating a simple 2
drum pattern with a kick and hi-hat, then using random CV patterns to
drive voices.

## Basic Usage
1. Connect a clock input to the Digital input
2. Connect a Bass Drum to output 1, Hi-hat to output 2
3. Start your clock - the pattern will output gates on outputs 1/2.
4. Select different patterns manually using knob 2 (right-hand
knob). The selected pattern is shown visually on the screen.

## Voices 
1. Connect output 3 to gate on voice 1
2. Connect output 4 to pitch on voice 1, optionally via quantiser/attenuator.
3. Connect output 5 to gate on voice 2
4. Connect output 6 to pitch on voice 2, optionally via quantiser/attenuator.
5. Gates will be output on 3/5 according to the gate pattern
6. The gate pattern for track 1 will be shown on the screen.
7. Knob 1 increases or decreases the sparsity of the gates sent to
   outputs 3 and 5. Fully CCW all notes are played, as the knob is
   turned CW, notes will drop out of the sequence.

## Sparsity

A key feature of the two voice tracks in Hamlet is *sparsity*
control. With this set to 0, all events in the track are present. As
the level of sparsity increases, the number of gates emitted
reduces. The CV output values will only change when a gate is
emitted.

This is done as follows. Each track has a number of steps, each with a
voltage and sparsity value. Sparsities are allocated randomly from 1
to the length of the track. When the value selected by the left knob
is greater than the sparsity value, the step is disabled, and no
change to CV value is made. The figure below shows this, with values
`V1` up to `V16` being the voltages in the pattern and the sparsity
values shown in the second row. As the knob value increases, more
gates are disabled. Here, `VX` refers to the CV value that was being
emitted before the pattern started. For example, if the knob sparsity
is 10 and the pattern is looping, then `VX` will be `V16`.

Note that every time a CV pattern is created through a right button
press, that pattern will have a new random set of sparsity
values. Note also that track 1 and track 2 have *different* gate
patterns, thus different notes will drop out giving some nice
interplay between the voices.

## Selecting analogue input modes

Hamlet can perform 3 different actions when a control voltage input is received at the analogue input.
The current running mode is shown on the bottom right of the screen (e.g. M1, M2, M3)
Cycle through the modes by long-pressing and releasing button 2. The following modes are available:

- Mode 1: Randomness
- Mode 2: Control voltage selects the gate pattern
- Mode 3: Control voltage selects the stepped CV pattern

## Controlling a pattern using CV

1. Select analogue mode 2.
2. Send a control voltage into the analogue input

A fixed voltage will select a single pattern and varying voltage (e.g. an envelope or LFO) will smoothly cycle through patterns.

## Adding / Removing / Updating Gate Patterns

1. Update patterns in the code
2. Restart the Europi module, or restart the program if using a micropython IDE/CLI

The syntax is like Consequencer, but with only two tracks.

The mapping of `BD`, `HH` is as follows:
- BD: Output 1
- HH: Output 2

```
    BD.append("1000100010001000")
    HH.append("1111111111111111")
```

# Known bugs / Interesting features

Probably. 
