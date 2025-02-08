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
"""
Generates CV and gate signals based on the slope of an incoming analogue signal
"""

from europi import *
from europi_script import EuroPiScript

from experimental.math_extras import median

class Slopes(EuroPiScript):
    noise_attenuator = k1
    output_attenuator = k2

    ain_rising_gate = cv1
    ain_falling_gate = cv2
    ain_steady_gate = cv3
    ain_pos_slope_cv = cv4
    ain_neg_slope_cv = cv5
    ain_slope_magnitude_cv = cv6

    MIN_BINS = 1
    MAX_BINS = 12

    MIN_SAMPLES = 32
    MAX_SAMPLES = 512

    MAX_SLOPE = europi_config.MAX_INPUT_VOLTAGE / 10.0

    DEAD_ZONE = 0.01

    def __init__(self):
        super().__init__()

        # bins used for median smoothing of the raw AIN data
        self.bins = [0] * self.MAX_BINS

    def denoise(self, window_size):
        return median(self.bins[len(self.bins) - window_size - 1:])

    def main(self):
        turn_off_all_cvs()
        oled.fill(0)
        oled.show()

        while True:
            denoise_percent = self.noise_attenuator.percent()
            n_bins = round(denoise_percent * (self.MAX_BINS - self.MIN_BINS) + self.MIN_BINS)
            n_samples = round(denoise_percent * (self.MAX_SAMPLES - self.MIN_SAMPLES) + self.MIN_SAMPLES)
            deadzone = self.DEAD_ZONE * denoise_percent
            output_attenuation_percent = self.output_attenuator.percent() * 2

            # calculate the previous sample based on our current noise filter size
            prev_volts = self.denoise(n_bins)

            # grab the new sample and add it to the end of the list
            self.bins.pop(0)
            self.bins.append(ain.read_voltage(samples=n_samples))
            curr_volts = self.denoise(n_bins)

            # calculate the change in volts
            d_volts = curr_volts - prev_volts
            slope = d_volts / self.MAX_SLOPE
            if slope > 1:
                slope = 1.0
            elif slope < -1.0:
                slope = -1.0

            # Set the outputs
            if d_volts > deadzone:
                # ain rising
                self.ain_rising_gate.on()
                self.ain_falling_gate.off()
                self.ain_steady_gate.off()

                self.ain_pos_slope_cv.voltage(slope * output_attenuation_percent * europi_config.MAX_OUTPUT_VOLTAGE)
                self.ain_neg_slope_cv.off()
                self.ain_slope_magnitude_cv.voltage(slope * output_attenuation_percent * europi_config.MAX_OUTPUT_VOLTAGE)
            elif d_volts < -deadzone:
                # ain falling
                self.ain_rising_gate.off()
                self.ain_falling_gate.on()
                self.ain_steady_gate.off()

                self.ain_pos_slope_cv.off()
                self.ain_neg_slope_cv.voltage(-slope * output_attenuation_percent * europi_config.MAX_OUTPUT_VOLTAGE)
                self.ain_slope_magnitude_cv.voltage(-slope * output_attenuation_percent * europi_config.MAX_OUTPUT_VOLTAGE)
            else:
                # ain steady
                self.ain_rising_gate.off()
                self.ain_falling_gate.off()
                self.ain_steady_gate.on()

                self.ain_pos_slope_cv.off()
                self.ain_neg_slope_cv.off()
                self.ain_slope_magnitude_cv.off()

if __name__ == "__main__":
    Slopes().main()
