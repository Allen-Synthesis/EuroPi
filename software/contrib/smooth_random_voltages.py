"""
Smooth Random Voltages
author: Adam Wonak (github.com/awonak)
date: 2022-03-08
labels: random, s&h


Random cv with adjustable slew rate.
Inspired by: https://youtu.be/tupkx3q7Dyw

3 smooth unique random voltages paired with matching steped random voltages.

New voltages assigned upon each digital input trigger. Top row outputs move
towards target voltage according to slew rate set by knob 1. Bottom row outputs
immediately change to new target voltage.

Col 1, change on each clock pulse.
Col 2, change on each clock pulse if target voltage has been reached.
Col 3, change on clock pulse with knob 2 probability.

digital_input: set a new target voltage
analog_input: (TODO) if non-zero voltage present, use that value for new target voltage and shift values.

knob_1: slew rate
knob_2: probability of voltage 3

output_1: smooth random voltage 1 - clocked
output_2: smooth random voltage 2 - clocked after target reached
output_3: smooth random voltage 3 - clocked based on k2 probability

output_4: stepped random voltage 1 - clocked
output_5: stepped random voltage 2 - clocked after target reached
output_6: stepped random voltage 3 - clocked based on k2 probability

"""
from random import random, uniform
import machine

try:
    from software.firmware import europi
except ImportError:
    import europi

# Overclocked for faster display refresh.
machine.freq(250000000)

class SmoothRandomVoltages:

    def __init__(self):
        self.voltages = [0, 0 , 0]
        self.target_voltages = [0, 0 , 0]

        # Exponential incremental value for assigning slew rate.
        self.slew_rate = lambda: (1 << europi.k1.range(14) + 1) / 100

        # Register digital input handler
        @europi.din.handler
        def new_target_voltages():
            """Check if next voltage conditions and update if ready."""
            self.set_target_voltages()

    def set_target_voltages(self):
        """Get next random voltage value."""
        # Col 1, change on each clock pulse.
        self.target_voltages[0] = uniform(europi.MIN_OUTPUT_VOLTAGE, europi.MAX_OUTPUT_VOLTAGE)
        # Col 2, change on each clock pulse if target voltage has been reached.
        if self.voltages[1] == self.target_voltages[1]:
            self.target_voltages[1] = uniform(
                europi.MIN_OUTPUT_VOLTAGE, europi.MAX_OUTPUT_VOLTAGE)
        # Col 3, change on clock pulse with knob 2 probability.
        if europi.k2.percent() > random():
            self.target_voltages[2] = uniform(
                europi.MIN_OUTPUT_VOLTAGE, europi.MAX_OUTPUT_VOLTAGE)

    def main(self):
        pixel_x = europi.OLED_WIDTH-1
        pixel_y = europi.OLED_HEIGHT-1

        # Start the main loop.
        while True:
            # Smooth voltage rising
            for i in range(len(self.voltages)):
                if self.voltages[i] < self.target_voltages[i]:
                    self.voltages[i] += self.slew_rate()
                    self.voltages[i] = min(self.voltages[i], self.target_voltages[i])

                # Smooth voltage falling
                elif self.voltages[i] > self.target_voltages[i]:
                    self.voltages[i] -= self.slew_rate()
                    self.voltages[i] = max(self.voltages[i], self.target_voltages[i])

                # Set the current smooth / stepped voltage.
                europi.cvs[i].voltage(self.voltages[i])
                europi.cvs[i + 3].voltage(self.target_voltages[i])

            # self.debug()
            europi.oled.scroll(-1, 0)
            europi.oled.vline(pixel_x, 0, europi.OLED_HEIGHT, 0)
            europi.oled.pixel(pixel_x, pixel_y - int(self.voltages[0] * (pixel_y / 10)), 1)
            europi.oled.pixel(pixel_x, pixel_y - int(self.voltages[1] * (pixel_y / 10)), 1)
            europi.oled.pixel(pixel_x, pixel_y - int(self.voltages[2] * (pixel_y / 10)), 1)
            europi.oled.show()


# if __name__ == '__main__':
srv = SmoothRandomVoltages()
srv.main()
