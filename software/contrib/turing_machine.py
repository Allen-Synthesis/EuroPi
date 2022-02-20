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
INT_MAX_16 = 0xFFFF
BIT_COUNT = 16

class TuringMachine():
    
    def __init__(self):
        self.bits = getrandbits(16)
        self.flip_probability = 0

    def get_bit_string(self):
        return f"{self.bits:016b}"

    def rotate_bits(self):
        self.bits = ((self.bits << 1) % (1 << BIT_COUNT))|(self.bits >> (BIT_COUNT - 1))

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