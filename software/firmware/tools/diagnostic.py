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
from machine import ADC
from time import sleep

from europi import (
    OLED_HEIGHT,
    OLED_WIDTH,
    ain,
    b1,
    b2,
    cv1,
    cv2,
    cv3,
    cv4,
    cv5,
    cv6,
    din,
    k1,
    k2,
    oled,
    europi_config,
    thermometer,
)
from europi_script import EuroPiScript
import configuration

"""
A diagnostic utility intended to help prove out a new EuroPi build and calibration. Each aspect of the EuroPi's hardware
is exercised.

- din: value displayed on screen
- ain: value displayed on screen
- b1: rotate output voltages backwards
- b2: rotate output voltages forwards
- k1: value 0-99 displayed on screen
- k2: value 0-99 displayed on screen
- cvX: output a constant voltage, one of [0, 0.5, 1, 2.5, 5, 10]
"""


class Diagnostic(EuroPiScript):
    def __init__(self):
        super().__init__()
        self.voltages = [
            0,  # min
            0.5,  # not 0 but still below DI's threshold
            1,
            2.5,
            5,
            10,  # max
        ]
        self.temp_units = self.config.TEMP_UNITS
        self.use_fahrenheit = self.temp_units == "F"

    @classmethod
    def config_points(cls):
        return [configuration.choice(name="TEMP_UNITS", choices=["C", "F"], default="C")]

    def calc_temp(self):
        t = thermometer.read_temperature()
        if t is None:
            return 0

        if self.use_fahrenheit:
            t = (t * 1.8) + 32
        return t

    def rotate_r(self):
        self.voltages = self.voltages[-1:] + self.voltages[:-1]

    def rotate_l(self):
        self.voltages = self.voltages[1:] + self.voltages[:1]

    def main(self):
        b1.handler(self.rotate_l)
        b2.handler(self.rotate_r)

        while True:
            # Set the outputs to useful values
            cv1.voltage(self.voltages[0])
            cv2.voltage(self.voltages[1])
            cv3.voltage(self.voltages[2])
            cv4.voltage(self.voltages[3])
            cv5.voltage(self.voltages[4])
            cv6.voltage(self.voltages[5])

            oled.fill(0)

            # calc and format temp
            t = self.calc_temp()
            formatted_temp = f"{int(t)}{self.temp_units}"

            # display the input values
            oled.text(f"ain: {ain.read_voltage(samples=512):5.2f}v {formatted_temp}", 2, 3, 1)
            oled.text(f"k1: {k1.read_position():2}  k2: {k2.read_position():2}", 2, 13, 1)
            oled.text(f"din:{din.value()} b1:{b1.value()} b2:{b2.value()}", 2, 23, 1)

            # show the screen boundaries
            oled.rect(0, 0, OLED_WIDTH, OLED_HEIGHT, 1)
            oled.show()

            sleep(0.1)


if __name__ == "__main__":
    Diagnostic().main()
