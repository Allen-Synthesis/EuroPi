"""Logic gates for the EuroPi

Treats ain as a digital input with a threshold of 0.8V

@author Chris Iverach-Brereton <ve4cib@gmail.com>
@date   2023-02-13
"""

from europi import *
from europi_script import EuroPiScript

## How many milliseconds of idleness do we need before we trigger the screensaver?
#
#  =20 minutes
SCREENSAVER_TIMEOUT_MS = 1000 * 60 * 20

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
        
        # keep track of the last time the user interacted with the module
        # if we're idle for too long, start the screensaver
        self.last_interaction_time = time.ticks_ms()
            
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
            self.last_interaction_time = time.ticks_ms()
            
        @b2.handler
        def on_b2_press():
            self.last_interaction_time = time.ticks_ms()
        
        while True:
            
            # read both inputs as 0/1
            x = din.value()
            y = 1 if ain.read_voltage() > AIN_VOLTAGE_CUTOFF else 0
            
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
            
            # check if we've been idle for too long; if so, blank the screen
            # to prevent burn-in
            now = time.ticks_ms()
            if time.ticks_diff(now, self.last_interaction_time) > SCREENSAVER_TIMEOUT_MS:
                oled.fill(0)
            else:
                display_txt = " &:{0}  |:{1}  ^:{2}\n!&:{3} !|:{4} !^:{5}".format(
                    x_and_y,
                    x_or_y,
                    x_xor_y,
                    x_nand_y,
                    x_nor_y,
                    x_xnor_y
                )
                oled.centre_text(display_txt)
            oled.show()
    
if __name__ == "__main__":
    Logic().main()

