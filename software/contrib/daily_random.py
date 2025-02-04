# Copyright 2024 Allen Synthesis
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from europi import *
from europi_script import EuroPiScript

from experimental.rtc import clock

import random


class Sequence:
    """
    A single gate or CV sequence
    """
    BASE_SEQUENCE_LENGTH = 16

    def __init__(self, seed):
        self.index = 0
        self.regenerate(seed)

    def regenerate(self, seed):
        random.seed(seed)

        # randomize the length so the majority are 16, but we get some longer or shorter
        length = self.BASE_SEQUENCE_LENGTH
        r = random.random()
        if r < 0.1:
            length -= 2
        elif r < 0.25:
            length -= 1
        elif r > 0.8:
            length += 2
        elif r > 0.75:
            length += 1

        pattern = []
        for i in range(length):
            pattern.append(random.random())

        self.pattern = pattern

    def next(self):
        self.index = (self.index + 1) % len(self.pattern)

    @property
    def gate_volts(self):
        return (int(self.pattern[self.index] * 2) % 2) * europi_config.GATE_VOLTAGE

    @property
    def cv_volts(self):
        return self.pattern[self.index] * europi_config.MAX_OUTPUT_VOLTAGE


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
        0b000111000111,
        0b111111000000,
        0b111000111000,
        0b110011001100,
        0b010101010101,
    ]

    def __init__(self):
        super().__init__()

        self.sequences = [
            Sequence(0) for cv in cvs
        ]
        self.regenerate_sequences()

        self.trigger_recvd = False

        @din.handler
        def advance_sequence():
            for s in self.sequences:
                s.next()
            self.trigger_recvd = True

        @din.handler_falling
        def gates_off():
            for i in range(len(cvs) // 2):
                cvs[i].off()

    def regenerate_sequences(self):
        datetime = clock.localnow()
        year = datetime.year
        month = datetime.month
        day = datetime.day
        hour = datetime.hour
        minute = datetime.minute
        second = datetime.second if datetime.second is not None else 0
        weekday = datetime.weekday if datetime.weekday is not None else 1

        # bit-shift the fields around to reduce collisions
        # mask: 12 bits
        # year: 11 bits
        # month: 4 bits
        # day: 5 bits
        # hour: 6 bits
        # minute: 6 bits
        seeds = [
            self.BITMASKS[weekday - 1] ^ year ^ (month << 7) ^ day,
            self.BITMASKS[weekday - 1] ^ year ^ (month << 6) ^ day ^ ~hour,
            self.BITMASKS[weekday - 1] ^ year ^ (month << 7) ^ day ^ (hour << 6) ^ minute,
        ]

        for i in range(len(self.sequences)):
            self.sequences[i].regenerate(seeds[i % len(seeds)])

    def main(self):
        last_draw_at = clock.localnow()
        oled.centre_text(str(last_draw_at).replace(" ", "\n"))

        while True:
            now = clock.localnow()
            if now != last_draw_at:
                self.regenerate_sequences()
                oled.centre_text(str(now).replace(" ", "\n"))
                last_draw_at = now

            if self.trigger_recvd:
                self.trigger_recvd = False
                for i in range(len(self.sequences)):
                    if i < len(cvs) // 2:
                        cvs[i].voltage(self.sequences[i].gate_volts)
                    else:
                        cvs[i].voltage(self.sequences[i].cv_volts)


if __name__ == "__main__":
    DailyRandom().main()
