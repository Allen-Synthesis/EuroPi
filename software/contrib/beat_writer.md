# Beat Writer

author: Rory Allen

date: 2023-05-25

labels: triggers, drums, sequencer, looper

A beat programmer for 2 channels of trigger patterns
User input on both buttons is recorded, grid quantized, and played back to the time of an external clock source

Inputs and Outputs:
- **digital in:** external clock source (1 external trigger is one sequence step)
- **analog in:** n/a
- **button 1:** add beat on current step on channel 1 (or remove existing beat)
- **button 2:** add beat on current step on channel 2 (or remove existing beat)
- **knob 1:** n/a
- **knob 2:** n/a
- **cv 1:** a copy of the digital input
- **cv 2:** channel 1 output
- **cv 3:** channel 2 output