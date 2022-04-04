# EuroPi Hamlet - A 6-channel open source sequencer and random source power house!

author: Sean Bechhofer (github.com/seanbechhofer)


date: 2022-04-03

labels: sequencer, gates, triggers, drums, randomness

TB or not TB? Consequencer is a gate and stepped CV sequencer based on
Nik Ansell's Consequencer, which is itself inspired by Grids from
Mutable Instruments. It includes features inspired by O_C's TB3PO,
adding two tracks of CV and gates. Density of notes played on the CV
tracks can be adjusted. 

Use outputs 1/2 for drum gates. Pairs 3/4 and 5/6 provide gate/CV for
melody lines. Send a clock to the digital input to start the sequence.

Credits:
- The Europi hardware and firmware was designed by Allen Synthesis:
https://github.com/Allen-Synthesis/EuroPi
- Hamlet is based on the Consequencer by Nik Ansell (github.com/gamecat69)

# Controls

![Operating Diagram](https://user-images.githubusercontent.com/79809962/154732035-ccc0d8c1-0e4e-4b8c-97e3-ccfa07a4880b.png)

- digital_in: Clock in
- analog_in: Mode 1: Adjusts sparsity, Mode 2: Selects gate pattern, Mode 3: Selects stepped CV pattern

- knob_1: Adjust sparsity
- knob_2: Select pre-loaded gate pattern

- button_1: Short Press: Play previous stepped CV sequence. Long Press: Generate new gate pattern
- button_2: Short Press: Generate a new random stepped cv sequence for outputs 4 - 6. Long Press: Cycle through analogue input modes

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
3. Start your clock - a pattern will output gates on outputs 1/2.
4. Select different patterns manually using knob 2 (right-hand
knob). The selected pattern is shown visually on the screen.

## Voices 
1. Connect output 3 to gate on voice 1
2. Connect output 4 to pitch on voice 1, optionally via quantiser/attenuator.
3. Connect output 5 to gate on voice 2
4. Connect output 6 to pitch on voice 2, optionally via quantiser/attenuator.
5. Gates will be output on 3/5 according to the gate pattern
6. A long-press and release of button 1 regenerates the gate patterns.
7. Knob 1 increases or decreases the sparsity of the gates sent to
   outputs 3 and 5

## Selecting analogue input modes

Consequencer can perform 3 different actions when a control voltage input is received at the analogue input.
The current running mode is shown on the bottom right of the screen (e.g. M1, M2, M3)
Cycle through the modes by long-pressing and releasing button 2. The following modes are available:

- Mode 1: Sparsity (unimplemented)
- Mode 2: Control voltage selects the gate pattern
- Mode 3: Control voltage selects the stepped CV pattern

## Controlling a pattern using CV

1. Select analogue mode 2.
2. Send a control voltage into the analogue input

A fixed voltage will select a single pattern and varying voltage (e.g. an envelope or LFO) will smoothly cycle through patterns.

## Adding / Removing / Updating Gate Patterns

1. Update consequencer_patterns.py
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
