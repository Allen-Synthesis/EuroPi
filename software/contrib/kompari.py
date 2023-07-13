#!/usr/bin/env python3
"""A EuroPi re-imagining of the Kompari module

Input A is provided in AIN.  K1 and K2 provide the lower and upper bounds

Outputs:
- CV1: +5V if K1 < AIN, otherwise 0
- CV2: +5V if AIN < K2, otherwise 0
- CV3: +5V if K1 < AIN < K2, otherwise 0
- CV4: max( K1, AIN )
- CV5: min( AIN, K2 )
- CV6: max( K1, min( AIN, K2 ) ) )

B1, B2, and DIN are not used

@author Chris Iverach-Brereton
@year 2023
"""

from europi import *
from europi_script import EuroPiScript

class Kompari(EuroPiScript):
    """The main Kompari script.  See module comment for usage
    """
    HIGH_VOLTAGE = 5.0
    LOW_VOLTAGE = 0.0

    def __init__(self):
        super().__init__()

    @classmethod
    def display_name(cls):
        return "Kompari"

    def main(self):
        """Run the main loop
        """
        while True:
            lower_bound = k1.percent()
            upper_bound = k2.percent()
            x = ain.percent()

            if lower_bound < x:
                cv1.voltage(self.HIGH_VOLTAGE)
            else:
                cv1.voltage(self.LOW_VOLTAGE)

            if x < upper_bound:
                cv2.voltage(self.HIGH_VOLTAGE)
            else:
                cv2.voltage(self.LOW_VOLTAGE)

            if lower_bound < x and x < upper_bound:
                cv3.voltage(self.HIGH_VOLTAGE)
            else:
                cv3.voltage(self.LOW_VOLTAGE)

            cv4.voltage(max(lower_bound, x) * MAX_OUTPUT_VOLTAGE)
            cv5.voltage(min(x, upper_bound) * MAX_OUTPUT_VOLTAGE)
            cv6.voltage(max(lower_bound, min(x, upper_bound)) * MAX_OUTPUT_VOLTAGE)

            oled.fill(0)
            oled.centre_text(f"{lower_bound:0.1f}  {x:0.1f}  {upper_bound:0.1f}")
            oled.show()

if __name__ == "__main__":
    Kompari().main()
