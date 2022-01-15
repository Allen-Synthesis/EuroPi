"""
Rory Allen 19/11/2021 CC BY-SA 4.0

You can then use the inputs, outputs, knobs, and buttons as objects, and make use of the general purpose functions

Import this library into your own programs using 'from europi import *'
You can use this library by importing individual comonents:

"""
from time import sleep_ms
from time import ticks_ms

from machine import ADC
from machine import I2C
from machine import PWM
from machine import Pin

from ssd1306 import SSD1306_I2C

from calibration import INPUT_MULTIPLIER
from calibration import OUTPUT_MULTIPLIER
from calibration import INPUT_OFFSET


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

# Default font is 8x8 pixel monospaced font
CHAR_WIDTH = 8
CHAR_HEIGHT = 8


def clamp(value, low, high):
    return max(min(value, high), low)


class AnalogueReader:
    def __init__(self, pin, samples=32):
        self.pin = ADC(Pin(pin))
        self._samples = samples

    def _sample_adc(self, samples=None):
        # Over-samples the ADC and returns the average. Default 256 samples.
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

    def value(self, samples=None):
        """Current voltage as a 16 bit int."""
        return self._sample_adc(samples)

    def percent(self, samples=None):
        """Current voltage as a relative percentage of the component's range."""
        return self.value(samples) / MAX_UINT16

    def range(self, steps, samples=None):
        """Return a value from steps chosen by the current voltages relative position."""
        if not isinstance(steps, int):
            raise ValueError(f"range expects an int value, got: {steps}")
        return int(self.percent(samples) * steps)

    def choice(self, values):
        """Return a value from a range chosen by the knob position."""
        if not isinstance(values, list):
            raise ValueError(f"choice expects a list, got: {values}")
        return values[int(self.percent() * (len(values) - 1))]


class AnalogueInput(AnalogueReader):
    def __init__(self, pin):
        super().__init__(pin)

    def read_voltage(self, samples=None):
        """Read the analogue input voltage within the range of 0 to 12 volts."""
        cv = (self.value(samples) * INPUT_MULTIPLIER) + INPUT_OFFSET
        return clamp(cv, MIN_VOLTAGE, MAX_VOLTAGE)


class Knob(AnalogueReader):
    def __init__(self, pin):
        super().__init__(pin)

    def percent(self, samples=None):
        # Reverse range to provide increasing range.
        return 1 - self.value(samples)


class DigitalReader:
    def __init__(self, pin, debounce_delay=500):
        self.pin = Pin(pin, Pin.IN)
        self.debounce_delay = debounce_delay
        self.last_pressed = 0

    def value(self):
        # Both the digital input and buttons are normally high, and 'pulled'
        # low when on, so this is flipped to be more intuitive (1 when on, 0
        # when off)
        return 1 - self.pin.value()

    def handler(self, func):
        def bounce_wrapper(pin):
            if (ticks_ms() - self.last_pressed) > self.debounce_delay:
                self.last_pressed = ticks_ms()
                func()
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
            raise ValueError(f"voltage expects a value between 0 and 10, got: {voltage}")
        self._set_duty(voltage * OUTPUT_MULTIPLIER)

    def on(self):
        self.voltage(5)

    def off(self):
        self._set_duty(0)

    def toggle(self):
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
for cv in cvs:
    cv.off()
