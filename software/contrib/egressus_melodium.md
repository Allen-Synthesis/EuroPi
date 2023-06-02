# Egressus Melodium (Stepped Melody)

author: Nik Ansell (github.com/gamecat69)
date: 22-Apr-23
labels: sequencer, CV, randomness

Generates variable length looping patterns of random stepped CV.
Patterns can be linked together into sequences to create rhythmically evolving CV patterns.
Inspired by the Noise Engineering Mimetic Digitalis.

Demo video: TBC

# Inputs, Outputs and Controls

digital_in: clock in
analog_in: Adjusts pattern length - summed with k2 (0 to +9V)

knob_1: Set pattern sequence
knob_2: Set pattern length - summed with ain

button_1: Short Press: Select CV Pattern bank (-). Medium Press (> 0.3s < 2s) cycle experimental slew mode Long Press (>2s): Generates new CV pattern in existing bank
button_2: Short Press: Select CV Pattern bank (+). Long Press (>2s): Enables / Disables pattern sequence mode

output_1: randomly generated CV (0 to +9V)
output_2: randomly generated CV (0 to +9V)
output_3: randomly generated CV (0 to +9V)
output_4: randomly generated CV (0 to +9V)
output_5: randomly generated CV (0 to +9V)
output_6: randomly generated CV (0 to +9V)

# Getting started

1. Patch a clock into the digital input
2. Connect one or more outputs to an input on another module (e.g. CV modulation inputs)
3. Select a pattern pength using Knob 2
4. Start your clock. Each output will now send a random looping CV to your module!

So, what happened in the above example?
When the module first powered on it automatically generated 6 x 32 step random CV patterns - one for each of the 6 outputs.
Each time a clock is received, the step advances by one step and then loops when it get to the end of the pattern.
The length of the pattern loop is controlled using knob 2, which supports a value from 1 to 32.

# Screen

The OLED screen is broken into 3 sections:

- Left: CV Pattern bank number
- Middle: Current step / Pattern length e.g. `1/8` indicates step 1 of an 8 step pattern.
- Right: (Only visivle when Pattern sequences are enabled) Selected CV Pattern sequence

# CV Pattern banks

There are 4 banks of CV patterns. A pattern bank can be selected using buttons 1 and 2. Button 1 will select a lower pattern, while button 2 will select a higher pattern.
Patterns can be selected while the module is playing (receiving clock input) and will maintain the correct tempo and step number when selecting patterns.

# CV Pattern sequences

In addition to selecting CV pattern banks manually, sequences of CV patterns can also be played.
Pattern sequences are enabled by long-pressing button 2. Sequence mode is on whenever `Seq` is shown on-screen.
Different CV pattern sequences can be selected using knob 1.
The currently selected CV pattern sequence is shown underneath `Seq` on screen.
For example when `0001` is shown, this indicates that CV pattern `0` will be played 3 times, followed by pattern `1`. The sequence will then return back to pattern `0`.

# Changing CV pattern length using incoming CV

The analogue input (ain) can be used to vary the pattern length. This can be used to create wonky patterns using an LFO as the CV source.
Or specific CV values can be used to select specific pattern lengths.

# Generating new CV patterns

New CV patterns for all outputs in a selected CV pattern bank can be generated by a long-press of button 1.
Press this as many times as you like until you like the pattern!

# Saving and loading

CV patterns, CV pattern sequences and the last-selected CV pattern are saved - so things will be exactly as you left them when you next power up.