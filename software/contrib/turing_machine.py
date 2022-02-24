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
    from firmware.europi import din, ain, k1, k2, b1, b2, cv1, cv2, cv3, cv4, cv5, cv6, oled
except ImportError:
    import europi
    from europi import din, ain, k1, k2, b1, b2, cv1, cv2, cv3, cv4, cv5, cv6, oled

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
        self._write = False

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

    def step_handler(self):
        pass

    def step(self):
        self.rotate_bits()
        if self.write:
            self.bits = self.bits & ~1
        if randint(0, 99) < self.flip_probability:
            self.bits = self.bits ^ 0b1
        self.step_handler()

    def get_8_bits(self):
        return self.bits & 0xFF

    def get_voltage(self):
        return self.get_8_bits() / INT_MAX_8 * self.scale

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

    @property
    def write(self):
        return self._write

    @write.setter
    def write(self, value: bool):
        self._write = value


# code to tie it to the EuroPi's interface
class EuroPiTuringMachine(TuringMachine):
    def __init__(self):
        super().__init__(bit_count=DEFAULT_BIT_COUNT, max_output_voltage=europi.MAX_OUTPUT_VOLTAGE)
        self.k2_scale_mode = True  # if it's not scale, it's length

        @din.handler
        def clock():
            self.step()

        @b2.handler_falling
        def mode_toggle():
            if self.k2_scale_mode:
                self._scale = self.scale
            else:
                self._length = self.length
            self.k2_scale_mode = not self.k2_scale_mode

    def step_handler(self):
        cv1.voltage(self.get_voltage())

    @TuringMachine.flip_probability.getter
    def flip_probability(self):
        return int((1 - k1.percent()) * 100)

    @flip_probability.setter
    def flip_probability(self):
        raise NotImplementedError("Setting the flip_probability is done via a knob.")

    @TuringMachine.scale.getter
    def scale(self):
        if self.k2_scale_mode:
            return k2.percent() * self.max_output_voltage
        else:
            return self._scale

    @scale.setter
    def scale(self):
        raise NotImplementedError("Setting the scale is done via a knob.")

    @TuringMachine.length.getter
    def length(self):
        if self.k2_scale_mode:
            return self._length
        else:
            return k2.choice([2, 3, 4, 5, 6, 8, 12, 16])  # TODO: vary based on bit_count?

    @length.setter
    def length(self):
        raise NotImplementedError("Setting the length is done via a knob.")

    @TuringMachine.write.getter
    def write(self):
        return b1.value()

    @write.setter
    def write(self):
        raise NotImplementedError("Setting the write flag is done via a button.")

async def main():
    tm = EuroPiTuringMachine()
    while True:
        oled.fill(0)
        probability = tm.flip_probability
        scale = tm.scale
        if tm.k2_scale_mode:
            primary = f"s: {tm.scale}"
            secondary = f"l: {tm.length}"
        else:
            primary = f"l: {tm.length}"
            secondary = f"s: {tm.scale}"
        oled.text(f"{tm.get_8_bits():08b}", 2, 3, 1)
        oled.text(f"p: {probability}   {primary}", 2, 13, 1)
        oled.text(f"     {secondary}", 2, 23, 1)
        oled.show()
        await asyncio.sleep(0.1)


if __name__ in ["__main__", "contrib.turing_machine"]:
    asyncio.run(main())
