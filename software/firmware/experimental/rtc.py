"""
Interface for realtime clock support.

EuroPi can have 0-1 realtime clocks at a time. The implementation is specified via experimental_config.
Underlying implementations to handle network and/or I2C hardware is contained with the experimental.clocks
namespace.

This module reads the desired implementation from experimental_config and instantiates a clock object
that can be used externally.
"""

import europi
from experimental.experimental_config import RTC_NONE, RTC_DS1307, RTC_DS3231


class DateTimeIndex:
    """
    Indices for the fields within a weekday tuple

    Note that SECOND and WEEKDAY are optional and may be omitted in some implementations
    """

    YEAR = 0
    MONTH = 1
    DAY = 2
    HOUR = 3
    MINUTE = 4
    SECOND = 5
    WEEKDAY = 6


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
        1: "Monday",
        2: "Tuesday",
        3: "Wednesday",
        4: "Thursday",
        5: "Friday",
        6: "Saturday",
        7: "Sunday",
    }


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

    def now(self):
        """
        Get the current UTC time.

        @return a tuple, (0-year, 1-month, 2-day, 3-hour, 4-minutes[, 5-seconds[, 6-weekday]])
        """
        return self.source.datetime()

    def __str__(self):
        """
        Return the current time as a string

        @return  A string with the format "[Weekday] YYYY/MM/DD HH:MM[:SS]"
        """
        t = self.now()
        if len(t) > DateTimeIndex.WEEKDAY:
            return f"{Weekday.NAME[t[DateTimeIndex.WEEKDAY]]} {t[DateTimeIndex.YEAR]}/{t[DateTimeIndex.MONTH]:02}/{t[DateTimeIndex.DAY]:02} {t[DateTimeIndex.HOUR]:02}:{t[DateTimeIndex.MINUTE]:02}:{t[DateTimeIndex.SECOND]:02}"
        elif len(t) > DateTimeIndex.SECOND:
            return f"{t[DateTimeIndex.YEAR]}/{t[DateTimeIndex.MONTH]:02}/{t[DateTimeIndex.DAY]:02} {t[DateTimeIndex.HOUR]:02}:{t[DateTimeIndex.MINUTE]:02}:{t[DateTimeIndex.SECOND]:02}"
        else:
            return f"{t[DateTimeIndex.YEAR]}/{t[DateTimeIndex.MONTH]:02}/{t[DateTimeIndex.DAY]:02} {t[DateTimeIndex.HOUR]:02}:{t[DateTimeIndex.MINUTE]:02}"


# fmt: off
if europi.experimental_config.RTC_IMPLEMENTATION == RTC_DS1307:
    from experimental.clocks.ds1307 import DS1307
    source = DS1307(europi.external_i2c)
elif europi.experimental_config.RTC_IMPLEMENTATION == RTC_DS3231:
    from experimental.clocks.ds3231 import DS3231
    source = DS3231(europi.external_i2c)
else:
    from experimental.clocks.null_clock import NullClock
    source = NullClock()
# fmt: on

clock = RealtimeClock(source)
