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

Col 1, change on each trigger.
Col 2, change on each trigger if target voltage has been reached.
Col 3, change on trigger with knob 2 probability.

The buttons will cycle through the visualizations: Bars, Scope, Blank.

digital_input: trigger to set a new target voltage
analog_input: if non-zero voltage present, use that value for new target voltage and shift values.

knob_1: slew rate
knob_2: probability of voltage 3

output_1: smooth random voltage 1 - new voltage on trigger
output_2: smooth random voltage 2 - new voltage after target reached
output_3: smooth random voltage 3 - new voltage based on k2 probability

output_4: stepped random voltage 1 - new voltage on trigger (no slew)
output_5: stepped random voltage 2 - new voltage after target reached (no slew)
output_6: stepped random voltage 3 - new voltage based on k2 probability (no slew)

"""
from random import random, uniform
import machine

try:
    from software.firmware import europi
    from software.firmware.europi import OLED_HEIGHT, OLED_WIDTH
    from software.firmware.europi_script import EuroPiScript

except ImportError:
    import europi
    from europi import OLED_HEIGHT, OLED_WIDTH
    from europi_script import EuroPiScript


# Overclocked for faster display refresh.
machine.freq(250000000)

# Adjust to match your max unplugged voltage noise level.
MIN_INPUT_VOLTAGE = 0.095


class SmoothRandomVoltages(EuroPiScript):
    def __init__(self):
        self.voltages = [0, 0, 0]
        self.target_voltages = [0, 0, 0]

        # Exponential incremental value for assigning slew rate.
        self.slew_rate = lambda: (1 << europi.k1.range(9) + 1) / 100

        # Visualization func
        self.visualization = 0  # 0: Bars, 1: Scope, 2: Blank.

        # Register digital input handler
        @europi.din.handler
        def new_target_voltages():
            """Check if next voltage conditions and update if ready."""
            self.set_target_voltages()

        # Cycle through the visualizations
        def change_visualization(dir):
            def func():
                europi.oled.fill(0)
                europi.oled.show()
                # 0: Bars, 1: Scope, 2: Blank.
                self.visualization = (self.visualization + dir) % 3

            return func

        europi.b1.handler(change_visualization(1))
        europi.b2.handler(change_visualization(-1))

    def set_target_voltages(self):
        """Get next random voltage value."""
        # Col 1, change on each clock pulse.
        self.target_voltages[0] = self.get_new_voltage()
        # Col 2, change on each clock pulse if target voltage has been reached.
        if self.voltages[1] == self.target_voltages[1]:
            self.target_voltages[1] = self.get_new_voltage()
        # Col 3, change on clock pulse with knob 2 probability.
        if europi.k2.percent() > random():
            self.target_voltages[2] = self.get_new_voltage()

    def get_new_voltage(self):
        """Return a new voltage from analog in or random value."""
        if europi.ain.read_voltage() > MIN_INPUT_VOLTAGE:
            return europi.ain.read_voltage()
        return uniform(europi.MIN_OUTPUT_VOLTAGE, europi.MAX_OUTPUT_VOLTAGE)

    def update_display(self):
        """Show current voltage visualizations."""
        if self.visualization == 0:
            self.display_bars()
        elif self.visualization == 1:
            self.display_scope()

    def display_bars(self):
        europi.oled.fill(0)
        for i in range(3):
            x1 = 0
            y1 = int(i * (OLED_HEIGHT / 3))
            y2 = int(OLED_HEIGHT / 3) - 1

            # Slew
            x2 = int((self.voltages[i] / europi.MAX_OUTPUT_VOLTAGE) * OLED_WIDTH)
            if self.voltages[i] > self.target_voltages[i]:
                europi.oled.rect(x1, y1, x2, y2, 1)
            else:
                europi.oled.fill_rect(x1, y1, x2, y2, 1)

            # Stepped
            x2 = int((self.target_voltages[i] / europi.MAX_OUTPUT_VOLTAGE) * OLED_WIDTH)
            if self.voltages[i] > self.target_voltages[i]:
                europi.oled.fill_rect(x1, y1, x2, y2, 1)
            else:
                europi.oled.rect(x1, y1, x2, y2, 1)

        europi.oled.show()

    def display_scope(self):
        pixel_x = europi.OLED_WIDTH - 1
        pixel_y = europi.OLED_HEIGHT - 1
        europi.oled.scroll(-1, 0)
        europi.oled.vline(pixel_x, 0, europi.OLED_HEIGHT, 0)
        europi.oled.pixel(pixel_x, pixel_y - int(self.voltages[0] * (pixel_y / 10)), 1)
        europi.oled.pixel(pixel_x, pixel_y - int(self.voltages[1] * (pixel_y / 10)), 1)
        europi.oled.pixel(pixel_x, pixel_y - int(self.voltages[2] * (pixel_y / 10)), 1)
        europi.oled.show()

    def main(self):
        # Start the main loop.
        while True:
            for i in range(len(self.voltages)):
                # Smooth voltage rising
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

            self.update_display()


if __name__ == "__main__":
    srv = SmoothRandomVoltages()
    srv.main()
