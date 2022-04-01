import pytest

from turing_machine import EuroPiTuringMachine, MAX_OUTPUT_VOLTAGE, DEFAULT_BIT_COUNT
from europi import ain, k1


@pytest.fixture
def turing_machine():
    tm = EuroPiTuringMachine()
    tm.bits = 0b1100110011110000  # set the bits to a known value
    return tm


@pytest.mark.parametrize(
    "k1_value, ain_value, expected",
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
def test_flip_probability(monkeypatch, turing_machine: EuroPiTuringMachine, k1_value, ain_value, expected):
    monkeypatch.setattr(ain, "percent", lambda: ain_value)
    monkeypatch.setattr(k1, "percent", lambda: k1_value)
    assert turing_machine.flip_probability() == expected
