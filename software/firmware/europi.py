"""
Rory Allen 2024 Apache License Version 2.0

Before using any of this library, follow the instructions in
`programming_instructions.md <https://github.com/Allen-Synthesis/EuroPi/blob/main/software/programming_instructions.md>`_
to set up your module.

The EuroPi library is a single file named europi.py. It should be imported into any custom program by using ``from europi import *`` to give you full access to the functions within, which are outlined below. Inputs and outputs are used as objects, which each have methods to allow them to be used. These methods are used by using the name of the object, for example 'cv3' followed by a '.' and then the method name, and finally a pair of brackets containing any parameters that the method requires.

For example::

    cv3.voltage(4.5)

Will set the CV output 3 to a voltage of 4.5V.
"""

from calibration import INPUT_CALIBRATION_VALUES, OUTPUT_CALIBRATION_VALUES
from europi_config import europi_config
from experimental.experimental_config import experimental_config
from framebuf import FrameBuffer, MONO_HLSB
from hardware.buttons import Button
from hardware.display import Display, DummyDisplay
from hardware.io import AnalogueInput, DigitalInput
from hardware.jacks import Output
from hardware.knobs import Knob
from hardware.pins import *
from hardware.sensors import Thermometer, UsbConnection

from test_env import is_test_env

import sys
import time

from machine import I2C
from machine import Pin
from machine import freq

from version import __version__


# Analogue voltage read range.
MIN_INPUT_VOLTAGE = europi_config.MIN_INPUT_VOLTAGE
MAX_INPUT_VOLTAGE = europi_config.MAX_INPUT_VOLTAGE


# Output voltage range
MIN_OUTPUT_VOLTAGE = europi_config.MIN_OUTPUT_VOLTAGE
MAX_OUTPUT_VOLTAGE = europi_config.MAX_OUTPUT_VOLTAGE


def turn_off_all_cvs():
    """Calls cv.off() for every cv in cvs. This is done commonly enough in
    contrib scripts that a function seems useful.
    """
    for cv in cvs:
        cv.off()


def reset_state():
    """Return device to initial state with all components off and handlers reset."""
    if not is_test_env():
        oled.fill(0)
    turn_off_all_cvs()
    for d in (b1, b2, din):
        d.reset_handler()


def bootsplash():
    """Display the EuroPi version when booting."""
    image = b"\x00\x00\x00\x03\xe0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x07\xf8\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x06\x1c\x00\x00\x00\x00\x00\x00\x00\x01\x80\x00\x00\x00\x00\x00\x07\x0f\xe0\x00\x00\x00\x00\x00\x00\x01\x80\x00\x00\x00\x00\x00\x03\x07\xf0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x800\x00\xc0\x00\x00\x0e\x01\xc0\x00\x00\x00\x00\x00\x07\xe0\xc0p\x03\xf0\xc1\x971\x8e1\x80\x00\x00\x00\x00\x1f\xf8\xc1\xe0\x06\x18\xc1\x98`\xcc\x19\x80\x00\x00\x00\x00\x1c\x1f\xc3\x83\x04\x0c\xc1\x98@L\t\x80\x00\x00\x00\x000\x07\x87\x07\x0c\x0c\xc1\x90@H\t\x80\x00\x00\x00\x000\x00\x0e\x0e\x0f\xf8\xc1\x90@H\t\x80\x00\x00\x00\x008\x00\x1c\x0c\x0c\x00\xc1\x90@H\t\x80\x00\x00\x00\x00\x1f\x808\x0e\x04\x00\xc1\x90`\xcc\x19\x80\x00\x00\x00\x00\x0f\xe01\xc7\x06\x18c\x101\x8e1\x80\x00\x00\x00\x00\x00ps\xe3\x01\xe0\x1c\x10\x0e\r\xc1\x80\x00\x00\x00\x00\x00\x18c1\x80\x00\x00\x00\x00\x0c\x00\x00\x00\x00\x00\x00\x00\x18\xe31\x80\x00\x00\x00\x00\x0c\x00\x00\x00\x00\x00\x00\x008\xc1\x99\x80\x00\x00\x00\x00\x0c\x00\x00\x00\x00\x00\x00\x0e1\xc1\x99\x80\x00\x00\x00\x00\x0c\x00\x00\x00\x00\x00\x00\x1f\xe3\x80\xcf\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00;\xc7\x00\xc6\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x000\x0e\x00@\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x000\x1c\x00`\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00xp`\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xf0\xf80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\xc1\xd80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x03\x83\x980\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x03\x07\x180\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x86\x0c`\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xfe\x0e\xe0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00|\x07\xc0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x03\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
    TH = bytearray(image)
    fb = FrameBuffer(TH, 128, 32, MONO_HLSB)
    oled.blit(fb, 0, 0)

    version_str = str(__version__)
    version_length = len(version_str)
    offset = int(((150 - (version_length * CHAR_WIDTH)) / 2))
    oled.text(version_str, offset, 20, 1)

    oled.show()


# Define all the I/O using the appropriate class and with the pins used
din = DigitalInput(PIN_DIN)
ain = AnalogueInput(PIN_AIN)
k1 = Knob(PIN_K1)
k2 = Knob(PIN_K2)
b1 = Button(PIN_B1)
b2 = Button(PIN_B2)

try:
    oled = Display()
except Exception as e:
    print(e)
    oled = DummyDisplay()

cv1 = Output(PIN_CV1, calibration_values=OUTPUT_CALIBRATION_VALUES[0])
cv2 = Output(PIN_CV2, calibration_values=OUTPUT_CALIBRATION_VALUES[1])
cv3 = Output(PIN_CV3, calibration_values=OUTPUT_CALIBRATION_VALUES[2])
cv4 = Output(PIN_CV4, calibration_values=OUTPUT_CALIBRATION_VALUES[3])
cv5 = Output(PIN_CV5, calibration_values=OUTPUT_CALIBRATION_VALUES[4])
cv6 = Output(PIN_CV6, calibration_values=OUTPUT_CALIBRATION_VALUES[5])
cvs = [cv1, cv2, cv3, cv4, cv5, cv6]

# External I2C
external_i2c = I2C(
    europi_config.EXTERNAL_I2C_CHANNEL,
    sda=Pin(europi_config.EXTERNAL_I2C_SDA),
    scl=Pin(europi_config.EXTERNAL_I2C_SCL),
    freq=europi_config.EXTERNAL_I2C_FREQUENCY,
    timeout=europi_config.EXTERNAL_I2C_TIMEOUT,
)

thermometer = Thermometer()
usb_connected = UsbConnection()
led = Pin(PIN_LED, Pin.OUT)

# Overclock the Pico for improved performance.
freq(europi_config.CPU_FREQ)

# Reset the module state upon import.
reset_state()
