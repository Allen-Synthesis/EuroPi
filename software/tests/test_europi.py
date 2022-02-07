import pytest

from europi import clamp


@pytest.mark.parametrize(
    "value, low, high, expected",
    [
        (0, 1, 10, 1),
        (1, 1, 10, 1),
        (5, 1, 10, 5),
        (10, 1, 10, 10),
        (11, 1, 10, 10),
    ],
)
def test_clamp(value, low, high, expected):
    assert clamp(value, low, high) == expected
