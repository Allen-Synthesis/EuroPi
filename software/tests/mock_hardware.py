from machine import ADC, Pin

from europi import AnalogueReader, DigitalReader, AnalogueInput


class MockHardware:
    """A class used in tests to stand in for actual EuroPi hardware. Allows a test to set the values for various
    hardware components, such as the position of a knob. Then a test can run a script and assert the script's behavior.
    """

    def __init__(self, monkeypatch):
        self._monkeypatch = monkeypatch
        self._adc_pin_values = {}
        self._digital_pin_values = {}

        self._patch()

    def _patch(self):
        self._monkeypatch.setattr(ADC, "read_u16", lambda pin: self._adc_pin_values[pin])
        self._monkeypatch.setattr(Pin, "value", lambda pin: self._digital_pin_values[pin])

    def set_ADC_u16_value(self, reader: AnalogueReader, value: int):
        """Sets the value that will be returned by a call to `read_u16` on the given AnalogueReader."""
        self._adc_pin_values[reader.pin] = value

    def set_digital_value(self, reader: DigitalReader, value: bool):
        """Sets the value that will be returned by a call to `value` on the given DigitalReader."""
        self._digital_pin_values[reader.pin] = not value
    
    def set_min_max_voltage(self, reader: AnalogueInput, min_voltage: float, max_voltage: float):
        """Sets the minimum and maximum voltage that will be returned by a call to `read_voltage` on the given AnalogueInput."""
        reader.MIN_VOLTAGE = min_voltage
        reader.MAX_VOLTAGE = max_voltage
