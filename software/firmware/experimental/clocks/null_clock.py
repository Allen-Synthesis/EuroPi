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
from experimental.clocks.clock_source import ExternalClockSource
from utime import ticks_ms, ticks_diff


class NullClock(ExternalClockSource):
    """
    A placeholder replacement for a realtime clock.

    This class sets the base time to 1 January, 1970, 00:00:00.0 and adds the current value of
    ticks_ms() to that time. This allows the RTC to tick up, but won't actually be indicitave of the real time.

    Because ticks_ms() rolls over ever 2**30 ms, the datetime returned by this clock will also roll over
    at the same interval. BUT, 2**30 ms ~= 298 hours, so unless your EuroPi is powered-on 12 days continuously
    this won't ever cause problems.
    """

    def __init__(self):
        super().__init__()
        self.last_check_at = ticks_ms()

    def set_datetime(self, datetime):
        # we don't allow configuring the time here
        pass

    def datetime(self):
        t = ticks_ms()

        s = (t // 1000) % 60
        m = (t // (1000 * 60)) % 60
        h = (t // (1000 * 60 * 60)) % 24
        dd = (t // (1000 * 60 * 60 * 24)) % 31
        mm = 1
        yy = 1970
        wd = (4 + dd) % 7  # 1 jan 1970 was a thursday
        yd = 0  # ignore yearday

        return (yy, mm, dd, h, m, s, wd, yd)
