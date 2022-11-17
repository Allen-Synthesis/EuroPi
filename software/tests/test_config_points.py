import pytest

from firmware.config_points import ConfigPointsBuilder


def test_builder_empty():

    config_points = ConfigPointsBuilder().build()

    assert len(config_points) == 0
    assert config_points.default_config() == {}


def test_duplicate_config_point_raises():
    with pytest.raises(ValueError):
        (
            ConfigPointsBuilder()
            .with_choice(name="a", choices=[1, 2, 3], default=2)
            .with_choice(name="a", choices=[1, 2, 3], default=2)
        )


def test_builder_choice():

    config_points = (
        ConfigPointsBuilder()
        .with_choice(name="a", choices=[1, 2, 3], default=2)
        .with_choice(name="b", choices=[4, 5, 6], default=6)
        .build()
    )

    assert len(config_points) == 2
    assert config_points.default_config() == {"a": 2, "b": 6}
    assert config_points.points["a"]["type"] == "choice"
    assert config_points.points["b"]["type"] == "choice"
    assert config_points.points["a"]["choices"] == [1, 2, 3]
    assert config_points.points["b"]["choices"] == [4, 5, 6]


def test_builder_int():

    config_points = (
        ConfigPointsBuilder()
        .with_int(name="a", stop=5, default=2)
        .with_int(name="b", start=-5, stop=6, default=0)
        .with_int(name="c", start=-5, stop=6, step=2, default=1)
        .build()
    )

    assert len(config_points) == 3
    assert config_points.default_config() == {"a": 2, "b": 0, "c": 1}
    assert config_points.points["a"]["type"] == "choice"
    assert config_points.points["b"]["type"] == "choice"
    assert config_points.points["c"]["type"] == "choice"
    assert config_points.points["a"]["choices"] == [0, 1, 2, 3, 4]
    assert config_points.points["b"]["choices"] == [-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5]
    assert config_points.points["c"]["choices"] == [-5, -3, -1, 1, 3, 5]
