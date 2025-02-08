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
"""Clock multiplier & divider
"""

import time

from collections import OrderedDict
from europi import *
from europi_script import EuroPiScript
from experimental.a_to_d import AnalogReaderDigitalWrapper
from experimental.knobs import KnobBank
from experimental.screensaver import Screensaver
from math import floor


# This script operates in microseconds, so for convenience define one second as a constant
ONE_SECOND = 1000000

# Automatically reset if we receive no input clocks after 5 seconds
# This lets us handle resonably slow input clocks, while also providing some reasonable timing
CLOCK_IN_TIMEOUT = 5 * ONE_SECOND


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
    ## The smallest common multiple of the allowed clock divisions (2, 3, 4, 5, 6, 8, 12)
    #
    #  Used to reset the input gate counter to avoid integer overflows/performance degredation with large values
    MAX_GATE_COUNT = 120

    def __init__(self, output_port, modifier):
        """Constructor

        @param output_port  One of the six output CV ports, e.g. cv1, cv2, etc... that this class will control
        @param modifier     The initial clock modifier for this output channel
        """
        self.last_external_clock_at = time.ticks_us()
        self.last_interval_us = 0
        self.modifier = modifier
        self.output_port = output_port

        # Should the output be high or low?
        self.is_high = False

        # Used to implement basic gate-skipping for clock divisions
        self.input_gate_counter = 0

    def set_external_clock(self, ticks_us):
        """Notify this output when the last external clock signal was received.

        The calculate_state function will use this to calculate the duration of the high/low phases
        of the output gate
        """
        if self.last_external_clock_at != ticks_us:
            self.last_interval_us = time.ticks_diff(ticks_us, self.last_external_clock_at)
            self.last_external_clock_at = ticks_us

            self.input_gate_counter += 1
            if self.input_gate_counter >= self.MAX_GATE_COUNT:
                self.input_gate_counter = 0

    def calculate_state(self, ticks_us):
        """Calculate whether this output should be high or low based on the current time

        Must be called before calling set_output_voltage

        @param ticks_us  The current time in microseconds; passed as a parameter to synchronize multiple channels
        """
        if self.modifier >= 1:
            # We're in clock multiplication mode; calculate the duration of output gates and set high/low state
            gate_duration_us = self.last_interval_us / self.modifier
            hi_lo_duration_us = gate_duration_us / 2

            # The time elapsed since our last external clock
            elapsed_us = time.ticks_diff(ticks_us, self.last_external_clock_at)

            # The number of phases that have happened since the last incoming clock
            n_phases = elapsed_us // hi_lo_duration_us

            self.is_high = n_phases % 2 == 0
        else:
            # We're in clock division mode; just do a simple gate-skip to stay in sync with the input
            n_gates = round(1.0 / self.modifier)
            self.is_high = self.input_gate_counter % (n_gates * 2) < n_gates

    def set_output_voltage(self):
        """Set the output voltage either high or low.

        Must be called after calling calculate_state
        """
        if self.is_high:
            self.output_port.on()
        else:
            self.output_port.off()

    def reset(self):
        """Reset the pattern to the initial position
        """
        self.is_high = False
        self.output_port.off()
        self.input_gate_counter = 0


class ClockModifier(EuroPiScript):
    """The main script class; multiplies and divides incoming clock signals
    """
    def __init__(self):
        self.ui_dirty = False
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
        #
        #  Initially negative 1s to avoid starting the module
        self.last_clock_at = -1000

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

        # Indicates that the modifiers have changed and a save is required
        self.state_dirty = False

        @b1.handler
        def b1_rising():
            """Activate channel b controls while b1 is held
            """
            self.k1_bank.set_current("channel_b")
            self.k2_bank.set_current("channel_b")
            self.channel_markers[0] = ' '
            self.channel_markers[1] = '>'
            self.channel_markers[2] = ' '
            self.ui_dirty = True

        @b2.handler
        def b2_rising():
            """Activate channel c controls while b1 is held
            """
            self.k1_bank.set_current("channel_c")
            self.k2_bank.set_current("channel_c")
            self.channel_markers[0] = ' '
            self.channel_markers[1] = ' '
            self.channel_markers[2] = '>'
            self.ui_dirty = True

        @b1.handler_falling
        def b1_falling():
            """Revert to channel a when the button is released
            """
            self.k1_bank.set_current("channel_a")
            self.k2_bank.set_current("channel_a")
            self.channel_markers[0] = '>'
            self.channel_markers[1] = ' '
            self.channel_markers[2] = ' '
            self.state_dirty = True
            self.ui_dirty = True

        @b2.handler_falling
        def b2_falling():
            """Revert to channel a when the button is released
            """
            self.k1_bank.set_current("channel_a")
            self.k2_bank.set_current("channel_a")
            self.channel_markers[0] = '>'
            self.channel_markers[1] = ' '
            self.channel_markers[2] = ' '
            self.state_dirty = True
            self.ui_dirty = True

        @din.handler
        def on_din():
            """Record the start time of our rising edge
            """
            self.last_clock_at = time.ticks_us()

        def on_ain():
            """Reset all channels when AIN goes high
            """
            for output in self.outputs:
                output.reset()

        self.d_ain = AnalogReaderDigitalWrapper(
            ain,
            cb_rising=on_ain
        )

    def save_state(self):
        """Save the clock modifiers for channels 2, 3, 5, 6 to the config file for loading

        Channels 1 and 4 are read directly from the knob positions on startup, and are considered volatile
        """
        state = {
            "mod_cv2": self.k1_bank["channel_b"].percent(),
            "mod_cv3": self.k1_bank["channel_c"].percent(),
            "mod_cv5": self.k2_bank["channel_b"].percent(),
            "mod_cv6": self.k2_bank["channel_c"].percent()
        }
        self.save_state_json(state)

    def main(self):
        """The main loop
        """
        screensaver = Screensaver()
        last_render_at = time.ticks_us()

        knob_choices = list(self.clock_modifiers.keys())

        prev_mods = [
            knob_choices[0],
            knob_choices[0],
            knob_choices[0],
            knob_choices[0],
            knob_choices[0],
            knob_choices[0],
        ]

        while True:
            # update AIN so its rising edge callback can fire
            self.d_ain.update()

            # Save the clock modifiers for channels 2, 3, 5, 6 if they've been edited
            if self.state_dirty:
                self.state_dirty = False
                self.save_state()

            # Get the clock modifiers for all 6 channels and apply them to the outputs
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

            # if we don't get an external signal within the timeout duration, reset the outputs
            now = time.ticks_us()
            if time.ticks_diff(now, self.last_clock_at) <= CLOCK_IN_TIMEOUT:
                # separate calculating the high/low state and setting the output voltage into two loops
                # this helps reduce phase-shifting across outputs
                for output in self.outputs:
                    output.set_external_clock(self.last_clock_at)
                    output.calculate_state(now)

                for output in self.outputs:
                    output.set_output_voltage()
            else:
                for output in self.outputs:
                    output.reset()

            # Update the GUI
            # This only needs to be done if the modifiers have changed or a button has been pressed/released
            self.ui_dirty = self.ui_dirty or any([mods[i] != prev_mods[i] for i in range(len(mods))])
            if self.ui_dirty:
                # Yes, this is a very long string, but it centers nicely
                # It looks something like this:
                #
                #    > 1: x1   4: /2
                #      2: x2   5: x3
                #      3: /4   6: /3
                #
                oled.fill(0)
                oled.centre_text(
                    f"{self.channel_markers[0]} 1:{ljust(mods[0], 3)} 4:{ljust(mods[3], 3)}\n{self.channel_markers[1]} 2:{ljust(mods[1], 3)} 5:{ljust(mods[4], 3)}\n{self.channel_markers[2]} 3:{ljust(mods[2], 3)} 6:{ljust(mods[5], 3)}"
                )
                self.ui_dirty = False
                last_render_at = time.ticks_us()
            elif time.ticks_diff(now, last_render_at) > screensaver.ACTIVATE_TIMEOUT_US:
                last_render_at = time.ticks_add(now, -screensaver.ACTIVATE_TIMEOUT_US)
                screensaver.draw()

            for i in range(len(mods)):
                prev_mods[i] = mods[i]


if __name__=="__main__":
    ClockModifier().main()
