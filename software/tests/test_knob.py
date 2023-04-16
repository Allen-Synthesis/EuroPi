import pytest

from europi import k1, k2, MAX_UINT16

from mock_hardware import MockHardware


@pytest.mark.parametrize(
    "value, expected",
    [
        (1, 1.0000),
        (0.75, 0.7500),
        (0.66, 0.6600),
        (0.5, 0.5000),
        (0, 0.0000),
    ],
)
def test_set_knob_percent(mockHardware: MockHardware, value, expected):
    mockHardware.set_knob_percent(k1, value)

    assert round(k1.percent(deadzone=0.0), 4) == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        (1, 1.0000),
        (0.75, 0.755),
        (0.66, 0.6632),
        (0.5, 0.5000),
        (0, 0.0000),
    ],
)
def test_set_knob_percent_w_deadzone(mockHardware: MockHardware, value, expected):
    mockHardware.set_knob_percent(k1, value)

    assert round(k1.percent(deadzone=0.01), 4) == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        (0, 1.0000),
        (MAX_UINT16 / 4, 0.7500),
        (MAX_UINT16 / 3, 0.6667),
        (MAX_UINT16 / 2, 0.5000),
        (MAX_UINT16, 0.0000),
    ],
)
def test_percent(mockHardware: MockHardware, value, expected):
    mockHardware.set_ADC_u16_value(k1, value)

    assert round(k1.percent(deadzone=0.0), 4) == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        (0, 1.0000),
        (MAX_UINT16 / 4, 0.7550),
        (MAX_UINT16 / 3, 0.6700),
        (MAX_UINT16 / 2, 0.5000),
        (MAX_UINT16, 0.0000),
    ],
)
def test_percent_w_deadzone(mockHardware: MockHardware, value, expected):
    mockHardware.set_ADC_u16_value(k1, value)

    assert round(k1.percent(deadzone=0.01), 4) == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        (0, 99),
        (MAX_UINT16 / 4, 74),
        (MAX_UINT16 / 3, 66),
        (MAX_UINT16 / 2, 49),
        (MAX_UINT16, 0),
    ],
)
def test_read_position(mockHardware: MockHardware, value, expected):
    mockHardware.set_ADC_u16_value(k1, value)

    assert k1.read_position(deadzone=0.0) == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        (0, 99),
        (MAX_UINT16 / 4, 75),
        (MAX_UINT16 / 3, 67),
        (MAX_UINT16 / 2, 49),
        (MAX_UINT16, 0),
    ],
)
def test_read_position_w_deadzone(mockHardware: MockHardware, value, expected):
    mockHardware.set_ADC_u16_value(k1, value)

    assert k1.read_position(deadzone=0.01) == expected


def test_knobs_are_independent(mockHardware: MockHardware):
    mockHardware.set_ADC_u16_value(k1, 0)
    mockHardware.set_ADC_u16_value(k2, MAX_UINT16)

    assert k1.percent(deadzone=0.01) == 1.0
    assert k2.percent(deadzone=0.01) == 0.0
