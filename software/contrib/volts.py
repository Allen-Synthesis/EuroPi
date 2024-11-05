#!/usr/bin/env python3
"""Generates fixed voltages

Voltages can be configured via an optional JSON file
"""


from europi import *
from europi_script import EuroPiScript

import configuration


class OffsetVoltages(EuroPiScript):
    def __init__(self):
        super().__init__()

    @classmethod
    def config_points(cls):
        """Return the static configuration options for this class
        """
        return [
            configuration.floatingPoint(name="CV1", minimum=0.0, maximum=europi_config.MAX_OUTPUT_VOLTAGE, default=0.5),
            configuration.floatingPoint(name="CV2", minimum=0.0, maximum=europi_config.MAX_OUTPUT_VOLTAGE, default=1.0),
            configuration.floatingPoint(name="CV3", minimum=0.0, maximum=europi_config.MAX_OUTPUT_VOLTAGE, default=2.0),
            configuration.floatingPoint(name="CV4", minimum=0.0, maximum=europi_config.MAX_OUTPUT_VOLTAGE, default=2.5),
            configuration.floatingPoint(name="CV5", minimum=0.0, maximum=europi_config.MAX_OUTPUT_VOLTAGE, default=5.0),
            configuration.floatingPoint(name="CV6", minimum=0.0, maximum=europi_config.MAX_OUTPUT_VOLTAGE, default=10.0),
        ]

    def main(self):
        oled.fill(0)
        oled.show()

        cv1.voltage(self.config.CV1)
        cv2.voltage(self.config.CV2)
        cv3.voltage(self.config.CV3)
        cv4.voltage(self.config.CV4)
        cv5.voltage(self.config.CV5)
        cv6.voltage(self.config.CV6)

        while True:
            pass
