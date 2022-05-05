from machine import ADC

class MockHardware:
    """A class used in tests to stand in for actual EuroPi hardware. Allows a test to set the values for various
    hardware components, such as the position of a knob. Then a test can run a script and assert the script's behavior.
    """

    def __init__(self, monkeypatch):
        self._monkeypatch = monkeypatch
        self._adc_pin_values = {}

        self._patch()

    def _patch(self):
        self._monkeypatch.setattr(ADC, "read_u16", lambda pin: self._adc_pin_values[pin])

    def set_ADC_u16_value(self, component, value):
        """Sets the value that will be returned by a call to `read_u16` on the given component."""
        self._adc_pin_values[component.pin] =  value