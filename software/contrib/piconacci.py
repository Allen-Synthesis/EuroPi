from europi import *
import machine
from time import ticks_diff, ticks_ms
from random import randint, uniform, choice

from europi_script import EuroPiScript

"""
Piconacci
author: Sean Bechhofer (github.com/seanbechhofer)
date: 2022-05
labels: triggers, maths

Triggers based on the Fibonacci sequence

digital_in: clock in
analog_in: 

knob_1: 
knob_2: 

button_1: Short Press: Move window on sequence left. Long Press: Rotate values left
button_2: Short Press: Move window on sequence to the right. Long Press: Rotate values right
output_1: trigger
output_2: trigger
output_3: trigger
output_4: trigger
output_5: trigger
output_6: trigger

"""


# This probably works for most sensible circumstances. The 50th value
# (disregarding 0, 1) is 20,365,011,074. At a BPM of 120, that'll be a
# trigger every 300 years which is quite a lot even for slow moving
# ambient pieces,
MAX_FIB = 50


class Piconacci(EuroPiScript):
    def __init__(self):
        # Flag to indicate whether the display needs updating.
        self.display_update_required = True
        # offset determines the sublist to be used for the values.
        self.offset = 0
        # rotate adjusts how the values are mapped to the cv
        # outputs. A value of 0 means that cv1 is controlled by the
        # first, cv2 the second etc. A rotate value of 1 means that
        # cv2 is controlled by the first, cv3 the second, and cv1 the
        # last.
        self.rotate = 0
        # Overclock the Pico for improved performance.
        machine.freq(250_000_000)
        # List of fibonacci numbers.
        self.fib = [1, 1]
        for i in range(0, MAX_FIB):
            self.fib.append(self.fib[-2] + self.fib[-1])
        # Strip off first 1
        self.fib = self.fib[1:]

        self.steps = [0] * 6

        @b1.handler_falling
        def b1Pressed():
            if ticks_diff(ticks_ms(), b1.last_pressed()) > 300:
                # Rotate values left
                self.rotate = (self.rotate - 1) % 6
            else:
                # Shift all the values left in the sequence
                if self.offset > 0:
                    self.offset -= 1
            # State has changed
            self.display_update_required = True

        @b2.handler_falling
        def b2Pressed():
            if ticks_diff(ticks_ms(), b2.last_pressed()) > 300:
                # Rotate values right
                self.rotate = (self.rotate + 1) % 6
            else:
                # Shift all the values right in the sequence
                if self.offset < MAX_FIB - 7:
                    self.offset += 1
            # State has changed
            self.display_update_required = True

        # Triggered on each clock into digital input. Output triggers.
        @din.handler
        def clockTrigger():
            for tr in range(0, 6):
                self.steps[tr] += 1
                if self.steps[tr] >= self.value(tr):
                    # Trigger on tr
                    cvs[tr].on()
                    # If the values change due to shift or rotation,
                    # we may get slightly odd behaviour here,
                    # particularly if the values reduce.
                    self.steps[tr] = 0

        @din.handler_falling
        def clockTriggerEnd():
            for cv in cvs:
                cv.off()

    def value(self, index):
        # Return a value from the series, taking into account offset and rotation
        return self.fib[self.offset : self.offset + 6][(index + self.rotate) % 6]

    def main(self):
        # Reset all outputs
        [cv.off() for cv in cvs]
        while True:
            # If the state has changed, update display
            if self.display_update_required:
                self.updateScreen()
                self.display_update_required = False

    def updateScreen(self):
        oled.fill(0)

        # Show the values.
        oled.text("Piconacci", 28, 0, 1)
        oled.text(str(self.value(0)), 10, 12, 1)
        oled.text(str(self.value(1)), 50, 12, 1)
        oled.text(str(self.value(2)), 90, 12, 1)
        oled.text(str(self.value(3)), 10, 24, 1)
        oled.text(str(self.value(4)), 50, 24, 1)
        oled.text(str(self.value(5)), 90, 24, 1)
        oled.show()


if __name__ == "__main__":
    pc = Piconacci()
    pc.main()
