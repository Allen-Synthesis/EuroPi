from machine import ADC
from time import sleep

from europi import OLED_HEIGHT, OLED_WIDTH, ain, b1, b2, cv1, cv2, cv3, cv4, cv5, cv6, din, k1, k2, oled
from europi_script import EuroPiScript

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

TEMP_CONV_FACTOR = 3.3 / 65535

class Diagnostic(EuroPiScript):

    def __init__(self):
        super().__init__()
        self.temp_sensor = ADC(4)
        self.voltages = [
            0,  # min
            0.5,  # not 0 but still below DI's threshold
            1,
            2.5,
            5,
            10,  # max
        ]


    def calc_temp(self):
        # see the pico's datasheet for the details of this calculation
        return 27 - ((self.temp_sensor.read_u16() * TEMP_CONV_FACTOR) - 0.706) / 0.001721

    @staticmethod
    def convert_fahrenheit(temp_c):
        return (temp_c * 1.8) + 32


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
            use_fahrenheit = b1.value() or b2.value()
            t = self.calc_temp()
            formatted_temp = f"{int(self.convert_fahrenheit(t) if use_fahrenheit else t)}{'F' if use_fahrenheit else 'C'}"

            # display the input values
            oled.text(f"ain: {ain.read_voltage():5.2f}v {formatted_temp}", 2, 3, 1)
            oled.text(f"k1: {k1.read_position():2}  k2: {k2.read_position():2}", 2, 13, 1)
            oled.text(f"din:{din.value()} b1:{b1.value()} b2:{b2.value()}", 2, 23, 1)

            # show the screen boundaries
            oled.rect(0, 0, OLED_WIDTH, OLED_HEIGHT, 1)
            oled.show()

            sleep(0.1)


if __name__ == "__main__":
    Diagnostic().main()
