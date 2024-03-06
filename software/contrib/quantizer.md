# Quantizer

An equal-temperment quantizer with a selection of scales.

For best results make sure your EuroPi is well-calibrated.

The quantizer can operate in two modes: triggered (default)
and continuous.

- `ain`: the analog input to be quantized
- `din`: when in triggered mode, the trigger to quantize is
  received on this input
- `cv1`: the quantized output
- `cv2-5`: the quantized output, shifted up or down a fixed
  number of semitones
- `cv6`: a trigger when the output note changes (in continuous
  mode) or a copy of the signal sent to `din` (in triggered mode)
- `button 1`: toggle note (on keyboard screen) or apply new
  setting (on menu screen)
- `button 2`: toggle between the keyboard & menu screens
- `knob 1`: cycle through the note to toggle (on keyboard
  screen) or the menu items (on menu screen)
- `knob 2`: cycle through available options for the current
  setting (on menu screen). Unused on keyboard screen


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
button 2.

In keyboard view, use knob 1 to select and note and press
button 1 to enable/disable it.  Enabled notes are marked
with a small circle near the top of the keyboard.

In the menu view, use knob 1 to scroll through items.  Use
knob 2 to scroll through available options for the given
item.  To apply the selection, press button 1.


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