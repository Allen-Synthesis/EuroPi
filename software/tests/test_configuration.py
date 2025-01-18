import pytest

import re

from firmware import configuration as config
from firmware.configuration import ConfigSpec, ConfigFile, Validation


class AClassWithConfig:
    pass


@pytest.fixture
def class_with_config():
    yield AClassWithConfig
    ConfigFile.delete_config(AClassWithConfig)


@pytest.fixture
def simple_config_spec():
    return ConfigSpec(
        [
            config.choice(name="a", choices=[1, 2, 3], default=2),
            config.integer(name="b", minimum=0, maximum=4, default=3),
        ]
    )


def test_builder_empty():
    config_spec = ConfigSpec([])

    assert len(config_spec) == 0
    assert config_spec.default_config() == {}


def test_duplicate_config_point_raises():
    with pytest.raises(ValueError):
        ConfigSpec(
            [
                config.choice(name="a", choices=[1, 2, 3], default=2),
                config.choice(name="a", choices=[1, 2, 3], default=2),
            ]
        )


def test_validate_with_valid_configuration(simple_config_spec: ConfigSpec):
    c = simple_config_spec.default_config()

    validation = simple_config_spec.validate(c)

    assert validation.is_valid


def test_validate_with_empty_configuration(simple_config_spec: ConfigSpec):
    c = {}

    validation = simple_config_spec.validate(c)

    assert validation.is_valid


def test_validate_with_invalid_configuration(simple_config_spec: ConfigSpec):
    c = {"a": 4}

    validation = simple_config_spec.validate(c)

    assert not validation.is_valid


def test_helper_choice():
    config_points = ConfigSpec(
        [
            config.choice(name="a", choices=[1, 2, 3], default=2),
            config.choice(name="b", choices=[4, 5, 6], default=6),
        ]
    )

    assert len(config_points) == 2
    assert config_points.default_config() == {"a": 2, "b": 6}
    assert config_points.points["a"].type == "choice"
    assert config_points.points["b"].type == "choice"
    assert config_points.points["a"].choices == [1, 2, 3]
    assert config_points.points["b"].choices == [4, 5, 6]


def test_helper_int():
    config_points = ConfigSpec(
        [
            config.integer(name="a", minimum=0, maximum=4, default=2),
            config.integer(name="b", minimum=-5, maximum=5, default=0),
        ]
    )

    assert len(config_points) == 2
    assert config_points.default_config() == {"a": 2, "b": 0}
    assert config_points.points["a"].type == int
    assert config_points.points["b"].type == int
    assert config_points.points["a"].minimum == 0
    assert config_points.points["a"].maximum == 4
    assert config_points.points["b"].minimum == -5
    assert config_points.points["b"].maximum == 5


# ConfigFile


def test_config_file_name(class_with_config):
    assert ConfigFile.config_filename(class_with_config) == "config/AClassWithConfig.json"


def test_load_config_no_config(class_with_config):
    assert ConfigFile.load_config(class_with_config, ConfigSpec([])) == {}


def test_load_config_defaults(class_with_config, simple_config_spec):
    assert ConfigFile.load_config(class_with_config, simple_config_spec) == {
        "a": 2,
        "b": 3,
    }


def test_save_and_load_saved_config(class_with_config, simple_config_spec):
    ConfigFile.save_config(class_with_config, {"a": 1, "b": 2})

    with open(ConfigFile.config_filename(class_with_config), "r") as f:
        # allow arbitrary whitespace in the JSON formatting
        assert re.match(r'\{\s*"a"\s*:\s*1\s*,\s*"b"\s*:\s*2\s*\}', f.read())

    assert ConfigFile.load_config(class_with_config, simple_config_spec) == {
        "a": 1,
        "b": 2,
    }


def test_load_config_with_fallback_to_defaults(class_with_config, simple_config_spec):
    ConfigFile.save_config(class_with_config, {"a": 1})

    with open(ConfigFile.config_filename(class_with_config), "r") as f:
        # allow arbitrary whitespace in the JSON formatting
        assert re.match(r'\{\s*"a"\s*:\s*1\s*\}', f.read())

    assert ConfigFile.load_config(class_with_config, simple_config_spec) == {
        "a": 1,
        "b": 3,
    }


def test_load_config_with_unspecd_config_points(class_with_config, simple_config_spec):
    ConfigFile.save_config(class_with_config, {"a": 1, "c": 8})

    with pytest.raises(ValueError):
        ConfigFile.load_config(class_with_config, simple_config_spec) == {
            "a": 6,
            "b": 7,
        }
