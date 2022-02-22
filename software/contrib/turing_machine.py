"""

din - clock
ain - cv
k1 - the big one
k2 - scale
b1 - length cycle
b2 - write
cv1 - out
cv2 - noise
cv3 - pulse
cv4 - pulse
cv5 - pulse
cv6 - pulse
"""
from random import getrandbits, randint

try:
    from firmware import europi
    from firmware.europi import cv1, oled
except ImportError:
    import europi
    from europi import cv1, oled

try:
    import uasyncio as asyncio
except ImportError:
    import asyncio


INT_MAX_8 = 0xFF
DEFAULT_BIT_COUNT = 16
MAX_OUTPUT_VOLTAGE = europi.MAX_OUTPUT_VOLTAGE


def _mask(n):
    return (1 << n) - 1


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

    def get_bit_string(self):
        return f"{self.bits:0{self.bit_count}b}"

    def rotate_bits(self):
        length_mask = _mask(self.length)
        bits_to_rotate = self.bits & length_mask
        inverse_length_mask = _mask(self.bit_count) ^ length_mask
        bits_to_ignore = self.bits & inverse_length_mask
        self.bits = (
            ((bits_to_rotate << 1) % (1 << self.length)) | (bits_to_rotate >> (self.length - 1))
        ) | bits_to_ignore

    def step(self):
        self.rotate_bits()
        if randint(0, 99) < self._flip_probability:
            self.bits = self.bits ^ 0b1

    def get_8_bits(self):
        return self.bits & 0xFF

    def get_voltage(self):
        return self.get_8_bits() / INT_MAX_8 * self._scale

    @property
    def flip_probability(self):
        return self._flip_probability

    @flip_probability.setter
    def flip_probability(self, probability: int):
        if probability < 0 or probability > 100:
            raise ValueError(f"Probability of {probability} is outside the expected range of [0,100]")
        self._flip_probability = probability

    @property
    def scale(self):
        return self._scale

    @scale.setter
    def scale(self, scale: float):
        if scale < 0 or scale > self.max_output_voltage:
            raise ValueError(f"Scale of {scale} is outside the expected range of [0,{self.max_output_voltage}]")
        self._scale = scale

    @property
    def length(self):
        return self._length

    @length.setter
    def length(self, length):
        if length < 2 or length > self.bit_count:
            raise ValueError(f"Length of {length} is outside the expected range of [2,{self.bit_count}]")
        self._length = length


# code to tie it to the EuroPi's interface


async def main():
    tm = TuringMachine()
    while True:

        oled.centre_text(f"{tm.get_8_bits()}\n{tm.get_voltage()}")
        cv1.voltage(tm.get_voltage())

        await asyncio.sleep(0.5)
        tm.step()


if __name__ in ["__main__", "contrib.turing_machine"]:
    asyncio.run(main())
