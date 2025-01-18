# Sequential Switch

This script acts as a sequential switch, routing a copy of the analogue input
to one of the outputs.  When a gate is received the output is changed.

Note that the output is a digital copy of the input, and not a direct circuit
path. The output may undergo some transformation in the process.  See the
section on limitations, below.

- `ain`: the input signal that is copied to one of the 6 output channels
- `din`: when a rising edge is detected, the active output changes
- `cv1-6`: one of these will have a copy of `ain`, the others will be zero
- `button 1`: manually advance the output (on default view), or apply the current
  option (in menu view)
- `button 2`: long-press to toggle between menu view and the visualization
- `knob 1`: unused
- `knob 2`: menu navigation (when inside menu view)

Pressing button 1 will manually advance the output, just like a trigger
on the digital input.

Long-pressing button 2 will toggle between the default visualization and
the settings menu.

When in the settings menu, use knob 2 to select a setting to change. Short-
press B2 to edit the selected setting. Rotate knob 2 to select a new value
for the setting and short-press B2 to apply it.  Long-pressing B2 will
cancel the edit and return to the visualization.

Options:
- number of outputs: 2-6, determines the number of output ports used
- mode: one of:
    - sequential: port changes in order 1->2->3->4->5->6->1->....
    - reverse: port changes in order 1->6->5->4->3->2->1->6->....
    - ping-pong: port changes in order 1->2->3->4->5->6->5->4->...
    - random: port changes randomly, with a 1/n chance of repeating
      the current port
    - shift: instead of a traditional sequential switch, treat the module as a
      sample & hold shift register

After 20 minutes of idle time the screen will go blank. While blank the module
will continue to operate normally.

Pressing button 1 while the screen is blank will wake the module up
_and_ advance the output.  Pressing button 2 will only wake up the screen.


## Shift Register Mode

When operating in shift mode, every time `b1` is pressed or a trigger is read on `din`,
the current value from `ain` is read and inserted into the first position of a shift register.
Outputs 1-N (where N is the number of outputs set in the menu) are set to the first N items
in the shift register. In other words, `cv1` is the most-recent S&H reading, `cv2` is the
second most recent, `cv3` is the third most recent, and so on.

Unused outputs (e.g. if the number of outputs is 4, `cv5` and `cv6`) are set to zero.

## Limitations

Because the Sequential Switch script reads the input voltage, processes it
through an A-to-D converter and uses that to determine the output voltage
the output signal will never be a perfect 1:1 copy of the input.

Audio signals will be completely destroyed.  You should only use this program
for routing control voltages or gates/triggers.

Square LFOs, gate, and trigger signals may be slightly noisy, but should still
be within Eurorack tolerance for triggering external modules.

Constant input voltages will also be noisy.  Be careful if you're sending a
quantized input into the module, as the quantization may be ruined in the
A-to-D and D-to-A conversions.

Smoothly-changing voltages, like triangle or sine LFOs may undergo some
bit-crushing effects, which depending on your use may be desirable.


## Patch Idea 1

Patch a constant voltage of 1V into `ain`.  Every time the output changes it will
effectively trigger a gate that will last until the next cycle. This will let
you trigger effects, envelopes, etc... in sequence.
