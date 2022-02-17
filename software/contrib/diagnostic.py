from machine import ADC
from time import sleep

from europi import OLED_HEIGHT, OLED_WIDTH, ain, b1, b2, cv1, cv2, cv3, cv4, cv5, cv6, din, k1, k2, oled

"""
A diagnostic utility intended to help prove out a new europi build and calibration.
- Input values, including knobs and buttons, are shown on the screen.
- Outputs are held at specific, predictable, and hopefully useful values.
- The boundary of the screen is outlined.
- temperature as read by the Pico's on board temperature sensor, in deg F when a button is pressed, deg C otherwise
- Inputs can be tested by self-patching the various CV outputs.
"""

# Set the outputs to useful values
cv1.voltage(0)  # min
cv2.voltage(0.5)  # not 0 but still below DI's threshold
cv3.voltage(1)
cv4.voltage(4)
cv5.voltage(5)
cv6.voltage(10)  # max

temp_sensor = ADC(4)
TEMP_CONV_FACTOR = 3.3 / 65535


def calc_temp():
    # see the pico's datasheet for the details of this calculation
    return 27 - ((temp_sensor.read_u16() * TEMP_CONV_FACTOR) - 0.706) / 0.001721


def convert_fahrenheit(temp_c):
    return (temp_c * 1.8) + 32


while True:
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
