import pytest
from europi_script import EuroPiScript
from collections import namedtuple
from struct import pack, unpack


class ScriptForTesting(EuroPiScript):
    pass


@pytest.fixture
def script_for_testing():
    s = ScriptForTesting()
    yield s
    s.remove_state()


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
