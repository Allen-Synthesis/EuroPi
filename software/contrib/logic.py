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
"""Logic gates for the EuroPi

Treats ain as a digital input with a threshold of 0.8V

@author Chris Iverach-Brereton <ve4cib@gmail.com>
@date   2023-02-13
"""

from europi import *
from europi_script import EuroPiScript

from experimental.a_to_d import AnalogReaderDigitalWrapper
from experimental.screensaver import OledWithScreensaver

ssoled = OledWithScreensaver()

class Logic(EuroPiScript):
    """The main workhorse of the whole module

    Does all 6 basic logic operations, sending the result to each of the
    6 outputs
    """
    def __init__(self):
        super().__init__()

        # the six logic operations' outputs, as 0/1 values
        # this lets us use bitwise math operations to set the output voltages to either 0 or 1V
        # as well as satisfying the input requirements for the europi.Output.value function
        self.x_and_y = 0
        self.x_or_y = 0
        self.x_xor_y = 0
        self.x_nand_y = 0
        self.x_nor_y = 0
        self.x_xnor_y = 0

        self.din1 = din
        self.din2 = AnalogReaderDigitalWrapper(ain)

        # connect ISRs
        self.din1.handler(self.update_logic)
        self.din1.handler_falling(self.update_logic)
        self.din2.handler(self.update_logic)
        self.din2.handler_falling(self.update_logic)
        b1.handler(self.button_state_change)
        b1.handler_falling(self.button_state_change)
        b2.handler(self.button_state_change)
        b2.handler_falling(self.button_state_change)

    def button_state_change(self):
        self.update_logic()
        ssoled.notify_user_interaction()

    @classmethod
    def display_name(cls):
        return "Logic"

    def update_logic(self):
        """Updates the values of our 6 logic operations
        """
        x = self.din1.value() | b1.value()
        y = self.din2.value() | b2.value()

        self.x_and_y = x & y
        self.x_or_y = x | y
        self.x_xor_y = x ^ y
        self.x_nand_y = abs(self.x_and_y - 1) # bit of a hack to get the inverted values
        self.x_nor_y = abs(self.x_or_y -1)    # ~ results in some -2 results, which we don't want
        self.x_xnor_y = abs(self.x_xor_y -1)  # so some simple int math will suffice

    def main(self):
        knob_wakeup_threshold = 0.05

        prev_k1 = k1.percent()
        prev_k2 = k2.percent()

        while True:
            # update ain
            self.din2.update()

            # check to see if we've wiggled a knob to exit the screensaver
            current_k1 = k1.percent()
            current_k2 = k2.percent()

            if (
                abs(current_k1 - prev_k1) >= knob_wakeup_threshold or
                abs(current_k2 - prev_k2) >= knob_wakeup_threshold
            ):
                ssoled.notify_user_interaction()
                prev_k1 = current_k1
                prev_k2 = current_k2

            # set the output voltages
            cv1.value(self.x_and_y)
            cv2.value(self.x_or_y)
            cv3.value(self.x_xor_y)
            cv4.value(self.x_nand_y)
            cv5.value(self.x_nor_y)
            cv6.value(self.x_xnor_y)

            display_txt = " &:{0}  |:{1}  ^:{2}\n!&:{3} !|:{4} !^:{5}".format(
                self.x_and_y,
                self.x_or_y,
                self.x_xor_y,
                self.x_nand_y,
                self.x_nor_y,
                self.x_xnor_y
            )

            ssoled.centre_text(display_txt)

if __name__ == "__main__":
    Logic().main()
