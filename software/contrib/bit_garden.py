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
try:
    # Local development
    from software.firmware import europi_config
    from software.firmware.europi import CHAR_HEIGHT, CHAR_WIDTH, OLED_WIDTH
    from software.firmware.europi import ain, din, k1, k2, oled, b1, b2, cvs
    from software.firmware.europi_script import EuroPiScript
    from software.firmware.experimental.a_to_d import AnalogReaderDigitalWrapper
    from software.firmware.experimental.custom_font import CustomFontDisplay
    from software.firmware.experimental.fonts import ubuntumono20

except ImportError:
    # Device import path
    from europi import *
    from europi_script import EuroPiScript
    from experimental.a_to_d import AnalogReaderDigitalWrapper
    from experimental.custom_font import CustomFontDisplay
    from experimental.fonts import ubuntumono20

from random import random, seed, randint
from time import sleep_ms, ticks_diff, ticks_ms

DEFAULT_SEQUENCE_LENGTH = 16
DEFAULT_SEED = 0x8F26
DEFAULT_PROBABILITIES = [0.92, 0.86, 0.64, 0.48, 0.32, 0.18]
MAX_STEPS = 32
LONG_PRESS_MS = 500

# Use the Custom Font wrapper for oled display.
oled = CustomFontDisplay()


class TriggerMode:
    TRIGGER = 1
    GATE = 2
    FLIP = 3


class Page:
    MAIN = 1
    EDIT_PROBABILITY = 2
    EDIT_SEED = 3


class Output:
    def __init__(self, cv, probability):
        self.cv = cv
        self.probability = probability
        self.pattern = [0] * MAX_STEPS
        self.build_pattern()

    def build_pattern(self):
        for i in range(MAX_STEPS):
            self.pattern[i] = random() < self.probability

    def trigger(self, step, mode):
        """Input trigger has gone high. Change the cv state based on mode for given step."""
        # If random is greater than the probability range, return without triggering.
        if not self.pattern[step]:
            return

        if mode == TriggerMode.FLIP:
            self.cv.toggle()
        else:
            self.cv.on()

    def trigger_off(self):
        """Input trigger has gone low. Turn off when in 'trigger' mode."""
        self.cv.off()


class SeedPacket:
    def __init__(self, seed, outputs, probabilities, mode):
        self.seed = seed
        self.mode = mode
        self.outputs = []
        for cv, prob in zip(outputs, probabilities):
            self.outputs.append(Output(cv, prob))

    def new_seed(self):
        """Seed the pseudo-random number generator with a new random seed and generate new patterns."""
        self.seed = randint(0,0xFFFF)
        seed(self.seed)
        for out in self.outputs:
            out.build_pattern()
        return self.seed

    def trigger(self, step):
        """Input trigger has gone high."""
        if self.mode == TriggerMode.GATE:
            for out in self.outputs:
                out.trigger_off()
            # Brief low period between gates.
            sleep_ms(5)

        for out in self.outputs:
            out.trigger(step, self.mode)

    def trigger_off(self):
        """Input trigger has gone low."""
        if self.mode != TriggerMode.TRIGGER:
            return

        for out in self.outputs:
            out.trigger_off()

    @property
    def probabilities(self):
        """Return the list of output probability between 0 and 1."""
        return [out.probability for out in self.outputs]

    def update_probability(self, index, prob):
        """Update the probability and pattern for the given output."""
        self.outputs[index].probability = prob
        self.outputs[index].build_pattern()


class BitGarden(EuroPiScript):
    def __init__(self):
        super().__init__()
        # Default initial state
        self.state = {
            "sequence_length": DEFAULT_SEQUENCE_LENGTH,
            "seed": DEFAULT_SEED,
            "mode": TriggerMode.TRIGGER,
            "probabilities": DEFAULT_PROBABILITIES,
        }
        self.state.update(self.load_state_json())

        # Class state variables
        self.step_counter = 0
        self.sequence_length = self.state["sequence_length"]
        self.packet = SeedPacket(self.state["seed"], cvs, self.state["probabilities"], self.state["mode"])
        self.pattern_index = 0

        # Private class instance variables
        self._page = Page.MAIN
        self._update_display = True
        self._prev_k1 = None
        self._prev_k2 = None
        self._seed_index = 0
        self._prob_index = 0

        # Attach IRQ Handlers
        din.handler(self.digital_rising)
        din.handler_falling(self.digital_falling)
        b1.handler_falling(self.b1_handler)
        b2.handler_falling(self.b2_handler)
        self.din2 = AnalogReaderDigitalWrapper(ain, cb_rising=self.digital2_rising)


    @classmethod
    def display_name(cls):
        return "Bit Garden"

    def save_state(self):
        """Save the current state variables as JSON."""
        self.state.update({
            "sequence_length": self.sequence_length,
            "seed": self.packet.seed,
            "mode": self.packet.mode,
            "probabilities": self.packet.probabilities,
        })
        self.save_state_json(self.state)

    def digital_rising(self):
        """Advance the pseudo-random sequence step counter."""
        self.step_counter = (self.step_counter + 1) % self.sequence_length
        self.packet.trigger(self.step_counter)
        self._update_display = True

    def digital_falling(self):
        """Tell the SeedPacket the digital input has gone low for Trigger mode."""
        self.packet.trigger_off()

    def digital2_rising(self):
        self.packet.new_seed()
        self._update_display = True

    def b1_handler(self):
        self._update_display = True

        # Short press  to toggle modde, long press to switch to edit probability page.
        if self._page == Page.MAIN:
            if ticks_diff(ticks_ms(), b1.last_pressed()) < LONG_PRESS_MS:
                self.toggle_mode()
            else:
                self._prev_k2 = None
                self._page = Page.EDIT_PROBABILITY

        # If on Edit Probability page, b1 press will return home.
        elif self._page == Page.EDIT_PROBABILITY:
            self._prob_index = (self._prob_index + 1) % 6

        # Change seed edit index.
        elif self._page == Page.EDIT_SEED:
            self._seed_index = (self._seed_index + 1) % 4

    def b2_handler(self):
        self._update_display = True

        if self._page == Page.MAIN:
            # Short press vs Long press
            if ticks_diff(ticks_ms(), b2.last_pressed()) < LONG_PRESS_MS:
                self.new_seed()
            else:
                self._temp_seed = self.packet.seed
                self._prev_k2 = None
                self._page = Page.EDIT_SEED

        elif self._page == Page.EDIT_PROBABILITY:
            self._page = Page.MAIN

        elif self._page == Page.EDIT_SEED:
            # If on Edit Seed page, b2 press will return home.
            self.packet.seed = self._temp_seed
            self._page = Page.MAIN

    def toggle_mode(self):
        """Change the current output mode."""
        if self.packet.mode == TriggerMode.TRIGGER:
            self.packet.mode = TriggerMode.GATE
        elif self.packet.mode == TriggerMode.GATE:
            self.packet.mode = TriggerMode.FLIP
        elif self.packet.mode == TriggerMode.FLIP:
            self.packet.mode = TriggerMode.TRIGGER
        self.save_state()

    def new_seed(self):
        """Generate a new seed to produce a new pseudo-random trigger sequence."""
        self.state.update({"seed": self.packet.new_seed()})
        self.save_state()

    def update_sequence_length(self):
        """Check if the knob has changed value and update the sequence length accordingly."""
        read = k1.range(MAX_STEPS-1) + 2  # range of 2..MAX_STEPS
        if read != self._prev_k1:
            self._prev_k1 = read
            self.sequence_length = read
            self.step_counter = min(self.step_counter, self.sequence_length)
            self._update_display = True

    def update_selected_pattern(self):
        """Change which pattern is currently displayed."""
        index = k2.range(len(self.packet.outputs))
        if index == self._prev_k2 or self._prev_k2 is None:
            self._prev_k2 = index
            return
        self._prev_k2 = index
        self.pattern_index = index
        self._update_display = True

    def update_seed_digit(self):
        """Update the seed digit for selected digit index."""
        value = k2.range(16)
        if value == self._prev_k2 or self._prev_k2 is None:
            self._prev_k2 = value
            return
        self._prev_k2 = value

        if self._seed_index == 0:
            position = 0x1000
            clear = 0x0FFF
        elif self._seed_index == 1:
            position = 0x0100
            clear = 0xF0FF
        elif self._seed_index == 2:
            position = 0x0010
            clear = 0xFF0F
        elif self._seed_index == 3:
            position = 0x0001
            clear = 0xFFF0
        self._temp_seed = (self._temp_seed & clear) + (int(position) * value)
        self._update_display = True

    def update_selected_prob(self):
        value = k2.range(100)
        if value == self._prev_k2 or self._prev_k2 is None:
            self._prev_k2 = value
            return
        self._prev_k2 = value
        self.packet.update_probability(self._prob_index, k2.percent())
        self._update_display = True

    def mode_text(self):
        """Return the display text for current Trigger Mode."""
        if self.packet.mode == TriggerMode.TRIGGER:
            return "TRIG"
        elif self.packet.mode == TriggerMode.GATE:
            return "GATE"
        elif self.packet.mode == TriggerMode.FLIP:
            return "FLIP"

    def update_display(self):
        """If UI state has changed, update the display."""
        if not self._update_display:
            return
        self._update_display = False

        oled.fill(0)
        if self._page == Page.MAIN:
            self.display_main(self.packet.outputs[self.pattern_index].pattern)
        elif self._page == Page.EDIT_PROBABILITY:
            self.display_edit_probability()
        elif self._page == Page.EDIT_SEED:
            self.display_edit_seed()
        oled.show()

        return

    def display_main(self, pattern):
        start = 2
        top = 0
        left = start
        boxSize = 8
        trigSize = 2
        tpadding = 3
        lpadding = 3
        wrap = 8

        for i in range(self.sequence_length):
            _top = top
            if self.sequence_length <= 8:
                _top += 8
            elif self.sequence_length <= 16:
                _top += 6
                tpadding = 2
            elif self.sequence_length <= 24:
                _top += 4
                tpadding = 1
            else:
                tpadding = 0

            # Step boxes
            oled.rect(left, _top, boxSize, boxSize, 1)

            # Fill current step
            if i == self.step_counter:
                oled.rect(left, _top, boxSize, boxSize, 1, 1)

            # Trigger indicator inside the step box
            if pattern[i]:
                if (i == self.step_counter):
                    oled.rect(left+2, _top+2, trigSize+2, trigSize+2, 0, 1)
                else:
                    oled.rect(left+3, _top+3, trigSize, trigSize, 1, 1)

            left += boxSize + lpadding

            # Wrap the box draw cursor if we hit wrap count.
            if (i+1) % wrap == 0:
                top += boxSize + tpadding
                left = start

        oled.text(f"CV:{self.pattern_index+1}", OLED_WIDTH-(CHAR_WIDTH*4), 0, 1)
        oled.text(f"{self.mode_text()}", OLED_WIDTH-(CHAR_WIDTH*4), CHAR_HEIGHT, 1)
        oled.text(f"{self.packet.seed:04X}", OLED_WIDTH-(CHAR_WIDTH*4), CHAR_HEIGHT*2, 1)
        oled.text(f"{self.step_counter+1:>2}/{self.sequence_length:>2} ", OLED_WIDTH-(5*CHAR_WIDTH), CHAR_HEIGHT*3, 1)

    def display_edit_seed(self):
        """Display the editable seed and digit indicator."""
        start = 40
        top = 6
        charw = ubuntumono20.max_width()
        charh = ubuntumono20.height()
        oled.text(f"{self._temp_seed:04X}", start, top, font=ubuntumono20)
        oled.hline(start + (self._seed_index * charw), top+charh, charw, 1)

    def display_edit_probability(self):
        """Display each output probability as a vertical filled bar with edit indicator."""
        top = 0
        left = 16
        barWidth = 10
        barHeight = 30
        padding = 8

        for i, prob in enumerate(self.packet.probabilities):
            # Draw output probability bar.
            oled.rect(left, top, barWidth, barHeight, 1)

            # Fill current bar probability.
            probFill = int(float(barHeight) * prob)
            probTop = top + barHeight - probFill
            oled.rect(left, probTop, barWidth, probFill, 1, 1)

            # Show selected output.
            if i == self._prob_index:
                oled.text(">", left - CHAR_WIDTH, probTop, 1)

            left += barWidth + padding

    def main(self):
        """Main loop for detecing knob changes and updating display."""
        while True:
            self.din2.update()
            # Current page determines which input methods is called.
            if self._page == Page.MAIN:
                self.update_sequence_length()
                self.update_selected_pattern()
            elif self._page == Page.EDIT_PROBABILITY:
                self.update_selected_prob()
            elif self._page == Page.EDIT_SEED:
                self.update_seed_digit()
            self.update_display()


if __name__ == "__main__":
    BitGarden().main()
