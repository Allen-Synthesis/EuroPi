# EuroPi Piconacci - Fibonacci based triggers

author: Sean Bechhofer (github.com/seanbechhofer)

date: 2022-05-165

labels: triggers, numbers

Piconacci is a sinple trigger generator that produces a collection of triggers, one of each of the six outputs. Each output is associated with a clock division value. Those values are drawn from the Fibonacci series. So for example, clock divisions of 1, 2, 3, 5, 8, and 13.

Short button presses will move the trigger values through the sequence, e.g. to 2, 3, 5, 8, 13, and 21.

Long button presses will rotate the values, e.g. to 3, 5, 8, 13, 21, and 2.

Credits:
- The Europi hardware and firmware was designed by Allen Synthesis:
https://github.com/Allen-Synthesis/EuroPi
- The name was suggested by @djmjr on the EuroPi Discord. 

# Controls

- digital_in: Clock in
- analog_in: Not used
- knob_1: Not used
- knob_2: Not used

- button_1: Short Press: move left in Fibb sequence
  Long Press: Rotate triggers
- button_2: Short Press: move right in Fibb sequence
  Long Press: Rotate triggers

- output_1: trigger
- output_2: trigger
- output_3: trigger
- output_4: trigger
- output_5: trigger
- output_6: trigger

## Basic Usage
1. Connect a clock input to the Digital input
2. Triggers will appear on the outputs.
3. Use buttons to move values or rotate the triggers.

# Known bugs / Interesting features

Probably. 
