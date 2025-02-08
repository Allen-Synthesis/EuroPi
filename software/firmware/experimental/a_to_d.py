# Copyright 2024 Allen Synthesis
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from europi import HIGH, LOW

import utime


class AnalogReaderDigitalWrapper:
    """Wraps an AnalogReader to allow it to simulate a DigitalReader.

    The EuroPiScript class using the AnalogReaderDigitalWrapper must call `.update()` to read the current state of
    the analogue input and trigger any rising/falling edge callbacks.

    The value returned by `.value()` is accurate to the last time `.update()` was called.
    """

    def __init__(
        self, ain, debounce=1, high_low_cutoff=0.8, cb_rising=lambda: None, cb_falling=lambda: None
    ):
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
        """Returns europi.HIGH or europi.LOW depending on the state of the input"""
        return HIGH if self.state else LOW

    def update(self):
        """Reads the current value of the analogue input and updates the internal state"""
        volts = self.ain.read_voltage()

        # count how many opposite-voltage readings we have
        if (self.state and volts < self.high_low_cutoff) or (
            not self.state and volts >= self.high_low_cutoff
        ):
            self.debounce_counter += 1

        # change state if we've reached the debounce threshold
        if self.debounce_counter >= self.debounce:
            self.debounce_counter = 0
            self.state = not self.state
            if self.state:
                self.last_rising_time = utime.ticks_ms()
                self.cb_rising()
            else:
                self.last_falling_time = utime.ticks_ms()
                self.cb_falling()

    def last_rising_ms(self):
        return self.last_rising_time

    def last_falling_ms(self):
        return self.last_falling_time

    def handler(self, func):
        """Define the callback function to call when rising edge detected."""
        if not callable(func):
            raise ValueError("Provided handler func is not callable")
        self.cb_rising = func

    def handler_falling(self, func):
        """Define the callback function to call when falling edge detected."""
        if not callable(func):
            raise ValueError("Provided handler func is not callable")
        self.cb_falling = func
