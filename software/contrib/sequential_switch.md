# Sequential Switch

This script acts as a sequential switch, routing a copy of the analogue input
to one of the outputs.  When a gate is received the output is changed.

Pressing the left button will manually advance the output, just like a trigger
on the digital input.

Pressing the right button will enter the options menu.  Use the left knob to
advance through the available options.  The right knob will cycle through the
values for the selected option.  Pressing the left button will apply the
current selection.  Pressing the right button will return to the default view.

Options:
- number of outputs: 2-6, determines the number of output ports used
- mode: either sequential or random.  In sequential mode the output port changes
  in order 1->2->3->4->5->6->1->.... In random order the output port is randomly
  chosen, and has a 1/n chance of being the same port already in-use.
  
After 20 minutes of idle time the screen will go blank. While blank the module
will continue to operate normally.

Pressing the left button while the screen is blank will wake the module up
_and_ advance the output.  Pressing the right button will only wake up the
screen.