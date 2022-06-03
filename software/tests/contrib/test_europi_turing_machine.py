import pytest

from contrib.turing_machine import EuroPiTuringMachine, ain, k1
from mock_hardware import MockHardware


@pytest.fixture
def turing_machine():
    tm = EuroPiTuringMachine()
    tm.bits = 0b1100110011110000  # set the bits to a known value
    return tm


@pytest.mark.parametrize(
    "k1_percent, ain_percent, expected_probability",
    [
        # k1 locked ain varies
        (1.0, 0.0, 0),
        (1.0, 0.01, 0),
        (1.0, 0.1, 0),
        (1.0, 0.5, 0),
        (1.0, 0.9, 0),
        (1.0, 0.99, 0),
        (1.0, 1.0, 0),
        # k1 at midpoint ain varies
        (0.5, 0.0, 50),
        (0.5, 0.004, 50),
        (0.5, 0.01, 49),
        (0.5, 0.1, 40),
        (0.5, 0.5, 0),
        (0.5, 0.8, 0),
        (0.5, 0.9, 0),
        (0.5, 0.99, 0),
        (0.5, 1.0, 0),
        # k1 looped ain varies
        (0.0, 0.0, 100),
        (0.0, 0.004, 100),
        (0.0, 0.01, 99),
        (0.0, 0.1, 90),
        (0.0, 0.5, 50),
        (0.0, 0.9, 10),
        (0.0, 0.99, 1),
        (0.0, 0.999, 0),
        (0.0, 1.0, 0),
    ],
)
def test_flip_probability(
    mockHardware: MockHardware,
    turing_machine: EuroPiTuringMachine,
    k1_percent,
    ain_percent,
    expected_probability,
):
    mockHardware.set_analogue_input_percent(ain, ain_percent)
    mockHardware.set_knob_percent(k1, k1_percent)
    assert turing_machine.flip_probability() == expected_probability
