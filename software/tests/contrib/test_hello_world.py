import pytest
from contrib.hello_world import HelloWorld


@pytest.fixture
def hw():
    hw = HelloWorld()
    yield hw
    hw.remove_state()


def test_increment(hw):
    assert hw.counter == 0
    hw.increment_counter()
    assert hw.counter == 1

def test_toggle_enablement(hw):
    assert hw.enabled == True
    hw.toggle_enablement()
    assert hw.enabled == False


def test_save_load_state_json(hw, monkeypatch):
    # Mock last_saved to return a deterministic time duration.
    monkeypatch.setattr(hw, "last_saved", lambda *args: 6000)

    # Verity initial state.
    assert hw.load_state_json() == {}
    assert hw.counter == 0
    assert hw.enabled == True
    assert hw._state_filename == "saved_state_HelloWorld.txt"

    # Modify state.
    hw.increment_counter()
    hw.toggle_enablement()

    # Verify state modified.
    assert hw.counter == 1
    assert hw.enabled == False

    # Test save and load state behaves as expected.
    hw.save_state()
    with open(hw._state_filename, 'r') as f:
        assert f.read() == '{"counter": 1, "enabled": false}'
    assert hw.load_state_json() == {"counter": 1, "enabled": False}
