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
import configuration
from configuration import ConfigFile, ConfigSpec


# sub-key constants for CPU_FREQS dict (see below)
# the Europi default is to overclock, so to avoid confusion about the default
# not being "default" just use a different word
# fmt: off
DEFAULT_FREQ = "normal"
OVERCLOCKED_FREQ = "overclocked"
UNDERCLOCKED_FREQ = "underclocked"
# fmt: on

# Supported Pico model types
MODEL_PICO = "pico"
MODEL_PICO_H = "pico h"
MODEL_PICO_W = "pico w"
MODEL_PICO_2 = "pico 2"
MODEL_PICO_2W = "pico 2w"

# Default & overclocked CPU frequencies for supported boards
# Key: board type (corresponds to EUROPI_MODEL setting)
# Sub-key: "default" or "overclocked" or "underclocked"
# fmt: off
CPU_FREQS = {
    MODEL_PICO: {
        DEFAULT_FREQ: 125_000_000,      # Pico default frequency is 125MHz
        OVERCLOCKED_FREQ: 250_000_000,  # Overclocked frequency is 250MHz
        UNDERCLOCKED_FREQ: 75_000_000   # Underclock to 75MHz
    },
    MODEL_PICO_2: {
        DEFAULT_FREQ: 150_000_000,      # Pico 2 default frequency is 150MHz
        OVERCLOCKED_FREQ: 300_000_000,  # Overclocked frequency is 300MHz
        UNDERCLOCKED_FREQ: 75_000_000,  # Underclock to 75MHz
    },
    MODEL_PICO_2W: {
        DEFAULT_FREQ: 150_000_000,      # Pico 2 W default frequency is 150MHz
        OVERCLOCKED_FREQ: 250_000_000,  # Overclocked frequency is 250MHz; 300MHz breaks wifi. See https://github.com/micropython/micropython/issues/16799
        UNDERCLOCKED_FREQ: 75_000_000,  # Underclock to 75MHz
    },
    MODEL_PICO_H: {
        DEFAULT_FREQ: 125_000_000,      # Pico H default frequency is 125MHz
        OVERCLOCKED_FREQ: 250_000_000,  # Overclocked frequency is 250MHz
        UNDERCLOCKED_FREQ: 75_000_000,  # Underclock to 75MHz
    },
    MODEL_PICO_W: {
        DEFAULT_FREQ: 125_000_000,      # Pico W default frequency is 125MHz
        OVERCLOCKED_FREQ: 250_000_000,  # Overclocked frequency is 250MHz
        UNDERCLOCKED_FREQ: 75_000_000,  # Underclock to 75MHz
    }
}
# fmt: on


class EuroPiConfig:
    """This class provides EuroPi's global config points.

    To override the default values, create /config/EuroPiConfig.json on the Raspberry Pi Pico
    and populate it with a JSON object. e.g. if your build has the oled mounted upside-down compared
    to normal, the contents of /config/EuroPiConfig.json should look like this:

    {
        "ROTATE_DISPLAY": true
    }
    """

    @classmethod
    def config_points(cls):
        # fmt: off
        return [
            # EuroPi revision -- this is currently unused, but reserved for future expansion
            configuration.choice(
                name="EUROPI_MODEL",
                choices = ["europi"],
                default="europi",
            ),

            # CPU & board settings
            configuration.choice(
                name="PICO_MODEL",
                choices=[
                    MODEL_PICO,
                    MODEL_PICO_W,
                    MODEL_PICO_H,
                    MODEL_PICO_2,
                    MODEL_PICO_2W,
                ],
                default=MODEL_PICO,
            ),
            configuration.choice(
                name="CPU_FREQ",
                choices=[
                    DEFAULT_FREQ,
                    OVERCLOCKED_FREQ,
                    UNDERCLOCKED_FREQ,
                ],
                default=OVERCLOCKED_FREQ,
            ),

            # Display settings
            configuration.boolean(
                name="ROTATE_DISPLAY",
                default=False,
            ),
            configuration.integer(
                name="DISPLAY_CONTRAST",
                minimum=0,
                maximum=255,
                default=255,
            ),
            configuration.integer(
                name="DISPLAY_WIDTH",
                minimum=8,
                maximum=1024,
                default=128,
                danger=True,
            ),
            configuration.integer(
                name="DISPLAY_HEIGHT",
                minimum=8,
                maximum=1024,
                default=32,
                danger=True,
            ),
            configuration.choice(
                name="DISPLAY_SDA",
                choices=[0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 26],
                default=0,
                danger=True,
            ),
            configuration.choice(
                name="DISPLAY_SCL",
                choices=[1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 27],
                default=1,
                danger=True,
            ),
            configuration.choice(
                name="DISPLAY_CHANNEL",
                choices=[0, 1],
                default=0,
                danger=True,
            ),
            configuration.choice(
                name="DISPLAY_FREQUENCY",
                choices=[
                    100000,  # 100k (Sm)
                    400000,  # 400k (Fm)
                    1000000, # 1M   (Fm+)
                    1700000, # 1.7M (Hs)
                    3400000, # 3.4M (Hs)
                    5000000, # 5M   (UFm)
                ],
                default=400000,
                danger=True,
            ),

            # External I2C connection (header between Pico & power connector)
            configuration.choice(
                name="EXTERNAL_I2C_SDA",
                choices=[0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 26],
                default=2,
            ),
            configuration.choice(
                name="EXTERNAL_I2C_SCL",
                choices=[1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 27],
                default=3,
            ),
            configuration.choice(
                name="EXTERNAL_I2C_CHANNEL",
                choices=[0, 1],
                default=1,
            ),
            configuration.choice(
                name="EXTERNAL_I2C_FREQUENCY",
                choices=[
                    100000,  # 100k (Sm)
                    400000,  # 400k (Fm)
                    1000000, # 1M   (Fm+)
                    1700000, # 1.7M (Hs)
                    3400000, # 3.4M (Hs)
                    5000000, # 5M   (UFm)
                ],
                default=100000,
            ),
            configuration.choice(
                name="EXTERNAL_I2C_TIMEOUT",
                choices=[
                    # somewhat arbitrary subset of 0-5000
                    # this should cover a good range of use-cases
                    0,
                    1,
                    5,
                    10,
                    25,
                    50,
                    100,
                    250,
                    500,
                    1000,
                    2500,
                    5000,
                ],
                default=1000,
            ),

            # I/O voltage settings
            configuration.floatingPoint(
                name="MAX_OUTPUT_VOLTAGE",
                minimum=1.0,
                maximum=10.0,
                default=10.0,
            ),
            configuration.floatingPoint(
                name="MAX_INPUT_VOLTAGE",
                minimum=1.0,
                maximum=12.0,
                default=10.0,
            ),
            configuration.floatingPoint(
                name="GATE_VOLTAGE",
                minimum=1.0,
                maximum=10.0,
                default=5.0,
            ),

            # Menu settings
            configuration.boolean(
                name="MENU_AFTER_POWER_ON",
                default=False,
            ),
        ]
        # fmt: on


def load_europi_config():
    return ConfigFile.load_config(EuroPiConfig, ConfigSpec(EuroPiConfig.config_points()))
