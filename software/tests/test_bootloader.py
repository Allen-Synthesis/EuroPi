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


def test_build_scripts_config():
    scripts = [GoodTestScript1, GoodTestScript2, BadTestScript]

    config = BootloaderMenu._build_scripts_config(scripts)

    assert len(config) == 2
    assert list(config.keys()) == ["GoodTestScript1", "GoodTestScript2"]

    assert config["GoodTestScript1"] == GoodTestScript1
    assert config["GoodTestScript2"] == GoodTestScript2
