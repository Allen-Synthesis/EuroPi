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


class RealtimeClock:
    """
    A continually-running clock that provides the day & date.

    This class wraps around an external clock source, e.g. an I2C-compatible RTC
    module or a network connection to an NTP server
    """

    YEAR = 0
    MONTH = 1
    DAY = 2
    HOUR = 3
    MINUTE = 4
    SECOND = 5
    WEEKDAY = 6

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

    def is_leap_year(self, datetime):
        """
        Determine if the datetime's year is a leap year or not

        @return  True if the datetime is a leap year, otherwise False
        """
        # a year is a leap year if it is divisible by 4
        # but NOT a multple of 100, unless it's also a multiple of 400
        year = datetime[self.YEAR]
        return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)

    def year_length(self, datetime):
        """
        Determine the number of days in the datetime's year

        @return  The number of days in the year, taking leap years into account
        """
        if self.is_leap_year(datetime):
            return 366
        return 365

    def month_length(self, datetime):
        """
        Get the numer of days in the month

        This takes leap-years into consideration

        @return  The number of days in the datetime's month
        """
        if datetime[self.MONTH] == 2 and self.is_leap_year(datetime):
            return 29
        return self._month_lengths[datetime[self.MONTH] - 1]


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
