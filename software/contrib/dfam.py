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
from experimental.math_extras import rescale

clock_input = din
reset_input = AnalogReaderDigitalWrapper(ain)
advance_button = b1
reset_button = b2

advance_output = cv1
end_of_sequence_output = cv2

sequence_length_knob = k1
step_size_knob = k2

# Duration of triggers sent to DFAM to advance
# based on experimentation, 1ms is sufficient and doesn't produce
# audio artefacts when burst-advancing
TRIGGER_DURATION = 0.001

# What length of sequences can we output?
# We allow up to DFAM's max length of 8
MIN_SEQUENCE_LEN = 1
MAX_SEQUENCE_LEN = 8

# How many steps does DFAM advance with each trigger
# This is all modular, so setting to 7 will advance 1 space backwards
MIN_STEP = 1
MAX_STEP = 7

# DFAM has an 8-step sequencer
DFAM_SEQUENCER_LENGTH = 8

# The size of the circles we draw on the UI
CIRCLE_SIZE = 4

# Screen colours
BLACK = 0
WHITE = 1

# Circle fill constants
YES_FILL = -1
NO_FILL = 0


class DfamController(EuroPiScript):
    def __init__(self):
        super().__init__()

        self.reset_request = False
        self.advance_request = False

        # the current step within our internal sequencer
        self.current_step = 0

        # the maximum number of steps in the sequence
        self.max_steps = MAX_SEQUENCE_LEN

        # the number of advances we output per input step
        self.step_size = MIN_STEP

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

    def reset(self, force_trigger=False):
        pulses = (DFAM_SEQUENCER_LENGTH - self.dfam_sync_counter) % DFAM_SEQUENCER_LENGTH
        if force_trigger and pulses == 0:
            pulses = DFAM_SEQUENCER_LENGTH
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
        self.dfam_sync_counter = (self.dfam_sync_counter + self.step_size) % DFAM_SEQUENCER_LENGTH

    def main(self):
        render_needed = True

        while True:
            reset_input.update()  # a-to-d wrapper, so we need to poll it!

            new_steps = int(rescale(sequence_length_knob.percent(), 0, 1, MIN_SEQUENCE_LEN, MAX_SEQUENCE_LEN))
            if new_steps != self.max_steps:
                render_needed = True
                self.max_steps = new_steps

            new_size = int(rescale(step_size_knob.percent(), 0, 1, MIN_STEP, MAX_STEP))
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
                    if self.max_steps == 1:
                        self.advance()

                    end_of_sequence_output.on()
                    self.reset(force_trigger=True)
                else:
                    end_of_sequence_output.off()
                    self.advance()

            if render_needed:
                render_needed = False
                oled.fill(0)
                oled.centre_text(f"{self.current_step + 1}/{self.max_steps}\nx{self.step_size}\n", auto_show=False, clear_first=False)

                for i in range(DFAM_SEQUENCER_LENGTH):
                    # the 0th LED is actually the last one, so the pattern should be shifted 1 to the left
                    if i == (self.dfam_sync_counter - 1) % DFAM_SEQUENCER_LENGTH:
                        fill = YES_FILL
                    else:
                        fill = NO_FILL
                    oled.ellipse(
                        i * OLED_WIDTH // DFAM_SEQUENCER_LENGTH + CIRCLE_SIZE,
                        OLED_HEIGHT - CIRCLE_SIZE - 1,
                        CIRCLE_SIZE,
                        CIRCLE_SIZE,
                        WHITE,
                        fill
                    )

                oled.show()


if __name__ == "__main__":
    DfamController().main()
