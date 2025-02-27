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
"""
Interface for interacting with realtime clock hardware.

For consistency, we always assume that the external clock source is synchronized with UTC. This means
your I2C clock should be set to UTC time, not local time. If you set your I2C clock to local time
some scripts may behave incorrectly.

The Raspberry Pi Pico (and official variants like the Pico W, Pico 2, etc...) does NOT
include a realtime clock. All RTC implementations rely on some external reference time, e.g.
- external hardware (e.g. an I2C-supported external clock module)
- a wireless connection and an accessible NTP server

The external clock source must implement the ExternalClockSource class
"""


class ExternalClockSource:
    """
    A generic class representing any external, canonical clock source.

    Any network- or I2C-based external time source should inherit from this class and
    implement the relevant functions.

    The implemented clock source must provide the time and date in UTC, 24-hour time.
    """

    YEAR = 0
    MONTH = 1
    DAY = 2
    HOUR = 3
    MINUTE = 4
    SECOND = 5
    WEEKDAY = 6
    YEARDAY = 7

    # fmt: off
    # The lengths of the months in a non-leap-year
    _month_lengths = [
        31,
        28,
        31,
        30,
        31,
        30,
        31,
        31,
        30,
        31,
        30,
        31
    ]
    # fmt: on

    def __init__(self):
        pass

    def datetime(self):
        """
        Get the current UTC time as a tuple.

        see: https://docs.micropython.org/en/latest/library/time.html#time.localtime

        @return a tuple of the form (0-year, 1-month, 2-day, 3-hour, 4-minutes, 5-seconds, 6-weekday, 7-yearday)
        """
        raise NotImplementedError()

    def set_datetime(self, datetime):
        """
        Set the clock's current UTC time.

        If the clock does not support setting (e.g. it's an NTP source we can only read from)
        your sub-class should implement this method anyway and simply pass.

        see: https://docs.micropython.org/en/latest/library/time.html#time.localtime

        @param datetime  A tuple of the form (0-year, 1-month, 2-day, 3-hour, 4-minutes, 5-seconds, 6-weekday, 7-yearday)
        """
        raise NotImplementedError()

    def is_leap_year(self, datetime):
        """
        Determine if the datetime's year is a leap year or not.

        @return  True if the datetime is a leap year, otherwise False
        """
        # a year is a leap year if it is divisible by 4
        # but NOT a multple of 100, unless it's also a multiple of 400
        year = datetime[self.YEAR]
        return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)

    def year_length(self, datetime):
        """
        Determine the number of days in the datetime's year.

        @return  The number of days in the year, taking leap years into account
        """
        if self.is_leap_year(datetime):
            return 366
        return 365

    def month_length(self, datetime):
        """
        Get the numer of days in the month.

        This takes leap-years into consideration

        @return  The number of days in the datetime's month
        """
        if datetime[self.MONTH] == 2 and self.is_leap_year(datetime):
            return 29
        return self._month_lengths[datetime[self.MONTH] - 1]

    def check_valid_datetime(self, datetime):
        """
        Check if a datetime contains valid values.

        Raises a ValueError if any field is out of range

        @param datetime
        """
        # fmt: off
        n_days = self.month_length(datetime)
        if (
            # To anyone reading this from the past: congrats on time-travel! Your year is not supported
            # To anyone reading this from the future: sorry, you'll need to modify some code to get your
            # dates supported
            # Also, it's pretty cool if you're actually reading this beyond 2099. I'm flattered.
            datetime[self.YEAR] < 2000 or
            datetime[self.YEAR] > 2099 or  # somewhat arbitrary, but the DS3231 library I'm using cuts off here, too
            datetime[self.MONTH] < 1 or
            datetime[self.MONTH] > 12 or
            datetime[self.DAY] < 1 or
            datetime[self.DAY] > n_days or
            datetime[self.HOUR] < 0 or
            datetime[self.HOUR] >= 24 or  # time is 00:00:00 to 23:59:59
            datetime[self.MINUTE] < 0 or
            datetime[self.MINUTE] >= 60 or
            (
                # seconds are optional, must be 0-59
                len(datetime) >= self.SECOND + 1 and
                (
                    datetime[self.SECOND] < 0 or
                    datetime[self.SECOND] >= 60
                )
            ) or
            (
                # weekday is optional, must be 1-7
                len(datetime) >= self.WEEKDAY + 1 and
                (
                    datetime[self.WEEKDAY] < 1 or
                    datetime[self.WEEKDAY] > 7
                )
            )
        ):
            raise ValueError("Invalid datetime tuple")
        # fmt: on
