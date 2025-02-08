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
import framebuf

from machine import I2C
from machine import Pin
from ssd1306 import SSD1306_I2C

from europi import (
    europi_config,
    TEST_ENV,
    CHAR_HEIGHT,
)
from europi_display import Display as BasicDisplay


# TODO: add a method to select the font to use by default


class CustomFontWriter:
    def __init__(self, device, font):
        """Initialize the Writer.

        device: the OLED display instance
        font: a font module
        """
        self.device = device
        self.font = font
        if font.hmap():
            self.map = framebuf.MONO_HMSB if font.reverse() else framebuf.MONO_HLSB
        else:
            raise ValueError("Font must be horizontally mapped.")
        self.screenwidth = device.width  # In pixels
        self.screenheight = device.height

    def print(self, string, x, y, c=1):
        """Print the string using the x, y coordinates as the upper-left corner of the text.
        With c=0, the text is display as black text on white background.
        """
        for char in string:
            if char == "\n":  # line breaks are ignored
                return
            glyph, char_height, char_width = self.font.get_ch(char)
            buf = bytearray(glyph)
            if c != 1:
                for i, v in enumerate(buf):
                    buf[i] = 0xFF & ~v
            fbc = framebuf.FrameBuffer(buf, char_width, char_height, self.map)
            self.device.blit(fbc, x, y)
            x += char_width

    def string_len(self, string):
        """Returns the length of string in pixels."""
        n = 0
        for char in string:
            n += self._char_len(char)
        return n

    def _char_len(self, char):
        """Returns the length of char in pixels."""
        if char == "\n":
            char_width = 0
        else:
            _, _, char_width = self.font.get_ch(char)
        return char_width


class CustomFontDisplay(BasicDisplay):
    """A class for adding custom font capability to the OLED display.

    This class can be used identically to the parent class, with the added
    parameter of 'font' which can be passed when using any of the methods to
    specify an alternative to the default 8x8 pixel font
    """

    def __init__(self, default_font=None):  # by default will use the monospaced 8x8 font
        self.writers = {}  # re-usable large font writer instances
        self.default_font = default_font
        super().__init__(
            width=europi_config.DISPLAY_WIDTH,
            height=europi_config.DISPLAY_HEIGHT,
            sda=europi_config.DISPLAY_SDA,
            scl=europi_config.DISPLAY_SCL,
            channel=europi_config.DISPLAY_CHANNEL,
            freq=europi_config.DISPLAY_FREQUENCY,
            contrast=europi_config.DISPLAY_CONTRAST,
            rotate=europi_config.ROTATE_DISPLAY,
        )

    def _writer(self, font):
        """Returns the large font writer for the specified font."""
        n = font.__name__
        if n not in self.writers:
            self.writers[n] = CustomFontWriter(self, font)
        return self.writers[n]

    def text_width(self, s, font=None):
        """Returns the length of the string s in pixels."""
        if font or self.default_font:
            return self._writer(font or self.default_font).string_len(s)
        else:
            return len(s) * CHAR_WIDTH

    def text_height(self, s=None, font=None):
        """Returns the height of the font s in pixels.
        The name text_height() is to be coherent with the text_width() method above.
        The string s is optional and ignored if present. The parameter is
        there for a future version which could return a more precise value based on
        the supplied text.
        """
        if font:
            return font.height()
        elif self.default_font:
            return self.default_font.height()
        else:
            return CHAR_HEIGHT

    def text(self, s, x, y, c=1, font=None):
        """Display the string s using the x, y coordinates as the upper-left corner of the text."""
        if font or self.default_font:
            self._writer(font or self.default_font).print(s, x, y, c)
        else:
            super().text(s, x, y, c)

    def centre_text(self, text, clear_first=True, auto_show=True, font=None):
        """Split the provided text across 3 lines of display."""

        # Default font is 8x8 pixel monospaced font which can be split to a
        # maximum of 4 lines on a 128x32 display, but we limit it to 3 lines
        # for readability.

        if font or self.default_font:
            # f = font or self.default_font

            if clear_first:
                self.fill(0)

            lines = str(text).split("\n")
            maximum_lines = self.height // self.text_height(font=font)
            if len(lines) > maximum_lines:
                raise Exception("Provided text exceeds available space on oled display.")

            h = self.text_height(font=font) + 1
            padding_top = (self.height - (len(lines) * h)) // 2

            for index, content in enumerate(lines):
                w = self.text_width(content, font=font)
                x_offset = int((self.width - w) / 2) - 1
                y_offset = index * h + padding_top
                self.text(content, x_offset, y_offset, font=font)

        else:
            super().centre_text(text, clear_first=clear_first, auto_show=auto_show)

        if auto_show:
            self.show()


oled = CustomFontDisplay()
