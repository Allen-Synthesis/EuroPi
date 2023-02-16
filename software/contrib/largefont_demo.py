"""
Large font demo
author: François Georgy (https://github.com/francoisgeorgy)
date: 2023-02-15

Use this script to test and demo the support for large fonts.

See the largefont_writer module for information about how to import your own fonts.
"""
import time

from europi_script import EuroPiScript
from europi import oled, OLED_WIDTH, OLED_HEIGHT
import freesans14
import freesans17
import freesans20
import freesans24


class LargeFontDemo(EuroPiScript):
    @classmethod
    def display_name(cls):
        return "Large font demo"

    def __init__(self):
        super().__init__()
        self.demo = 4
        self.boxed = True  # alternate one round boxed, one round unboxed.

    def update_demo(self):
        self.demo = (self.demo + 1) % 5
        if self.demo == 0:
            oled.centre_text("Default\nmonospaced\n8x8 font")
            self.boxed = not self.boxed
        elif self.demo == 1:
            oled.centre_text("14 ABC gpq\n0123456 gp", font=freesans14)
        elif self.demo == 2:
            oled.centre_text("17 ABC gp", font=freesans17)
        elif self.demo == 3:
            oled.centre_text("20 ABC gp", font=freesans20)
        elif self.demo == 4:
            oled.centre_text("24 ABC gp", font=freesans24)
        if self.boxed:
            oled.rect(0, 0, OLED_WIDTH, OLED_HEIGHT, 1)
            oled.show()

    def main(self):
        t = 0
        while True:
            if (time.time() - t) >= 1:
                self.update_demo()
                t = time.time()
            time.sleep(0.1)


if __name__ == "__main__":
    oled.contrast(0)  # dim the display
    LargeFontDemo().main()
