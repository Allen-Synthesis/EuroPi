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

See https://docs.micropython.org/en/latest/library/network.WLAN.html for details on
wifi implementation
"""
from europi_config import (
    load_europi_config,
    MODEL_PICO_W,
    MODEL_PICO_2W,
)
from experimental.experimental_config import *


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
        try:
            import network
        except ImportError:
            raise WifiError("Failed to import network module")

        eu_cfg = load_europi_config()
        ex_cfg = load_experimental_config()

        if eu_cfg.PICO_MODEL != MODEL_PICO_2W and eu_cfg.PICO_MODEL != MODEL_PICO_W:
            raise WifiError(f"Hardware {eu_cfg.PICO_MODEL} doesn't support wifi")

        ssid = ex_cfg.WIFI_SSID
        password = ex_cfg.WIFI_PASSWORD
        channel = ex_cfg.WIFI_CHANNEL
        if ex_cfg.WIFI_BSSID:
            bssid = ex_cfg.WIFI_BSSID
        else:
            bssid = None

        if password:
            security = network.WLAN.SEC_WPA_WPA2
        else:
            security = network.WLAN.SEC_OPEN

        self._ssid = ssid
        if ex_cfg.WIFI_MODE == WIFI_MODE_AP:
            print("Starting wifi in AP mode...")
            try:
                self._nic = network.WLAN(network.WLAN.IF_AP)
                if self._nic.active():
                    self._nic.active(False)

                self._nic.config(
                    ssid=ssid,
                    channel=channel,
                    key=password,
                    security=security,
                )

                if not self._nic.active():
                    self._nic.active(True)
            except Exception as err:
                raise WifiError(f"Failed to enable AP mode: {err}")
        else:
            print("Starting wifi in client mode...")
            try:
                self._nic = network.WLAN(network.WLAN.IF_STA)
                if self._nic.active():
                    self._nic.active(False)
                if not self._nic.active():
                    self._nic.active(True)
                self._nic.connect(
                    ssid=ssid,
                    key=password,
                    bssid=bssid,
                    security=security,
                )

            except Exception as err:
                raise WifiError(f"Failed to connect to network {ssid}: {err}")

    @property
    def ip_addr(self) -> str:
        """Get our current IP address"""
        (addr, _, _, _) = self._nic.ifconfig()
        return addr

    @property
    def netmask(self) -> str:
        """Get our current netmask"""
        (_, netmask, _, _) = self._nic.ifconfig()
        return netmask

    @property
    def gateway(self) -> str:
        """Get our current gateway"""
        (_, _, gateway, _) = self._nic.ifconfig()
        return gateway

    @property
    def dns(self) -> str:
        """Get our primary DNS"""
        (_, _, _, dns) = self._nic.ifconfig()
        return dns

    @property
    def ssid(self) -> str:
        """Get the SSID of our wireless network"""
        return self._ssid

    @property
    def is_connected(self) -> bool:
        """
        Is the Pico connected to anything?

        In client mode this returns True if we're connected to an access point

        In AP mode this returns True if at least one client is connected to us
        """
        return self._nic.isconnected()

    @property
    def interface(self):
        """Get the underlying network.WLAN interface"""
        return self._nic
