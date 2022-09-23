import pytest
from firmware.config_points import ConfigPointsBuilder
from europi_script import EuroPiScript
from collections import namedtuple
from struct import pack, unpack


class ScriptForTesting(EuroPiScript):
    pass


class ScriptForTestingWithConfig(EuroPiScript):
    @classmethod
    def config_points(cls, config_builder: ConfigPointsBuilder):
        return config_builder.with_choice(name="a", choices=[5, 6], default=5).with_choice(
            name="b", choices=[7, 8], default=7
        )


@pytest.fixture
def script_for_testing():
    s = ScriptForTesting()
    yield s
    s.remove_state()


@pytest.fixture
def script_for_testing_with_config():
    s = ScriptForTestingWithConfig()
    yield s
    s.remove_state()
    s._delete_config()


def test_save_state(script_for_testing):
    script_for_testing._save_state("test state")
    assert script_for_testing._load_state() == "test state"


def test_state_file_name(script_for_testing):
    assert script_for_testing._state_filename == "saved_state_ScriptForTesting.txt"


def test_save_load_state_json(script_for_testing):
    state = {"one": 1, "two": ["a", "bb"], "three": True}
    script_for_testing.save_state_json(state)
    with open(script_for_testing._state_filename, "r") as f:
        assert f.read() == '{"one": 1, "two": ["a", "bb"], "three": true}'
    assert script_for_testing.load_state_json() == state


def test_save_load_state_bytes(script_for_testing):
    State = namedtuple("State", "one two three")
    format_string = "b2s?"  # https://docs.python.org/3/library/struct.html#format-characters
    state = pack(format_string, 1, bytes([8, 16]), True)
    script_for_testing.save_state_bytes(state)
    with open(script_for_testing._state_filename, "rb") as f:
        assert f.read() == b"\x01\x08\x10\x01"
    got_bytes = script_for_testing.load_state_bytes()
    assert got_bytes == state
    got_struct = State(*unpack(format_string, got_bytes))
    assert got_struct.one == 1
    assert list(got_struct.two) == [8, 16]
    assert got_struct.three == True


def test_config_file_name(script_for_testing):
    assert script_for_testing._config_filename() == "config/config_ScriptForTesting.json"


def test_load_config_no_config(script_for_testing):
    assert script_for_testing._load_config() == {}


def test_load_config_defaults(script_for_testing_with_config):
    assert script_for_testing_with_config._load_config() == {"a": 5, "b": 7}


def test_save_and_load_saved_config(script_for_testing_with_config):
    script_for_testing_with_config._save_config({"a": 6, "b": 8})

    with open(script_for_testing_with_config._config_filename(), "r") as f:
        assert f.read() == '{"a": 6, "b": 8}'

    assert script_for_testing_with_config._load_config() == {"a": 6, "b": 8}


def test_load_config_with_fallback_to_defaults(script_for_testing_with_config):
    script_for_testing_with_config._save_config({"a": 6})

    with open(script_for_testing_with_config._config_filename(), "r") as f:
        assert f.read() == '{"a": 6}'

    assert script_for_testing_with_config._load_config() == {"a": 6, "b": 7}
