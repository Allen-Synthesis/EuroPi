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
# limitations under the License.
"""
Custom font demo
author: François Georgy (https://github.com/francoisgeorgy)
date: 2023-03-30

Use this script to test the support for custom fonts.

Please refer to experimental/custom_font.md documentation for more information.
"""
import time

from europi_script import EuroPiScript

from experimental import custom_font
from experimental import freesans14
from experimental import freesans17
from experimental import freesans20
from experimental import freesans24

oled = custom_font.oled


class CustomFontDemo(EuroPiScript):

    @classmethod
    def display_name(cls):
        return "Custom font demo"

    def __init__(self):
        super().__init__()
        self.demo = 0

    def update_demo(self):
        self.demo = (self.demo + 1) % 11
        if self.demo == 0:
            oled.centre_text("size 8")
        elif self.demo == 1:
            oled.centre_text("size 14", font=freesans14)
        elif self.demo == 2:
            oled.centre_text("size 17", font=freesans17)
        elif self.demo == 3:
            oled.centre_text("size 20", font=freesans20)
        elif self.demo == 4:
            oled.centre_text("size 24", font=freesans24)
        elif self.demo == 5:
            oled.fill(0)
            oled.text("8", 2, 20)
            oled.text("14", 18, 16, font=freesans14)
            oled.text("17", 40, 13, font=freesans17)
            oled.text("20", 66, 10, font=freesans20)
            oled.text("24", 96, 6, font=freesans24)
            oled.show()
        elif self.demo == 6:
            oled.centre_text("Default\n8x8 font\ncentered")
        elif self.demo == 7:
            oled.centre_text("FreeSans 14\nline 2", font=freesans14)
        elif self.demo == 8:
            oled.centre_text("FreeSans 17", font=freesans17)
        elif self.demo == 9:
            oled.centre_text("FreeSans 24", font=freesans24)
        elif self.demo == 10:
            oled.fill(0)
            oled.text("Fonts can", 0, 0)
            oled.text("be", 0, 10, font=freesans24)
            oled.text("mixed", 35, 14, font=freesans14)
            oled.text("freely", 80, 10, font=freesans20)
            oled.show()

    def main(self):
        t = 0
        while True:
            if (time.time() - t) >= 1:
                self.update_demo()
                t = time.time()


if __name__ == "__main__":
    oled.contrast(0)  # dim the display
    CustomFontDemo().main()
