from europi import *
from europi_script import EuroPiScript

from experimental.a_to_d import AnalogReaderDigitalWrapper

clock_input = din
reset_input = AnalogReaderDigitalWrapper(ain)
advance_button = b1
reset_button = b2

advance_output = cv1
end_of_sequence_output = cv2

sequence_length_knob = k1


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

        clock_input.handler(self.request_advance)
        advance_button.handler(self.request_advance)

        reset_input.handler(self.request_reset)
        reset_button.handler(self.request_reset)

    def request_reset(self):
        self.reset_request = True

    def request_advance(self):
        self.advance_request = True

    def reset(self):
        pulses = (8 - self.current_step) % 8
        self.current_step = 0
        for i in range(pulses):
            advance_output.on()
            time.sleep(0.0001)
            advance_output.off()
            time.sleep(0.0001)

    def advance(self):
        advance_output.on()
        time.sleep(0.0001)
        advance_output.off()

    def main(self):
        while True:
            reset_input.update()  # a-to-d wrapper, so we need to poll it!

            self.max_steps = max(int(sequence_length_knob.percent() * 15), 1)

            if self.reset_request:
                self.reset_request = False
                self.reset()

            if self.advance_request:
                self.advance_request = False
                self.current_step += 1
                if self.current_step >= self.max_steps:
                    end_of_sequence_output.on()
                    self.reset()
                else:
                    end_of_sequence_output.off()

                self.advance()

            oled.centre_text(f"{self.current_step + 1}/{self.max_steps}")
