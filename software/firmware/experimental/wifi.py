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
from europi_hardware import b1, b2
from experimental.experimental_config import *

from europi_log import *
import utime


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

        self._ssid = ex_cfg.WIFI_SSID

        nic = network.WLAN()
        if nic.status() == network.STAT_GOT_IP:
            # see if we have a lingering connection from the previous boot
            self._nic = nic
            log_info(
                f"NIC reports we already have an IP address: {self.ip_addr}. Re-using exising connection",
                "wifi",
            )
        elif ex_cfg.WIFI_MODE == WIFI_MODE_AP:
            log_info("Starting wifi in AP mode...", "wifi")
            try:
                self.connect_ap(ex_cfg)
                log_info(f"Access point {self.ssid} is up. {self.ip_addr}", "wifi")
            except Exception as err:
                raise WifiError(f"Failed to enable AP mode: {err}")
        else:
            log_info("Starting wifi in client mode...", "wifi")
            try:
                self.connect_station(ex_cfg)
                log_info(f"Connected to {self.ssid}: {self.ip_addr}", "wifi")
            except Exception as err:
                log_error(f"Failed to connect to network {ex_cfg.WIFI_SSID}: {err}", "wifi")
                raise WifiError(f"Failed to connect to network {ex_cfg.WIFI_SSID}: {err}")

        if ex_cfg.ENABLE_WEBREPL:
            log_info("Starting WebREPL...", "wifi")
            self.setup_webrepl()
            self.start_webrepl()

    def connect_station(self, cfg):
        """
        Connect to an external wireless router as a client

        @param cfg  The ExperimentalConfig object
        """
        import network

        ssid = cfg.WIFI_SSID
        password = cfg.WIFI_PASSWORD
        bssid = cfg.WIFI_BSSID
        if len(bssid) == 0:
            bssid = None
        if password:
            security = network.WLAN.SEC_WPA_WPA2
        else:
            security = network.WLAN.SEC_OPEN

        self._nic = network.WLAN(network.WLAN.IF_STA)
        if self._nic.active():
            self._nic.active(False)

        if not cfg.WIFI_DHCP:
            self._nic.ifconfig(
                (
                    cfg.WIFI_IP,
                    cfg.WIFI_NETMASK,
                    cfg.WIFI_GATEWAY,
                    cfg.WIFI_DNS,
                )
            )

        if not self._nic.active():
            self._nic.active(True)

        # connecting can take some time, so give it a couple of tries
        max_tries = 3
        current_try = 1
        while current_try < max_tries and current_try > 0:
            log_info(f"Connecting to {ssid}... ({current_try})", "wifi")
            self._nic.connect(
                ssid=ssid,
                key=password,
                bssid=bssid,
                security=security,
            )

            connect_timeout_ms = 15_000
            start_time = utime.ticks_ms()
            abort_wifi = False
            while (
                not abort_wifi
                and not self.is_connected
                and utime.ticks_diff(utime.ticks_ms(), start_time) <= connect_timeout_ms
            ):
                abort_wifi = b1.value() != 0 or b2.value() != 0

            if abort_wifi:
                log_info("User aborted wifi connection", "wifi")
                raise WifiError("User aborted wifi connection")
            elif self.is_connected:
                log_info("Connection established!", "wifi")
                current_try = -1
            else:
                log_warning("Timed-out waiting for connection. Will try again.", "wifi")
                current_try += 1

        if current_try > 0:
            raise WifiError(f"Failed to connect to network {ssid}")

    def connect_ap(self, cfg):
        """
        Connect in access point mode

        We can optionally set the IP address and netmask in this mode

        @param cfg  The ExperimentalConfig object
        """
        import network

        ssid = cfg.WIFI_SSID
        password = cfg.WIFI_PASSWORD
        channel = cfg.WIFI_CHANNEL

        if password:
            security = network.WLAN.SEC_WPA_WPA2
        else:
            security = network.WLAN.SEC_OPEN

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

    def setup_webrepl(self):
        """
        Create the additional configuration files needed for WebREPL.

        Creates the following files (if they do not exist already):
        - /boot.py (empty)
        - /webrepl_cfg.py (contains default WebREPL password)
        """

        def exists(path):
            import os

            try:
                os.stat(path)
                return True
            except OSError:
                return False

        if not exists("/boot.py"):
            log_info("Creating empty /boot.py for WebREPL...", "wifi")
            with open("/boot.py", "w") as boot_py:
                boot_py.write("\n")

        if not exists("/webrepl_cfg.py"):
            log_info("Creating default /webrepl_cfg.py for WebREPL...", "wifi")
            with open("/webrepl_cfg.py", "w") as webrepl_cfg_py:
                webrepl_cfg_py.write('PASS = "EuroPi"\n')

    def start_webrepl(self):
        import webrepl

        webrepl.start()
