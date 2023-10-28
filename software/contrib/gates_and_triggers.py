#!/usr/bin/env python3
"""Convert incoming triggers to gates or gates to triggers

Also outputs a toggle input which changes state every time an incoming gate is received, or when either button is
pressed.

@author Chris Iverach-Brereton <ve4cib@gmail.com>
@year   2023
"""

import time

from europi import *
from europi_script import EuroPiScript
from math import sqrt

## All digital output signals are 5V
OUTPUT_VOLTAGE = 5.0

## Trigger outputs are 10ms long (rising/falling edges of gate signals)
TRIGGER_DURATION_MS = 10

class GatesAndTriggers(EuroPiScript):
    def __init__(self):
        super().__init__()

        self.on_incoming_rise_start_time = 0
        self.on_incoming_fall_start_time = 0
        self.on_gate_fall_start_time = 0
        self.on_toggle_fall_start_time = 0

        # assign each of the CV outputs to specific duties
        self.gate_out = cv1
        self.incoming_rise_out = cv2
        self.incoming_fall_out = cv3
        self.gate_fall_out = cv4
        self.toggle_out = cv5
        self.toggle_fall_out = cv6

        self.gate_on = False
        self.toggle_on = False

        # turn off all outputs initially
        for cv in cvs:
            cv.voltage(0)

        @din.handler
        def on_din_rising():
            self.on_rise()

        @din.handler_falling
        def on_din_falling():
            self.on_fall()

        @b1.handler
        def on_b1_press():
            self.on_rise()

        @b1.handler_falling
        def on_b1_release():
            self.on_fall()

        @b2.handler
        def on_b2_press():
            self.on_toggle()

    def on_rise(self):
        """Handle the rising edge of the input signal
        """
        self.gate_on = True
        self.on_incoming_rise_start_time = time.ticks_ms()
        self.incoming_rise_out.voltage(OUTPUT_VOLTAGE)
        self.gate_out.voltage(OUTPUT_VOLTAGE)

        self.on_toggle()

    def on_fall(self):
        """Handle the falling edge of the input signal
        """
        self.on_incoming_fall_start_time = time.ticks_ms()
        self.incoming_fall_out.voltage(OUTPUT_VOLTAGE)

    def on_toggle(self):
        """Handle toggling the toggle output
        """
        self.toggle_on = not self.toggle_on
        if self.toggle_on:
            self.toggle_out.voltage(OUTPUT_VOLTAGE)
        else:
            self.toggle_out.voltage(0)
            self.toggle_fall_out.voltage(OUTPUT_VOLTAGE)
            self.on_toggle_fall_start_time = time.ticks_ms()

    def tick(self):
        """Advance the clock and set the outputs high/low as needed
        """
        now = time.ticks_ms()
        knob_lvl = k1.percent()*100
        cv_lvl = ain.percent() * k2.percent() * 2 * 100
        gate_duration = self.quadratic_knob(cv_lvl + knob_lvl)

        if self.gate_on and time.ticks_diff(now, self.on_incoming_rise_start_time) > gate_duration:
            self.gate_on = False
            self.gate_out.voltage(0)
            self.gate_fall_out.voltage(OUTPUT_VOLTAGE)
            self.on_gate_fall_start_time = now

        if time.ticks_diff(now, self.on_gate_fall_start_time) > TRIGGER_DURATION_MS:
            self.gate_fall_out.voltage(0)

        if time.ticks_diff(now, self.on_incoming_rise_start_time) > TRIGGER_DURATION_MS:
            self.incoming_rise_out.voltage(0)

        if time.ticks_diff(now, self.on_incoming_fall_start_time) > TRIGGER_DURATION_MS:
            self.incoming_fall_out.voltage(0)

        if time.ticks_diff(now, self.on_toggle_fall_start_time) > TRIGGER_DURATION_MS:
            self.toggle_fall_out.voltage(0)

    def quadratic_knob(self, x):
        """Some magic math to give us a quadratic response on the knob percentage

        This gives us 10ms @ 0% and 2000ms @ 100% with greater precision at the higher end
        where the differences will be more noticeable
        """
        if x <= 0:
            return 10
        return 199 * sqrt(x) + 10

    def main(self):
        # blank the screen since it's not needed
        oled.fill(0)
        oled.show()
        while(True):
            self.tick()


if __name__=="__main__":
    GatesAndTriggers().main()
