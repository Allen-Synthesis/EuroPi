# Quantizer

An equal-temperment quantizer with a selection of scales.

For best results make sure your EuroPi is well-calibrated.

The quantizer can operate in two modes: triggered (default)
and continuous.


## Usage

Connect the signal to be quantized to the analog input.

If operating in triggered mode, connect a clock pulse, 
square LFO, or other trigger source to the digital input.

When a trigger is received on the digital input, the analog input
will be quantized to the nearest note on the selected scale and
output out Output 1.

Outputs 2-5 output the same note as output 1, but can be shifted
up/down a fixed number of semitones.  This allows the EuroPi to
generate quantized voltages to produce chords across multiple
oscillators.

In continuous mode output 6 will output a trigger whenever the
output note changes.

In triggered mode output 6 will mirror the digital input.


## Patch Idea

Connect outputs 2-5 to a sequential switch, with the output of
the switch going to an oscillator.  This way the interval
between one oscillator connected to output 1 and the second
connected to the sequential switch will change every time the
switch gets triggered.