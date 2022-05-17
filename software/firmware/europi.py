"""
Rory Allen 19/11/2021 Apache License Version 2.0

Before using any of this library, follow the instructions in
`programming_instructions.md <https://github.com/Allen-Synthesis/EuroPi/blob/main/software/programming_instructions.md>`_
to set up your module.

The EuroPi library is a single file named europi.py. It should be imported into any custom program by using ``from europi import *`` to give you full access to the functions within, which are outlined below. Inputs and outputs are used as objects, which each have methods to allow them to be used. These methods are used by using the name of the object, for example 'cv3' followed by a '.' and then the method name, and finally a pair of brackets containing any parameters that the method requires.

For example::

    cv3.voltage(4.5)

Will set the CV output 3 to a voltage of 4.5V.
"""
import sys
import time

from machine import ADC
from machine import I2C
from machine import PWM
from machine import Pin

from ssd1306 import SSD1306_I2C

if sys.implementation.name == "micropython":
    TEST_ENV = False # We're in micropython, so we can assume access to real hardware
else:
    TEST_ENV = True # This var is set when we don't have any real hardware, for example in a test or doc generation setting

try:
    from calibration_values import INPUT_CALIBRATION_VALUES, OUTPUT_CALIBRATION_VALUES
except ImportError:
    # Note: run calibrate.py to get a more precise calibration.
    INPUT_CALIBRATION_VALUES=[384, 44634]
    OUTPUT_CALIBRATION_VALUES = [0, 6300, 12575, 19150, 25375, 31625, 38150, 44225, 50525, 56950, 63475]


# OLED component display dimensions.
OLED_WIDTH = 128
OLED_HEIGHT = 32
I2C_CHANNEL = 0
I2C_FREQUENCY = 400000

# Standard max int consts.
MAX_UINT16 = 65535

# Analogue voltage read range.
MIN_INPUT_VOLTAGE = 0
MAX_INPUT_VOLTAGE = 12
DEFAULT_SAMPLES = 32

# Output voltage range
MIN_OUTPUT_VOLTAGE = 0
MAX_OUTPUT_VOLTAGE = 10

# Default font is 8x8 pixel monospaced font.
CHAR_WIDTH = 8
CHAR_HEIGHT = 8


# Helper functions.

def clamp(value, low, high):
    """Returns a value that is no lower than 'low' and no higher than 'high'."""
    return max(min(value, high), low)


def reset_state():
    """Return device to initial state with all components off and handlers reset."""
    if not TEST_ENV:
        oled.fill(0)
    [cv.off() for cv in cvs]
    [d.reset_handler() for d in (b1, b2, din)]


# Component classes.

class AnalogueReader:
    """A base class for common analogue read methods.

    This class in inherited by classes like Knob and AnalogueInput and does
    not need to be used by user scripts.
    """

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
        """Return a value (upper bound excluded) chosen by the current voltage value."""
        if not isinstance(steps, int):
            raise ValueError(f"range expects an int value, got: {steps}")
        percent = self.percent(samples)
        if int(percent) == 1:
            return steps -1
        return int(percent * steps)

    def choice(self, values, samples=None):
        """Return a value from a list chosen by the current voltage value."""
        if not isinstance(values, list):
            raise ValueError(f"choice expects a list, got: {values}")
        percent = self.percent(samples)
        if percent == 1.0:
            return values[-1]
        return values[int(percent * len(values))]


class AnalogueInput(AnalogueReader):
    """A class for handling the reading of analogue control voltage.

    The analogue input allows you to 'read' CV from anywhere between 0 and 12V.

    It is protected for the entire Eurorack range, so don't worry about
    plugging in a bipolar source, it will simply be clipped to 0-12V.

    The functions all take an optional parameter of ``samples``, which will
    oversample the ADC and then take an average, which will take more time per
    reading, but will give you a statistically more accurate result. The
    default is 32, provides a balance of performance vs accuracy, but if you
    want to process at the maximum speed you can use as little as 1, and the
    processor won't bog down until you get way up into the thousands if you
    wan't incredibly accurate (but quite slow) readings.
    """
    def __init__(self, pin, min_voltage=MIN_INPUT_VOLTAGE, max_voltage=MAX_INPUT_VOLTAGE):
        super().__init__(pin)
        self.MIN_VOLTAGE = min_voltage
        self.MAX_VOLTAGE = max_voltage
        self._gradients = []
        for index, value in enumerate(INPUT_CALIBRATION_VALUES[:-1]):
            try:
                self._gradients.append(1 / (INPUT_CALIBRATION_VALUES[index+1] - value))
            except ZeroDivisionError:
                raise Exception(
                    "The input calibration process did not complete properly. Please complete again with rack power turned on")
        self._gradients.append(self._gradients[-1])

    def percent(self, samples=None):
        """Current voltage as a relative percentage of the component's range."""
        # Determine the percent value from the max calibration value.
        reading = self._sample_adc(samples)
        max_value = max(reading, INPUT_CALIBRATION_VALUES[-1])
        return reading / max_value

    def read_voltage(self, samples=None):
        reading = self._sample_adc(samples)
        max_value = max(reading, INPUT_CALIBRATION_VALUES[-1])
        percent = reading / max_value
        # low precision vs. high precision
        if len(self._gradients) == 2:
            cv = 10 * (reading / INPUT_CALIBRATION_VALUES[-1])
        else:
            index = int(percent * (len(INPUT_CALIBRATION_VALUES) - 1))
            cv = index + (self._gradients[index] *
                          (reading - INPUT_CALIBRATION_VALUES[index]))
        return clamp(cv, self.MIN_VOLTAGE, self.MAX_VOLTAGE)


class Knob(AnalogueReader):
    """A class for handling the reading of knob voltage and position.

    Read_position has a default value of 100, meaning if you simply use
    ``kx.read_position()`` you will return a whole number percent style value
    from 0-100.

    There is also the optional parameter of ``samples`` (which must come after the
    normal parameter), the same as the analogue input uses (the knob positions
    are 'read' via an analogue to digital converter). It has a default value
    of 256, but you can use higher or lower depending on if you value speed or
    accuracy more. If you really want to avoid 'noise' which would present as
    a flickering value despite the knob being still, then I'd suggest using
    higher samples (and probably a smaller number to divide the position by).
    The default ``samples`` value can also be set using the ``set_samples()``
    method, which will then be used on all analogue read calls for that
    component.

    Additionally, the ``choice()`` method can be used to select a value from a
    list of values based on the knob's position::

        def clock_division(self):
            return k1.choice([1, 2, 3, 4, 5, 6, 7, 8, 16, 32])

    When the knob is all the way to the left, the return value will be ``1``,
    at 12 o'clock it will return the mid point value of ``5`` and when fully
    clockwise, the last list item of ``32`` will be returned.

    The ADCs used to read the knob position are only 12 bit, which means that
    any read_position value above 4096 (2^12) will not actually be any finer
    resolution, but will instead just go up in steps. For example using 8192
    would only return values which go up in steps of 2.
    """

    def __init__(self, pin):
        super().__init__(pin)

    def percent(self, samples=None):
        """Return the knob's position as relative percentage."""
        # Reverse range to provide increasing range.
        return 1 - (self._sample_adc(samples) / MAX_UINT16)

    def read_position(self, steps=100, samples=None):
        """Returns the position as a value between zero and provided integer."""
        return self.range(steps, samples)


class DigitalReader:
    """A base class for common digital inputs methods.

    This class in inherited by classes like Button and DigitalInput and does
    not need to be used by user scripts.

    """
    def __init__(self, pin, debounce_delay=500):
        self.pin = Pin(pin, Pin.IN)
        self.debounce_delay = debounce_delay

        # Default handlers are noop callables.
        self._rising_handler = lambda: None
        self._falling_handler = lambda: None

        # Both high handler
        self._both_handler = lambda: None
        self._other = None

        # IRQ event timestamps
        self.last_rising_ms = 0
        self.last_falling_ms = 0

    def _bounce_wrapper(self, pin):
        """IRQ handler wrapper for falling and rising edge callback functions."""
        if self.value() == 1:
            if time.ticks_diff(time.ticks_ms(), self.last_rising_ms) < self.debounce_delay:
                return
            self.last_rising_ms = time.ticks_ms()
            return self._rising_handler()

        elif self.value() == 0:
            if time.ticks_diff(time.ticks_ms(), self.last_falling_ms) < self.debounce_delay:
                return
            self.last_falling_ms = time.ticks_ms()

            # Check if 'other' pin is set and if 'other' pins is high and if this pin has been high for long enough.
            if self._other and self._other.value() and time.ticks_diff(self.last_falling_ms, self.last_rising_ms) > 500:
                return self._both_handler()

            return self._falling_handler()

    def value(self):
        """The current binary value, HIGH (1) or LOW (0)."""
        # Both the digital input and buttons are normally high, and 'pulled'
        # low when on, so this is flipped to be more intuitive (1 when on, 0
        # when off)
        return 1 - self.pin.value()

    def handler(self, func):
        """Define the callback function to call when rising edge detected."""
        if not callable(func):
            raise ValueError("Provided handler func is not callable")
        self._rising_handler = func
        self.pin.irq(handler=self._bounce_wrapper)

    def handler_falling(self, func):
        """Define the callback function to call when falling edge detected."""
        if not callable(func):
            raise ValueError("Provided handler func is not callable")
        self._falling_handler = func
        self.pin.irq(handler=self._bounce_wrapper)

    def reset_handler(self):
        self.pin.irq(handler=None)

    def _handler_both(self, other, func):
        """When this and other are high, execute the both func."""
        if not callable(func):
            raise ValueError("Provided handler func is not callable")
        self._other = other
        self._both_handler = func
        self.pin.irq(handler=self._bounce_wrapper)


class DigitalInput(DigitalReader):
    """A class for handling reading of the digital input.

    The Digital Input jack can detect a HIGH signal when recieving voltage >
    0.8v and will be LOW when below.

    To use the handler method, you simply define whatever you want to happen
    when a button or the digital input is triggered, and then use
    ``x.handler(new_function)``. Do not include the brackets for the function,
    and replace the 'x' in the example with the name of your input, either
    ``b1``, ``b2``, or ``din``.

    Here is another example how you can write digital input handlers to react
    to a clock source and match its trigger duration.::

        @din.handler
        def gate_on():
            # Trigger outputs with a probability set by knobs.
            cv1.value(random() > k1.percent())
            cv2.value(random() > k2.percent())

        @din.handler_falling
        def gate_off():
            # Turn off all triggers on falling clock trigger to match clock.
            cv1.off()
            cv2.off()

    When writing a handler, try to keep the code as minimal as possible.
    Ideally handlers should be used to change state and allow your main loop
    to change behavior based on the altered state. See `tips <https://docs.micropython.org/en/latest/reference/isr_rules.html#tips-and-recommended-practices>`_
    from the MicroPython documentation for more details.
    """
    def __init__(self, pin, debounce_delay=0):
        super().__init__(pin, debounce_delay)

    def last_triggered(self):
        """Return the ticks_ms of the last trigger.

        If the button has not yet been pressed, the default return value is 0.
        """
        return self.last_rising_ms


class Button(DigitalReader):
    """A class for handling push button behavior.

    Button instances have a method ``last_pressed()``
    (similar to ``DigitalInput.last_triggered()``) which can be used by your
    script to help perform some action or behavior relative to when the button
    was last pressed (or input trigger received). For example, if you want to
    call a function to display a message that a button was pressed, you could
    add the following code to your main script loop::

        # Inside the main loop...
        if b1.last_pressed() > 0 and ticks_diff(ticks_ms(), b1.last_pressed()) < 2000:
            # Call this during the 2000 ms duration after button press.
            display_button_pressed()

    Note, if a button has not yet been pressed, the ``last_pressed()`` default
    return value is 0, so you may want to add the check `if b1.last_pressed() > 0`
    before you check the elapsed duration to ensure the button has been
    pressed. This is also useful when checking if the digital input has been
    triggered with the ``DigitalInput.last_triggered()`` method.

    """
    def __init__(self, pin, debounce_delay=200):
        super().__init__(pin, debounce_delay)

    def last_pressed(self):
        """Return the ticks_ms of the last button press

        If the button has not yet been pressed, the default return value is 0.
        """
        return self.last_rising_ms


class Display(SSD1306_I2C):
    """A class for drawing graphics and text to the OLED.

    The OLED Display works by collecting all the applied commands and only
    updates the physical display when ``oled.show()`` is called. This allows
    you to perform more complicated graphics without slowing your program, or
    to perform the calculations for other functions, but only update the
    display every few steps to prevent lag.
    
    To clear the display, simply fill the display with the colour black by using ``oled.fill(0)``

    More explanations and tips about the the display can be found in the oled_tips file
    `oled_tips.md <https://github.com/Allen-Synthesis/EuroPi/blob/main/software/oled_tips.md>`_
    """
    def __init__(self, sda, scl, width=OLED_WIDTH, height=OLED_HEIGHT, channel=I2C_CHANNEL, freq=I2C_FREQUENCY):
        i2c = I2C(channel, sda=Pin(sda), scl=Pin(scl), freq=freq)
        self.width = width
        self.height = height

        if len(i2c.scan()) == 0:
            if not TEST_ENV:
                raise Exception(
                    "EuroPi Hardware Error:\nMake sure the OLED display is connected correctly")

        super().__init__(self.width, self.height, i2c)

    def centre_text(self, text):
        """Split the provided text across 3 lines of display."""
        self.fill(0)
        # Default font is 8x8 pixel monospaced font which can be split to a
        # maximum of 4 lines on a 128x32 display, but we limit it to 3 lines
        # for readability.
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
    """A class for sending digital or analogue voltage to an output jack.

    The outputs are capable of providing 0-10V, which can be achieved using
    the ``cvx.voltage()`` method.

    So that there is no chance of not having the full range, the chosen
    resistor values actually give you a range of about 0-10.5V, which is why
    calibration is important if you want to be able to output precise voltages.
    """
    def __init__(self, pin, min_voltage=MIN_OUTPUT_VOLTAGE, max_voltage=MAX_OUTPUT_VOLTAGE):
        self.pin = PWM(Pin(pin))
        # Set freq to 1kHz as the default is too low and creates audible PWM 'hum'.
        self.pin.freq(100_000)
        self._duty = 0
        self.MIN_VOLTAGE = min_voltage
        self.MAX_VOLTAGE = max_voltage

        self._gradients = []
        for index, value in enumerate(OUTPUT_CALIBRATION_VALUES[:-1]):
            self._gradients.append(OUTPUT_CALIBRATION_VALUES[index+1] - value)
        self._gradients.append(self._gradients[-1])


    def _set_duty(self, cycle):
        cycle = int(cycle)
        self.pin.duty_u16(clamp(cycle, 0, MAX_UINT16))
        self._duty = cycle

    def voltage(self, voltage=None):
        """Set the output voltage to the provided value within the range of 0 to 10."""
        if voltage is None:
            return self._duty / MAX_UINT16

        voltage = clamp(voltage, self.MIN_VOLTAGE, self.MAX_VOLTAGE)
        index = int(voltage//1)
        self._set_duty(OUTPUT_CALIBRATION_VALUES[index] + (self._gradients[index]*(voltage%1)))

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

    def value(self, value):
        """Sets the output to 0V or 5V based on a binary input, 0 or 1."""
        if value == 1:
            self.on()
        else:
            self.off()


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
