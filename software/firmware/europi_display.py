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
Classes and definitions for interacting with the OLED display
"""

from machine import I2C, Pin
import ssd1306
from ssd1306 import SSD1306_I2C

# Default font is 8x8 pixel monospaced font.
CHAR_WIDTH = 8
CHAR_HEIGHT = 8


class Display(SSD1306_I2C):
    """
    A class for drawing graphics and text to the OLED.

    The OLED Display works by collecting all the applied commands and only
    updates the physical display when ``oled.show()`` is called. This allows
    you to perform more complicated graphics without slowing your program, or
    to perform the calculations for other functions, but only update the
    display every few steps to prevent lag.

    To clear the display, simply fill the display with the colour black by using ``oled.fill(0)``

    More explanations and tips about the the display can be found in the oled_tips file
    `oled_tips.md <https://github.com/Allen-Synthesis/EuroPi/blob/main/software/oled_tips.md>`_
    """

    def __init__(
        # fmt: off
        self,
        width,
        height,
        sda,
        scl,
        channel,
        freq,
        contrast,
        rotate
        # fmt: on
    ):
        i2c = I2C(channel, sda=Pin(sda), scl=Pin(scl), freq=freq)
        self.width = width
        self.height = height
        super().__init__(self.width, self.height, i2c)
        self.rotate(rotate)
        self.contrast(contrast)

    def rotate(self, rotate):
        """Flip the screen from its default orientation

        @param rotate  True or False, indicating whether we want to flip the screen from its default orientation
        """
        # From a hardware perspective, the default screen orientation of the display _is_ rotated
        # But logically we treat this as right-way-up.
        if rotate:
            rotate = 0
        else:
            rotate = 1
        self.write_cmd(ssd1306.SET_COM_OUT_DIR | ((rotate & 1) << 3))
        self.write_cmd(ssd1306.SET_SEG_REMAP | (rotate & 1))

    def centre_text(self, text, clear_first=True, auto_show=True):
        """Display one or more lines of text centred both horizontally and vertically.

        @param text  The text to display
        @param clear_first  If true, the screen buffer is cleared before rendering the text
        @param auto_show  If true, oled.show() is called after rendering the text. If false, you must call oled.show() yourself
        """
        if clear_first:
            self.fill(0)
        # Default font is 8x8 pixel monospaced font which can be split to a
        # maximum of 4 lines on a 128x32 display, but the maximum_lines variable
        # is rounded down for readability
        lines = str(text).split("\n")
        maximum_lines = round(self.height / CHAR_HEIGHT)
        if len(lines) > maximum_lines:
            raise Exception("Provided text exceeds available space on oled display.")
        padding_top = (self.height - (len(lines) * (CHAR_HEIGHT + 1))) / 2
        for index, content in enumerate(lines):
            x_offset = int((self.width - ((len(content) + 1) * (CHAR_WIDTH - 1))) / 2) - 1
            y_offset = int((index * (CHAR_HEIGHT + 1)) + padding_top) - 1
            self.text(content, x_offset, y_offset)

        if auto_show:
            self.show()


class DummyDisplay:
    """
    An alternative to Display that provides software compatibility, but no hardware interface

    Useful e.g when debugging a breadboard version of the module without a display connected
    """

    def __init__(self, width, height):
        self.width = width
        self.height = height

    def rotate(self, rotate):
        pass

    def centre_text(self, text, clear_first=True, auto_show=True):
        pass

    def show(self):
        pass

    def fill(self, color):
        pass

    def text(self, string, x, y, color=1):
        pass

    def line(self, x1, y1, x2, y2, color=1):
        pass

    def hline(self, x, y, length, color=1):
        pass

    def vline(self, x, y, length, color=1):
        pass

    def rect(self, x, y, width, height, color=1):
        pass

    def fill_rect(self, x, y, width, height, color=1):
        pass

    def ellipse(self, x, y, xr, yr, colour=1, fill=False):
        pass

    def blit(self, buffer, x, y):
        pass

    def scroll(self, x, y):
        pass

    def invert(self, color=1):
        pass

    def contrast(self, contrast):
        pass

    def pixel(self, x, y, color=1):
        pass
