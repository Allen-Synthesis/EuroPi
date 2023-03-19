import pytest
from firmware import configuration as config
from europi_script import EuroPiScript
from configuration import ConfigFile
from collections import namedtuple
from struct import pack, unpack


class ScriptForTesting(EuroPiScript):
    pass


class ScriptForTestingWithConfig(EuroPiScript):
    @classmethod
    def config_points(cls):
        return [
            config.choice(name="a", choices=[5, 6], default=5),
            config.choice(name="b", choices=[7, 8], default=7),
        ]


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
    ConfigFile.delete_config(s.__class__)


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


def test_load_config_no_config(script_for_testing):
    assert EuroPiScript._load_config_for_class(script_for_testing.__class__) == {}


def test_load_config_defaults(script_for_testing_with_config):
    assert EuroPiScript._load_config_for_class(script_for_testing_with_config.__class__) == {
        "a": 5,
        "b": 7,
    }


def test_load_europi_config(script_for_testing_with_config):
    assert script_for_testing_with_config.europi_config["pico_model"] == "pico"
