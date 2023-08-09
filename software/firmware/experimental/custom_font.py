import framebuf

from machine import I2C
from machine import Pin
from ssd1306 import SSD1306_I2C

from europi import OLED_WIDTH, I2C_FREQUENCY, OLED_HEIGHT, I2C_CHANNEL, TEST_ENV, CHAR_HEIGHT


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
                    buf[i] = 0xFF & ~ v
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


class Display(SSD1306_I2C):
    """A class for drawing graphics and text to the OLED.

    The OLED Display works by collecting all the applied commands and only
    updates the physical display when ``oled.show()`` is called. This allows
    you to perform more complicated graphics without slowing your program, or
    to perform the calculations for other functions, but only update the
    display every few steps to prevent lag.

    To clear the display, simply fill the display with the colour black by using ``oled.fill(0)``

    More explanations and tips about the display can be found in the oled_tips file
    `oled_tips.md <https://github.com/Allen-Synthesis/EuroPi/blob/main/software/oled_tips.md>`_
    """

    def __init__(
            self,
            sda,
            scl,
            width=OLED_WIDTH,
            height=OLED_HEIGHT,
            channel=I2C_CHANNEL,
            freq=I2C_FREQUENCY,
            default_font=None  # by default will use the monospaced 8x8 font
    ):
        i2c = I2C(channel, sda=Pin(sda), scl=Pin(scl), freq=freq)
        self.width = width
        self.height = height
        self.writers = {}  # re-usable large font writer instances
        self.default_font = default_font
        if len(i2c.scan()) == 0:
            if not TEST_ENV:
                raise Exception(
                    "EuroPi Hardware Error:\nMake sure the OLED display is connected correctly"
                )
        super().__init__(self.width, self.height, i2c)

    def writer(self, font):
        """Returns the large font writer for the specified font."""
        n = font.__name__
        if n not in self.writers:
            self.writers[n] = CustomFontWriter(self, font)
        return self.writers[n]

    def text_width(self, s, font=None):
        """Returns the length of the string s in pixels."""
        if font or self.default_font:
            return self.writer(font or self.default_font).string_len(s)
        else:
            return len(s) * CHAR_HEIGHT

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
        """Display the string s using the x, y coordinates as the upper-left corner of the text.
        """
        if font or self.default_font:
            self.writer(font or self.default_font).print(s, x, y, c)
        else:
            super().text(s, x, y, c)

    def centre_text(self, text, font=None):
        """Split the provided text across 3 lines of display."""

        self.fill(0)

        # Default font is 8x8 pixel monospaced font which can be split to a
        # maximum of 4 lines on a 128x32 display, but we limit it to 3 lines
        # for readability.

        if font or self.default_font:
            # f = font or self.default_font

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
            lines = str(text).split("\n")
            maximum_lines = round(self.height / CHAR_HEIGHT)
            if len(lines) > maximum_lines:
                raise Exception("Provided text exceeds available space on oled display.")
            padding_top = (self.height - (len(lines) * 9)) / 2
            for index, content in enumerate(lines):
                x_offset = int((self.width - ((len(content) + 1) * 7)) / 2) - 1
                y_offset = int((index * 9) + padding_top) - 1
                self.text(content, x_offset, y_offset)

        self.show()