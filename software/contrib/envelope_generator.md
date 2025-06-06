# Envelope Generator

A simple one channel envelope generator with exponential attack and decay, sustain option, and
looping capability.

## Inputs and Outputs

- **digital in:** trigger an envelope
- **analog in:** added to knob 2 to determine fall time
- **button 1:** change sustain mode between AR (Attack Release) and ASR (Attack Sustain Release)
- **button 2:** change looping mode between Once and Loop (Loop mode overrides sustain mode to AR)
- **knob 1:** rise time
- **knob 2:** fall time
- **cv 1:** a copy of the digital input
- **cv 2:** the generated envelope
- **cv 3:** the inversion of the generated envelope
- **cv 4:** a gate that is high whenever the envelope is in a sustain state
- **cv 5:** a 10ms end-of-rise trigger
- **cv 6:** a 10ms end-of-fall trigger

The 10ms end-of-rise trigger will fire every time the envelope transitions from the rising to either
the falling or sustain states. This can occur as a result of the incoming gate signal dropping low
while a slow rise is still being processed.

The 10ms end-of-fall trigger will only fire if the full duration of the fall portion is reached; if
the envelope is re-triggered before the fall completes, this trigger will _not_ fire.
