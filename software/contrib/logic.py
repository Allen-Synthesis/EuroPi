"""Logic gates for the EuroPi

Treats ain as a digital input with a threshold of 0.8V

@author Chris Iverach-Brereton <ve4cib@gmail.com>
@date   2023-02-13
"""

from europi import *
from europi_script import EuroPiScript

from experimental.screensaver import OledWithScreensaver

ssoled = OledWithScreensaver()

## Anything above this threshold is considered ON for the analog
#  input
AIN_VOLTAGE_CUTOFF = 0.8

class Logic(EuroPiScript):
    """The main workhorse of the whole module

    Does all 6 basic logic operations, sending the result to each of the
    6 outputs
    """
    def __init__(self):
        super().__init__()

    @classmethod
    def display_name(cls):
        return "Logic"

    def main(self):
        """The main loop

        Connects event handlers for clock-in and button presses
        and runs the main loop
        """

        @b1.handler
        def on_b1_press():
            ssoled.notify_user_interaction()

        @b2.handler
        def on_b2_press():
            ssoled.notify_user_interaction()

        while True:

            # read both inputs as 0/1
            x = din.value() | b1.value()
            y = (1 if ain.read_voltage() > AIN_VOLTAGE_CUTOFF else 0) | b2.value()

            x_and_y = x & y
            x_or_y = x | y
            x_xor_y = x ^ y
            x_nand_y = abs(x_and_y - 1) # bit of a hack to get the inverted values
            x_nor_y = abs(x_or_y -1)    # ~ results in some -2 results, which we don't want
            x_xnor_y = abs(x_xor_y -1)  # so some simple int math will suffice

            cv1.value(x_and_y)
            cv2.value(x_or_y)
            cv3.value(x_xor_y)
            cv4.value(x_nand_y)
            cv5.value(x_nor_y)
            cv6.value(x_xnor_y)
            display_txt = " &:{0}  |:{1}  ^:{2}\n!&:{3} !|:{4} !^:{5}".format(
                x_and_y,
                x_or_y,
                x_xor_y,
                x_nand_y,
                x_nor_y,
                x_xnor_y
            )

            ssoled.centre_text(display_txt)

if __name__ == "__main__":
    Logic().main()
