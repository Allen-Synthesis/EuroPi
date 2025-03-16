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
"""Additional configuration settings for experimental firmware features

Any scripts in firmware/experimental that need editiable, persistent settings should use this. If/when
they're moved out of experimental, their associated settings should be migrated to europi_config.py
"""

import configuration
from configuration import ConfigFile, ConfigSpec

# Moog/Eurorack standard is 1.0 volts per octave
MOOG_VOLTS_PER_OCTAVE = 1.0

# Buchla standard is 1.2 volts per octave (0.1 volts per semitone)
BUCHLA_VOLTS_PER_OCTAVE = 1.2

# RTC implementations
RTC_NONE = ""
RTC_DS3231 = "ds3231"
RTC_DS1307 = "ds1307"
RTC_NTP = "ntp"

# WIFI modes
WIFI_MODE_AP = "access_point"
WIFI_MODE_CLIENT = "client"


class ExperimentalConfig:
    """This class provides global config points for experimental features.

    To override the default values, create /config/config_ExperimentalConfig.json on the Raspberry Pi Pico
    and populate it with a JSON object. e.g. if your build needs Buchla compatibility using 1.2V/octave
    quantization, it should look like this:

    {
        "VOLTS_PER_OCTAVE": 1.2
    }
    """

    @classmethod
    def config_points(cls):
        # fmt: off
        return [
            # Quantizer settings
            # Normally this is intended for Eurorack compatibility, but being open-source someone may
            # want to use it in an ecosystem that uses different specs
            configuration.choice(
                "VOLTS_PER_OCTAVE",
                choices=[MOOG_VOLTS_PER_OCTAVE, BUCHLA_VOLTS_PER_OCTAVE],
                default=MOOG_VOLTS_PER_OCTAVE,
            ),

            # RTC implementation
            # by default there is no RTC
            configuration.choice(
                "RTC_IMPLEMENTATION",
                choices=[
                    RTC_NONE,
                    RTC_DS3231,
                    RTC_DS1307,
                    RTC_NTP,
                ],
                default=RTC_NONE,
            ),

            # RTC Timezone offset for local time
            configuration.integer(
                "UTC_OFFSET_HOURS",
                minimum=-24,
                maximum=24,
                default=0,
            ),
            configuration.integer(
                "UTC_OFFSET_MINUTES",
                minimum=-59,
                maximum=59,
                default=0,
            ),

            # Wifi connection options
            # only applicable with Pico W, Pico 2 W
            configuration.choice(
                "WIFI_MODE",
                choices=[
                    WIFI_MODE_CLIENT,
                    WIFI_MODE_AP
                ],
                default=WIFI_MODE_AP,
            ),
            configuration.string(
                "WIFI_SSID",
                default="EuroPi",
            ),
            configuration.string(
                "WIFI_PASSWORD",
                default="europi",
            ),
            configuration.integer(
                "WIFI_CHANNEL",
                minimum=1,
                maximum=13,
                default=10,
            ),
            configuration.string(
                "WIFI_BSSID",
                default="",
            ),
            configuration.boolean(
                "WIFI_DHCP",
                default=True
            ),
            configuration.string(
                "WIFI_IP",
                default="192.168.4.1"
            ),
            configuration.string(
                "WIFI_NETMASK",
                default="255.255.255.0"
            ),
            configuration.string(
                "WIFI_GATEWAY",
                default="0.0.0.0"
            ),
            configuration.string(
                "WIFI_DNS",
                default="8.8.8.8"
            ),

            # WebREPL support
            # requires wifi configuration (above)
            configuration.boolean(
                "ENABLE_WEBREPL",
                default=False
            ),
        ]
        # fmt: on


def load_experimental_config():
    return ConfigFile.load_config(
        ExperimentalConfig, ConfigSpec(ExperimentalConfig.config_points())
    )
