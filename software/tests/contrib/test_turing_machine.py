import pytest

try:
    from contrib.turing_machine import TuringMachine, MAX_OUTPUT_VOLTAGE, DEFAULT_BIT_COUNT
except ImportError:
    from turing_machine import TuringMachine, MAX_OUTPUT_VOLTAGE, DEFAULT_BIT_COUNT


@pytest.fixture
def turing_machine():
    tm = TuringMachine()
    tm.bits = 0b1100110011110000  # set the bits to a known value
    return tm


def tm(bit_count, starting_bits):
    tm = TuringMachine(bit_count)
    tm.bits = starting_bits  # set the bits to a known value
    return tm


def test_bad_bit_count():
    with pytest.raises(ValueError, match=r"4") as e:
        tm = TuringMachine(4)


@pytest.mark.parametrize(
    "bit_count,length,starting_bits,expected1,expected2",
    [
        (16, 16, 0b1100110011110000, "1001100111100001", "0011001111000011"),
        (16, 2, 0b1100110011110001, "1100110011110010", "1100110011110001"),
        (8, 8, 0b11110000, "11100001", "11000011"),
    ],
)
def test_rotate_bits(bit_count, length, starting_bits, expected1, expected2):
    turing_machine = tm(bit_count, starting_bits)
    turing_machine.length = length
    turing_machine.rotate_bits()
    assert turing_machine.get_bit_string() == expected1
    turing_machine.rotate_bits()
    assert turing_machine.get_bit_string() == expected2


@pytest.mark.parametrize(
    "bit_count,starting_bits,expected",
    [
        (16, 0b1100110011110000, "11110000"),
        (8, 0b11110000, "11110000"),
    ],
)
def test_get_8_bits(bit_count, starting_bits, expected):
    turing_machine = tm(bit_count, starting_bits)
    eight_bits = turing_machine.get_8_bits()
    assert f"{eight_bits:08b}" == expected


def test_get_voltage(turing_machine):
    turing_machine.bits = 0xFFFF  # MAX
    assert turing_machine.get_voltage() == 10

    turing_machine.bits = 0x0000  # MIN
    assert turing_machine.get_voltage() == 0

    turing_machine.bits = 0x007F  # MED
    assert turing_machine.get_voltage() >= 4.9
    assert turing_machine.get_voltage() <= 5

    turing_machine.bits = 0x0080  # MED
    assert turing_machine.get_voltage() >= 5
    assert turing_machine.get_voltage() <= 5.1


def test_locked_loop(turing_machine):
    for i in range(16 * 100):  # step until we're back where we started many times
        turing_machine.step()
    assert turing_machine.get_bit_string() == "1100110011110000"


def test_mobius_loop(turing_machine):
    turing_machine.flip_probability = 100
    for _ in range(100):
        for i in range(16):  # step halfway through
            turing_machine.step()
        assert turing_machine.get_bit_string() == "0011001100001111"  # inverted
        for i in range(16):  # step back to the beginning
            turing_machine.step()
        assert turing_machine.get_bit_string() == "1100110011110000"


def test_random_loop(turing_machine):
    turing_machine.flip_probability = 50
    for _ in range(100):
        turing_machine.step()
        assert turing_machine.get_bit_string() != "1100110011110000"
        # technically, we _could_ randomply end up back at our starting sequence, but probably not in 100 steps


def test_bad_flip_probability(turing_machine):
    with pytest.raises(ValueError, match=r"-1") as e:
        turing_machine.flip_probability = -1

    with pytest.raises(ValueError, match=r"101") as e:
        turing_machine.flip_probability = 101


def test_scale(turing_machine):
    turing_machine.flip_probability = 50
    turing_machine.scale = 5
    for _ in range(100):
        assert turing_machine.get_voltage() <= 5
        turing_machine.step()


def test_bad_scale(turing_machine):
    with pytest.raises(ValueError, match=r"-1") as e:
        turing_machine.scale = -1

    with pytest.raises(ValueError, match=r"" + str(MAX_OUTPUT_VOLTAGE + 1)) as e:
        turing_machine.scale = MAX_OUTPUT_VOLTAGE + 1


def test_length(turing_machine):
    turing_machine.bits = 0b1100110011110001

    turing_machine.length = 2
    for _ in range(10):
        assert turing_machine.get_voltage() == 9.450980392156863
        turing_machine.step()
        assert turing_machine.get_voltage() ==  9.490196078431373
        turing_machine.step()

    turing_machine.length = 4
    for _ in range(10):
        print(_)
        assert turing_machine.get_voltage() == 9.450980392156863
        turing_machine.step()
        assert turing_machine.get_voltage() ==  9.490196078431373
        turing_machine.step()
        assert turing_machine.get_voltage() == 9.568627450980392
        turing_machine.step()
        assert turing_machine.get_voltage() ==  9.72549019607843
        turing_machine.step()

def test_bad_length(turing_machine):
    with pytest.raises(ValueError, match=r"1") as e:
        turing_machine.length = 1

    with pytest.raises(ValueError, match=r"" + str(DEFAULT_BIT_COUNT + 1)) as e:
        turing_machine.length = DEFAULT_BIT_COUNT + 1
