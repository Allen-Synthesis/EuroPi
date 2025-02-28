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
Interface for realtime clock support.

EuroPi can have 0-1 realtime clocks at a time. The implementation is specified via experimental_config.
Underlying implementations to handle network and/or I2C hardware is contained with the experimental.clocks
namespace.

This module reads the desired implementation from experimental_config and instantiates a clock object
that can be used externally.
"""

import europi
from experimental.clocks.clock_source import ExternalClockSource
from experimental.experimental_config import RTC_DS1307, RTC_DS3231, RTC_NTP


class Month:
    """
    Container class for month names
    """

    JANUARY = 1
    FEBRUARY = 2
    MARCH = 3
    APRIL = 4
    MAY = 5
    JUNE = 6
    JULY = 7
    AUGUST = 8
    SEPTEMBER = 9
    OCTOBER = 10
    NOVEMBER = 11
    DECEMBER = 12

    NAME = {
        1: "January",
        2: "February",
        3: "March",
        4: "April",
        5: "May",
        6: "June",
        7: "July",
        8: "August",
        9: "September",
        10: "October",
        11: "November",
        12: "December",
    }


class Weekday:
    """
    Container class for weekday names

    ISO 8601 specifies the week starts on Monday (1) and ends on Sunday (7)
    """

    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5
    SATURDAY = 6
    SUNDAY = 7

    NAME = {
        0: "Unspecified",
        1: "Monday",
        2: "Tuesday",
        3: "Wednesday",
        4: "Thursday",
        5: "Friday",
        6: "Saturday",
        7: "Sunday",
    }


class Timezone:
    """
    Represents a timezone shift relative to UTC

    We allow minutes & hours, since there are 15-, 30-, and 45-minute timzeones in the world
    """

    def __init__(self, hours, minutes):
        """
        Create a time zone we can add to a datetime to get local time

        @param hours  The number of hours ahead/behind we need to adjust [-24 to +24]
        @param minutes  The number of minutes ahead/behind we need to adjust [-59 to +59]
        """
        if (hours < 0 and minutes > 0) or (hours > 0 and minutes < 0):
            raise ValueError("Timezone offset must be in a consistent direction")
        if abs(hours) > 24 or abs(minutes) > 59:
            raise ValueError("Invalid time zone adjustment")
        self.hours = hours
        self.minutes = minutes

    def __str__(self):
        """
        Get the offset as a string

        Result is of the format is {+|-}hh:mm
        """
        s = f"{abs(self.hours):02}:{abs(self.minutes):02}"
        if self.hours < 0:
            s = f"-{s}"
        else:
            s = f"+{s}"
        return s


class DateTime:
    """Represents a date and time"""

    def __init__(self, year, month, day, hour, minute, second=None, weekday=None, yearday=None):
        """
        Create a DateTime representing a specific moment

        @param year  The current year (e.g. 2025)
        @param month  The current month (e.g. Month.JANUARY)
        @param day  The current day within the month (e.g. 17)
        @param hour  The current hour on a 24-hour clock (0-23)
        @param minute  The current minute within the hour (0-59)
        @param second  The current second within the minute (0-59, optional)
        @param weekday  The current day of the week (e.g. Weekday.MONDAY, optional)
        @param yearday  The current day of the year (1-365, 1-366 if leap year, optional)
        """
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.minute = minute
        self.second = second
        self.weekday = weekday

    def __str__(self):
        """
        Get the current day and time as a string

        Result is of the format
            [Weekday ]YYYY/MM/DD hh:mm[:ss]
        """
        s = f"{self.year:04}/{self.month:02}/{self.day:02} {self.hour:02}:{self.minute:02}"
        if self.second is not None:
            s = f"{s}:{self.second:02}"
        if self.weekday is not None:
            s = f"{Weekday.NAME[self.weekday]} {s}"
        return s

    def __add__(self, tz):
        """
        Add a timezone offset to the current time, returning the result

        @param tz  The timezone we're adding to this Datetime
        """
        t = DateTime(
            self.year, self.month, self.day, self.hour, self.minute, self.second, self.weekday
        )

        # shortcut if there is no offset
        if tz.hours == 0 and tz.minutes == 0:
            return t

        # temporarily shift the month and day to be zero-indexed to make subsequent math easier
        t.month -= 1
        t.day -= 1
        if t.weekday is not None:
            t.weekday -= 1

        # add the offset; this can be positive or negative
        t.minute += tz.minutes
        t.hour += tz.hours

        # cascade through the units, borrowing/carrying-over as needed
        if t.minute < 0:
            t.minute += 60
            t.hour -= 1
        elif t.minute >= 60:
            t.minute -= 60
            t.hour += 1

        if t.hour < 0:
            t.hour += 24
            t.day -= 1
            if t.weekday is not None:
                t.weekday = (t.weekday - 1) % 7
        elif t.hour >= 24:
            t.hour -= 24
            t.day += 1
            if t.weekday is not None:
                t.weekday = (t.weekday + 1) % 7

        days_in_month = DateTime.calculate_days_in_month(t.month + 1, t.year)
        days_in_prev_month = DateTime.calculate_days_in_month((t.month + 1) % 12 + 1, t.year)
        if t.day < 0:
            t.day = days_in_prev_month - 1  # last day of the month, zero-indexed
            t.month -= 1
        elif t.day >= days_in_month:
            t.day = 1
            t.month += 1

        if t.month < 0:
            t.month += 12
            t.year -= 1
        elif t.month >= 12:
            t.month -= 12
            t.year += 1

        # shift the month, day and weekday back to be 1-indexed
        t.month += 1
        t.day += 1
        if t.weekday is not None:
            t.weekday += 1

        return t

    @staticmethod
    def calculate_days_in_month(month, year):
        month_lengths = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        if DateTime.calculate_is_leap_year(year) and month == Month.FEBRUARY:
            return 29
        else:
            return month_lengths[month - 1]

    @staticmethod
    def calculate_is_leap_year(year):
        # a year is a leap year if it is divisible by 4
        return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)

    @property
    def is_leap_year(self):
        return DateTime.calculate_is_leap_year(self.year)

    @property
    def days_in_month(self):
        return DateTime.calculate_days_in_month(self.month, self.year)

    @property
    def days_in_year(self):
        if self.is_leap_year:
            return 366
        else:
            return 365

    @property
    def tuple(self):
        return (
            self.year,
            self.month,
            self.day,
            self.hour,
            self.minute,
            self.second,
            self.weekday,
            0,
        )

    def __eq__(self, other):
        # fmt: off
        return (
            self.year == other.year and
            self.month == other.month and
            self.day == other.day and
            self.hour == other.hour and
            self.minute == other.minute and
            (
                (self.second is None or other.hour is None ) or
                (self.second == other.second)
            )
        )
        # fmt: on

    def __lt__(self, other):
        if self.year == other.year:
            if self.month == other.month:
                if self.hour == other.hour:
                    if self.minute == other.minute:
                        if self.second is None or other.second is None:
                            return False
                        return self.second < other.second
                    return self.minute < other.minute
                return self.hour < other.hour
            return self.month < other.month
        return self.year < other.year

    def __gt__(self, other):
        if self.year == other.year:
            if self.month == other.month:
                if self.hour == other.hour:
                    if self.minute == other.minute:
                        if self.second is None or other.second is None:
                            return False
                        return self.second > other.second
                    return self.minute > other.minute
                return self.hour > other.hour
            return self.month > other.month
        return self.year > other.year

    def __le__(self, other):
        if self.year == other.year:
            if self.month == other.month:
                if self.hour == other.hour:
                    if self.minute == other.minute:
                        if self.second is None or other.second is None:
                            return False
                        return self.second <= other.second
                    return self.minute <= other.minute
                return self.hour <= other.hour
            return self.month <= other.month
        return self.year <= other.year

    def __ge__(self, other):
        if self.year == other.year:
            if self.month == other.month:
                if self.hour == other.hour:
                    if self.minute == other.minute:
                        if self.second is None or other.second is None:
                            return False
                        return self.second >= other.second
                    return self.minute >= other.minute
                return self.hour >= other.hour
            return self.month >= other.month
        return self.year >= other.year


class RealtimeClock:
    """
    A continually-running clock that provides the day & date.

    This class wraps around an external clock source, e.g. an I2C-compatible RTC
    module or a network connection to an NTP server
    """

    def __init__(self, source):
        """
        Create a new realtime clock.

        @param source  An ExternalClockSource implementation we read the time from
        """
        self.source = source

    def utcnow(self):
        """
        Get the current UTC time.

        @return A DateTime object representing the current UTC time
        """

        # get the raw tuple from the clock, append Nones so we have all 7 fields
        t = list(self.source.datetime())
        if len(t) < ExternalClockSource.SECOND + 1:
            t.append(None)
        if len(t) < ExternalClockSource.WEEKDAY + 1:
            t.append(None)

        return DateTime(
            t[ExternalClockSource.YEAR],
            t[ExternalClockSource.MONTH],
            t[ExternalClockSource.DAY],
            t[ExternalClockSource.HOUR],
            t[ExternalClockSource.MINUTE],
            t[ExternalClockSource.SECOND],
            t[ExternalClockSource.WEEKDAY],
            t[ExternalClockSource.YEARDAY],
        )

    def localnow(self):
        """
        Get the current local time

        See experimental_config for instructions on how to configure the local timezone

        @return a DateTime object representing the current local time
        """
        return self.utcnow() + local_timezone


# fmt: off
if europi.experimental_config.RTC_IMPLEMENTATION == RTC_DS1307:
    from experimental.clocks.ds1307 import DS1307
    source = DS1307(europi.external_i2c)
elif europi.experimental_config.RTC_IMPLEMENTATION == RTC_DS3231:
    from experimental.clocks.ds3231 import DS3231
    source = DS3231(europi.external_i2c)
elif europi.experimental_config.RTC_IMPLEMENTATION == RTC_NTP:
    from experimental.clocks.ntp import NtpClock
    source = NtpClock()
else:
    from experimental.clocks.null_clock import NullClock
    source = NullClock()
# fmt: on

local_timezone = Timezone(
    europi.experimental_config.UTC_OFFSET_HOURS, europi.experimental_config.UTC_OFFSET_MINUTES
)

clock = RealtimeClock(source)
