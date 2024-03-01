"""
 A script meant to recreate the Music Thing Modular Turning Machine Random Sequencer as faithfully 
 as possible on the EuroPi hardware using bit shift operations to mimic the analog shift register.

din - clock
ain - cv control over the big knob, added to the knobs value
k1 - the big knob (probability that the sequence changes)
k2 - output scale (0-10v)  or sequence length (2-16 steps)
b1 - write (clear bits) (or config value write_value)
b2 - change k2 function
cv1 - pulse 1 (or config value cv1_pulse_bit)
cv2 - pulse 2 (or config value cv2_pulse_bit)
cv3 - pulse 4 (or config value cv3_pulse_bit)
cv4 - pulse cv1 & cv2
cv5 - pulse cv2 & cv3
cv6 - sequence out

If you'd like to use different bits for the pulse outputs you can update the `CVX_PULSE_BIT` 
constants below.

The length, scale, and bit pattern are saved whenever the knob 2 state is changed, or when the user
exits to the menu.
"""
from random import getrandbits, randint
from time import sleep


try:
    from firmware import europi
    from firmware.europi import clamp, MAX_UINT16
    from firmware.europi import din, ain, k1, k2, b1, b2, cv1, cv2, cv3, cv4, cv5, cv6, oled
    from firmware.experimental.knobs import KnobBank
except ImportError:
    import europi
    from europi import clamp, MAX_UINT16
    from europi import din, ain, k1, k2, b1, b2, cv1, cv2, cv3, cv4, cv5, cv6, oled
    from experimental.knobs import KnobBank

import configuration
from europi_script import EuroPiScript

INT_MAX_8 = 0xFF
DEFAULT_BIT_COUNT = 16
MAX_OUTPUT_VOLTAGE = europi.MAX_OUTPUT_VOLTAGE


class TuringMachine:
    """A class meant to recreate the Music Thing Modular Turning Machine Random Sequencer as faithfully as possible in
    micropython using bit shift operations to mimic the TM's analog shift register.

    The `TuringMachine` class keeps its state in several internal member variables which are accessed via property
    variables. See `flip_probability`, `scale`, `length` and `write`. users of the class can modify these
    variables in order to configure the TM's behavior. In many cases script authors will want to tie one of these
    variables to a hardware UI element, for example, assigning the `flip_probability` to a knob. In this case clients
    can override the corresponding `*_getter` function. For example, to tie the write switch to button 1::

        tm = TuringMachine()

        def write(self):
          return b1.value()

        tm.write_getter = write

    This form allows clients to override where the `TuringMachine` obtains some of its state variables without
    explicitly sub-classing the `TuringMachine` class. See `EuroPiTuringMachine` for a more detailed example.
    """

    def __init__(
        self,
        bit_count=DEFAULT_BIT_COUNT,
        max_output_voltage=MAX_OUTPUT_VOLTAGE,
        clear_on_write=True,
        flip_probability=0,
        scale=MAX_OUTPUT_VOLTAGE,
        length=DEFAULT_BIT_COUNT,
    ):
        """Create a new TuringMachine with a shift register of the specified bit count. Default is 16, minimum is 8.
        The maximum output voltage is also configurable and defaults to `europi.MAX_OUTPUT_VOLTAGE`
        """

        if bit_count < 8:
            raise ValueError(f"Specified bit_count ({bit_count}) is less than the minimum (8).")
        self.bit_count = bit_count
        self.bits = getrandbits(self.bit_count)
        self._flip_probability = flip_probability
        self.max_output_voltage = max_output_voltage
        self.clear_on_write = clear_on_write
        self._scale = scale
        self._length = length
        self._write = False

        self.flip_probability_getter = lambda: self._flip_probability
        self.scale_getter = lambda: self._scale
        self.length_getter = lambda: self._length
        self.write_getter = lambda: self._write
        self.step_handler = lambda: None

    def _rotate_bits(self):
        self.bits = ((self.bits << 1) % (1 << self.bit_count)) | (
            (self.bits >> (self.length - 1)) & 1
        )

    def step(self):
        """Move the turing machine to its next state based on its current state. Parameters that affect the next state
        include: `flip_probability`, `length`, `write`, and, the internal bit register.

        Typically this method would be called in response to a clock tick.
        """
        self._rotate_bits()
        if self.write:
            if self.clear_on_write:
                self.bits = self.bits & ~1
            else:
                self.bits = self.bits | (1 << 0)

        if randint(0, 99) < self.flip_probability:
            self.bits = self.bits ^ 0b1
        self.step_handler()

    def get_8_bits(self):
        """Returns the least significant eight bits from the internal bit register, which are the same bits used to
        determine the voltage returned by `get_voltage()`. This method is useful when displaying the current state in a
        UI."""
        return self.bits & 0xFF

    def get_bit(self, i):
        """Returns the bit at the specified index. This method exists to support the Pulses Expander functionality."""
        return self.bits >> i & 1

    def get_bit_and(self, *args):
        """Returns the result of a bitwise and of the bits at the specified indexes. This method exists to support the
        Pulses Expander functionality."""
        result = 1
        for i in args:
            result = result & self.get_bit(i)
        return result

    def get_voltage(self):
        """Returns the voltage described by the eight least significant bits of the internal bit register, scaled by the
        current `scale` factor."""
        return self.get_8_bits() / INT_MAX_8 * self.scale

    @property
    def flip_probability(self):
        """Returns the probability that the most significant bit will be flipped when it is rotated into the least
        significant bit's position. This translates to the probability that the sequence will change. The
        flip_probability is represented as an integer in the range [0, 100].
        """
        return self.flip_probability_getter()

    @flip_probability.setter
    def flip_probability(self, probability: int):
        """Set the flip probability as an integer in the range [0, 100]."""
        if probability < 0 or probability > 100:
            raise ValueError(
                f"Probability of {probability} is outside the expected range of [0,100]"
            )
        self._flip_probability = probability

    @property
    def scale(self):
        """Returns the current scaling factor, used to reduce the range of the output voltage to something lower than
        the `max_output_voltage`. Represented by a float in the range [0, `max_output_voltage`]"""
        return self.scale_getter()

    @scale.setter
    def scale(self, scale):
        """Set the scale factor as a float in the range [0, `max_output_voltage`]"""
        if scale < 0 or scale > self.max_output_voltage:
            raise ValueError(
                f"Scale of {scale} is outside the expected range of [0,{self.max_output_voltage}]"
            )
        self._scale = scale

    @property
    def length(self):
        """Returns the length of the current sequence as an integer in the range of [2, `bit_count`]"""
        return self.length_getter()

    @length.setter
    def length(self, length):
        """Sets the length of the current sequence as an integer in the range of [2, `bit_count`]"""
        if length < 2 or length > self.bit_count:
            raise ValueError(
                f"Length of {length} is outside the expected range of [2,{self.bit_count}]"
            )
        self._length = length

    @property
    def write(self):
        """Returns the current value of the 'write switch'. When true the least significant bit will be cleared during
        rotation, regardless of the `flip_probability`. This allows for real-time user manipulation of the sequence.
        """
        return self.write_getter()

    @write.setter
    def write(self, value: bool):
        """Set the state of the 'write switch'. `True` means that the least significant bit will be cleared."""
        self._write = value


class EuroPiTuringMachine(EuroPiScript):
    def __init__(self, bit_count=DEFAULT_BIT_COUNT, max_output_voltage=MAX_OUTPUT_VOLTAGE):
        super().__init__()

        self.LENGTH_CHOICES = [2, 3, 4, 5, 6, 8, 12, 16]  # TODO: vary based on bit_count?
        initial_scale_percent = 0.5  # TODO: load from saved state
        initial_length = 8  # TODO: load from saved state

        self.tm = TuringMachine(
            bit_count=bit_count,
            max_output_voltage=max_output_voltage,
            clear_on_write=self.config["write_value"] == 0,
            length=initial_length,
            scale=MAX_OUTPUT_VOLTAGE * initial_scale_percent,
        )
        self.tm.flip_probability_getter = self.flip_probability
        self.tm.scale_getter = self.scale
        self.tm.length_getter = self.length
        self.tm.write_getter = self.write
        self.tm.step_handler = self.step_handler
        self.request_next_k2 = False
        self.kb2 = (
            KnobBank.builder(k2)
            .with_disabled_knob()
            .with_locked_knob("scale", initial_percentage_value=initial_scale_percent)
            .with_locked_knob(
                "length",
                initial_percentage_value=(self.LENGTH_CHOICES.index(initial_length) * 2 + 1)
                / (len(self.LENGTH_CHOICES) * 2),
            )
            .build()
        )

        self.cv1_pulse_bit = self.config["cv1_pulse_bit"]
        self.cv2_pulse_bit = self.config["cv2_pulse_bit"]
        self.cv3_pulse_bit = self.config["cv3_pulse_bit"]

        @din.handler
        def clock():
            self.tm.step()

        @b2.handler_falling
        def request_next_k2_mode():
            self.request_next_k2 = True

    def next_k2_mode(self):
        if self.kb2.current_name == "scale":
            self.tm.scale = self.scale()
        elif self.kb2.current_name == "length":
            self.tm.length = self.length()
        self.kb2.next()
        self.request_next_k2 = False

    def step_handler(self):
        cv1.value(self.tm.get_bit(self.cv1_pulse_bit))
        cv2.value(self.tm.get_bit(self.cv2_pulse_bit))
        cv3.value(self.tm.get_bit(self.cv3_pulse_bit))
        cv4.value(self.tm.get_bit_and(self.cv1_pulse_bit, self.cv2_pulse_bit))
        cv5.value(self.tm.get_bit_and(self.cv2_pulse_bit, self.cv3_pulse_bit))
        cv6.voltage(self.tm.get_voltage())

    def flip_probability(self):
        return clamp(int(round(1 - k1.percent() - ain.percent(), 2) * 100), 0, 100)

    def scale(self):
        if self.kb2.current_name == "scale":
            return self.kb2.scale.percent() * self.tm.max_output_voltage
        else:
            return self.tm._scale

    def length(self):
        if self.kb2.current_name == "length":
            return self.kb2.length.choice(self.LENGTH_CHOICES)
        else:
            return self.tm._length

    def write(self):
        return b1.value()

    @staticmethod
    def bits_as_led_line(oled, bits):
        bit_str = f"{bits:08b}"
        x_pos = 0
        width = int(europi.OLED_WIDTH / 8)
        for c in bit_str:
            if c == "1":
                oled.hline(x_pos, 0, width - 1, 1)
            x_pos += width

    @classmethod
    def display_name(cls):
        return "Turing Machine"

    @classmethod
    def config_points(cls):
        bitcount_range = range(1, min(DEFAULT_BIT_COUNT, 8))

        return [
            configuration.choice(name="write_value", choices=[0, 1], default=0),
            # simulate the actual bits available in the pulses expander (1-7)
            configuration.integer(name="cv1_pulse_bit", range=bitcount_range, default=1),
            configuration.integer(name="cv2_pulse_bit", range=bitcount_range, default=2),
            configuration.integer(name="cv3_pulse_bit", range=bitcount_range, default=4),
        ]

    def main(self):
        line1_y = 11
        line2_y = 23
        while True:
            if self.request_next_k2:
                self.next_k2_mode()

            oled.fill(0)
            prob = self.tm.flip_probability
            prob_2 = (
                "locked"
                if self.tm.flip_probability == 0
                else "looped"
                if self.tm.flip_probability == 100
                else ""
            )
            scale_str = (
                f"{'*' if self.kb2.current_name == 'scale' else ' '}scale:{self.tm.scale:3.1f}"
            )
            len_str = f"{'*' if self.kb2.current_name == 'length' else ' '}{self.tm.length:2} steps"

            self.bits_as_led_line(oled, self.tm.get_8_bits())

            oled.text(f" {prob}%", 0, line1_y, 1)
            oled.text(f"{scale_str}", 40, line1_y, 1)

            oled.text(f"{prob_2}", 0, line2_y, 1)
            oled.text(f"{len_str}", 63, line2_y, 1)
            oled.show()


if __name__ == "__main__":
    EuroPiTuringMachine(DEFAULT_BIT_COUNT, europi.MAX_OUTPUT_VOLTAGE).main()
