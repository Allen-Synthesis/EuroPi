#!/usr/bin/env python3
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
        self.b1_high = False
        self.b2_high = False

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

        self.b1_rising = not self.b1_high and b1_state
        self.b1_falling = self.b1_high and not b1_state

        self.b2_rising = not self.b2_high and b2_state
        self.b2_falling = self.b2_high and not b2_state

        self.din_high = din_state
        self.b1_high = b1_state
        self.b2_high = b2_state

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
