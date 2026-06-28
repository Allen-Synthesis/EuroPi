#!/usr/bin/env python3
# Copyright 2026 Allen Synthesis
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
"""
Set Timer

Acts as a simple stopwatch/timer module to help manage recording durations, set timing, etc...
"""

from europi import *
from europi_script import EuroPiScript

import configuration
import time


MODE_GATE = "gate"
MODE_TRIGGER = "trigger"

# The duration of the trigger output on CV2
TRIGGER_DURATION_MS = 10

from experimental.a_to_d import AnalogReaderDigitalWrapper


def time2str(t):
    """
    Convert an incrementing timer to a formatted string.

    @return  A string of the form HH:MM:SS.ss
    """
    ms = t % 1000
    s = (t - ms) // 1000
    m = (s // 60)
    h = m // 60
    s = s%60
    m = m%60
    return f"{h:02}:{m:02}:{s:02}.{ms//10:02}"


class SetTimer(EuroPiScript):
    def __init__(self):
        super().__init__()

        # Is the clock currently running?
        self.is_running = False

        # How many times have we split?
        self.n_splits = 1

        # The total elapsed time since we started (ms resolution)
        self.elapsed_time = 0

        # The current split time (ms resolution)
        self.split_time = 0

        # The clock time of our last tick
        self.last_tick_at = time.ticks_ms()

        @b1.handler
        def b1_press():
            self.toggle()

        @b2.handler
        def b2_press():
            if self.is_running:
                self.split()
            else:
                self.reset()

        @din.handler
        def din_rise():
            if self.config.MODE == MODE_GATE:
                self.start()
            else:
                self.toggle()

        @din.handler_falling
        def din_fall():
            if self.config.MODE == MODE_GATE:
                self.stop()

        def ain_rise():
            self.split()

        self.din2 = AnalogReaderDigitalWrapper(ain, cb_rising=ain_rise)

    @classmethod
    def config_points(cls):
        return [
            configuration.choice(
                name="MODE",
                choices=[MODE_TRIGGER, MODE_GATE],
                default=MODE_GATE
            ),
        ]

    def start(self):
        cv1.on()
        self.is_running = True

    def stop(self):
        cv1.off()
        self.is_running = False

    def toggle(self):
        if self.is_running:
            self.stop()
        else:
            self.start()

    def reset(self):
        self.n_splits = 0
        self.elapsed_time = 0
        self.split_time = 0

    def split(self):
        if self.is_running:
            self.n_splits += 1
            self.split_time = 0

    def draw(self):
        oled.centre_text(f"""{time2str(self.elapsed_time)}
{time2str(self.split_time)}
({self.n_splits})""")

    def tick(self):
        now = time.ticks_ms()

        if self.is_running:
            delta = time.ticks_diff(now, self.last_tick_at)

            self.elapsed_time += delta
            self.split_time += delta

            if self.split_time < TRIGGER_DURATION_MS:
                cv2.on()
            else:
                cv2.off()

        self.last_tick_at = now

    def main(self):
        while True:
            self.din2.update()
            self.tick()
            self.draw()


if __name__ == "__main__":
    SetTimer().main()
