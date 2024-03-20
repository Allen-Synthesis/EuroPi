#!/usr/bin/env python3
"""Clock multiplier & divider
"""

import time

from collections import OrderedDict
from europi import *
from europi_script import EuroPiScript
from experimental.a_to_d import AnalogReaderDigitalWrapper
from experimental.knobs import KnobBank
from math import floor


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
        """Constructor

        @param output_port  One of the six output CV ports, e.g. cv1, cv2, etc... that this class will control
        @param modifier     The initial clock modifier for this output channel
        """
        self.last_external_clock_at = time.ticks_ms()
        self.last_interval_ms = 0
        self.modifier = modifier
        self.output_port = output_port

        self.is_high = False
        self.last_state_change_at = time.ticks_ms()

    def set_external_clock(self, ticks_ms):
        """Notify this output when the last external clock signal was received.

        The calculate_state function will use this to calculate the duration of the high/low phases
        of the output gate
        """
        if self.last_external_clock_at != ticks_ms:
            self.last_interval_ms = time.ticks_diff(ticks_ms, self.last_external_clock_at)
            self.last_external_clock_at = ticks_ms

    def calculate_state(self, ms):
        """Calculate whether this output should be high or low based on the current time

        Must be called before calling set_output_voltage

        @param ms  The current time in ms; passed as a parameter to synchronize multiple channels
        """
        gate_duration_ms = self.last_interval_ms / self.modifier
        hi_lo_duration_ms = gate_duration_ms / 2

        elapsed_ms = time.ticks_diff(ms, self.last_state_change_at)

        if elapsed_ms > hi_lo_duration_ms:
            self.last_state_change_at = ms
            if self.is_high:
                self.is_high = False

            else:
                self.is_high = True
                self.output_port.on()

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
        self.last_state_change_at = time.ticks_ms()

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
            self.state_dirty = True

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

        @din.handler
        def on_din():
            """Record the start time of our rising edge
            """
            self.last_clock_at = time.ticks_ms()

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
        knob_choices = list(self.clock_modifiers.keys())
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

            # if we don't get an external signal within 1s, stop
            now = time.ticks_ms()
            if time.ticks_diff(now, self.last_clock_at) < 1000:
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

if __name__=="__main__":
    ClockModifier().main()
