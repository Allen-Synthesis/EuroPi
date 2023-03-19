import pytest

from contrib.turing_machine import TuringMachine, MAX_OUTPUT_VOLTAGE, DEFAULT_BIT_COUNT


def tm(bit_count, starting_bits):
    tm = TuringMachine(bit_count)
    tm.bits = starting_bits  # set the bits to a known value
    return tm


@pytest.fixture
def turing_machine():
    return tm(16, 0b1100110011110000)  # set the bits to a known value


def get_bit_string(tm):
    return f"{tm.bits:0{tm.bit_count}b}"


def test_bad_bit_count():
    with pytest.raises(ValueError, match=r"4") as e:
        tm = TuringMachine(4)


@pytest.mark.parametrize(
    "bit_count,length,starting_bits,expected1,expected2",
    [
        (16, 16, 0b1100110010101010, "1001100101010101", "0011001010101011"),
        (16, 5, 0b1100110010101010, "1001100101010100", "0011001010101001"),
        (16, 4, 0b1100110010101010, "1001100101010101", "0011001010101010"),
        (16, 3, 0b1100110010101010, "1001100101010100", "0011001010101001"),
        (16, 2, 0b1100110010101010, "1001100101010101", "0011001010101010"),
        (8, 8, 0b11110110, "11101101", "11011011"),
        (8, 5, 0b11110110, "11101101", "11011010"),
        (8, 4, 0b11110110, "11101100", "11011001"),
        (8, 3, 0b11110110, "11101101", "11011011"),
        (8, 2, 0b11110110, "11101101", "11011010"),
    ],
)
def test_rotate_bits(bit_count, length, starting_bits, expected1, expected2):
    turing_machine = tm(bit_count, starting_bits)
    turing_machine.length = length
    turing_machine._rotate_bits()
    assert get_bit_string(turing_machine) == expected1
    turing_machine._rotate_bits()
    assert get_bit_string(turing_machine) == expected2


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


@pytest.mark.parametrize(
    "bit_count,starting_bits,index,expected",
    [
        (16, 0b1100110011110000, 0, 0),
        (16, 0b1100110011110000, 1, 0),
        (16, 0b1100110011110000, 2, 0),
        (16, 0b1100110011110000, 4, 1),
        (16, 0b1100110011110000, 7, 1),
        (16, 0b1100110011110000, 8, 0),
        (16, 0b1100110011110000, 10, 1),
        (16, 0b1100110011110000, 15, 1),
    ],
)
def test_get_bit(bit_count, starting_bits, index, expected):
    turing_machine = tm(bit_count, starting_bits)
    bit = turing_machine.get_bit(index)
    assert bit == expected


def test_get_bit_and(turing_machine):
    # 0b1100110011110000
    assert turing_machine.get_bit_and(0, 1) == 0
    assert turing_machine.get_bit_and(0, 5) == 0
    assert turing_machine.get_bit_and(5, 6) == 1
    assert turing_machine.get_bit_and(5, 6) == 1
    assert turing_machine.get_bit_and(0, 5, 6) == 0
    assert turing_machine.get_bit_and(5, 6, 7) == 1


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
    assert get_bit_string(turing_machine) == "1100110011110000"


def test_mobius_loop(turing_machine):
    turing_machine.flip_probability = 100
    for _ in range(100):
        for i in range(16):  # step halfway through
            turing_machine.step()
        assert get_bit_string(turing_machine) == "0011001100001111"  # inverted
        for i in range(16):  # step back to the beginning
            turing_machine.step()
        assert get_bit_string(turing_machine) == "1100110011110000"


def test_random_loop(turing_machine):
    turing_machine.flip_probability = 50
    for _ in range(100):
        turing_machine.step()
        assert get_bit_string(turing_machine) != "1100110011110000"
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


def test_length_2(turing_machine):
    turing_machine.bits = 0b1100110011110001

    turing_machine.length = 2
    for _ in range(6):
        # it takes 6 steps for us to settle into a repeating pattern
        turing_machine.step()

    for _ in range(10):
        assert turing_machine.get_voltage() == 3.333333333333333
        turing_machine.step()
        assert turing_machine.get_voltage() == 6.666666666666666
        turing_machine.step()


def test_length_4(turing_machine):
    turing_machine.bits = 0b1100110011110001

    turing_machine.length = 4
    for _ in range(3):
        # it takes 3 steps for us to settle into a repeating pattern
        turing_machine.step()

    for _ in range(10):
        print(_)
        assert turing_machine.get_voltage() == 5.333333333333333
        turing_machine.step()
        assert turing_machine.get_voltage() == 0.6666666666666666
        turing_machine.step()
        assert turing_machine.get_voltage() == 1.3333333333333333
        turing_machine.step()
        assert turing_machine.get_voltage() == 2.6666666666666665
        turing_machine.step()


def test_bad_length(turing_machine):
    with pytest.raises(ValueError, match=r"1") as e:
        turing_machine.length = 1

    with pytest.raises(ValueError, match=r"" + str(DEFAULT_BIT_COUNT + 1)) as e:
        turing_machine.length = DEFAULT_BIT_COUNT + 1


def test_write_0(turing_machine):
    turing_machine.write = True
    for _ in range(16):
        turing_machine.step()
    assert get_bit_string(turing_machine) == "0000000000000000"


def test_write_1(turing_machine):
    turing_machine.clear_on_write = False
    turing_machine.write = True
    for _ in range(16):
        turing_machine.step()
    assert get_bit_string(turing_machine) == "1111111111111111"
