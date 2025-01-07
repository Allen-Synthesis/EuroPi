from europi import *
from europi_script import EuroPiScript

from experimental.rtc import clock

import random


class DailyRandom(EuroPiScript):
    """
    Generates a set of pseudo-random gate and CV sequences every day

    This script requires a realtime clock. Please refer to
    experimental.clocks for supported clocks.

    If no RTC is installed & configured, the default clock will be used,
    but this will generate the same pattern every time the module is
    restarted.
    """

    SEQUENCE_LENGTH = 16

    BITMASKS = [
        0b101010101010,
        0b001100110011,
        0b100100100100,
        0b111000111000,
        0b011000111001,
        0b011011011011,
        0b110011001100,
    ]

    def __init__(self):
        super().__init__()

        current_time = clock.now()
        self.regenerate_sequences(current_time)

        self.sequence_index = 0

        @din.handler
        def advance_sequence():
            self.sequence_index += 1

    def regenerate_sequences(self, datetime):
        (year, month, day, hour, minute) = datetime[0:5]

        try:
            weekday = datetime[DateTimeIndex.WEEKDAY] % 7
        except IndexError:
            weekday = 0

        # bit-shift the fields around to reduce collisions
        # mask: 12 bits
        # year: 11 bits
        # month: 4 bits
        # day: 5 bits
        # hour: 6 bits
        # minute: 6 bits
        seed_1 = self.BITMASKS[weekday] ^ year ^ (month << 7) ^ day
        seed_2 = self.BITMASKS[weekday] ^ year ^ (month << 6) ^ day ^ hour
        seed_3 = self.BITMASKS[weekday] ^ year ^ (month << 7) ^ day ^ (hour << 6) ^ minute

        def generate_gates(seed):
            random.seed(seed)
            bits = random.getrandbits(self.SEQUENCE_LENGTH)
            pattern = []
            for i in range(self.SEQUENCE_LENGTH):
                pattern.append(bits & 0x01)
                bits = bits >> 1
            return pattern

        def generate_cv(seed):
            random.seed(seed)
            pattern = []
            for i in range(self.SEQUENCE_LENGTH):
                pattern.append(random.random() * europi_config.MAX_OUTPUT_VOLTAGE)
            return pattern

        self.sequences = [
            generate_gates(seed_1),
            generate_gates(seed_2),
            generate_gates(seed_3),
            generate_cv(seed_1),
            generate_cv(seed_2),
            generate_cv(seed_3),
        ]

    def main(self):
        # clear the display
        oled.fill(0)
        oled.show()

        while True:
            # regenerate the patterns when the day rolls over
            current_time = clock.now()
            self.regenerate_sequences(current_time)

            for i in range(len(cvs)):
                if i < len(cvs) // 2:
                    cvs[i].voltage(self.sequences[i][self.sequence_index % self.SEQUENCE_LENGTH] * europi_config.GATE_VOLTAGE)
                else:
                    cvs[i].voltage(self.sequences[i][self.sequence_index % self.SEQUENCE_LENGTH] * europi_config.MAX_OUTPUT_VOLTAGE)


if __name__ == "__main__":
    DailyRandom().main()
