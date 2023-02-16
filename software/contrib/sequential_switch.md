# Sequential Switch

This script acts as a sequential switch, routing a copy of the analogue input
to one of the outputs.  When a gate is received the output is changed.

- `ain`: the input signal that is copied to one of the 6 output channels
- `din`: when a rising edge is detected, the active output changes
- `cv1-6`: one of these will have a copy of `ain`, the others will be zero
- `button 1`: manually advance the output (on default view), or apply the current
  option (in menu view)
- `button 2`: cycle between default & menu views
- `knob 1`: cycle through the menu items (in menu view)
- `knob 2`: cycle through the options for the current menu item (in menu view)

Pressing button 1 will manually advance the output, just like a trigger
on the digital input.

Pressing button 2 will enter the options menu.  Use knob 1 to
advance through the available options.  Knob 2 will cycle through the
values for the selected option.  Pressing button 1 will apply the
current selection.  Pressing button 2 will return to the default view.

Options:
- number of outputs: 2-6, determines the number of output ports used
- mode: one of:
    - sequential: port changes in order 1->2->3->4->5->6->1->....
    - reverse: port changes in order 1->6->5->4->3->2->1->6->....
    - ping-pong: port changes in order 1->2->3->4->5->6->5->4->...
    - random: port changes randomly, with a 1/n chance of repeating
      the current port

After 20 minutes of idle time the screen will go blank. While blank the module
will continue to operate normally.

Pressing button 1 while the screen is blank will wake the module up
_and_ advance the output.  Pressing button 2 will only wake up the screen.


## Patch Idea
Patch a constant voltage into `ain`.  Every time the output changes it will
effectively trigger a gate that will last until the next cycle. This will let
you trigger effects, envelopes, etc... in sequence.