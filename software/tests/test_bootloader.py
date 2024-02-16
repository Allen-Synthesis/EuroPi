import pytest

from bootloader import BootloaderMenu
from europi_script import EuroPiScript


class GoodTestScript1(EuroPiScript):
    pass


class GoodTestScript2(EuroPiScript):
    pass


class BadTestScript:
    pass


@pytest.mark.parametrize(
    "cls, expected",
    [
        (GoodTestScript1, True),
        (GoodTestScript2, True),
        (BadTestScript, False),
    ],
)
def test_is_europi_script(cls, expected):
    assert BootloaderMenu._is_europi_script(cls) == expected
