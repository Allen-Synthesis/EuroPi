import pytest

from europi import DigitalReader

from mock_hardware import MockHardware


@pytest.fixture
def digitalReader():
    return DigitalReader(pin=1)  # actual pin value doesn't matter


@pytest.mark.parametrize(
    "value, expected",
    [
        (0, 0),
        (1, 1),
    ],
)
def test_value(mockHardware: MockHardware, digitalReader, value, expected):
    mockHardware.set_digital_value(digitalReader, value)

    assert digitalReader.value() == expected
