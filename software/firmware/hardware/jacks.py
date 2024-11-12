from europi_config import europi_config

from calibration import INPUT_CALIBRATION_VALUES, OUTPUT_CALIBRATION_VALUES

from hardware.io import HIGH, LOW, MAX_UINT16
from helpers import clamp

from machine import Pin
from machine import PWM

# PWM Frequency
PWM_FREQ = 100_000


class Output:
    """A class for sending digital or analogue voltage to an output jack.

    The outputs are capable of providing 0-10V, which can be achieved using
    the ``cvx.voltage()`` method.

    So that there is no chance of not having the full range, the chosen
    resistor values actually give you a range of about 0-10.5V, which is why
    calibration is important if you want to be able to output precise voltages.
    """

    def __init__(
        self,
        pin,
        min_voltage=europi_config.MIN_OUTPUT_VOLTAGE,
        max_voltage=europi_config.MAX_OUTPUT_VOLTAGE,
        calibration_values=OUTPUT_CALIBRATION_VALUES[0],
    ):
        self.pin = PWM(Pin(pin))
        self.pin.freq(PWM_FREQ)
        self.MIN_VOLTAGE = min_voltage
        self.MAX_VOLTAGE = max_voltage
        self.gate_voltage = clamp(europi_config.GATE_VOLTAGE, self.MIN_VOLTAGE, self.MAX_VOLTAGE)

        self._calibration_values = calibration_values
        self._duty = 0
        self._gradients = []
        for index, value in enumerate(self._calibration_values[:-1]):
            self._gradients.append(self._calibration_values[index + 1] - value)
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
        index = int(voltage // 1)
        self._set_duty(self._calibration_values[index] + (self._gradients[index] * (voltage % 1)))

    def on(self):
        """Set the voltage HIGH at 5 volts."""
        self.voltage(self.gate_voltage)

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
        if value == HIGH:
            self.on()
        else:
            self.off()