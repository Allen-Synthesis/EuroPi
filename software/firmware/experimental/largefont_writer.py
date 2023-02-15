"""
Large font write
author: François Georgy (https://github.com/francoisgeorgy)
date: 2023-02-15

Basic large font writer adapted from https://github.com/peterhinch/micropython-font-to-py/tree/master/writer

To create font files, use https://github.com/peterhinch/micropython-font-to-py/blob/master/font_to_py.py.

The fonts in this folder have been generated with :

    python3 font_to_py.py FreeSans.ttf 14 freesans14.py -x
    python3 font_to_py.py FreeSans.ttf 17 freesans17.py -x
    python3 font_to_py.py FreeSans.ttf 20 freesans20.py -x
    python3 font_to_py.py FreeSans.ttf 24 freesans24.py -x

The -x option is important to have the font horizontally mapped.
"""
import framebuf


class Writer:

    def __init__(self, device, font):
        """Initialize the Writer.

        device: the OLED display instance
        font: a font module created with the script referenced above.
        """
        self.device = device
        self.font = font
        if font.hmap():
            self.map = framebuf.MONO_HMSB if font.reverse() else framebuf.MONO_HLSB
        else:
            raise ValueError('Font must be horizontally mapped.')
        self.screenwidth = device.width  # In pixels
        self.screenheight = device.height

    def print(self, string, x, y, invert=False):
        """Print the string using the x, y coordinates as the upper-left corner of the text.
        With invert=True, the text is display as black text on white background.
        """
        for char in string:
            if char == '\n':    # line breaks are ignored
                return
            glyph, char_height, char_width = self.font.get_ch(char)
            # If the text does not fit in the display, the text is not displayed.
            if y + char_height > self.screenheight:
                return
            if x + char_width > self.screenwidth:
                return
            buf = bytearray(glyph)
            if invert:
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
        if char == '\n':
            char_width = 0
        else:
            _, _, char_width = self.font.get_ch(char)
        return char_width
