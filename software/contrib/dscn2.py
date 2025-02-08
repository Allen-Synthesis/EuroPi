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
Binary tree based looping gate sequencer
"""

from europi import *
from europi_script import EuroPiScript

from framebuf import FrameBuffer, MONO_HLSB
from random import random as rnd


class Dcsn2(EuroPiScript):

    randomness_cv = ain
    randomness_knob = k2

    length_knob = k1

    MAX_LENGTH = 16
    MIN_LENGTH = 2

    children = [cv1, cv4]
    grandchildren = [
        [cv2, cv3],
        [cv5, cv6]
    ]

    loop_image = FrameBuffer(bytearray(b'\x1cZ\x81\x81\x81\x81Z8'), CHAR_WIDTH, CHAR_HEIGHT, MONO_HLSB)

    def __init__(self):
        super().__init__()

        self.unhandled_clock = False

        # initialize random pattern
        self.pattern = []
        for i in range(self.MAX_LENGTH):
            self.pattern.append(self.choose_random())

        def on_clock_rise():
            self.unhandled_clock = True

        def on_clock_fall():
            turn_off_all_cvs()

        def regenerate_pattern():
            for i in range(self.MAX_LENGTH):
                self.pattern[i] = self.choose_random()

        din.handler(on_clock_rise)
        din.handler_falling(on_clock_fall)
        b1.handler(on_clock_rise)
        b1.handler_falling(on_clock_fall)

        b2.handler(regenerate_pattern)

        self.set_outputs()

    def calculate_randomness(self):
        """Combine AIN & K2 to determine the probability that the pattern loops
        """
        # this will be in the range [0, 2]
        randomness = self.randomness_cv.percent() + self.randomness_knob.percent()

        # restrict to [0, 1]
        if randomness >= 1:
            randomness = 2.0 - randomness

        return randomness

    def choose_random(self):
        """
        Pick a random gate for the output pattern

        0: child 1, grandchild 1-1
        1: child 1, grandchild 1-2
        2: child 2, grandchild 2-1
        3: child 2, grandchild 2-2
        """
        return int(rnd() * 4)

    def set_outputs(self):
        turn_off_all_cvs()
        g = self.pattern[0]
        self.children[g >> 1].on()
        self.grandchildren[g >> 1][g & 1].on()

    def draw(self, pattern_length, loop_prob):
        oled.fill(0)

        active_child = self.pattern[0] >> 1
        active_grandchild = self.pattern[0] & 1

        # draw the tree with lines & circles
        oled.ellipse(OLED_WIDTH//2, 5, 4, 4, 1, True)  # root, always filled

        # children
        oled.ellipse(OLED_WIDTH//4, OLED_HEIGHT//2, 4, 4, 1, active_child == 0)
        oled.ellipse(3*OLED_WIDTH//4, OLED_HEIGHT//2, 4, 4, 1, active_child != 0)

        # grandchildren
        oled.ellipse(6, OLED_HEIGHT-5, 4, 4, 1, active_child == 0 and active_grandchild == 0)
        oled.ellipse(OLED_WIDTH//2-6, OLED_HEIGHT-5, 4, 4, 1, active_child == 0 and active_grandchild != 0)
        oled.ellipse(OLED_WIDTH//2+6, OLED_HEIGHT-5, 4, 4, 1, active_child != 0 and active_grandchild == 0)
        oled.ellipse(OLED_WIDTH-6, OLED_HEIGHT-5, 4, 4, 1, active_child != 0 and active_grandchild != 0)

        if active_child == 0:
            oled.line(OLED_WIDTH//2, 5, OLED_WIDTH//4, OLED_HEIGHT//2, 1)
            if active_grandchild == 0:
                oled.line(OLED_WIDTH//4, OLED_HEIGHT//2, 6, OLED_HEIGHT-5, 1)
            else:
                oled.line(OLED_WIDTH//4, OLED_HEIGHT//2, OLED_WIDTH//2-6, OLED_HEIGHT-5, 1)
        else:
            oled.line(OLED_WIDTH//2, 5, 3*OLED_WIDTH//4, OLED_HEIGHT//2, 1)
            if active_grandchild == 0:
                oled.line(3*OLED_WIDTH//4, OLED_HEIGHT//2, OLED_WIDTH//2+6, OLED_HEIGHT-5, 1)
            else:
                oled.line(3*OLED_WIDTH//4, OLED_HEIGHT//2, OLED_WIDTH-6, OLED_HEIGHT-5, 1)

        oled.text(f"{pattern_length}", 0, 0, 1)
        s = f"{round(loop_prob * 100)}"
        oled.blit(self.loop_image, OLED_WIDTH - CHAR_WIDTH * (len(s)+1) - 1, 0)
        oled.text(s, OLED_WIDTH - len(s) * CHAR_WIDTH, 0, 1)
        oled.text(f"{self.pattern[0]}", OLED_WIDTH//2-CHAR_WIDTH//2, OLED_HEIGHT//2 - CHAR_HEIGHT//2, 1)
        oled.show()

    def main(self):
        while True:
            r = rnd()
            loop_prob = 1.0 - self.calculate_randomness()  # 0 -> random, 1 -> loop
            pattern_length = round(self.length_knob.percent() * (self.MAX_LENGTH - self.MIN_LENGTH) + self.MIN_LENGTH)

            if self.unhandled_clock:
                self.unhandled_clock = False

                # shift the pattern over 1 step, introducing randomness as needed
                if r <= loop_prob:
                    tmp = self.pattern[pattern_length - 1]
                else:
                    tmp = self.choose_random()
                for i in range(pattern_length - 1):
                    self.pattern[pattern_length-1-i] = self.pattern[pattern_length-2-i]
                self.pattern[0] = tmp
                self.set_outputs()

            self.draw(pattern_length, loop_prob)

if __name__ == "__main__":
    Dcsn2().main()
