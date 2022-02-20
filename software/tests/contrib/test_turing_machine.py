import pytest
from turing_machine import TuringMachine


@pytest.fixture
def turing_machine():
    tm = TuringMachine()
    tm.bits = 0b1100110011110000  # set the bits to a known value
    return tm


def test_rotate_bits(turing_machine):
    turing_machine.rotate_bits()
    assert turing_machine.get_bit_string() == "1001100111100001"
    turing_machine.rotate_bits()
    assert turing_machine.get_bit_string() == "0011001111000011"


def test_get_8_bits(turing_machine):
    eight_bits = turing_machine.get_8_bits()
    assert f"{eight_bits:08b}" == "11110000"

def test_get_voltage(turing_machine):
    turing_machine.bits = 0xFFFF # MAX
    assert turing_machine.get_voltage() == 10

    turing_machine.bits = 0x0000 # MIN
    assert turing_machine.get_voltage() == 0
    
    turing_machine.bits = 0x007F # MED
    assert turing_machine.get_voltage() >= 4.9
    assert turing_machine.get_voltage() <= 5

    turing_machine.bits = 0x0080 # MED
    assert turing_machine.get_voltage() >= 5
    assert turing_machine.get_voltage() <= 5.1