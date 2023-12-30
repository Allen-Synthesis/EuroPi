#!/usr/bin/env python3
"""Clock multiplier & divider
"""

import time

from collections import OrderedDict
from europi import *
from europi_script import EuroPiScript
from experimental.knobs import KnobBank
from math import floor

GATE_VOLTS = 5.0

def ljust(s, length):
    """Re-implements the str.ljust method from standard Python

    @param s  A string to left-align with spaces
    @param length  The desired final length of the string. If len(s) is greater or equal to this, no padding is done
    @return The padding string
    """
    n_spaces = max(0, length - len(s))
    return s + ' '*n_spaces

class ClockOutput:
    """A control class that handles a single output
    """
    def __init__(self, output_port, modifier):
        self.last_external_clock_at = time.ticks_ms()
        self.last_interval_ms = 0
        self.modifier = modifier
        self.output_port = output_port

        self.is_high = False
        self.last_state_change_at = time.ticks_ms()

    def set_external_clock(self, ticks_ms):
        if self.last_external_clock_at != ticks_ms:
            self.last_interval_ms = time.ticks_diff(ticks_ms, self.last_external_clock_at)
            self.last_external_clock_at = ticks_ms

    def tick(self):
        gate_duration_ms = self.last_interval_ms / self.modifier
        hi_lo_duration_ms = gate_duration_ms / 2

        now = time.ticks_ms()
        elapsed_ms = time.ticks_diff(now, self.last_state_change_at)

        if elapsed_ms > hi_lo_duration_ms:
            self.last_state_change_at = now
            if self.is_high:
                self.is_high = False
                self.output_port.voltage(0)
            else:
                self.is_high = True
                self.output_port.voltage(GATE_VOLTS)

class ClockModifier(EuroPiScript):
    """The main script class; multiplies and divides incoming clock signals
    """
    def __init__(self):
        state = self.load_state_json()

        self.k1_bank = (
            KnobBank.builder(k1) \
            .with_unlocked_knob("channel_a") \
            .with_locked_knob("channel_b", initial_percentage_value=state.get("mod_cv2", 0.5)) \
            .with_locked_knob("channel_c", initial_percentage_value=state.get("mod_cv3", 0.5)) \
            .build()
        )

        self.k2_bank = (
            KnobBank.builder(k2) \
            .with_unlocked_knob("channel_a") \
            .with_locked_knob("channel_b", initial_percentage_value=state.get("mod_cv5", 0.5)) \
            .with_locked_knob("channel_c", initial_percentage_value=state.get("mod_cv6", 0.5)) \
            .build()
        )

        ## The time the last rising edge of the clock was recorded
        self.last_clock_at = time.ticks_ms()

        ## The output channels
        self.outputs = [
            ClockOutput(cv, 1.0) for cv in cvs
        ]

        ## Gui labels to indicate what row of modifiers we're adjusting
        self.channel_markers = ['>', ' ', ' ']

        self.clock_modifiers = OrderedDict([
            ["/12", 1.0/12.0],
            ["/8", 1.0/8.0],
            ["/6", 1.0/6.0],
            ["/5", 1.0/5.0],
            ["/4", 1.0/4.0],
            ["/3", 1.0/3.0],
            ["/2", 1.0/2.0],
            ["x1", 1.0],
            ["x2", 2.0],
            ["x3", 3.0],
            ["x4", 4.0],
            ["x5", 5.0],
            ["x6", 6.0],
            ["x8", 8.0],
            ["x12", 12.0]
        ])

        @b1.handler
        def b1_rising():
            """Activate channel b controls while b1 is held
            """
            self.k1_bank.set_current("channel_b")
            self.k2_bank.set_current("channel_b")
            self.channel_markers[0] = ' '
            self.channel_markers[1] = '>'
            self.channel_markers[2] = ' '

        @b2.handler
        def b2_rising():
            """Activate channel c controls while b1 is held
            """
            self.k1_bank.set_current("channel_c")
            self.k2_bank.set_current("channel_c")
            self.channel_markers[0] = ' '
            self.channel_markers[1] = ' '
            self.channel_markers[2] = '>'

        @b1.handler_falling
        def b1_falling():
            """Revert to channel a when the button is released
            """
            self.k1_bank.set_current("channel_a")
            self.k2_bank.set_current("channel_a")
            self.channel_markers[0] = '>'
            self.channel_markers[1] = ' '
            self.channel_markers[2] = ' '
            self.save_state()

        @b2.handler_falling
        def b2_falling():
            """Revert to channel a when the button is released
            """
            self.k1_bank.set_current("channel_a")
            self.k2_bank.set_current("channel_a")
            self.channel_markers[0] = '>'
            self.channel_markers[1] = ' '
            self.channel_markers[2] = ' '
            self.save_state()

        @din.handler
        def on_din():
            """Record the start time of our rising edge
            """
            self.last_clock_at = time.ticks_ms()

    def save_state(self):
        state = {
            "mod_cv2": self.k1_bank["channel_b"].percent(),
            "mod_cv3": self.k1_bank["channel_c"].percent(),
            "mod_cv5": self.k2_bank["channel_c"].percent(),
            "mod_cv6": self.k2_bank["channel_c"].percent()
        }
        self.save_state_json(state)

    def main(self):
        """The main loop
        """
        knob_choices = list(self.clock_modifiers.keys())
        while True:
            mods = [
                self.k1_bank["channel_a"].choice(knob_choices),
                self.k1_bank["channel_b"].choice(knob_choices),
                self.k1_bank["channel_c"].choice(knob_choices),
                self.k2_bank["channel_a"].choice(knob_choices),
                self.k2_bank["channel_b"].choice(knob_choices),
                self.k2_bank["channel_c"].choice(knob_choices)
            ]

            for i in range(len(mods)):
                self.outputs[i].modifier = self.clock_modifiers[mods[i]]

            for output in self.outputs:
                output.set_external_clock(self.last_clock_at)
                output.tick()

            oled.fill(0)
            oled.centre_text(
                f"{self.channel_markers[0]} 1:{ljust(mods[0], 3)} 4:{ljust(mods[3], 3)}\n{self.channel_markers[1]} 2:{ljust(mods[1], 3)} 5:{ljust(mods[4], 3)}\n{self.channel_markers[2]} 3:{ljust(mods[2], 3)} 6:{ljust(mods[5], 3)}"
            )

if __name__=="__main__":
    ClockModifier().main()
