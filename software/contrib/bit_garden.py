try:
    # Local development
    from software.firmware.europi import CHAR_HEIGHT, CHAR_WIDTH, OLED_WIDTH
    from software.firmware.europi import din, k1, k2, oled, b1, b2, cvs
    from software.firmware.europi_script import EuroPiScript
    from software.firmware.experimental import custom_font, freesans20


except ImportError:
    # Device import path
    from europi import *
    from experimental import custom_font, freesans20
    from europi_script import EuroPiScript

from random import random, seed
from time import ticks_diff, ticks_ms


DEFAULT_SEQUENCE_LENGTH = 16
DEFAULT_SEED = 0x8F26
DEFAULT_PROBABILITIES = [0.92, 0.86, 0.64, 0.48, 0.32, 0.18]
MAX_STEPS = 32
LONG_PRESS_MS = 500

# Use the Custom Font wrapper for oled display.
oled = custom_font.oled


class TriggerMode:
    TRIGGER = 1
    GATE = 2
    FLIP = 3

class Page:
    MAIN = 1
    EDIT_PROBABILITY = 2
    EDIT_SEED = 3


class Output:

    def __init__(self, cv, probability, mode):
        self.cv = cv
        self.probability = probability
        self.mode = mode
        self.pattern = [0] * MAX_STEPS
        self.build_pattern()

    def build_pattern(self):
        for i in range(MAX_STEPS):
            self.pattern[i] = random() < self.probability

    def trigger(self, step):
        """Input trigger has gone high. Change the cv state based on mode for given step."""
        if self.mode == TriggerMode.GATE:
            self.cv.off()

        # If random is greater than the probability range, return without triggering.
        if not self.pattern[step]:
            return

        if self.mode == TriggerMode.FLIP:
            self.cv.toggle()
        else:
            self.cv.on()

    def trigger_off(self):
        """Input trigger has gone low. Turn off when in 'trigger' mode."""
        if self.mode == TriggerMode.TRIGGER:
           self.cv.off()


class SeedPacket:
    def __init__(self, seed, outputs, probabilities, mode):
        self.seed = seed
        self.mode = mode
        self.outputs = []
        for cv, prob in zip(outputs, probabilities):
            self.outputs.append(Output(cv, prob, mode))

    def new_seed(self):
        """Seed the pseudo-random number generator with a new random seed and generate new patterns."""
        self.seed = int(random() * 65535.)
        seed(self.seed)
        for out in self.outputs:
            out.build_pattern()
        return self.seed
    
    def trigger(self, step):
        """Input trigger has gone high."""
        for out in self.outputs:
            out.trigger(step)

    def trigger_off(self):
        """Input trigger has gone low."""
        for out in self.outputs:
            out.trigger_off()
    
    def set_mode(self, mode):
        """Set the output mode."""
        self.mode = mode
        for out in self.outputs:
            out.mode = mode

    @property
    def probabilities(self):
        """Return the list of output probability between 0 and 1."""
        return [out.probability for out in self.outputs]


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
        self._prev_k1 = DEFAULT_SEQUENCE_LENGTH
        self._prev_k2 = 0

        # Attach IRQ Handlers
        din.handler(self.digital_rising)
        din.handler_falling(self.digital_falling)
        b1.handler_falling(self.b1_handler)
        b2.handler_falling(self.b2_handler)

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

    def b1_handler(self):
        self._update_display = True
        # If on Edit Probability page, b1 press will return home.
        if self._page == Page.EDIT_PROBABILITY:
            self._page = Page.MAIN
            return

        # Short press vs Long press
        if ticks_diff(ticks_ms(), b1.last_pressed()) < LONG_PRESS_MS:
            self.toggle_mode()
        else:
            self._page = Page.EDIT_PROBABILITY

    def b2_handler(self):
        self._update_display = True
        # If on Edit Seed page, b2 press will return home.
        if self._page == Page.EDIT_SEED:
            self._page = Page.MAIN
            return
        
        # Short press vs Long press
        if ticks_diff(ticks_ms(), b2.last_pressed()) < LONG_PRESS_MS:
            self.new_seed()
        else:
            self._page = Page.EDIT_SEED

    def toggle_mode(self):
        """Change the current output mode."""
        if self.packet.mode == TriggerMode.TRIGGER:
            self.packet.set_mode(TriggerMode.GATE)
        elif self.packet.mode == TriggerMode.GATE:
            self.packet.set_mode(TriggerMode.FLIP)
        elif self.packet.mode == TriggerMode.FLIP:
            self.packet.set_mode(TriggerMode.TRIGGER)
        self.save_state()
    
    def new_seed(self):
        """Generate a new seed to produce a new pseudo-random trigger sequence."""
        self.state.update({"seed": self.packet.new_seed()})
        self.save_state()
    
    def edit_seed(self):
        self._page = Page.EDIT_PROBABILITY

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
        if index != self._prev_k2:
            self._prev_k2 = index
            self.pattern_index = index
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
            self.display_pattern(self.packet.outputs[self.pattern_index].pattern)
        elif self._page == Page.EDIT_PROBABILITY:
            pass
        elif self._page == Page.EDIT_SEED:
            self.display_edit_seed()
        oled.show()

        return

    def display_pattern(self, pattern):
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
        oled.text(f"{self.packet.seed:04X}", 32, 6, font=freesans20)

    def main(self):
        """Main loop for detecing knob changes and updating display."""
        while True:
            # Current page determines which input methods is called.
            if self._page == Page.MAIN:
                self.update_sequence_length()
                self.update_selected_pattern()
            elif self._page == Page.EDIT_PROBABILITY:
                pass
            elif self._page == Page.EDIT_SEED:
                pass
            self.update_display()


if __name__ == "__main__":
    BitGarden().main()


