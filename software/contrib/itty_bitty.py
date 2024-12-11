"""
Two 8-step trigger, gate & CV sequencers based on the binary representation of an 8-bit number
"""

from europi import *
from europi_script import EuroPiScript
import time


class BittySequence:
    """
    A container class for one sequencer
    """
    def __init__(self, button_in, trigger_out, gate_out, cv_out):
        """
        Create a new sequencer

        @param button_in  The button the user can press to manually advance the sequence
        @param trigger_out  The CV output for the trigger signal
        @param gate_out  The CV output for the gate signal
        @param cv_out  The CV output for the CV signal
        """
        button_in.handler(self.advance)
        button_in.handler_falling(self.trigger_off)

        self.trigger_out = trigger_out
        self.gate_out = gate_out
        self.cv_out = cv_out

        # the 0-255 value that's the basis for our sequence
        self.sequence_n = 0

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
        n_prime = ((self.sequence_n << self.step) & 0xff) | ((self.sequence_n & 0xff) >> (8 - self.step))
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
        if n == self.sequence_n:
            return

        self.sequence_n = n


class IttyBitty(EuroPiScript):
    def __init__(self):
        super().__init__()

        self.sequencers = [
            BittySequence(b1, cv1, cv2, cv3),
            BittySequence(b2, cv4, cv5, cv6),
        ]

        @din.handler
        def on_clock_rise():
            for s in self.sequencers:
                s.advance()

        @din.handler_falling
        def on_clock_fall():
            for s in self.sequencers:
                s.trigger_off()

    def main(self):
        while True:
            n1 = k1.read_position(steps=256, samples=200)
            n2 = k2.read_position(steps=256, samples=200)

            self.sequencers[0].change_sequence(n1)
            self.sequencers[1].change_sequence(n2)

            display_text = ""
            for s in self.sequencers:
                n_prime = ((s.sequence_n << s.step) & 0xff) | ((s.sequence_n & 0xff) >> (8 - s.step))
                display_text = display_text + f"\n{s.sequence_n:3} {n_prime:08b}"
                if s.output_dirty:
                    s.apply_output()

            display_text = display_text.strip()
            oled.centre_text(display_text)


if __name__ == "__main__":
    IttyBitty().main()
