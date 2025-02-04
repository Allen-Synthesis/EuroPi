# Copyright 2023 Allen Synthesis
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
# limitations under the License."""A simple screensaver class for the EuroPi
"""
A simple screensaver implementation for EuroPi

@author Chris Iverach-Brereton <ve4cib@gmail.com>
@year   2023
"""

import random
import utime

from europi import *


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

    ## Standard duration before we activate the screensaver
    ACTIVATE_TIMEOUT_MS = 1000 * 60 * 5
    ACTIVATE_TIMEOUT_US = ACTIVATE_TIMEOUT_MS * 1000

    ## Standard duration before we blank the screen
    BLANK_TIMEOUT_MS = 1000 * 60 * 20
    BLANK_TIMEOUT_US = BLANK_TIMEOUT_MS * 1000

    def __init__(self):
        self.last_logo_reposition_at = 0

    def draw(self, force=False):
        """Draw the logo to a random position on the screen

        If the current ticks_ms is an even multiple of the screensaver interval,
        or the `force` paramter is True, we will draw.  Otherwise this does
        nothing

        @param force  Force the logo to be drawn, regardless of the current ticks
        """
        LOGO_UPDATE_INTERVAL = 2000

        now = utime.ticks_ms()
        elapsed_ms = time.ticks_diff(now, self.last_logo_reposition_at)
        if force or abs(elapsed_ms) >= LOGO_UPDATE_INTERVAL:
            self.last_logo_reposition_at = now
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


class OledWithScreensaver:
    """A wrapper for europi.oled that provides automatic screensaver & blank if enabled

    The notify_user_interaction() method should be called in the ISR for any events that should interrupt or
    defer the screensaver/blank

    Set .enable_screensaver or .enable_blank to False to disable the screensaver/blanking activation completely
    (though if you do that, just use europi.oled instead of this class)
    """

    def __init__(self, enable_screensaver=True, enable_blank=True):
        """Constructor

        @param enable_screensaver  If true, the screensaver will activate when needed
        @param enable_blank        If true, the screen will blank after the screensaver has been active for a while
        """
        self.screensaver = Screensaver()
        self.enable_screensaver = enable_screensaver
        self.enable_blank = enable_blank

        self.show_screensaver = False
        self.show_blank = False

        self.last_user_interaction_at = utime.ticks_ms()

    def is_screenaver(self):
        """Is the screensaver currently showing?"""
        return self.show_screensaver

    def is_blank(self):
        """Is the screen blanked due to inactivity?"""
        return self.show_blank

    def notify_user_interaction(self):
        """Notifies the screensaver subsystem that the user has physically interacted with the module
        and that the screensaver should defer/shutdown as appropriate
        """
        self.last_user_interaction_at = utime.ticks_ms()

    def show(self):
        now = utime.ticks_ms()
        if (
            self.enable_blank
            and utime.ticks_diff(now, self.last_user_interaction_at)
            > self.screensaver.BLANK_TIMEOUT_MS
        ):
            self.show_blank = True
            self.show_screensaver = False
            self.screensaver.draw_blank()
        elif (
            self.enable_screensaver
            and utime.ticks_diff(now, self.last_user_interaction_at)
            > self.screensaver.ACTIVATE_TIMEOUT_MS
        ):
            self.show_screensaver = True
            self.show_blank = False
            self.screensaver.draw()
        else:
            self.show_blank = False
            self.show_screensaver = False
            oled.show()

    # The following are just wrappers for the functions in the Display class to allow 1:1 access
    # See europi.Display for documentation details

    def fill(self, color):
        oled.fill(color)

    def text(self, string, x, y, color=1):
        oled.text(string, x, y, color)

    def centre_text(self, text, clear_first=True, auto_show=True):
        oled.centre_text(text, clear_first=clear_first, auto_show=False)
        if auto_show:
            self.show()

    def line(self, x1, y1, x2, y2, color=1):
        oled.line(x1, y1, x2, y2, color)

    def hline(self, x, y, length, color=1):
        oled.hline(x, y, length, color)

    def vline(self, x, y, length, color=1):
        oled.vline(x, y, length, color)

    def rect(self, x, y, width, height, color=1):
        oled.rect(x, y, width, height, color)

    def fill_rect(self, x, y, width, height, color=1):
        oled.fill_rect(x, y, width, height, color)

    def ellipse(self, x, y, xr, yr, colour=1, fill=False):
        oled.ellipse(x, y, xr, yr, colour, fill)

    def blit(self, buffer, x, y):
        oled.blit(buffer, x, y)

    def scroll(self, x, y):
        oled.scroll(x, y)

    def invert(self, color=1):
        oled.invert(color)

    def contrast(self, contrast):
        oled.contrast(contrast)

    def pixel(self, x, y, color=1):
        oled.pixel(x, y, color)
