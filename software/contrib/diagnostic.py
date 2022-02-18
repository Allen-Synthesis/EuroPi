from machine import ADC
from time import sleep

from europi import OLED_HEIGHT, OLED_WIDTH, ain, b1, b2, cv1, cv2, cv3, cv4, cv5, cv6, din, k1, k2, oled

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

voltages = [
    0,  # min
    0.5,  # not 0 but still below DI's threshold
    1,
    2.5,
    5,
    10,  # max
]

temp_sensor = ADC(4)
TEMP_CONV_FACTOR = 3.3 / 65535


def calc_temp():
    # see the pico's datasheet for the details of this calculation
    return 27 - ((temp_sensor.read_u16() * TEMP_CONV_FACTOR) - 0.706) / 0.001721


def convert_fahrenheit(temp_c):
    return (temp_c * 1.8) + 32


def rotate_r():
    global voltages
    voltages = voltages[-1:] + voltages[:-1]

def rotate_l():
    global voltages
    voltages = voltages[1:] + voltages[:1]


b1.handler(rotate_l)
b2.handler(rotate_r)

while True:

    # Set the outputs to useful values
    cv1.voltage(voltages[0])
    cv2.voltage(voltages[1])
    cv3.voltage(voltages[2])
    cv4.voltage(voltages[3])
    cv5.voltage(voltages[4])
    cv6.voltage(voltages[5])

    oled.fill(0)

    # calc and format temp
    use_fahrenheit = b1.value() or b2.value()
    t = calc_temp()
    formatted_temp = f"{int(convert_fahrenheit(t) if use_fahrenheit else t)}{'F' if use_fahrenheit else 'C'}"

    # display the input values
    oled.text(f"ain: {ain.read_voltage():5.2f}v {formatted_temp}", 2, 3, 1)
    oled.text(f"k1: {k1.read_position():2}  k2: {k2.read_position():2}", 2, 13, 1)
    oled.text(f"din:{din.value()} b1:{b1.value()} b2:{b2.value()}", 2, 23, 1)

    # show the screen boundaries
    oled.rect(0, 0, OLED_WIDTH, OLED_HEIGHT, 1)
    oled.show()

    sleep(0.1)
