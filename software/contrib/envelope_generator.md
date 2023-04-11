# Envelope Generator

author: Rory Allen

date: 2023-04-11

labels: utility

A simple one channel envelope generator with exponential attack and decay, sustain option, and looping capability

Inputs and Outputs:
- **digital in:** trigger an envelope
- **analog in:** added to knob 2 to determine fall time
- **button 1:** change sustain mode between AR (Attack Release) and ASR (Attack Sustain Release)
- **button 2:** change looping mode between Once and Loop (Loop mode overrides sustain mode to AR)
- **knob 1:** rise time
- **knob 2:** fall time
- **cv 1:** a copy of the digital input
- **cv 2:** the generated envelope
- **cv 3:** the inversion of the generated envelope