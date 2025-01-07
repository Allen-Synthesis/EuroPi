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

        seed_1 = year ^ month ^ day
        seed_2 = year ^ month ^ day ^ hour
        seed_3 = year ^ month ^ day ^ hour ^ minute

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
