from time import sleep

from europi_script import EuroPiScript

try:
    # local dev
    from software.firmware.europi import (
        MAX_INPUT_VOLTAGE,
        OLED_HEIGHT,
        OLED_WIDTH,
        ain,
        b1,
        b2,
        cv1,
        cv2,
        cv4,
        din,
        k1,
        k2,
        oled,
    )
except ImportError:
    from europi import MAX_INPUT_VOLTAGE, OLED_HEIGHT, OLED_WIDTH, ain, b1, b2, cv1, cv2, cv4, din, k1, k2, oled

MAX_RATE = OLED_WIDTH
Y_TRUE = int(OLED_HEIGHT / 3 * 2)
Y_FALSE = int(OLED_HEIGHT / 3)
D_WAVE_HEIGHT = Y_TRUE - Y_FALSE + 1
RIGHT_EDGE = OLED_WIDTH - 1
Y_PIXELS = OLED_HEIGHT - 1


class Scope(EuroPiScript):
    """
    Can we make a functional oscilloscope on the EuroPi? Kinda! This script displays the inputs received on both the analog
    and digital inputs. Both waves can be toggled, and when no waves are displayed we switch to a text output, which also
    includes the knob values. The knobs each control an aspect of the x and y resolution respectively, allowing you to coax
    a little more detail out of the display.

    Note that the digital wave is displayed at a fixed y position that is not related to the value of the analog wave.

    Limitations include:
        - negative voltages are clipped to 0
        - screen height is only 32 pixels, so limited resolution
        - we can only refresh the screen so fast
        - analog pass through will be 'digitized'


    knob1 - samples per screen refresh. This effectively lets you 'zoom in' on the x-axis. Start at the lowest setting, 1 sample.
    knob2 - y voltage scale (only affects analog wave). This effectively lets you 'zoom in' on the low voltages. Start at
    the highest setting, 12v.

    button1 - toggle digital wave display
    button2 - toggle analog wave display

    out1 - digital in pass through
    out2 - analog in pass through
    out4 - inverted digital pass through
    """

    def __init__(self) -> None:
        super().__init__()
        self.enabled = [True, True]  # digital, analog

    def toggle(self, index):
        def f():
            self.enabled[index] = not self.enabled[index]

        return f

    @staticmethod
    def read_sample_rate():
        return k1.read_position(MAX_RATE) + 1

    @staticmethod
    def read_max_disp_voltage():
        return k2.read_position(MAX_INPUT_VOLTAGE) + 1

    @staticmethod
    def calc_y_pos(max_disp_voltage, a_voltage):
        return Y_PIXELS - int(a_voltage / max_disp_voltage * Y_PIXELS)

    def main(self):
        b1.handler(self.toggle(0))
        b2.handler(self.toggle(1))

        oled.fill(0)
        old_value = din.value()

        while True:
            rate = self.read_sample_rate()
            max_disp_voltage = self.read_max_disp_voltage()

            for _ in range(rate):
                if any(self.enabled):
                    oled.scroll(-1, 0)
                    oled.vline(RIGHT_EDGE, 0, OLED_HEIGHT, 0)

                d_value = din.value()
                cv2.value(d_value)
                cv4.value(not d_value)

                if self.enabled[0]:  # digital wave
                    y_pos = Y_TRUE if d_value else Y_FALSE
                    oled.pixel(RIGHT_EDGE, OLED_HEIGHT - y_pos, 1)
                    if d_value != old_value:
                        oled.vline(RIGHT_EDGE, Y_FALSE + 1, D_WAVE_HEIGHT, 1)
                    old_value = d_value

                a_voltage = ain.read_voltage(1)
                cv1.voltage(a_voltage)

                if self.enabled[1]:  # analog wave
                    y_pos = self.calc_y_pos(max_disp_voltage, a_voltage)
                    oled.pixel(RIGHT_EDGE, y_pos, 1)

                if not self.enabled[0] and not self.enabled[1]:  # details output
                    rate = self.read_sample_rate()
                    max_disp_voltage = self.read_max_disp_voltage()
                    oled.fill(0)
                    oled.text(f"a: {a_voltage:4.1f}v d:{d_value}", 2, 3, 1)
                    oled.text(f"samples: {rate:3}", 2, 13, 1)
                    oled.text(f"y scale: {max_disp_voltage:4.1f}v", 2, 23, 1)
                    oled.show()

                sleep(0.001)

            oled.show()


if __name__ == "__main__":
    Scope().main()
