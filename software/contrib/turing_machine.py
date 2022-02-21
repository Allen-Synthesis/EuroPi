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
from europi import MAX_OUTPUT_VOLTAGE, cv1

try:
    import uasyncio as asyncio
except ImportError:
    import asyncio
from europi import oled

INT_MAX_8 = 0xFF
DEFAULT_BIT_COUNT = 16

class TuringMachine():
    
    def __init__(self, bit_count=DEFAULT_BIT_COUNT):
        """Create a new TuringMachine with a shift register of the specified bit count. Default is 16, minimum is 8.
        """
        if bit_count < 8:
            raise ValueError(f"Specified bit_count ({bit_count}) is less than the minimum (8).")
        self.bit_count = bit_count
        self.bits = getrandbits(self.bit_count)
        self.flip_probability = 0

    def get_bit_string(self):
        return f"{self.bits:0{self.bit_count}b}"

    def rotate_bits(self):
        self.bits = ((self.bits << 1) % (1 << self.bit_count))|(self.bits >> (self.bit_count - 1))

    def step(self):
        self.rotate_bits()
        if randint(0, 100) <= self.flip_probability:
            self.bits = self.bits ^ 0b1

    def get_8_bits(self):
        return self.bits & 0xFF

    def get_voltage(self):
        return self.get_8_bits() / INT_MAX_8 * MAX_OUTPUT_VOLTAGE


# code to tie it to the EuroPi's interface



async def main():
    tm = TuringMachine()
    while True:

        oled.centre_text(f"{tm.get_bit_string()}\n{tm.get_voltage()}")
        cv1.voltage(tm.get_voltage())

        await asyncio.sleep(0.5)
        tm.step()


if __name__ in ["__main__", "contrib.turing_machine"]:
    asyncio.run(main())