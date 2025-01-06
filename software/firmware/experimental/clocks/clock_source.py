"""
Interface for interacting with realtime clock hardware.

For simplicity, we always assume that the external clock source is synchronized with UTC. This means
your I2C clocks should be set to UTC time, not local time. To configure the time zone offset, use
experimental_config to set the desired offset hours and minutes. For regions using Daylight Savings
time (most of North America, western Europe, Australia, and New Zealand, among others) you will
need to manually adjust your config file to keep local time properly adjusted.

The Raspberry Pi Pico (and official variants like the Pico W, Pico 2, etc...) does NOT
include a realtime clock. All RTC implementations rely on some external reference time, e.g.
- external hardware (e.g. an I2C-supported external clock module)
- an wireless connection and an accessible NTP server

The external clock source must implement the ExternalClockSource class
"""


class ExternalClockSource:
    """
    A generic class representing any external, canonical clock source.

    Any network- or I2C-based external time source should inherit from this class and
    implement the relevant functions.

    The implemented clock source must provide the time and date in UTC, 24-hour time.
    """

    def __init__(self):
        pass

    def datetime(self):
        """
        Get the current UTC time as a tuple.

        @return a tuple of the form (0-year, 1-month, 2-day, 3-hour, 4-minutes[, 5-seconds[, 6-weekday]])
        """
        raise NotImplementedError()

    def set_datetime(self, datetime):
        """
        Set the clock's current UTC time.

        If the clock does not support setting (e.g. it's an NTP source we can only read from)
        your sub-class should implement this method anyway and simply pass.

        @param datetime  A tuple of the form (0-year, 1-month, 2-day, 3-hour, 4-minutes[, 5-seconds[, 6-weekday]])
        """
        raise NotImplementedError()
