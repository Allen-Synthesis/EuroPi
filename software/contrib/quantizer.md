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


## Menu Operation

To switch between the keyboard view and the advanced menu, press
the button on the right.

In keyboard view, use the left knob to select and note and press
the left button to enable/disable it.  Enabled notes are marked
with a small circle near the top of the keyboard.

In the menu view, use the left knob to scroll through items.  Use
the right knob to scroll through available options for the given
item.  To apply the selection, press the left button.


### Menu Items

- Mode: either continuous or triggered (see Usage, above)
- Transpose: used to transpose the output voltage up a set
  number of semitones. Note that the keyboard view will remain
  unchanged; only the output voltage(s) will be transposed
- Octave: used to shift the output voltage up or down a number
  of octaves.  Because the module cannot output negative
  voltages, if your auxilliary outputs are set to negative
  intervals they may be clipped to zero if the octave is not
  raised (-1 to +2).
- Output 2-5: set the interval between Output 1 and Output N.
  The interval can be any semitone between -1 octave and +1
  octave.  Note that if the input signal is less than 1 volt
  and the octave is set to 0, negative intervals may be
  clipped.


## Screensaver

After 20 minutes of idleness the screen on the EuroPi will go blank
to prevent burn-in.  It will continue to quantize inputs normally,
just without visual feedback.

To wake the screen back up, simply press either button once.


## Patch Idea

Connect outputs 2-5 to a sequential switch, with the output of
the switch going to an oscillator.  This way the interval
between one oscillator connected to output 1 and the second
connected to the sequential switch will change every time the
switch gets triggered.