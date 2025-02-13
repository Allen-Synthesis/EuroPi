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
Enables managing the wireless connection on the Pico W and Pico 2 W

Wifi credentials are saved via experimental_config
"""
from europi_config import (
    load_europi_config,
    MODEL_PICO_W,
    MODEL_PICO_2W,
)
from experimental.experimental_config import *
from mpython import wifi


class WifiError(Exception):
    """Custom exception for wifi related errors"""

    def __init__(self, message):
        super().__init__(message)


class WifiConnection:
    """
    Class to manage the wifi connection

    Raises a WifiError if the model doesn't support wifi
    """
    def __init__(self):
        eu_cfg = load_europi_config()
        ex_cfg = load_experimental_config()

        if eu_cfg.PICO_MODEL != MODEL_PICO_2W and eu_cfg.PICO_MODEL != MODEL_PICO_W:
            raise WifiError(f"Hardware {eu_cfg.PICO_MODEL} doesn't support wifi")

        self.ssid = ex_cfg.WIFI_SSID
        self.password = ex_cfg.WIFI_PASSWORD
        self.wifi = wifi()

        if ex_cfg.WIFI_MODE == WIFI_MODE_AP:
            self.enable_ap()
        else:
            self.connect()

    def connect(self):
        try:
            self.wifi = wifi()
            wifi.connectWiFi(
                self.ssid,
                self.password,
                timeout=30
            )
        except Exception as err:
            raise WifiError(f"Failed to connect to network: {err}")

    def disconnect(self):
        self.wifi.disconnectWiFi()

    def enable_ap(self):
        self.wifi.enable_APWiFi(self.ssid, self.password, timeout=30)

    def disable_ap(self):
        self.wifi.disable_APWiFi()