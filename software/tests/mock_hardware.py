from machine import ADC, Pin

from europi import (
    AnalogueReader,
    DigitalReader,
    Knob,
    MAX_UINT16,
    INPUT_CALIBRATION_VALUES,
)


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

    def set_percent(self, reader: AnalogueReader, value: float):
        self.set_ADC_u16_value(reader, value * MAX_UINT16)

    def set_analogue_input_percent(self, reader: AnalogueReader, value: float):
        self.set_ADC_u16_value(
            reader,
            value * (INPUT_CALIBRATION_VALUES[-1] - INPUT_CALIBRATION_VALUES[0])
            + INPUT_CALIBRATION_VALUES[0],
        )

    def set_knob_percent(self, knob: Knob, value: float):
        self.set_ADC_u16_value(knob, (1 - value) * MAX_UINT16)
