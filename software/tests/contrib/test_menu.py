import pytest

from menu import BootloaderMenu


@pytest.mark.parametrize(
    "filestat, expected",
    [
        (("script.py", 32768), True),
        (("script.py", 16384), False),
        (("script", 32768), False),
        (("script", 16384), False),
    ],
)
def test_is_script(filestat, expected):
    assert BootloaderMenu._is_script(filestat) == expected


def test_build_scripts_config():
    scripts = ["diagnostic.py", "coin_toss.py"]

    config = BootloaderMenu._build_scripts_config(scripts)

    assert len(config) == 3
    assert list(config.keys()) == ["coin toss", "diagnostic", "calibrate"]

    assert config["coin toss"] == "contrib.coin_toss"
    assert config["diagnostic"] == "contrib.diagnostic"
    assert config["calibrate"] == "calibrate"
