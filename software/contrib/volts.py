#!/usr/bin/env python3
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
        def restrict_voltage(v):
            """If the max output voltage has been lowered, disable the too-high output
            """
            if v > europi_config.MAX_OUTPUT_VOLTAGE:
                return 0.0
            return v

        return [
            configuration.floatingPoint(
                name="CV1",
                minimum=0.0,
                maximum=europi_config.MAX_OUTPUT_VOLTAGE,
                default=restrict_voltage(0.5)
            ),
            configuration.floatingPoint(
                name="CV2",
                minimum=0.0,
                maximum=europi_config.MAX_OUTPUT_VOLTAGE,
                default=restrict_voltage(1.0)
            ),
            configuration.floatingPoint(
                name="CV3",
                minimum=0.0,
                maximum=europi_config.MAX_OUTPUT_VOLTAGE,
                default=restrict_voltage(2.0)
            ),
            configuration.floatingPoint(
                name="CV4",
                minimum=0.0,
                maximum=europi_config.MAX_OUTPUT_VOLTAGE,
                default=restrict_voltage(2.5)
            ),
            configuration.floatingPoint(
                name="CV5",
                minimum=0.0,
                maximum=europi_config.MAX_OUTPUT_VOLTAGE,
                default=restrict_voltage(5.0)
            ),
            configuration.floatingPoint(
                name="CV6",
                minimum=0.0,
                maximum=europi_config.MAX_OUTPUT_VOLTAGE,
                default=restrict_voltage(10.0)
            ),
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
