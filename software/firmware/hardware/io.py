from europi_config import europi_config

from machine import ADC, Pin

import time

# Digital input and output binary values.
HIGH = 1
LOW = 0


# Standard max int consts.
MAX_UINT16 = 65535

# Default number of samples when reading an ADC
DEFAULT_SAMPLES = 32


class AnalogueReader:
    """A base class for common analogue read methods.

    This class in inherited by classes like Knob and AnalogueInput and does
    not need to be used by user scripts.
    """

    def __init__(self, pin, samples=DEFAULT_SAMPLES, deadzone=0.0):
        self.pin_id = pin
        self.pin = ADC(Pin(pin))
        self.set_samples(samples)
        self.set_deadzone(deadzone)

    def _sample_adc(self, samples=None):
        # Over-samples the ADC and returns the average.
        value = 0
        for _ in range(samples or self._samples):
            value += self.pin.read_u16()
        return round(value / (samples or self._samples))

    def set_samples(self, samples):
        """Override the default number of sample reads with the given value."""
        if not isinstance(samples, int):
            raise ValueError(f"set_samples expects an int value, got: {samples}")
        self._samples = samples

    def set_deadzone(self, deadzone):
        """Override the default deadzone with the given value."""
        if not isinstance(deadzone, float):
            raise ValueError(f"set_deadzone expects an float value, got: {deadzone}")
        self._deadzone = deadzone

    def percent(self, samples=None, deadzone=None):
        """Return the percentage of the component's current relative range."""
        dz = self._deadzone
        if deadzone is not None:
            dz = deadzone
        value = self._sample_adc(samples) / MAX_UINT16
        value = value * (1.0 + 2.0 * dz) - dz
        return clamp(value, 0.0, 1.0)

    def range(self, steps=100, samples=None, deadzone=None):
        """Return a value (upper bound excluded) chosen by the current voltage value."""
        if not isinstance(steps, int):
            raise ValueError(f"range expects an int value, got: {steps}")
        percent = self.percent(samples, deadzone)
        if int(percent) == 1:
            return steps - 1
        return int(percent * steps)

    def choice(self, values, samples=None, deadzone=None):
        """Return a value from a list chosen by the current voltage value."""
        if not isinstance(values, list):
            raise ValueError(f"choice expects a list, got: {values}")
        percent = self.percent(samples, deadzone)
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

    The percent function takes an optional parameter ``deadzone``. However this
    parameter is ignored and just present to be compatible with the percent
    function of the AnalogueReader and Knob classes
    """

    def __init__(
        self,
        pin,
        min_voltage=europi_config.MIN_INPUT_VOLTAGE,
        max_voltage=europi_config.MAX_INPUT_VOLTAGE
    ):
        super().__init__(pin)
        self.MIN_VOLTAGE = min_voltage
        self.MAX_VOLTAGE = max_voltage
        self._gradients = []
        for index, value in enumerate(INPUT_CALIBRATION_VALUES[:-1]):
            try:
                self._gradients.append(1 / (INPUT_CALIBRATION_VALUES[index + 1] - value))
            except ZeroDivisionError:
                raise Exception(
                    "The input calibration process did not complete properly. Please complete again with rack power turned on"
                )
        self._gradients.append(self._gradients[-1])

    def percent(self, samples=None, deadzone=None):
        """Current voltage as a relative percentage of the component's range."""
        # Determine the percent value from the max calibration value.
        reading = self._sample_adc(samples) - INPUT_CALIBRATION_VALUES[0]
        max_value = max(
            reading,
            INPUT_CALIBRATION_VALUES[-1] - INPUT_CALIBRATION_VALUES[0],
        )
        return max(reading / max_value, 0.0)

    def read_voltage(self, samples=None):
        raw_reading = self._sample_adc(samples)
        reading = raw_reading - INPUT_CALIBRATION_VALUES[0]
        max_value = max(
            reading,
            INPUT_CALIBRATION_VALUES[-1] - INPUT_CALIBRATION_VALUES[0],
        )
        percent = max(reading / max_value, 0.0)
        # low precision vs. high precision
        if len(self._gradients) == 2:
            cv = 10 * max(
                reading / (INPUT_CALIBRATION_VALUES[-1] - INPUT_CALIBRATION_VALUES[0]),
                0.0,
            )
        else:
            index = int(percent * (len(INPUT_CALIBRATION_VALUES) - 1))
            cv = index + (self._gradients[index] * (raw_reading - INPUT_CALIBRATION_VALUES[index]))
        return clamp(cv, self.MIN_VOLTAGE, self.MAX_VOLTAGE)


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
        if self.value() == HIGH:
            if time.ticks_diff(time.ticks_ms(), self.last_rising_ms) < self.debounce_delay:
                return
            self.last_rising_ms = time.ticks_ms()
            return self._rising_handler()
        else:
            if time.ticks_diff(time.ticks_ms(), self.last_falling_ms) < self.debounce_delay:
                return
            self.last_falling_ms = time.ticks_ms()

            # Check if 'other' pin is set and if 'other' pins is high and if this pin has been high for long enough.
            if (
                self._other
                and self._other.value()
                and time.ticks_diff(self.last_falling_ms, self.last_rising_ms) > 500
            ):
                return self._both_handler()
            return self._falling_handler()

    def value(self):
        """The current binary value, HIGH (1) or LOW (0)."""
        # Both the digital input and buttons are normally high, and 'pulled'
        # low when on, so this is flipped to be more intuitive
        # (high when on, low when off)
        return LOW if self.pin.value() else HIGH

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
