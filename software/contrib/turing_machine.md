# Turing Machine

A script meant to recreate the [Music Thing Modular Turning Machine Random Sequencer](https://www.musicthing.co.uk/Turing-Machine/)
as faithfully as possible on the EuroPi hardware. Plenty of information is available at that link,
but the most important bit is this:

>  In the Turing Machine, looping is controlled by the big knob.
>    * At noon, the sequences are random.
>    * At 5 o'clock, it locks into a repeating sequence.
>    * At 7 o'clock, it double locks into a repeating sequence twice as long as the 'length' setting.
>    * At 3 o'clock or 9 o'clock, it slips; looping but occasionally changing notes.

The left knob (`k1`) acts as the TM's big knob. The right knob (`k2`) serves dual duty as the scale
and length knob. The mode of the knob is changed with the right button (`b2`).

- **din:** clock
- **ain:** cv control over the big knob, added to the knobs value
- **k1:** the big knob (probability that the sequence changes)
- **k2:** output scale (0-10v) or sequence length (2-16 steps)
- **b1:** write (clear bits)
- **b2:** change k2 function
- **cv1:** pulse 1
- **cv2:** pulse 2
- **cv3:** pulse 4
- **cv4:** pulse 1 & 2
- **cv5:** pulse 2 & 4
- **cv6:** sequence out
