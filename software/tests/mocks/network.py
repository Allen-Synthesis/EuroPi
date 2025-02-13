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


class WIFI:
    """
    Dummy implementation if MicroPython's network.WIFI class

    See: https://docs.micropython.org/en/latest/library/network.WLAN.html
    """

    # TODO: are these correct?
    IF_STA = 0
    IF_AP = 1

    # TODO: are these correct?
    PM_PERFORMANCE = 0
    PM_POWERSAVE = 1
    PM_NONE = 2

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
