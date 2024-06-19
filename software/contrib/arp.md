# Arpeggiator

This program plays ascending and descending quantized scales/arpeggios.

## Inputs & Outputs

Inputs:
- `b1` and `b2` cycle through the available scales. All notes in the
  indicated scale are played
- `din` is a trigger input that changes the current note of the scale
- `ain` is a CV output that takes 0-10V, allowing transposition control
  over the root of the scale. Note that the octave of the transposition is
  ignored; only the quantized semitone is applied
- `k1` the root octave (from C0 up to C5)
- `k2` changes the octave range; from 1 octave ascending/descending up to 5

Outputs:
- `cv1` is the primary output, supplying quantized control voltage from C
  up through the desired number of octaves
- `cv2` follows `cv1`, but shifted a perfect fifth up
- `cv3` follows `cv1`, but shifted a perfect fifth down
- `cv4` is the descending output. The main scale is played in reverse order,
  but with ascending octaves (if more than 1 octave is set with `k2`)
- `cv5` follows `cv2`, but shifted a perfect fifth up
- `cv6` follows `cv2`, but shifted a perfect fifth down