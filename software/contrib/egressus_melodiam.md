# Egressus Melodiam (Stepped Melody)

author: Nik Ansell (github.com/gamecat69)
date: 02-Feb-24
labels: clocked lfo, sequencer, CV, randomness

Clockable and free-running LFO and random CV pattern generator.
Six different wave shapes either define the LFO shape or the slew shape between CV pattern steps.
Use it to generate variable length melodies (using a quantizer), LFOs or wierd and wonderful control voltages.   

# Inputs, Outputs and Controls

digital_in: clock in
analog_in: not used

knob_1: Set global CV pattern length / free-running clock speed (A pattern length of 1 produces an cycling LFO)
knob_2: Set LFO / CV Pattern clock division per output

button_1:
- Short Press (< 300ms): Cycle through slew/LFO shapes for the selected output
- Long Press (Between 2 and 5 seconds): Generate a new random CV pattern for the selected output

button_2:
- Short Press (< 300ms): Cycle through outputs to edit
- Long Press (Between 2 and 5 seconds): Toggle between clocked mode and free-running mode

output_1: LFO / randomly generated CV pattern (0 to +10V)
output_2: LFO / randomly generated CV pattern (0 to +10V)
output_3: LFO / randomly generated CV pattern (0 to +10V)
output_4: LFO / randomly generated CV pattern (0 to +10V)
output_5: LFO / randomly generated CV pattern (0 to +10V)
output_6: LFO / randomly generated CV pattern (0 to +10V)

# Getting started

1. Patch a 50% duty cycle square wave or clock with pulses >= 18ms in duration  into the digital input
2. Connect one or more outputs to an input on another module (e.g. CV modulation inputs)
3. Select a pattern pength using Knob 1
4. Start your clock. Each output will now send a random looping CV to your module!

So, what happened in the above example?
When the module first powered on it automatically generated 6 x 32 step random CV patterns - one for each of the 6 outputs.
Each time a clock is received, the step advances by one step and then loops when it get to the end of the pattern.
The length of the pattern loop is controlled using knob 1, which supports a value from 1 to 32.

# Changing the wave shape and clock division of an output

1. Press and release button 2 until the output number you would like edit is shown on the top-right.
2. Press button 1 to cycle through the available wave shapes
3. Adjust knob 2 to select the output division. An output division of 1 causes the CV pattern / LFO for that
output to run at the clock rate. An output greater than one reduces the CV pattern / LFO to run at the selected division (e.g. selecting a division of 2 would run at half the clock rate)

In LFO mode (pattern length of 1) the wave shape determines the shape of the cycling LFO. However, when in CV pattern mode (Pattern length > 1) the wave shape determines the slew between pattern steps.

# Generating a new CV pattern for an output

A new CV pattern is generated for the selected output by holding down button 1 for 2 seconds and releasing. An indicator is shown on the top left of the screen to show a new CV pattern has been generated. Note that if you are in LFO mode (pattern length of 1) this function will have no effect until the pattern length is increased. 

# LFO Mode / CV Pattern mode

Selecting a pattern length of 1 will output an LFO.
Selecting a pattern length greater than one plays through the generated CV patterns.
Slew is generated between CV pattern steps when a wave shape other then square is selected.

# Clocked / Free-running mode

Clocked mode is selected by default - indicated by showing the length of the CV pattern (in dots) in the middle of the screen.
To enter free-running mode, hold button 2 for 2 seconds and release. The configured clock rate in milliseconds is shown
in the middle of the screen to indicate you are in free-running mode.

Note that when in free-running mode, the previously selected pattern length remains unchanged, it is therefore a good idea to select the required pattern length before changing to unclocked mode.

# Display

The OLED screen is broken into 3 sections:

- Left: The currently selected wave / slew shape for the selected output is shown on the bottom left. When a new CV pattern is generated (by holding down and releasing button 1 for longer than 2 seconds) an icon is displayed on the top left to show the pattern was generated.

- Middle: The global pattern length is shown in rows of 8 dots

- Right: The selected output is shown on the top-right; the currerntly configured output division is shown on the bottom-right.

# Saving and loading

All settings and CV patterns are saved when changes are made and will not be lost when the module is powered off.

# Changing the maximum CV voltage

CV Patterns (including LFOs) output a range of 0-10V based on the default globally configured value.
If you would like to change this value, two methods are available 1) Create a json file (see below), 2) Configure the global configuration value using the UI (coming soon in a later firmware release).

## Reducing the maximum CV output using a json file

1. Create a file on your pico named `config/config_EuroPiConfig.json`. Thonny is the easiest method for this.
2. Add the following to the json file:

```json
{
    "max_output_voltage": 5
}
```
