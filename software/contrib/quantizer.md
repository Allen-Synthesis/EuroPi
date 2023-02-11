# Quantizer

An equal-temperment quantizer with a selection of scales.

For best results make sure your EuroPi is well-calibrated.


## Usage

Connect the signal to be quantized to the analog input.

Connect a clock pulse, square LFO, or other trigger source to the
digital input.

When a trigger is received on the digital input, the analog input
will be quantized to the nearest note on the selected scale and
output out Output 1.

Outputs 2-5 output the same note as output 1, but can be shifted
up/down a fixed number of semitones.  This allows the EuroPi to
generate quantized voltages to produce chords across multiple
oscillators.

Output 6 is currently reserved for future expansion


## Patch Idea

Connect outputs 2-5 to a sequential switch, with the output of
the switch going to an oscillator.  This way the interval
between one oscillator connected to output 1 and the second
connected to the sequential switch will change every time the
switch gets triggered


# Future Plans

Unlike many other quantizers that can operate continuously,
this one requires triggering from an external source.

I'd like to overcome this limitation eventually, and the
intent is for Output 6 to output a trigger when the note
changes in continuous quantization mode.