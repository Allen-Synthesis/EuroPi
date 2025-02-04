#!/usr/bin/env python3
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
"""Additional classes and utilities for multi-threading support using _thread
"""

from europi import *


class DigitalInputHelper:
    """Helper class for reading digital inputs & outputs without using ISRs

    _thread can lock up if ISRs fire too frequently (e.g. pressing B1 repeatedly to select a mode). To avoid using
    ISRs this class can be used in your main thread to simulate the behaviour of ISRs by running a callback function
    when the state of the digital input changes.

    In your main loop you must call `.update()` to read the current state of the inputs & invoke the callback
    functions

    Calling `.update()` will populate the following fields of the DigitalInputHelper:
    - b1_last_pressed: the ms tick time that b1 was last pressed
    - b1_last_released: the ms tick time that b1 was last released
    - b1_pressed: True if b1 is currently pressed down, otherwise False
    - b1_rising: True if b1 transitioned to the pressed state during the last update() call, otherwise False
    - b1_falling: True if b1 transitioned to the released state during the last update() call, otherwise False
    - b2_last_pressed: the ms tick time that b2 was last pressed
    - b2_last_released: the ms tick time that b2 was last released
    - b2_pressed: True if b2 is currently pressed down, otherwise False
    - b2_rising: True if b1 transitioned to the pressed state during the last update() call, otherwise False
    - b2_falling: True if b1 transitioned to the released state during the last update() call, otherwise False
    - din_last_rise: the ms tick time that din last received a rising signal
    - din_last_fall: the ms tick time that din last received a falling signal
    - din_high: True if din is currently high, otherwise False
    - din_rising: True if din transitioned to the high state during the last update() call, otherwise False
    - din_falling: True if b1 transitioned to the low state during the last update() call, otherwise False
    """

    def __init__(
        self,
        on_din_rising=lambda: None,
        on_din_falling=lambda: None,
        on_b1_rising=lambda: None,
        on_b1_falling=lambda: None,
        on_b2_rising=lambda: None,
        on_b2_falling=lambda: None,
    ):
        """Constructor

        @param on_din_rising   Callback function to invoke when din detects a rising edge
        @param on_din_falling  Callback function to invoke when din detects a falling edge
        @param on_b1_rising    Callback function to invoke when b1 detects a rising edge
        @param on_b1_falling   Callback function to invoke when b1 detects a falling edge
        @param on_b2_rising    Callback function to invoke when b2 detects a rising edge
        @param on_b2_falling   Callback function to invoke when b2 detects a falling edge
        """
        # Connect the callback functions
        self.on_din_rising = on_din_rising
        self.on_din_falling = on_din_falling
        self.on_b1_rising = on_b1_rising
        self.on_b1_falling = on_b1_falling
        self.on_b2_rising = on_b2_rising
        self.on_b2_falling = on_b2_falling

        # Rising/falling states; these get updated inside the `update()` function
        self.din_rising = False
        self.din_falling = False
        self.b1_rising = False
        self.b1_falling = False
        self.b2_rising = False
        self.b2_falling = False

        # High/low flags for each input
        self.din_high = False
        self.b1_pressed = False
        self.b2_pressed = False

        # MS ticks when events were last recorded
        self.b1_last_pressed = 0
        self.b1_last_released = 0
        self.b2_last_pressed = 0
        self.b2_last_released = 0
        self.din_last_rise = 0
        self.din_last_fall = 0

    def update(self):
        """Check the state of the digital inputs, call the callback functions when appropriate

        This function should be called inside the main loop of your program
        """
        din_state = din.value() != 0
        b1_state = b1.value() != 0
        b2_state = b2.value() != 0

        self.din_rising = not self.din_high and din_state
        self.din_falling = self.din_high and not din_state

        self.b1_rising = not self.b1_pressed and b1_state
        self.b1_falling = self.b1_pressed and not b1_state

        self.b2_rising = not self.b2_pressed and b2_state
        self.b2_falling = self.b2_pressed and not b2_state

        self.din_high = din_state
        self.b1_pressed = b1_state
        self.b2_pressed = b2_state

        if self.b1_rising:
            self.b1_last_pressed = time.ticks_ms()
            self.on_b1_rising()
        elif self.b1_falling:
            self.b1_last_released = time.ticks_ms()
            self.on_b1_falling()

        if self.b2_rising:
            self.b2_last_pressed = time.ticks_ms()
            self.on_b2_rising()
        elif self.b2_falling:
            self.b2_last_released = time.ticks_ms()
            self.on_b2_falling()

        if self.din_rising:
            self.din_last_rise = time.ticks_ms()
            self.on_din_rising()
        elif self.din_falling:
            self.din_last_fall = time.ticks_ms()
            self.on_din_falling()
