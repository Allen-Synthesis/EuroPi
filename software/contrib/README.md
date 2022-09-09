# Contributions

Please see the [contributing guide](/contributing.md) for details on how to contribute a script to this 
directory, specifically [the section on contrib scripts](/contributing.md#contrib-scripts).

# List of current scripts

### [Bernoulli Gates](/software/contrib/menubernoulli_gates.md)
A probability script based on Mutable Instruments Branches
Two channels of probability based routing, where the digital input will be routed to one of two outputs based on a weighted random chance, controlled by a knob per channel, and the analogue input for channel 1

### Coin Toss
A probability utility with an output based on a percentage choice between 1 or 0
Using the threshold knob and analogue input, users can determine whether a 1 or a 0 is preferred by the weighted random choice each time the digital input is triggered, or an internal clock depending on the mode

### Consequencer
A gate and CV sequencer inspired by Mutable Instruments Grids and the Music Thing Modular Turing Machine
Users can morph between patterns and CV sequences during operation, with 3 gate and 3 CV outputs based on the current pattern, programmed randomness, and CV input, running from an external clock

### CVecorder
6 channels of control voltage recording
Record 6 banks of 6 channels of control voltage, and then play them back at a consistent rate set by an external clock.
Recording of CV can be primed so that you can record a movement without missing a beat

### Diagnostic
Test the hardware of the module
The values of all inputs are shown on the display, and the outputs are set to fixed voltages.
Users can rotate the outputs to ensure they each output the same voltage when sent the same instruction from the script

### Hamlet
A variation of the Consequencer script specifically geared towards driving voices
2pairs of gate and CV outputs are available to drive two voices, as well as 2 drum gate outputs.
As with the consequencer, the patterns can be smoothly morphed between while performing

### Harmonic LFOs
6 tempo-related LFOs with adjustable wave shape
Users can run up to 6 LFOs with one internal master clock, with wave shapes of either sine, saw, square, semi-random, or off.
The division of the master clock that each LFO runs at, as well as each of their wave shapes, can be adjusted during operation

### Hello World
An example script for the menu system
This script can be copied and altered as a starting point for your own scripts that are to be menu compatible, and make use of the save state functionality

### Noddy Holder
Two channels of sample/track and hold based on a single trigger and CV source
Users have a copy of the original trigger signal, a sample and hold and a track and hold of the analogue input, and the all above but with the gate inverted, available from the CV outputs

### Polyhythmic Sequencer
A sequencer that advances notes according to a polyrhythmic clock, inspired by the operation of the Moog Subharmonicon sequencer
Users can run two simultaneous polyrhythmic sequences clocked by the same external clock.
Quantised outputs are available, with the note for each step, and the polyrhythm it runs at, being easily changed to write the sequence

### Radio Scanner
A tool for exploring sounds and control voltage combinations by navigating a 2D plane
The two knobs allow users to scan in 2 separate axis, with the value of each knob available as a CV output.
There is also a CV output for the difference between the two knob positions, and then the lower row of CV outputs is the inverse of each jack above.
The outputs can also be rotated as inspired by the 4MS Rotating Clock Divider

### Scope
An oscilloscope script to monitor the analogue and digital inputs
The current values of the analogue and digital inputs are displayed in an oscilloscope style on the OLED display, and copies of both signals, as well as an inverted gate signal, are available from the CV outputs

### Strange Attractor
A source of chaotic modulation using systems of differential equations such as the Lorenz System
Users have the x, y, and z values of the output of each attractor model available as CV outputs, as well as 3 gate signals related to the relationships between these values