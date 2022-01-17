"""
Rory Allen 19/11/2021 CC BY-SA 4.0

You can then use the inputs, outputs, knobs, and buttons as objects, and makeuse of the general purpose functions

Import this library into your own programs using 'from europi import *'
You can use this library by importing individual comonents:

"""
from time import ticks_ms

from machine import ADC
from machine import I2C
from machine import PWM
from machine import Pin

from ssd1306 import SSD1306_I2C

try:
    from calibration import CALIBRATION_VALUES
except ImportError:
    raise Exception("Please run calibration script.")

# TODO: update calibrate.py to provide output calibration value.
OUTPUT_MULTIPLIER = 6347.393

# OLED component display dimensions.
OLED_WIDTH = 128
OLED_HEIGHT = 32
I2C_CHANNEL = 0
I2C_FREQUENCY = 400000

# Standard max int consts.
MAX_UINT16 = 65535
MAX_UINT12 = 4096

# Analogue voltage read range.
MIN_VOLTAGE = 0
MAX_VOLTAGE = 12
DEFAULT_SAMPLES = 32

# Default font is 8x8 pixel monospaced font.
CHAR_WIDTH = 8
CHAR_HEIGHT = 8


# Helper functions.

def clamp(value, low, high):
    return max(min(value, high), low)


def reset_state():
    """Return device to initial state with all components off and handlers reset."""
    oled.clear()
    [cv.off() for cv in cvs]
    [d.reset_handler() for d in (b1, b2, din)]


class AnalogueReader:
    def __init__(self, pin, samples=DEFAULT_SAMPLES):
        self.pin = ADC(Pin(pin))
        self.set_samples(samples)

    def _sample_adc(self, samples=None):
        # Over-samples the ADC and returns the average.
        values = []
        for _ in range(samples or self._samples):
            values.append(self.pin.read_u16())
        return round(sum(values) / len(values))

    def set_samples(self, samples):
        """Override the default number of sample reads with the given value."""
        if not isinstance(samples, int):
            raise ValueError(
                f"set_samples expects an int value, got: {samples}")
        self._samples = samples

    def percent(self, samples=None):
        """Return the percentage of the component's current relative range."""
        return self._sample_adc(samples) / MAX_UINT16

    def range(self, steps=100, samples=None):
        """Return a value from steps chosen by the current voltages relative position."""
        if not isinstance(steps, int):
            raise ValueError(f"range expects an int value, got: {steps}")
        return int(self.percent(samples) * steps)

    def choice(self, values, samples=None):
        """Return a value from a list chosen by the knob position."""
        if not isinstance(values, list):
            raise ValueError(f"choice expects a list, got: {values}")
        return values[int(self.percent(samples) * (len(values) - 1))]


class AnalogueInput(AnalogueReader):
    def __init__(self, pin):
        super().__init__(pin)
        self._gradients = []
        for index, value in enumerate(CALIBRATION_VALUES[:-1]):
            self._gradients.append(1 / (CALIBRATION_VALUES[index+1] - value))
        self._gradients.append(self._gradients[-1])

    def percent(self, samples=None):
        """Current voltage as a relative percentage of the component's range."""
        # Determine the percent value from the max calibration value.
        reading = self._sample_adc(samples)
        max_value = max(reading, CALIBRATION_VALUES[-1])
        return reading / max_value

    def read_voltage(self, samples=None):
        reading = self._sample_adc(samples)
        index = int(self.percent(samples) * (len(CALIBRATION_VALUES) - 1))
        cv = index + (self._gradients[index] *
                      (reading - CALIBRATION_VALUES[index]))
        return clamp(cv, MIN_VOLTAGE, MAX_VOLTAGE)


class Knob(AnalogueReader):
    def __init__(self, pin):
        super().__init__(pin)

    def percent(self, samples=None):
        """Return the knob's position as relative percentage."""
        # Reverse range to provide increasing range.
        return 1 - (self._sample_adc(samples) / MAX_UINT16)


class DigitalReader:
    def __init__(self, pin, debounce_delay=500):
        self.pin = Pin(pin, Pin.IN)
        self.debounce_delay = debounce_delay
        self.last_pressed = 0

    def value(self):
        """The current binary value, HIGH (1) or LOW (0)."""
        # Both the digital input and buttons are normally high, and 'pulled'
        # low when on, so this is flipped to be more intuitive (1 when on, 0
        # when off)
        return 1 - self.pin.value()

    def handler(self, func):
        """Define the callback func to call when rising edge detected."""
        def bounce_wrapper(pin):
            if (ticks_ms() - self.last_pressed) > self.debounce_delay:
                self.last_pressed = ticks_ms()
                func()
        # Both the digital input and buttons are normally high, and 'pulled'
        # low when on, so here we use IRQ_FALLING to detect rising edge.
        self.pin.irq(trigger=Pin.IRQ_FALLING, handler=bounce_wrapper)

    def reset_handler(self):
        self.pin.irq(trigger=Pin.IRQ_FALLING)


class DigitalInput(DigitalReader):
    def __init__(self, pin, debounce_delay=0):
        super().__init__(pin, debounce_delay)


class Button(DigitalReader):
    def __init__(self, pin, debounce_delay=500):
        super().__init__(pin, debounce_delay)


class Display(SSD1306_I2C):
    def __init__(self, sda, scl, width=OLED_WIDTH, height=OLED_HEIGHT, channel=I2C_CHANNEL, freq=I2C_FREQUENCY):
        i2c = I2C(channel, sda=Pin(sda), scl=Pin(scl), freq=freq)
        self.width = width
        self.height = height

        if len(i2c.scan()) == 0:
            raise Exception(
                "EuroPi Hardware Error:\nMake sure the OLED display is connected correctly")

        super().__init__(self.width, self.height, i2c)

    def clear(self):
        """Clear the display upon call."""
        self.fill(0)
        self.show()

    def centre_text(self, text):
        """Split the provided text across 3 lines of display."""
        self.fill(0)
        # Default font is 8x8 pixel monospaced font which can be split to a
        # maximum of 4 lines on a 128x32 display.
        lines = str(text).split('\n')
        maximum_lines = round(self.height / CHAR_HEIGHT)
        if len(lines) > maximum_lines:
            raise Exception(
                "Provided text exceeds available space on oled display.")

        padding_top = (self.height - (len(lines) * 9)) / 2
        for index, content in enumerate(lines):
            x_offset = int((self.width - ((len(content) + 1) * 7)) / 2) - 1
            y_offset = int((index * 9) + padding_top) - 1
            self.text(content, x_offset, y_offset)
        oled.show()


class Output:
    def __init__(self, pin):
        self.pin = PWM(Pin(pin))
        # Set freq to 1kHz as the default is too low and creates audible PWM 'hum'.
        self.pin.freq(1_000_000)
        self._duty = 0

    def _set_duty(self, cycle):
        cycle = int(cycle)
        self.pin.duty_u16(clamp(cycle, 0, MAX_UINT16 - 1))
        self._duty = cycle

    def voltage(self, voltage=None):
        """Set the output voltage to the provided value within the range of 0 to 10."""
        if voltage is None:
            return self._duty / OUTPUT_MULTIPLIER
        if 0 > voltage or voltage > 10:
            raise ValueError(
                f"voltage expects a value between 0 and 10, got: {voltage}")
        self._set_duty(voltage * OUTPUT_MULTIPLIER)

    def on(self):
        """Set the voltage HIGH at 5 volts."""
        self.voltage(5)

    def off(self):
        """Set the voltage LOW at 0 volts."""
        self._set_duty(0)

    def toggle(self):
        """Invert the Output's current state."""
        if self._duty > 500:
            self.off()
        else:
            self.on()


# Define all the I/O using the appropriate class and with the pins used
din = DigitalInput(22)
ain = AnalogueInput(26)
k1 = Knob(27)
k2 = Knob(28)
b1 = Button(4)
b2 = Button(5)

oled = Display(0, 1)
cv1 = Output(21)
cv2 = Output(20)
cv3 = Output(16)
cv4 = Output(17)
cv5 = Output(18)
cv6 = Output(19)
cvs = [cv1, cv2, cv3, cv4, cv5, cv6]

# Reset the module state upon import.
reset_state()
