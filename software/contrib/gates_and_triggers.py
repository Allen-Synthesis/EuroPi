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

from experimental.screensaver import OledWithScreensaver

ssoled = OledWithScreensaver()

## Trigger outputs are 10ms long (rising/falling edges of gate signals)
TRIGGER_DURATION_MS = 10

class GatesAndTriggers(EuroPiScript):
    def __init__(self):
        super().__init__()

        now = time.ticks_ms()

        self.on_incoming_rise_start_time = now
        self.on_incoming_fall_start_time = now
        self.on_gate_fall_start_time = now
        self.on_toggle_fall_start_time = now

        # assign each of the CV outputs to specific duties
        self.gate_out = cv1
        self.incoming_rise_out = cv2
        self.incoming_fall_out = cv3
        self.gate_fall_out = cv4
        self.toggle_out = cv5
        self.toggle_fall_out = cv6

        self.gate_on = False
        self.toggle_on = False

        self.k1_percent = int(k1.percent() * 100)
        self.k2_percent = int(k2.percent() * 100)

        turn_off_all_cvs()

        @din.handler
        def on_din_rising():
            self.on_rise()

        @din.handler_falling
        def on_din_falling():
            self.on_fall()

        @b1.handler
        def on_b1_press():
            self.on_rise()
            ssoled.notify_user_interaction()

        @b1.handler_falling
        def on_b1_release():
            self.on_fall()

        @b2.handler
        def on_b2_press():
            self.on_toggle()
            ssoled.notify_user_interaction()

    def on_rise(self):
        """Handle the rising edge of the input signal
        """
        self.gate_on = True
        self.on_incoming_rise_start_time = time.ticks_ms()
        self.incoming_rise_out.on()
        self.gate_out.on()

        self.on_toggle()

    def on_fall(self):
        """Handle the falling edge of the input signal
        """
        self.on_incoming_fall_start_time = time.ticks_ms()
        self.incoming_fall_out.on()

    def on_toggle(self):
        """Handle toggling the toggle output
        """
        self.toggle_on = not self.toggle_on
        if self.toggle_on:
            self.toggle_out.on()
        else:
            self.toggle_out.off()
            self.toggle_fall_out.on()
            self.on_toggle_fall_start_time = time.ticks_ms()

    def tick(self):
        """Advance the clock and set the outputs high/low as needed
        """
        now = time.ticks_ms()

        k1_percent = int(k1.percent() * 100)
        k2_percent = int(k2.percent() * 100)

        # if the user moved the knobs by more than 1% deactivate the screensaver
        if abs(self.k1_percent - k1_percent) > 0 or abs(self.k2_percent - k2_percent) > 0:
            ssoled.notify_user_interaction()

        knob_lvl = k1_percent
        cv_lvl = ain.percent() * (k2_percent * 0.02 - 1)
        self.gate_duration = max(self.quadratic_knob(knob_lvl) + cv_lvl * 2000, TRIGGER_DURATION_MS)

        if self.gate_on and time.ticks_diff(now, self.on_incoming_rise_start_time) > self.gate_duration:
            self.gate_on = False
            self.gate_out.off()
            self.gate_fall_out.on()
            self.on_gate_fall_start_time = now

        if time.ticks_diff(now, self.on_gate_fall_start_time) > TRIGGER_DURATION_MS:
            self.gate_fall_out.off()

        if time.ticks_diff(now, self.on_incoming_rise_start_time) > TRIGGER_DURATION_MS:
            self.incoming_rise_out.off()

        if time.ticks_diff(now, self.on_incoming_fall_start_time) > TRIGGER_DURATION_MS:
            self.incoming_fall_out.off()

        if time.ticks_diff(now, self.on_toggle_fall_start_time) > TRIGGER_DURATION_MS:
            self.toggle_fall_out.off()

        self.k1_percent = k1_percent
        self.k2_percent = k2_percent

    def quadratic_knob(self, x):
        """Some magic math to give us a quadratic response on the knob percentage

        This gives us 10ms @ 0% and 2000ms @ 100% with greater precision at the higher end
        where the differences will be more noticeable
        """
        if x <= 0:
            return 10
        return 199 * sqrt(x) + 10

    def main(self):
        while(True):
            self.tick()

            ssoled.centre_text(f"Gate: {self.gate_duration:0.0f}ms")


if __name__=="__main__":
    GatesAndTriggers().main()
