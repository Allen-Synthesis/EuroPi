# EuroPi Consequencer - A 6-channel open source sequencer and random source power house!

author: Nik Ansell (github.com/gamecat69)

date: 2022-02-09

labels: sequencer, gates, triggers, drums, randomness

Consequencer is a gate and stepped CV sequencer inspired by Grids from Mutable Instruments and the randomness created by the Turing Machine.
Pattern changes and randomness are introduced as a consequence of both manual input and control voltages sent to the analogue input.
A large number of popular gate patterns are pre-loaded. Stepped CV sequences are automatically generated.

Both gate patterns and CV sequences can be smoothly morphed between without disrupting playback.
Use outputs 1 - 3 for gates and outputs 4 - 6 for randomised stepped CV patterns.
Send a clock to the digital input to start the sequence.

Demo video: https://youtu.be/UwjajP6uiQU

Credits:
- The Europi hardware and firmware was designed by Allen Synthesis: https://github.com/Allen-Synthesis/EuroPi
- A small number of preloaded drum patterns were recreated from here: https://docs.google.com/spreadsheets/d/19_3BxUMy3uy1Gb0V8Wc-TcG7q16Amfn6e8QVw4-HuD0/edit#gid=0

# July 2022 Update - Probability based drum patterms

Consequencer now includes the ability to add probability-based steps to patterns!
You can use probability in patterns to add variabilty in interesting ways.
Some example patterns have been included in this release and you can find instructions below in the "Advanced usage" section for adding your own.

You can easiliy identify steps within patterns that have a probability less than 100%.
Normal steps are shown with a `^` character, whereas steps with a probability are shown with a `-`.

# Controls

![Operating Diagram](https://user-images.githubusercontent.com/79809962/154732035-ccc0d8c1-0e4e-4b8c-97e3-ccfa07a4880b.png)

- digital_in: Clock in
- analog_in: Mode 1: Adjusts randonmess, Mode 2: Selects gate pattern, Mode 3: Selects stepped CV pattern

- knob_1: Adjust randomness
- knob_2: Select pre-loaded gate pattern

- button_1: Short Press: Toggle randomized pattern on output 3 on / off. Long Press: Play previous stepped CV sequence
- button_2:
  - Short Press  (<300ms)  : Generate a new random cv pattern for outputs 4 - 6.
  - Medium Press (>300ms)  : Cycle through analogue input modes
  - Long Press   (>3000ms) : Toggle option to send clocks from output 4

- output_1: gate 1 e.g Kick Drum
- output_2: gate 2 e.g Snare Drum
- output_3: gate 3 e.g Hi-Hat
- output_4: randomly generated stepped CV
- output_5: randomly generated stepped CV
- output_6: randomly generated stepped CV

# Getting Started

The following sections provide instructions for creating a simple 3 drum pattern with a kick, snare and hi-hat, then using random CV patterns to vary the timbre in each drum pattern.
You can of course connect outputs 1 - 3 to any module which expects gates and outputs 4 - 6 to any module expecting a control voltage.

## Basic Usage
1. Connect a clock input to the Digital input
2. Connect a Bass Drum to output 1, Snare to output 2 and Hi-hat to output 3
3. Start your clock - a pattern will output gates on outputs 1 -3
4. Select different patterns manually using knob 2 (right-hand knob). The selected pattern is shown visually on the screen.

## Adding randomness
1. A medium-press (>300ms and < 3000ms) and release of button 1 toggles on/off the real-time generation of a random gate pattern to output 3. A small filled rectangle is shown on the bottom left of the screen when this feature is active.
2. Knob 1 increases or decreases the randomness of the patterns sent to outputs 1 -3
3. Randomness can also be controlled by sending CV to the analogue input if analogInputMode 1 is selected (default).

## Using random CV from outputs 4 - 6

Outputs 4 - 6 provide a random pattern of stepped CV which is sync'd with the inbound clock.
A short-press and release of button 2 will generate a new pattern for all 3 outputs.

Example usage for these CV outputs, (this will depend on the inputs your drum module has):
- Snare Decay
- Hi-Hat decay (simulate an open hi-hat)
- Hi-Hat pitch
- Velocity
- Kick decay
- Kick accent
- Send stepped CV into the cutoff frequencer of a VCF (Voltage Controlled Filter)
- Send stepped CV into a quantizer, then feed the quantized output into a VCO (Voltage Controlled Oscillator)

## Selecting analogue input modes

Consequencer can perform 3 different actions when a control voltage input is received at the analogue input.
The current running mode is shown on the bottom right of the screen (e.g. M1, M2, M3)
Cycle through the modes by long-pressing and releasing button 2. The following modes are available:

- Mode 1: Control voltage adjusts randomness of the gate patterns sent to outputs 1 - 3
- Mode 2: Control voltage selects the gate pattern
- Mode 3: Control voltage selects the stepped CV pattern

## Controlling a pattern using CV

1. Select analogue mode 2.
2. Send a control voltage into the analogue input

A fixed voltage will select a single pattern and varying voltage (e.g. an envelope or LFO) will smoothly cycle through patterns.

# Advanced usage

## Adding / Removing / Updating Gate Patterns

Patterns can be added, removed or updated by updating the relevant list structures at the end of the consequencer.py file in the pattern class (look for the line `class pattern:`). Once patterns are updated make sure you save a copy of the updated file to the EuroPi using yoru favourite method (Thonny / REPL), then restart the Consequencer script.

The syntax should be intuitive. An example pattern is shown below. Each `1` or `0` represents a gate or no gate at that point in the sequence.
The mapping of `BD`, `SN`, `HH` is as follows:
- BD: Output 1
- SN: Output 2
- HH: Output 3

Starting with the July 2022 update, steps now also have a probability which is configured using the BdProb, SnProb and HhProb sections as shown below.
Use a value from `1` to `9` to set the desired level of probability for each step.
A value of `9` will cause the step to trigger 100% of the time, any value from `1` to `8` will trigger the step from n/9 times.

You can also use shorthand to define probabilities, for example:

- A single digit probability string is auto-populated for all values. e.g. a probability of `9` for an 8 step pattern will automatically become `99999999`

- A multi-digit probability string that is shorter in length than the pattern string is automatically filled with the last digit in the probability string. e.g. a probability of `9995` for an 8 step pattern will automatically become `99995555`.

Example valid patterns and probability patterns are shown below.

```
    BD.append("1001001001000100")
    SN.append("0001000000010000")
    HH.append("1111111111111111")
    BdProb.append("9999999999999999")
    SnProb.append("9999999999999999")
    HhProb.append("9999999999999999")

    BD.append("1001001001000100")
    SN.append("0001100000010000")
    HH.append("1010101010110101")
    BdProb.append("9")
    SnProb.append("99995")
    HhProb.append("95")

```

## Output clocks/gates on output 4

The Consequencer has a small amount of latency between receiving a clock or gate at the digital input and sending out gates to the outputs. This may not be noticable depending on how you incorporate Consequencer into your patch. However, there is an option for Consequencer to send out gates on output which are perfectly in time with the sequence being played. This allows you to clock other modules using output 4.

To enable this feature hold down button 1 for longer than 3 seconds, then release the button. A small unfilled rectangle is shown on the bottom left of the screen when this feature is active. This visual indicator is on the right of the random hi-hat visual indicator (filled rectangle on the bottom left of the screen).

# Known bugs / Interesting features

A small amount of noise causes the analogue input to vary slightly. This can sometimes cause the randomness, gate pattern or stepped CV pattern to flicker between values. It happens only occassionally, but introduces an interesting and subtle variation to the sequence being played.
