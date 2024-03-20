try:
    # Local development
    from software.firmware.europi import CHAR_HEIGHT
    from software.firmware.europi import din, k1, k2, oled, b1, b2, cvs
    from software.firmware.europi_script import EuroPiScript
except ImportError:
    # Device import path
    from europi import *
    from europi_script import EuroPiScript

from random import random, seed
from time import time_ns


DEFAULT_SEQUENCE_LENGTH = 16
DEFAULT_SEED = 0x8F26
DEFAULT_PROBABILITIES = [0.92, 0.86, 0.64, 0.48, 0.32, 0.18]


class TriggerMode:
    TRIGGER = 1
    GATE = 2
    FLIP = 3


class Output:
    def __init__(self, cv, probability, mode):
        self.cv = cv
        self.probability = probability
        self.mode = mode

    def trigger(self):
        """Input trigger has gone high. Change the cv state based on mode."""
        if self.mode == TriggerMode.GATE:
            self.cv.off()

        # If random is greater than the probability range, return without triggering.
        if random() > self.probability:
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
        """Seed the pseudo-random number generator with a new random seed."""
        seed(time_ns())
        self.seed = int(random() * 65535.)
        seed(self.seed)
        return self.seed
    
    def reseed(self):
        """Restart the pseudo-random number generator."""
        seed(self.seed)
        return self.seed

    def trigger(self):
        """Input trigger has gone high."""
        for out in self.outputs:
            out.trigger()

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

        # Private class instance variables
        self._update_display = True
        self._prev_k1 = DEFAULT_SEQUENCE_LENGTH

        # Attach IRQ Handlers
        din.handler(self.digital_rising)
        din.handler_falling(self.digital_falling)
        b1.handler(self.toggle_mode)
        b2.handler(self.new_seed)


    @classmethod
    def display_name(cls):
        return "Bit Garden"
    
    def save_state(self):
        """Save the current state variables as JSON."""
        # Don't save if it has been less than 5 seconds since last save.
        if self.last_saved() < 5000:
            return

        self.state.update({
            "sequence_length": self.sequence_length,
            "seed": self.packet.seed,
            "mode": self.packet.mode,
            "probabilities": self.packet.probabilities,
        })
        self.save_state_json(self.state)

    def digital_rising(self):
        """Advance the pseudo-random sequence step counter."""
        # When step count wraps, reset step count and reseed.
        self.step_counter = (self.step_counter + 1) % self.sequence_length
        if self.step_counter == 0:
            self.packet.reseed()

        self.packet.trigger()

        self._update_display = True

    def digital_falling(self):
        """Tell the SeedPacket the digital input has gone low for Trigger mode."""
        self.packet.trigger_off()

    def toggle_mode(self):
        """Change the current output mode."""
        if self.packet.mode == TriggerMode.TRIGGER:
            self.packet.set_mode(TriggerMode.GATE)
        elif self.packet.mode == TriggerMode.GATE:
            self.packet.set_mode(TriggerMode.FLIP)
        elif self.packet.mode == TriggerMode.FLIP:
            self.packet.set_mode(TriggerMode.TRIGGER)
        self._update_display = True
        self.save_state()

    def new_seed(self):
        """Generate a new seed to produce a new pseudo-random trigger sequence."""
        self.state.update({"seed": self.packet.new_seed()})
        self.save_state()
        self._update_display = True
    
    def update_sequence_length(self):
        """Check if the knob has changed value and update the sequence length accordingly."""
        read = k1.range(31) + 2  # range of 2..32
        if read != self._prev_k1:
            self._prev_k1 = read
            self.sequence_length = read
            self.step_counter = min(self.step_counter, self.sequence_length)
            self._update_display = True
            self.save_state()

    def mode_text(self):
        """Return the display text for current Trigger Mode."""
        if self.packet.mode == TriggerMode.TRIGGER:
            return "TRIGGER"
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
        padding = 2
        x = padding
        y = padding

        oled.text(f"Mode: {self.mode_text()}", x, y, 1)
        y += CHAR_HEIGHT
        oled.text(f"Seed: {self.packet.seed:04X}", x, y, 1)
        y += CHAR_HEIGHT
        oled.text(f"Step: {self.step_counter+1:>2}/{self.sequence_length:>2} ", x, y, 1)

        oled.show()

    def main(self):
        """Main loop for detecing knob changes and updating display."""
        while True:
            self.update_sequence_length()
            self.update_display()


if __name__ == "__main__":
    BitGarden().main()
