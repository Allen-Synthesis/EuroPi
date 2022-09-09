import pytest

from europi import AnalogueReader, MAX_UINT16

from mock_hardware import MockHardware


@pytest.fixture
def analogueReader():
    return AnalogueReader(pin=1)  # actual pin value doesn't matter


@pytest.mark.parametrize(
    "percent, expected",
    [
        (0, 0.0000),
        (0.1, 0.1000),
        (0.25, 0.2500),
        (0.3333, 0.3333),
        (0.5, 0.5000),
        (0.90, 0.9000),
        (0.99, 0.99000),
        (1, 1.0000),
    ],
)
def test_set_percent(mockHardware: MockHardware, analogueReader, percent, expected):
    mockHardware.set_percent(analogueReader, percent)

    assert round(analogueReader.percent(), 4) == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        (0, 0.0000),
        (MAX_UINT16 / 4, 0.2500),
        (MAX_UINT16 / 3, 0.3333),
        (MAX_UINT16 / 2, 0.5000),
        (MAX_UINT16, 1.0000),
    ],
)
def test_percent(mockHardware: MockHardware, analogueReader, value, expected):
    mockHardware.set_ADC_u16_value(analogueReader, value)

    assert round(analogueReader.percent(), 4) == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        (0, 0),
        (MAX_UINT16 / 4, 25),
        (MAX_UINT16 / 3, 33),
        (MAX_UINT16 / 2, 50),
        (MAX_UINT16, 99),
    ],
)
def test_range(mockHardware: MockHardware, analogueReader, value, expected):
    mockHardware.set_ADC_u16_value(analogueReader, value)

    assert analogueReader.range() == expected


@pytest.mark.parametrize(
    "values, value, expected",
    [
        ([i for i in range(10)], 0, 0),
        ([i for i in range(10)], MAX_UINT16 / 4, 2),
        ([i for i in range(10)], MAX_UINT16 / 3, 3),
        ([i for i in range(10)], MAX_UINT16 / 2, 5),
        ([i for i in range(10)], MAX_UINT16, 9),
        (["a", "b"], 0, "a"),
        (["a", "b"], MAX_UINT16, "b"),
    ],
)
def test_choice(mockHardware: MockHardware, analogueReader, values, value, expected):
    mockHardware.set_ADC_u16_value(analogueReader, value)

    assert analogueReader.choice(values) == expected
