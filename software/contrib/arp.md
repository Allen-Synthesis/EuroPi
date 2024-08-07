# Arpeggiator

This program plays ascending and descending quantized scales/arpeggios.

For simplicity, the term "arpeggio" is used below, even though it is technically inaccurate
from a musical perspective.

## Inputs & Outputs

Inputs:
- `b1` and `b2` cycle through the available arpeggios. All notes in the
  indicated scale are played
- `din` is a trigger input that changes the current note of the arpeggio
- `ain` is a CV output that takes 0-10V, allowing transposition control
  over the root note. Note that the octave of the transposition is
  ignored; only the quantized semitone is applied
- `k1` sets the root octave (0-5 octaves)
- `k2` changes the octave range (1-5 octaves)

Outputs:
- `cv1` outputs ascending arpgeggios with ascending octaves (e.g. `C0 E0 G0 C1 E1 G1 C2 E2 G2 ...`)
- `cv2` outputs ascending arpeggios with descending octaves (e.g. `C2 E2 G2 C1 E1 G1 C0 E0 G0 ...`)
- `cv3` outputs random notes from the arpeggio, with ascending octaves (e.g. `{C|E|G}0 {C|E|G}0 {C|E|G}0 {C|E|G}1 {C|E|G}1 {C|E|G}1 ...`)
- `cv4` outputs descending arpeggios with ascending octaves (e.g. `G0 E0 C0 G1 E1 C1 G2 E2 C2 ...`)
- `cv5` outputs descending arpeggios with descending octaves (e.g. `G2 E2 C2 G1 E1 C1 G0 E20 C0 ...`)
- `cv6` outputs random arpeggios with random octaves (e.g. `{C|E|G}{0-2} {C|E|G}{0-2} {C|E|G}{0-2} ...`)

Note that if the octave range is set to `1`, `cv1` & `cv2` will have identical output; `cv4` & `cv5` will have
identical output; and `cv3` & `cv6` will be randomly chosen from the same range of notes.

## Changing scales & transposing
Changing transposing by either changing the root octave, octave range, or applying CV to `ain` will apply
the new settings _on the next clock tick_. This prevents the output from changing between clock pulses.

Similarly, pressing `b1` or `b2` to change the arpeggio will apply the new set of notes on the next tick. Changing
the arpeggio will also reset the octaves & notes to their initial values (e.g. `cv1` will return to the root
octave and play the first note of the new arpeggio on the next tick)
