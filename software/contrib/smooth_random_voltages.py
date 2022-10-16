"""
Smooth Random Voltages
author: Adam Wonak (github.com/awonak)
date: 2022-06-01
labels: random, s&h


Random cv with adjustable slew rate.
Inspired by: https://youtu.be/tupkx3q7Dyw

3 random or analog input s&h voltages with changable slew smoothness.

New voltages assigned upon each digital input trigger. Top row outputs move
towards target voltage according to slew rate set by knob 1. Bottom row outputs
immediately change to new target voltage. Voltage source toggled by button 2,
which will switch between random and analog input voltage source. Button 1 will
toggle various display types for the oled.

Col 1, change on each trigger.
Col 2, change on each trigger if target voltage has been reached.
Col 3, change on trigger with knob 2 probability.

digital_input: trigger to set a new target voltage.
analog_input: source for new target value when enabled.

knob_1: slew rate
knob_2: probability of new Col 3 voltage

button_1: cycle through the visualizations: Bars, Scope, Blank.
button_2: cycle through voltage sources: random, analog input.

output_1: smooth random voltage 1 - new voltage on trigger
output_2: smooth random voltage 2 - new voltage after target reached
output_3: smooth random voltage 3 - new voltage based on k2 probability

output_4: stepped random voltage 1 - new voltage on trigger (no slew)
output_5: stepped random voltage 2 - new voltage after target reached (no slew)
output_6: stepped random voltage 3 - new voltage based on k2 probability (no slew)

"""
from random import random, uniform
from utime import ticks_diff, ticks_ms
import machine

try:
    from software.firmware import europi
    from software.firmware.europi import CHAR_HEIGHT, OLED_HEIGHT, OLED_WIDTH
    from software.firmware.europi_script import EuroPiScript

except ImportError:
    import europi
    from europi import CHAR_HEIGHT, OLED_HEIGHT, OLED_WIDTH
    from europi_script import EuroPiScript


# Script Constants
MENU_DURATION = 1800
MAX_SLEW_RATE = 100_000


def envelope_generator(start=0, target=10, slew_rate=512):
    """
    Creates a generator function returning the absolute value differece between
    the start and target voltages over the given duration in ms.
    """
    cv_diff = abs(target - start)
    cur = min(start, target)
    _target = max(start, target)
    slew_rate = max(slew_rate, 1)  # avoid div by zero
    env_start = ticks_ms()
    while cur < _target:
        time_since_start = ticks_diff(ticks_ms(), env_start)
        env_progress = time_since_start / slew_rate
        cur = env_progress * cv_diff
        cur = europi.clamp(cur, europi.MIN_OUTPUT_VOLTAGE, europi.MAX_OUTPUT_VOLTAGE)
        yield cur


class SmoothRandomVoltages(EuroPiScript):
    def __init__(self):
        self.voltages = [0, 0, 0]
        self.target_voltages = [0, 0, 0]

        # Maximim ms duration for slew rate.
        self.slew_rate = lambda: europi.k1.range(MAX_SLEW_RATE)

        # Visualization display choice.
        self.visualization = 0  # 0: Bars, 1: Scope, 2: Blank.

        # Voltage source choice.
        self.voltage_source = 0  # 0: random, 1: analog input.
        self.voltage_source_display = ["random", "analog"]

        # Envelopes
        self.env = [
            envelope_generator(0, 10),
            envelope_generator(0, 10),
            envelope_generator(0, 10),
        ]

        # Register digital input handler
        @europi.din.handler
        def new_target_voltages():
            """Check if next voltage conditions and update if ready."""
            self.set_target_voltages()

        # Cycle through the visualizations
        @europi.b1.handler
        def change_visualization():
            europi.oled.fill(0)
            europi.oled.show()
            # 0: Bars, 1: Scope, 2: Blank.
            self.visualization = (self.visualization + 1) % 3

        # Toggle between random and analog input voltage source
        @europi.b2.handler
        def change_voltage_source():
            # 0: random, 1: analog input.
            self.voltage_source = (self.voltage_source + 1) % 2

    def set_target_voltages(self):
        """Get next random voltage value."""
        # Col 1, change on each trigger.
        self.target_voltages[0] = self.get_new_voltage()
        self.env[0] = envelope_generator(self.voltages[0], self.target_voltages[0], self.slew_rate())

        # Col 2, change on each trigger if target voltage has been reached.
        if self.voltages[1] == self.target_voltages[1]:
            self.target_voltages[1] = self.get_new_voltage()
            self.env[1] = envelope_generator(
                self.voltages[1], self.target_voltages[1], self.slew_rate()
            )

        # Col 3, change on trigger with knob 2 probability.
        if europi.k2.percent() > random():
            self.target_voltages[2] = self.get_new_voltage()
            self.env[2] = envelope_generator(
                self.voltages[2], self.target_voltages[2], self.slew_rate()
            )

    def get_new_voltage(self):
        """Return a new voltage from analog in or random value."""
        # 0: random, 1: analog input.
        if self.voltage_source == 0:
            return uniform(europi.MIN_OUTPUT_VOLTAGE, europi.MAX_OUTPUT_VOLTAGE)
        else:
            return europi.ain.read_voltage()

    def update_display(self):
        """Show current voltage visualizations."""
        if self.visualization == 0:
            self.display_bars()
        elif self.visualization == 1:
            self.display_scope()
        self.show_menu_header()
        europi.oled.show()

    def show_menu_header(self):
        """When button2 has been pressed, show the current changed source value."""
        if ticks_diff(ticks_ms(), europi.b2.last_pressed()) < MENU_DURATION:
            europi.oled.fill_rect(0, 0, OLED_WIDTH, CHAR_HEIGHT, 1)
            msg = f"Source: {self.voltage_source_display[self.voltage_source]}"
            europi.oled.text(msg, 0, 0, 0)

    def display_bars(self):
        """Draw a bar representing the slew / target for each of the 3 voltages."""
        europi.oled.fill(0)
        for i in range(3):
            x1 = 0
            y1 = int(i * (OLED_HEIGHT / 3)) + 2
            y2 = int(OLED_HEIGHT / 3) - 2
            x2_slew = int((self.voltages[i] / europi.MAX_OUTPUT_VOLTAGE) * OLED_WIDTH)
            x2_target = int((self.target_voltages[i] / europi.MAX_OUTPUT_VOLTAGE) * OLED_WIDTH)
            # Smooth voltage rising
            if self.voltages[i] < self.target_voltages[i]:
                europi.oled.fill_rect(x1, y1, x2_slew, y2, 1)
                europi.oled.rect(x1, y1, x2_target, y2, 1)
            # Smooth voltage falling
            else:
                europi.oled.rect(x1, y1, x2_slew, y2, 1)
                europi.oled.fill_rect(x1, y1, x2_target, y2, 1)

    def display_scope(self):
        """Draw a real-time line representing the slew value for each of the 3 voltages."""
        pixel_x = 0
        pixel_y = europi.OLED_HEIGHT - 1
        europi.oled.scroll(1, 0)
        europi.oled.vline(pixel_x, 0, europi.OLED_HEIGHT, 0)
        europi.oled.pixel(pixel_x, pixel_y - int(self.voltages[0] * (pixel_y / 10)), 1)
        europi.oled.pixel(pixel_x, pixel_y - int(self.voltages[1] * (pixel_y / 10)), 1)
        europi.oled.pixel(pixel_x, pixel_y - int(self.voltages[2] * (pixel_y / 10)), 1)

    def main(self):
        # Start the main loop.
        while True:
            for i in range(len(self.voltages)):
                # Smooth voltage rising
                if self.voltages[i] < self.target_voltages[i]:
                    self.voltages[i] += next(self.env[i])
                    self.voltages[i] = min(self.voltages[i], self.target_voltages[i])

                # Smooth voltage falling
                elif self.voltages[i] > self.target_voltages[i]:
                    self.voltages[i] -= next(self.env[i])
                    self.voltages[i] = max(self.voltages[i], self.target_voltages[i])

                # Set the current smooth / stepped voltage.
                europi.cvs[i].voltage(self.voltages[i])
                europi.cvs[i + 3].voltage(self.target_voltages[i])

            self.update_display()


if __name__ == "__main__":
    srv = SmoothRandomVoltages()
    srv.main()
