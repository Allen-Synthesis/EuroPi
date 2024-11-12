from europi_config import europi_config

from hardware.io import DigitalReader
from hardware.pins import *

from hardware.pins import *
from machine import ADC
from machine import mem32

class Thermometer:
    """
    Wrapper for the temperature sensor connected to Pin 4

    Reports the module's current temperature in Celsius.

    If the module's temperature sensor is not working correctly, the temperature will always be reported as None
    """

    # Conversion factor for converting from the raw ADC reading to sensible units
    # See Raspberry Pi Pico datasheet for details
    TEMP_CONV_FACTOR = 3.3 / 65535

    def __init__(self):
        # The Raspberry Pi Pico 2's temperature sensor doesn't work reliably (yet)
        # so do some basic exception handling
        try:
            self.pin = ADC(PIN_TEMPERATURE)
        except:
            self.pin = None

    def read_temperature(self):
        """
        Read the ADC and return the current temperature

        @return  The current temperature in Celsius, or None if the hardware did not initialze properly
        """
        if self.pin:
            # see the pico's datasheet for the details of this calculation
            return 27 - ((self.pin.read_u16() * self.TEMP_CONV_FACTOR) - 0.706) / 0.001721
        else:
            return None


class UsbConnection:
    """
    Checks the USB terminal is connected or not

    On the original Pico we can check Pin 24, but on the Pico 2 this does not work. In that case
    check the SIE_STATUS register and check bit 16
    """

    def __init__(self):
        if europi_config.PICO_MODEL == "pico2":
            self.pin = None
        else:
            self.pin = DigitalReader(PIN_USB_CONNECTED)

    def value(self):
        """Return 0 or 1, indicating if the USB connection is disconnected or connected"""
        if self.pin:
            return self.pin.value()
        else:
            # see https://forum.micropython.org/viewtopic.php?t=10814#p59545
            SIE_STATUS = 0x50110000 + 0x50
            BIT_CONNECTED = 1 << 16
            if mem32[SIE_STATUS] & BIT_CONNECTED:
                return 1
            else:
                return 0
