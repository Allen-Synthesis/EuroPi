"""

din - clock
ain - cv
k1 - the big one
k2 - scale
b1 - length cycle
b2 - write
cv1 - pulse 1
cv2 - pulse 2
cv3 - pulse 4
cv4 - pulse 1+2
cv5 - pulse 2+4
cv6 - sequence out
"""
from random import getrandbits, randint
from time import sleep

try:
    from firmware import europi
    from firmware.europi import clamp, din, ain, k1, k2, b1, b2, cv1, cv2, cv3, cv4, cv5, cv6, oled
except ImportError:
    import europi
    from europi import clamp, din, ain, k1, k2, b1, b2, cv1, cv2, cv3, cv4, cv5, cv6, oled

from europi_script import EuroPiScript

# Customize pulses output here
CV1_PULSE_BIT = 1
CV2_PULSE_BIT = 2
CV3_PULSE_BIT = 4

INT_MAX_8 = 0xFF
DEFAULT_BIT_COUNT = 16
MAX_OUTPUT_VOLTAGE = europi.MAX_OUTPUT_VOLTAGE


class TuringMachine:
    def __init__(self, bit_count=DEFAULT_BIT_COUNT, max_output_voltage=MAX_OUTPUT_VOLTAGE):
        """Create a new TuringMachine with a shift register of the specified bit count. Default is 16, minimum is 8."""
        if bit_count < 8:
            raise ValueError(f"Specified bit_count ({bit_count}) is less than the minimum (8).")
        self.bit_count = bit_count
        self.bits = getrandbits(self.bit_count)
        self._flip_probability = 0
        self.max_output_voltage = max_output_voltage
        self._scale = max_output_voltage
        self._length = bit_count
        self._write = False

        self.flip_probability_getter = lambda: self._flip_probability
        self.scale_getter = lambda: self._scale
        self.length_getter = lambda: self._length
        self.write_getter = lambda: self._write
        self.step_handler = lambda: None

    def rotate_bits(self):
        self.bits = ((self.bits << 1) % (1 << self.bit_count)) | ((self.bits >> (self.length - 1)) & 1)

    def step(self):
        self.rotate_bits()
        if self.write:
            self.bits = self.bits & ~1
        if randint(0, 99) < self.flip_probability:
            self.bits = self.bits ^ 0b1
        self.step_handler()

    def get_8_bits(self):
        return self.bits & 0xFF

    def get_bit(self, i):
        return self.bits >> i & 1

    def get_bit_and(self, i, j):
        return self.get_bit(i) & self.get_bit(j)

    def get_voltage(self):
        return self.get_8_bits() / INT_MAX_8 * self.scale

    @property
    def flip_probability(self):
        return self.flip_probability_getter()

    @flip_probability.setter
    def flip_probability(self, probability: int):
        if probability < 0 or probability > 100:
            raise ValueError(f"Probability of {probability} is outside the expected range of [0,100]")
        self._flip_probability = probability

    @property
    def scale(self):
        return self.scale_getter()

    @scale.setter
    def scale(self, scale):
        if scale < 0 or scale > self.max_output_voltage:
            raise ValueError(f"Scale of {scale} is outside the expected range of [0,{self.max_output_voltage}]")
        self._scale = scale

    @property
    def length(self):
        return self.length_getter()

    @length.setter
    def length(self, length):
        if length < 2 or length > self.bit_count:
            raise ValueError(f"Length of {length} is outside the expected range of [2,{self.bit_count}]")
        self._length = length

    @property
    def write(self):
        return self.write_getter()

    @write.setter
    def write(self, value: bool):
        self._write = value


class EuroPiTuringMachine(EuroPiScript):
    def __init__(self):
        self.tm = TuringMachine(bit_count=DEFAULT_BIT_COUNT, max_output_voltage=europi.MAX_OUTPUT_VOLTAGE)
        self.tm.flip_probability_getter = self.flip_probability
        self.tm.scale_getter = self.scale
        self.tm.length_getter = self.length
        self.tm.write_getter = self.write
        self.tm.step_handler = self.step_handler
        self.k2_scale_mode = True  # scale mode or length mode

        @din.handler
        def clock():
            self.tm.step()

        @b2.handler_falling
        def mode_toggle():
            if self.k2_scale_mode:
                self.tm.scale = self.scale()
            else:
                self.tm.length = self.length()
            self.k2_scale_mode = not self.k2_scale_mode

    def step_handler(self):
        cv1.value(self.tm.get_bit(CV1_PULSE_BIT))
        cv2.value(self.tm.get_bit(CV2_PULSE_BIT))
        cv3.value(self.tm.get_bit(CV3_PULSE_BIT))
        cv4.value(self.tm.get_bit_and(CV1_PULSE_BIT, CV2_PULSE_BIT))
        cv5.value(self.tm.get_bit_and(CV2_PULSE_BIT, CV3_PULSE_BIT))
        cv6.voltage(self.tm.get_voltage())

    def flip_probability(self):
        return clamp(int((round(1 - k1.percent() - ain.percent(), 2)) * 100), 0, 100)

    def scale(self):
        if self.k2_scale_mode:
            return k2.percent() * self.tm.max_output_voltage
        else:
            return self.tm._scale

    def length(self):
        if self.k2_scale_mode:
            return self.tm._length
        else:
            return k2.choice([2, 3, 4, 5, 6, 8, 12, 16])  # TODO: vary based on bit_count?

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

    def main(self):
        line1_y = 11
        line2_y = 23
        while True:
            oled.fill(0)
            prob = self.tm.flip_probability
            prob_2 = "locked" if self.tm.flip_probability == 0 else "looped" if self.tm.flip_probability == 100 else ""
            scale_str = f"{'*' if self.k2_scale_mode else ' '}scale:{self.tm.scale:3.1f}"
            len_str = f"{' ' if self.k2_scale_mode else '*'}{self.tm.length:2} steps"

            self.bits_as_led_line(oled, self.tm.get_8_bits())

            oled.text(f" {prob}", 0, line1_y, 1)
            oled.text(f"{scale_str}", 40, line1_y, 1)

            oled.text(f"{prob_2}", 0, line2_y, 1)
            oled.text(f"{len_str}", 63, line2_y, 1)
            oled.show()
            sleep(0.1)


if __name__ == "__main__":
    EuroPiTuringMachine().main()
