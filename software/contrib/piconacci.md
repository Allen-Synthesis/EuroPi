# Piconacci - Fibonacci based triggers

Piconacci is a simple trigger generator that produces a collection of triggers, one of each of the
six outputs. Each output is associated with a clock division value. Those values are drawn from the
Fibonacci series. So for example, clock divisions of 1, 2, 3, 5, 8, and 13.

Short button presses will move the trigger values through the sequence, e.g. to 2, 3, 5, 8, 13,
and 21.

Long button presses will rotate the values, e.g. to 3, 5, 8, 13, 21, and 2.

## Controls

- digital_in: Clock in
- analog_in: Not used
- knob_1: Not used
- knob_2: Not used

- button_1: Short Press: move left in Fibonacci sequence
  Long Press: Rotate triggers
- button_2: Short Press: move right in Fibonacci sequence
  Long Press: Rotate triggers

- output_1: trigger
- output_2: trigger
- output_3: trigger
- output_4: trigger
- output_5: trigger
- output_6: trigger

### Basic Usage

1. Connect a clock input to the Digital input
2. Triggers will appear on the outputs.
3. Use buttons to move values or rotate the triggers.

## Details

Piconnaci emits triggers on each output with clock divisions based on
values from the Fibonacci series. Those values are taken by selecting
a "window" of six consecutive values and then assigning values to the
outputs. The window can be moved and rotated through short and long
button presses.

In the diagrams below, the green boxes indicate the values in the
Fibonacci series. The blue boxes indicate the active "window" with the
numbers showing which division is used for each output.

![pico drawio](https://user-images.githubusercontent.com/1035997/168587520-de2286af-1ae4-45be-a0f4-0aeb8128c4a9.png)

## Limitations

The code has a limit on the number of values used (50). In practice this is unlikely to be an issue
and probably works for most sensible circumstances. The 50th value (disregarding 0, 1) is
20,365,011,074. At a BPM of 120, that'll be a trigger every 300 years which is pretty slow even for
glacial ambient.

Trigger length is coupled to the incoming clock.

## Known bugs / Interesting features

Probably.

## Credits:

- The Europi hardware and firmware was designed by Allen Synthesis:
https://github.com/Allen-Synthesis/EuroPi

- The name was suggested by @djmjr on the EuroPi Discord.
