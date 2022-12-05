# Contributions

Please see the [contributing guide](/contributing.md) for details on how to contribute a script to this 
directory, specifically [the section on contrib scripts](/contributing.md#contrib-scripts).

# List of packaged scripts

### Bernoulli Gates \[ [documentation](/software/contrib/bernoulli_gates.md) | [script](/software/contrib/bernoulli_gates.py) \]
A probability script based on Mutable Instruments Branches

Two channels of probability-based routing, where the digital input will be routed to one of two outputs based on a weighted random chance, controlled by a knob per channel, and the analogue input for channel 1

<i>Author: [Bridgee](https://github.com/Bridgee)</i>
<br><i>Labels: Random</i>

### Consequencer \[ [documentation](/software/contrib/consequencer.md) | [script](/software/contrib/consequencer.md) \]
A gate and CV sequencer inspired by Mutable Instruments Grids and the Music Thing Modular Turing Machine

Users can morph between patterns and CV sequences during operation, with 3 gate and 3 CV outputs based on the current pattern, programmed randomness, and CV input, running from an external clock

<i>Author: [gamecat69](https://github.com/gamecat69)</i>
<br><i>Labels: sequencer, gates, triggers, drums, randomness</i>

### CVecorder \[ [documentation](/software/contrib/cvecorder.md) | [script](/software/contrib/cvecorder.py) \]
6 channels of control voltage recording

Record 6 banks of 6 channels of control voltage, and then play them back at a consistent rate set by an external clock.
Recording of CV can be primed so that you can record a movement without missing a beat

<i>Author: [anselln](https://github.com/anselln)</i>
<br><i>Labels: sequencer, CV, performance</i>

### Hamlet \[ [documentation](/software/contrib/hamlet.md) | [script](/software/contrib/hamlet.py) \]
A variation of the Consequencer script specifically geared towards driving voices

2pairs of gate and CV outputs are available to drive two voices, as well as 2 drum gate outputs.
As with the consequencer, the patterns can be smoothly morphed between while performing

<i>Author: [seanbechhofer](https://github.com/seanbechhofer)</i>
<br><i>Labels: sequencer, gates, triggers, drums, randomness</i>

### Harmonic LFOs \[ [documentation](/software/contrib/harmonic_lfos.md) | [script](/software/contrib/harmonic_lfos.py) \]
6 tempo-related LFOs with adjustable wave shape

Users can run up to 6 LFOs with one internal master clock, with wave shapes of either sine, saw, square, semi-random, or off.
The division of the master clock that each LFO runs at, as well as each of their wave shapes, can be adjusted during operation

<i>Author: [roryjamesallen](https://github.com/roryjamesallen)</i>
<br><i>Labels: LFO</i>

### Noddy Holder \[ [documentation](/software/contrib/noddy_holder.md) | [script](/software/contrib/noddy_holder.py) \]
Two channels of sample/track and hold based on a single trigger and CV source

Users have a copy of the original trigger signal, a sample and hold and a track and hold of the analogue input, and the all above but with the gate inverted, available from the CV outputs

<i>Author: [seanbechhofer](https://github.com/seanbechhofer)</i>
<br><i>Labels: gates, sample&hold, track&hold</i>

### Poly Square \[ [documentation](/software/contrib/poly_square.md) | [script](/software/contrib/poly_square.py) \]
Six independent oscillators which output on CVs 1-6.

The base pitch is set by the analog input, which is interpreted as a V/oct input with 0V = C. Knob 1 allows for detuning of the 6 voices, and as the knob is turned clockwise, the spread between them increases. Button 2 toggles the maximum detune between a half step and a major 9th. Knob 2 sets the polyphony mode.

<i>Author: [t-schreibs](https://github.com/t-schreibs)</i>
<br><i>Labels: oscillator, poly</i>

### Polyrhythmic Sequencer \[ [script](/software/contrib/polyrhythmic_sequencer.py) \]
A sequencer that advances notes according to a polyrhythmic clock, inspired by the operation of the Moog Subharmonicon sequencer

Users can run two simultaneous polyrhythmic sequences clocked by the same external clock.
Quantised outputs are available, with the note for each step, and the polyrhythm it runs at, being easily changed to write the sequence

<i>Author: [awonak](https://github.com/awonak)</i>
<br><i>Labels: polyrhythms, sequencer, triggers</i>

### Probapoly \[ [documentation](/software/contrib/probapoly.md) | [script](/software/contrib/probapoly.py) \]
Creates interesting polyrhythmic gate patterns while also allowing probabilities to be set on gates.

Given values for and upper and lower rhythmic ratios, Probapoly will create a looping pattern as short as possible with no repetition of the pattern within the loop.

<i>Author: [gamecat69](https://github.com/gamecat69)</i>
<br><i>Labels: sequencer, performance, gates, polyrhythm, probability</i>

### Radio Scanner \[ [documentation](/software/contrib/radio_scanner.md) | [script](/software/contrib/radio_scanner.py) \]
A tool for exploring sounds and control voltage combinations by navigating a 2D plane

The two knobs allow users to scan in 2 separate axis, with the value of each knob available as a CV output.
There is also a CV output for the difference between the two knob positions, and then the lower row of CV outputs is the inverse of each jack above.
The outputs can also be rotated as inspired by the 4MS Rotating Clock Divider

<i>Author: [roryjamesallen](https://github.com/roryjamesallen)</i>
<br><i>Labels: n/a</i>

### Smooth Random Voltages \[ [script](/software/contrib/smooth_random_voltages.py) \]
Random CV with adjustable slew rate, inspired by: https://youtu.be/tupkx3q7Dyw.

3 random or analog input s&h voltages with changable slew smoothness. New voltages assigned upon each digital input trigger. Top row outputs move
towards target voltage according to slew rate set by knob 1. Bottom row outputs immediately change to new target voltage.

<i>Author: [awonak](https://github.com/awonak)</i>
<br><i>Labels: random, s&h</i>

### Strange Attractor \[ [documentation](/software/contrib/strange_attractor.md) | [script](/software/contrib/strange_attractor.py) \]
A source of chaotic modulation using systems of differential equations such as the Lorenz System

Users have the x, y, and z values of the output of each attractor model available as CV outputs, as well as 3 gate signals related to the relationships between these values

<i>Author: [seanbechhofer](https://github.com/seanbechhofer)</i>
<br><i>Labels: gates, triggers, randomness</i>

### Turing Machine \[ [documentation](/software/contrib/turing_machine.md) | [script](/software/contrib/turing_machine.py) \]
A script meant to recreate the [Music Thing Modular Turning Machine Random Sequencer](https://musicthing.co.uk/pages/turing.html)
as faithfully as possible on the EuroPi hardware.

<i>Author: [mjaskula](https://github.com/mjaskula)</i>
<br><i>Labels: sequencer, random, triggers</i>

---

<details>
<summary><h2>Proof of Concept Scripts</h2></summary>

### Coin Toss \[ [documentation](/software/contrib/coin_toss.md) | [script](/software/contrib/coin_toss.py) \]
A probability utility with an output based on a percentage choice between 1 or 0

Using the threshold knob and analogue input, users can determine whether a 1 or a 0 is preferred by the weighted random choice each time the digital input is triggered, or an internal clock depending on the mode

<i>Author: [awonak](https://github.com/awonak)</i>
<br><i>Labels: Clock, Random, CV Generation</i>

### Diagnostic \[ [documentation](/software/contrib/diagnostic.md) | [script](/software/contrib/diagnostic.py) \]
Test the hardware of the module

The values of all inputs are shown on the display, and the outputs are set to fixed voltages.
Users can rotate the outputs to ensure they each output the same voltage when sent the same instruction from the script

<i>Author: [mjaskula](https://github.com/mjaskula)</i>
<br><i>Labels: utility</i>

### Hello World \[ [script](/software/contrib/hello_world.py) \]
An example script for the menu system

This script can be copied and altered as a starting point for your own scripts that are to be menu compatible, and make use of the save state functionality

<i>Author: [mjaskula](https://github.com/mjaskula)</i>
<br><i>Labels: example</i>

### Scope \[ [script](/software/contrib/scope.py) \]
An oscilloscope script to monitor the analogue and digital inputs

The current values of the analogue and digital inputs are displayed in an oscilloscope style on the OLED display, and copies of both signals, as well as an inverted gate signal, are available from the CV outputs

<i>Author: [mjaskula](https://github.com/mjaskula)</i>
<br><i>Labels: utility</i>

</details>
