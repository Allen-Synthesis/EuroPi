#!/usr/bin/env python3
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

from experimental.screensaver import OledWithScreensaver

ssoled = OledWithScreensaver()

class Kompari(EuroPiScript):
    """The main Kompari script.  See module comment for usage
    """

    def __init__(self):
        super().__init__()

        @b1.handler
        def on_b1_press():
            ssoled.notify_user_interaction()

        @b2.handler
        def on_b2_press():
            ssoled.notify_user_interaction()

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
                cv1.on()
            else:
                cv1.off()

            if x < upper_bound:
                cv2.on()
            else:
                cv2.off()

            if lower_bound < x and x < upper_bound:
                cv3.on()
            else:
                cv3.off()

            cv4.voltage(max(lower_bound, x) * MAX_OUTPUT_VOLTAGE)
            cv5.voltage(min(x, upper_bound) * MAX_OUTPUT_VOLTAGE)
            cv6.voltage(max(lower_bound, min(x, upper_bound)) * MAX_OUTPUT_VOLTAGE)

            ssoled.centre_text(f"{lower_bound:0.1f}  {x:0.1f}  {upper_bound:0.1f}", clear_first=True, auto_show=True)

if __name__ == "__main__":
    Kompari().main()
