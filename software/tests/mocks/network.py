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
Mock implementation of Micropython's network module

This module is only present on the Pico W and Pico 2 W; on Pico variations
without wireless modules it cannot be imported.
"""

STAT_WRONG_PASSWORD = -3
STAT_NO_AP_FOUND = -2
STAT_CONNECT_FAIL = -1
STAT_IDLE = 0
STAT_CONNECTING = 1
STAT_GOT_IP = 3


def country(code=None):
    """
    Get/set the country code.

    @param code  The ISO-compatible 2-character country code
    @return The ISO-compatible 2-character country code, or XX if unset
    """
    if code:
        return code
    else:
        return "XX"


def hostname(name=None):
    """
    Get/set the hostname.

    @param name  The new hostname to assign
    @return This device's hostname
    """
    if name:
        return name
    else:
        return "PicoW"


def ipconfig(**kwargs):
    """
    Get/set global IP paramters.

    @param kwargs  Keyword arguments to assign: dns, prefer
    @return The value of the parameter
    """
    return None


def route():
    """
    Get static route information.

    This doesn't appear to be documented on
    https://docs.micropython.org/en/latest/library/network.html
    but exists on the Pico 2 W, returning an empty list when
    called. So that behaviour is replicated here.
    """
    return []


class WIFI:
    """
    Dummy implementation if MicroPython's network.WIFI class

    See: https://docs.micropython.org/en/latest/library/network.WLAN.html
    """

    IF_STA = 0
    IF_AP = 1

    SEC_OPEN = 0
    SEC_WPA_WPA2 = 4194310

    PM_NONE = 16
    PM_POWERSAVE = 17
    PM_PERFORMANCE = 10555714

    def __init__(self, mode):
        pass

    def connect(self, ssid=None, key=None, bssid=None):
        pass

    def disconnect(self):
        pass

    def config(self, params):
        pass

    def ifconfig(self, params=None):
        if params is None:
            return ("10.0.0.100", "255.0.0.0", "10.0.0.1", "8.8.8.8")
        else:
            pass

    def active(self):
        return False

    def isconnected(self):
        return False

    def param(self, **kwargs):
        pass

    def scan(self):
        return []
