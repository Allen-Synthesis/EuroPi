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

    ## The EuroPi logo as a 14x16 image
    LOGO = bytearray(b'\x00p\x18\x88&\x84AX1 E\x18\x99DiT\x1a(%\x10H\x88AD"$\x10X\x0c\x80\x03\x00')
    LOGO_WIDTH = 14
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
