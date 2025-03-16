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
"""
Before using any of this library, follow the instructions in
`programming_instructions.md <https://github.com/Allen-Synthesis/EuroPi/blob/main/software/programming_instructions.md>`_
to set up your module.

The EuroPi library is a single file named europi.py. It should be imported into any custom program by using ``from europi import *`` to give you full access to the functions within, which are outlined below. Inputs and outputs are used as objects, which each have methods to allow them to be used. These methods are used by using the name of the object, for example 'cv3' followed by a '.' and then the method name, and finally a pair of brackets containing any parameters that the method requires.

For example::

    cv3.voltage(4.5)

Will set the CV output 3 to a voltage of 4.5V.
"""


import sys

from version import __version__

from configuration import ConfigSettings
from framebuf import FrameBuffer, MONO_HLSB

from europi_config import load_europi_config, MODEL_PICO_2W, MODEL_PICO_W
from europi_display import Display, DummyDisplay
from europi_hardware import *
from europi_log import *

from experimental.experimental_config import load_experimental_config
from experimental.wifi import WifiConnection, WifiError


if sys.implementation.name == "micropython":
    TEST_ENV = False  # We're in micropython, so we can assume access to real hardware
else:
    TEST_ENV = True  # This var is set when we don't have any real hardware, for example in a test or doc generation setting

# Initialize EuroPi global singleton instance variables
europi_config = load_europi_config()
experimental_config = load_experimental_config()

# OLED component display dimensions.
OLED_WIDTH = europi_config.DISPLAY_WIDTH
OLED_HEIGHT = europi_config.DISPLAY_HEIGHT

# Default font is 8x8 pixel monospaced font.
CHAR_WIDTH = 8
CHAR_HEIGHT = 8


# Helper functions.


def turn_off_all_cvs():
    """Calls cv.off() for every cv in cvs. This is done commonly enough in
    contrib scripts that a function seems useful.
    """
    for cv in cvs:
        cv.off()


def reset_state():
    """Return device to initial state with all components off and handlers reset."""
    if not TEST_ENV:
        oled.fill(0)
        oled.show()
    turn_off_all_cvs()
    for d in (b1, b2, din):
        d.reset_handler()


def bootsplash():
    """Display the EuroPi version when booting."""
    image = b"\x00\x00\x00\x03\xe0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x07\xf8\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x06\x1c\x00\x00\x00\x00\x00\x00\x00\x01\x80\x00\x00\x00\x00\x00\x07\x0f\xe0\x00\x00\x00\x00\x00\x00\x01\x80\x00\x00\x00\x00\x00\x03\x07\xf0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x800\x00\xc0\x00\x00\x0e\x01\xc0\x00\x00\x00\x00\x00\x07\xe0\xc0p\x03\xf0\xc1\x971\x8e1\x80\x00\x00\x00\x00\x1f\xf8\xc1\xe0\x06\x18\xc1\x98`\xcc\x19\x80\x00\x00\x00\x00\x1c\x1f\xc3\x83\x04\x0c\xc1\x98@L\t\x80\x00\x00\x00\x000\x07\x87\x07\x0c\x0c\xc1\x90@H\t\x80\x00\x00\x00\x000\x00\x0e\x0e\x0f\xf8\xc1\x90@H\t\x80\x00\x00\x00\x008\x00\x1c\x0c\x0c\x00\xc1\x90@H\t\x80\x00\x00\x00\x00\x1f\x808\x0e\x04\x00\xc1\x90`\xcc\x19\x80\x00\x00\x00\x00\x0f\xe01\xc7\x06\x18c\x101\x8e1\x80\x00\x00\x00\x00\x00ps\xe3\x01\xe0\x1c\x10\x0e\r\xc1\x80\x00\x00\x00\x00\x00\x18c1\x80\x00\x00\x00\x00\x0c\x00\x00\x00\x00\x00\x00\x00\x18\xe31\x80\x00\x00\x00\x00\x0c\x00\x00\x00\x00\x00\x00\x008\xc1\x99\x80\x00\x00\x00\x00\x0c\x00\x00\x00\x00\x00\x00\x0e1\xc1\x99\x80\x00\x00\x00\x00\x0c\x00\x00\x00\x00\x00\x00\x1f\xe3\x80\xcf\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00;\xc7\x00\xc6\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x000\x0e\x00@\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x000\x1c\x00`\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00xp`\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xf0\xf80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\xc1\xd80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x03\x83\x980\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x03\x07\x180\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x86\x0c`\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xfe\x0e\xe0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00|\x07\xc0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x03\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
    TH = bytearray(image)
    fb = FrameBuffer(TH, 128, 32, MONO_HLSB)
    oled.blit(fb, 0, 0)

    version_str = str(__version__)
    version_length = len(version_str)
    offset = int(((150 - (version_length * CHAR_WIDTH)) / 2))
    oled.text(version_str, offset, 20, 1)

    oled.show()


# Initialize the OLED
if not TEST_ENV:
    try:
        oled = Display(
            width=europi_config.DISPLAY_WIDTH,
            height=europi_config.DISPLAY_HEIGHT,
            sda=europi_config.DISPLAY_SDA,
            scl=europi_config.DISPLAY_SCL,
            channel=europi_config.DISPLAY_CHANNEL,
            freq=europi_config.DISPLAY_FREQUENCY,
            contrast=europi_config.DISPLAY_CONTRAST,
            rotate=europi_config.ROTATE_DISPLAY,
        )
    except Exception as err:
        log_warning(
            f"Failed to initialize display: {err}. Is the hardware connected properly?", "europi"
        )
        oled = DummyDisplay(
            width=europi_config.DISPLAY_WIDTH,
            height=europi_config.DISPLAY_HEIGHT,
        )
else:
    log_warning("No display hardware detected; falling back to DummyDisplay", "europi")
    oled = DummyDisplay(
        width=europi_config.DISPLAY_WIDTH,
        height=europi_config.DISPLAY_HEIGHT,
    )

# Connect to wifi, if supported
if europi_config.PICO_MODEL == MODEL_PICO_W or europi_config.PICO_MODEL == MODEL_PICO_2W:
    try:
        oled.centre_text(
            f"""WiFi connecting
{experimental_config.WIFI_SSID}
Cancel: B1"""
        )
        wifi_connection = WifiConnection()
    except WifiError as err:
        wifi_connection = None
else:
    wifi_connection = None

# Reset the module state upon import.
reset_state()
