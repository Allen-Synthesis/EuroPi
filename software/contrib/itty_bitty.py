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
"""
Two 8-step trigger, gate & CV sequencers based on the binary representation of an 8-bit number
"""

from europi import *
from europi_script import EuroPiScript

import configuration
import time


class BittySequence:
    """
    A container class for one sequencer
    """
    def __init__(self, button_in, trigger_out, gate_out, cv_out, use_gray_encoding=False):
        """
        Create a new sequencer

        @param button_in  The button the user can press to manually advance the sequence
        @param trigger_out  The CV output for the trigger signal
        @param gate_out  The CV output for the gate signal
        @param cv_out  The CV output for the CV signal
        @param use_gray_encoding  If true, we use gray encoding instead of traditional binary
        """
        button_in.handler(self.advance)
        button_in.handler_falling(self.trigger_off)

        self.trigger_out = trigger_out
        self.gate_out = gate_out
        self.cv_out = cv_out

        self.use_gray_encoding = use_gray_encoding

        # the integer representation of our sequence
        # if we're not using gray encoding this should be the same as our binary sequence
        self.sequence_n = 0

        # the raw binary pattern that represents our sequence
        self.binary_sequence = 0x00

        # the current step
        self.step = 0

        # is the current output state in need of refreshing?
        self.output_dirty = False

        # turn everything off initially
        self.trigger_out.off()
        self.gate_out.off()
        self.cv_out.off()

    def advance(self):
        self.step = (self.step + 1) & 0x07  # restrict this to 0-7
        self.output_dirty = True

    def trigger_off(self):
        self.trigger_out.off()

    def apply_output(self):
        now = time.ticks_ms()

        if self.current_bit:
            self.trigger_out.on()
            self.gate_out.on()
        else:
            self.trigger_out.off()
            self.gate_out.off()

        self.cv_out.voltage(europi_config.MAX_OUTPUT_VOLTAGE * self.cv_sequence / 255)

        self.output_dirty = False

    def change_sequence(self, n):
        self.sequence_n = n

        if self.use_gray_encoding:
            # convert the number from traditional binary to its gray encoding equivalent
            n = (n & 0xff) ^ ((n & 0xff) >> 1)
        else:
            n = n & 0xff

        self.binary_sequence = n

    @property
    def shifted_sequence(self):
        return ((self.binary_sequence << self.step) & 0xff) | ((self.binary_sequence & 0xff) >> (8 - self.step))

    @property
    def cv_sequence(self):
        # reverse the bits of the shifted sequence
        s = self.shifted_sequence
        cv = 0x00
        while s:
            cv = cv << 1
            cv = cv | (s & 0x01)
            s = s >> 1
        return cv & 0xff

    @property
    def current_bit(self):
        return (self.shifted_sequence >> 7) & 0x01


class IttyBitty(EuroPiScript):
    def __init__(self):
        super().__init__()

        self.sequencers = [
            BittySequence(b1, cv1, cv2, cv3, use_gray_encoding=self.config.USE_GRAY_ENCODING),
            BittySequence(b2, cv4, cv5, cv6, use_gray_encoding=self.config.USE_GRAY_ENCODING),
        ]

        @din.handler
        def on_clock_rise():
            for s in self.sequencers:
                s.advance()

        @din.handler_falling
        def on_clock_fall():
            for s in self.sequencers:
                s.trigger_off()

    @classmethod
    def config_points(cls):
        return [
            # If true, use gray encoding instead of standard binary
            # Gray encding flips a single bit at each step, meaning any two adjacent
            # sequences differ by only 1 bit
            configuration.boolean(
                "USE_GRAY_ENCODING",
                False
            ),

            # Flags to enable AIN to control channel A and/or channel B
            # when enabled, the knob acts as an attenuator instead of a selector
            configuration.boolean(
                "USE_AIN_A",
                False
            ),
            configuration.boolean(
                "USE_AIN_B",
                False
            ),
        ]

    def main(self):
        TEXT_TOP = CHAR_HEIGHT
        BITS_LEFT = CHAR_WIDTH * 6

        N_STEPS = 256
        N_SAMPLES = 200

        while True:
            cv = ain.percent(samples=N_SAMPLES)

            if self.config.USE_AIN_A:
                atten = k1.percent(samples=N_SAMPLES)
                n1 = round(cv * atten * N_STEPS)
                if n1 == N_STEPS:
                    # prevent bounds problems since percent() returns [0, 1], not [0, 1)
                    n1 = N_STEPS - 1
            else:
                n1 = k1.read_position(steps=N_STEPS, samples=N_SAMPLES)

            if self.config.USE_AIN_B:
                atten = k2.percent(samples=N_SAMPLES)
                n2 = round(cv * atten * N_STEPS)
                if n2 == N_STEPS:
                    n2 = N_STEPS - 1
            else:
                n2 = k2.read_position(steps=N_STEPS, samples=N_SAMPLES)

            self.sequencers[0].change_sequence(n1)
            self.sequencers[1].change_sequence(n2)

            oled.fill(0)
            for i in range(len(self.sequencers)):
                s = self.sequencers[i]

                # Set the output voltages if needed
                if s.output_dirty:
                    s.apply_output()

                # Show the sequence number, sequence, and draw a box around the active bit
                oled.text(f"{s.sequence_n:5} {s.binary_sequence:08b}", 0, CHAR_HEIGHT*i + TEXT_TOP, 1)
                oled.fill_rect(
                    BITS_LEFT + s.step * CHAR_WIDTH,
                    CHAR_HEIGHT*i + TEXT_TOP,
                    CHAR_WIDTH,
                    CHAR_HEIGHT,
                    1
                )
                oled.text(
                    f"{s.current_bit}",
                    BITS_LEFT + s.step * CHAR_WIDTH,
                    CHAR_HEIGHT*i + TEXT_TOP,
                    0
                )

            oled.show()


if __name__ == "__main__":
    IttyBitty().main()
