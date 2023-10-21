#!/usr/bin/env python3
"""Convert incoming triggers to gates or gates to triggers

Buttons allow manually creating gates/triggers, knobs control the duration of the output signals.
"""

import time

from europi import *
from europi_script import EuroPiScript
from math import sqrt

## All digital output signals are 5V
OUTPUT_VOLTAGE = 5.0

## Trigger outputs are 10ms long (rising/falling edges of gate signals)
TRIGGER_DURATION_MS = 10

class A2D_Wrapper:
    """Wraps an AnalogReader to allow it to simulate a DigitalReader
    """
    def __init__(self, ain, debounce=1, high_low_cutoff=0.8, \
                 cb_rising=lambda: None, cb_falling=lambda: None):
        """Constructor

        @param ain  The AnalogReader we're wrapping
        @param debounce  The number of consecutive high/low signals needed to flip the digital state
        @param high_low_cutoff  The threshold at which the analog signal is considered high

        @param cb_rising  A function to call on the rising edge of the signal
        @param cb_falling  A function to call on the falling edge of the signal
        """
        self.ain = ain
        self.debounce = debounce
        self.high_low_cutoff = high_low_cutoff
        self.last_rising_time = 0
        self.last_falling_time = 0
        self.debounce_counter = 0
        self.state = False

        if not callable(cb_rising) or not callable(cb_falling):
            raise ValueError("Provided callback func is not callable")

        self.cb_rising = cb_rising
        self.cb_falling = cb_falling

    def value(self):
        """Returns europi.HIGH or europi.LOW depending on the state of the input
        """
        return HIGH if self.state else LOW

    def update(self):
        """Reads the current value of the analogue input and updates the internal state
        """
        volts = self.ain.read_voltage()

        # count how many opposite-voltage readings we have
        if (self.state and volts < self.high_low_cutoff) or \
           (not self.state and volts >= self.high_low_cutoff):
            self.debounce_counter += 1

        # change state if we've reached the debounce threshold
        if self.debounce_counter >= self.debounce:
            self.debounce_counter = 0
            self.state = not self.state
            if self.state:
                self.last_rising_time = time.ticks_ms()
                self.cb_rising()
            else:
                self.last_falling_time = time.ticks_ms()
                self.cb_falling()

    def last_rising_ms(self):
        return self.last_rising_time

    def last_falling_ms(self):
        return self.last_falling_time

class GtWorker:
    """Helper class for G&T

    Handles rising & falling edges from the input/button and sets the output channels as needed
    """

    def __init__(self, gate_out, rise_out, fall_out, length_input):
        """Constructor

        @param gate_out  The CV output for the primary gate output
        @param rise_out  The CV output for the rising-edge trigger
        @param fall_out  The CV output for the falling-edge trigger
        @param length_input  The analog input to control the length of the gate output
        """

        self.gate_out = gate_out
        self.rise_out = rise_out
        self.fall_out = fall_out
        self.length_input = length_input

        self.on_rise_start_time = 0
        self.on_fall_start_time = 0

    def on_rise(self):
        """Handle the rising edge of the input signal
        """
        self.on_rise_start_time = time.ticks_ms()
        self.rise_out.voltage(OUTPUT_VOLTAGE)
        self.gate_out.voltage(OUTPUT_VOLTAGE)

    def on_fall(self):
        """Handle the falling edge of the input signal
        """
        self.on_fall_start_time = time.ticks_ms()
        self.fall_out.voltage(OUTPUT_VOLTAGE)

    def tick(self):
        """Advance the clock and set the outputs high/low as needed
        """
        now = time.ticks_ms()
        gate_duration = self.quadratic_knob(self.length_input.percent()*100)

        if time.ticks_diff(now, self.on_rise_start_time) > gate_duration:
            self.gate_out.voltage(0)

        if time.ticks_diff(now, self.on_rise_start_time) > TRIGGER_DURATION_MS:
            self.rise_out.voltage(0)

        if time.ticks_diff(now, self.on_fall_start_time) > TRIGGER_DURATION_MS:
            self.fall_out.voltage(0)

    def quadratic_knob(self, x):
        """Some magic math to give us a quadratic response on the knob percentage

        This gives us 10ms @ 0% and 1000ms @ 100% with greater precision at the higher end
        where the differences will be more noticeable
        """
        return 90 * sqrt(x) + 10


class GatesAndTriggers(EuroPiScript):
    def __init__(self):
        super().__init__()

        self.channel1 = GtWorker(cv1, cv2, cv3, k1)
        self.channel2 = GtWorker(cv4, cv5, cv6, k2)

        @din.handler
        def on_din_rising():
            self.channel1.on_rise()

        @din.handler_falling
        def on_din_falling():
            self.channel1.on_fall()

        @b1.handler
        def on_b1_press():
            self.channel1.on_rise()

        @b1.handler_falling
        def on_b1_release():
            self.channel1.on_fall()

        @b2.handler
        def on_b1_press():
            self.channel2.on_rise()

        @b2.handler_falling
        def on_b1_release():
            self.channel2.on_fall()

        self.ain_wrapper = A2D_Wrapper(ain, \
            cb_rising=lambda: self.channel2.on_rise(), \
            cb_falling=lambda: self.channel2.on_fall)

    def main(self):
        while(True):
            self.ain_wrapper.update()
            self.channel1.tick()
            self.channel2.tick()


if __name__=="__main__":
    GatesAndTriggers().main()
