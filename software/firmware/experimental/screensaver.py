"""A simple screensaver class for the EuroPi

@author Chris Iverach-Brereton <ve4cib@gmail.com>
@year   2023
"""

from europi import *
import random
import time


class Screensaver:
    """A screensaver for the EuroPi

    This class' draw() function should be called from inside the application's main loop
    to draw the screensaver.

    At regular intervals the EuroPi logo will be drawn to a random location on the screen.

    Alternatively draw_blank() will simply clear the screen
    """

    ## The EuroPi logo as a 16x16 image
    LOGO = bytearray(
        b"\x01\xc0\x03p;\x18n1\xc0c\xf8\xc6\x0c\x93\r\xb9\x19-\xf37\xc6\x12\x0c\x98\x19\xc83L\x1el\x0c8"
    )
    LOGO_WIDTH = 16
    LOGO_HEIGHT = 16

    def draw(self, force=False):
        """Draw the logo to a random position on the screen

        If the current ticks_ms is an even multiple of the screensaver interval,
        or the `force` paramter is True, we will draw.  Otherwise this does
        nothing

        @param force  Force the logo to be drawn, regardless of the current ticks
        """
        LOGO_UPDATE_INTERVAL = 2000

        ms = time.ticks_ms()
        if force or ms % LOGO_UPDATE_INTERVAL == 0:
            x = random.randint(0, OLED_WIDTH - self.LOGO_WIDTH)
            y = random.randint(0, OLED_HEIGHT - self.LOGO_HEIGHT)

            oled.fill(0)
            fb = FrameBuffer(self.LOGO, self.LOGO_WIDTH, self.LOGO_HEIGHT, MONO_HLSB)
            oled.blit(fb, x, y)
            oled.show()

    def draw_blank(self):
        """Blank the screen completely"""
        oled.fill(0)
        oled.show()
