# Copyright 2025 Allen Synthesis
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
Interface for using an NTP server as a realtime clock source

This will only work if
1. we're using a wifi-supported Pico model
2. we have a valid network configuration
3. there's an accessible NTP server on the network (important if we're in AP mode)
"""
from experimental.clocks.clock_source import ExternalClockSource
from experimental.experimental_config import load_experimental_config

import utime


class NtpError(Exception):
    """Custom NTP-related errors"""

    def __init__(self, message):
        super().__init__(message)


try:
    import ntptime
except ImportError as err:
    raise NtpError(f"Failed to load NTP dependency: {err}")


class NtpClock(ExternalClockSource):
    """
    Realtime clock source that uses an external NTP server

    Requires a valid network connection on a Pico W or Pico 2 W
    """

    def __init__(self):
        super().__init__()
        cfg = load_experimental_config()
        try:
            # set the clock to UTC from the default NTP source
            ntptime.settime()
        except Exception as err:
            raise NtpError(f"Failed to initialize NTP clock: {err}")

    def set_datetime(self, datetme):
        """
        NTP server is read-only, so setting the time is nonsical.

        This function won't do anything, but don't raise an error.
        """
        pass

    def datetime(self):
        """
        Get the latest time from our NTP source and return it

        @return a tuple of the form tuple of the form (0-year, 1-month, 2-day, 3-hour, 4-minutes, 5-seconds, 6-weekday, 7-yearday)
        """
        return utime.gmtime()
