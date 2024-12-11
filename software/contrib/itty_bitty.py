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

        # shift the sequence
        n_prime = ((self.binary_sequence << self.step) & 0xff) | ((self.binary_sequence & 0xff) >> (8 - self.step))
        current_bit = n_prime & 0x01

        if current_bit:
            self.trigger_out.on()
            self.gate_out.on()
        else:
            self.trigger_out.off()
            self.gate_out.off()

        self.cv_out.voltage(europi_config.MAX_OUTPUT_VOLTAGE * n_prime / 255)

        self.output_dirty = False

    def change_sequence(self, n):
        self.sequence_n = n

        if self.use_gray_encoding:
            # convert the number from traditional binary to its gray encoding equivalent
            n = (n & 0xff) ^ ((n & 0xff) >> 1)
        else:
            n = n & 0xff

        self.binary_sequence = n


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
            )
        ]

    def main(self):
        while True:
            n1 = k1.read_position(steps=256, samples=200)
            n2 = k2.read_position(steps=256, samples=200)

            self.sequencers[0].change_sequence(n1)
            self.sequencers[1].change_sequence(n2)

            oled.fill(0)
            for i in range(len(self.sequencers)):
                s = self.sequencers[i]
                n_prime = ((s.binary_sequence << s.step) & 0xff) | ((s.binary_sequence & 0xff) >> (8 - s.step))
                oled.text(f"{s.sequence_n:5} {n_prime:08b}", 0, CHAR_HEIGHT*i + CHAR_HEIGHT, 1)
                if s.output_dirty:
                    s.apply_output()

            # draw a box around the active bits
            oled.rect(
                CHAR_WIDTH * 13,
                0,
                CHAR_WIDTH,
                OLED_HEIGHT - 1,
                1
            )
            oled.show()


if __name__ == "__main__":
    IttyBitty().main()
