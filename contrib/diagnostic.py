from time import sleep

from europi import OLED_HEIGHT, OLED_WIDTH, ain, b1, b2, cv1, cv2, cv3, cv4, cv5, cv6, din, k1, k2, oled

"""
A diagnostic utility intended to help prove out a new europi build and calibration.
- Input values, including knobs and buttons, are shown on the screen.
- Outputs are held at specific, predictible, and hopefully useful values.
- The boundary of the screen is outlined.
- Inputs can be tested by self-patching the various CV outputs.
"""

# Set the outputs to useful values
cv1.voltage(0)  # min
cv2.voltage(0.5)  # not 0 but still below DI's threshold
cv3.voltage(1)
cv4.voltage(4)
cv5.voltage(5)
cv6.voltage(10)  # max

while True:
    oled.fill(0)

    # display the input values
    oled.text(f"ain: {ain.read_voltage():5.2f}v", 2, 3, 1)
    oled.text(f"k1: {k1.read_position():2}  k2: {k2.read_position():2}", 2, 13, 1)
    oled.text(f"din:{din.value()} b1:{b1.value()} b2:{b2.value()}", 2, 23, 1)

    # show the screen boundaries
    oled.rect(0, 0, OLED_WIDTH, OLED_HEIGHT, 1)
    oled.show()

    sleep(0.1)
