# Copyright 2025 Allen Synthesis
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
step_size_knob = k2

TRIGGER_DURATION = 0.0001


class DfamController(EuroPiScript):
    def __init__(self):
        super().__init__()

        self.reset_request = False
        self.advance_request = False

        # the current step within our internal sequencer
        self.current_step = 0

        # the maximum number of steps in the sequence
        self.max_steps = 8

        # the number of advances we output per input step
        self.step_size = 1

        # the current step on DFAM's sequencer
        self.dfam_sync_counter = 0

        clock_input.handler(self.request_advance)
        advance_button.handler(self.request_advance)

        reset_input.handler(self.request_reset)
        reset_button.handler(self.request_reset)

    def request_reset(self):
        self.reset_request = True

    def request_advance(self):
        self.advance_request = True

    def reset(self):
        pulses = (8 - self.dfam_sync_counter) % 8
        self.current_step = 0
        self.dfam_sync_counter = 0
        for _ in range(pulses):
            advance_output.on()
            time.sleep(TRIGGER_DURATION)
            advance_output.off()
            time.sleep(TRIGGER_DURATION)

    def advance(self):
        for _ in range(self.step_size):
            advance_output.on()
            time.sleep(TRIGGER_DURATION)
            advance_output.off()
            time.sleep(TRIGGER_DURATION)
        self.dfam_sync_counter = (self.dfam_sync_counter + self.step_size) % 8

    def main(self):
        render_needed = True

        while True:
            reset_input.update()  # a-to-d wrapper, so we need to poll it!

            new_steps = max(int(sequence_length_knob.percent() * 15), 1)
            if new_steps != self.max_steps:
                render_needed = True
                self.max_steps = new_steps

            new_size = max(int(step_size_knob.percent() * 7), 1)
            if new_size != self.step_size:
                render_needed = True
                self.step_size = new_size

            if self.reset_request:
                render_needed = True
                self.reset_request = False
                self.reset()

            if self.advance_request:
                render_needed = True
                self.advance_request = False
                self.current_step += 1
                if self.current_step >= self.max_steps:
                    end_of_sequence_output.on()
                    self.reset()
                else:
                    end_of_sequence_output.off()

                self.advance()

            if render_needed:
                render_needed = False
                oled.centre_text(f"{self.current_step + 1}/{self.max_steps}\nx{self.step_size}")


if __name__ == "__main__":
    DfamController().main()
