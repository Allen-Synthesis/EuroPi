from europi import *
from europi_script import EuroPiScript

from experimental.a_to_d import AnalogReaderDigitalWrapper

din1 = din
din2 = AnalogReaderDigitalWrapper(ain)

class Dfam(EuroPiScript):
    def __init__(self):
        super().__init__()

        self.reset_request = False
        self.advance_request = False

        # the current step of the sequence, [0, max_steps)
        # this is the NEXT step in DFAM's sequencer, so if the last LED
        # is lit up, current_step is 0
        self.current_step = 0

        # the maximum number of steps in the sequence
        self.max_steps = 8

        b1.handler(self.request_advance)
        din1.handler(self.request_advance)

        b2.handler(self.request_reset)
        din2.handler(self.request_reset)

    def request_reset(self):
        self.reset_request = True

    def request_advance(self):
        self.advance_request = True

    def reset(self):
        pulses = (8 - self.current_step) % 8
        self.current_step = 0
        for i in range(pulses):
            cv1.on()
            time.sleep(0.0001)
            cv1.off()
            time.sleep(0.0001)

    def advance(self):
        cv1.on()
        time.sleep(0.0001)
        cv1.off()

    def main(self):
        while True:
            din2.update()

            self.max_steps = max(int(k1.percent() * 8), 1)

            if self.reset_request:
                self.reset_request = False
                self.reset()

            if self.advance_request:
                self.advance_request = False
                self.current_step = (self.current_step + 1) % 8
                if self.current_step >= self.max_steps:
                    cv2.on()
                    self.reset()
                else:
                    cv2.off()

                self.advance()

            oled.centre_text(f"{self.current_step + 1}/{self.max_steps}")
