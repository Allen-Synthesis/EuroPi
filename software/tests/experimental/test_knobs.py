import pytest
from experimental.knobs import MultiModeKnob, LockableKnob
from europi import k1, MAX_UINT16
from machine import ADC

from mock_hardware import MockHardware


@pytest.fixture
def multimode_knob(mockHardware: MockHardware):
    k = MultiModeKnob(k1, 3)

    # start the knob in the middle
    mockHardware.set_ADC_u16_value(k, MAX_UINT16 / 2)

    return k


@pytest.fixture
def locked_knob(mockHardware: MockHardware):
    k = LockableKnob(k1)

    # start the knob in the middle
    mockHardware.set_ADC_u16_value(k, MAX_UINT16 / 2)

    return k


# locked knob tests


def test_starting_state(locked_knob: LockableKnob):
    assert locked_knob.state == LockableKnob.STATE_UNLOCKED
    assert LockableKnob(k1).state == LockableKnob.STATE_UNLOCKED
    assert LockableKnob(k1, initial_value=1).state == LockableKnob.STATE_LOCKED


def test_unlocked_knob_changes_value(mockHardware: MockHardware, locked_knob: LockableKnob):
    assert locked_knob.state == LockableKnob.STATE_UNLOCKED
    assert round(locked_knob.percent(), 2) == 0.50

    mockHardware.set_ADC_u16_value(locked_knob, MAX_UINT16 / 3)
    assert round(locked_knob.percent(), 2) == 0.67


def test_locked_knob_stays_constant(mockHardware: MockHardware, locked_knob: LockableKnob):
    assert round(locked_knob.percent(), 2) == 0.50

    locked_knob.lock()
    assert locked_knob.state == LockableKnob.STATE_LOCKED

    mockHardware.set_ADC_u16_value(locked_knob, MAX_UINT16 / 3)
    assert round(locked_knob.percent(), 2) == 0.50

def test_request_unlock_outside_threshold(mockHardware: MockHardware, locked_knob: LockableKnob):
    assert round(locked_knob.percent(), 2) == 0.50
    
    locked_knob.lock()
    mockHardware.set_ADC_u16_value(locked_knob, 0)
    locked_knob.request_unlock()
    
    assert round(locked_knob.percent(), 2) == 0.50

def test_request_unlock_within_threshold(mockHardware: MockHardware, locked_knob: LockableKnob):
    assert round(locked_knob.percent(), 2) == 0.50
    
    locked_knob.lock()
    mockHardware.set_ADC_u16_value(locked_knob, 0)
    locked_knob.request_unlock()

    assert round(locked_knob.percent(), 2) == 0.50
    assert locked_knob.state == LockableKnob.STATE_UNLOCK_REQUESTED
    
    mockHardware.set_ADC_u16_value(locked_knob, (MAX_UINT16 / 2) + 10)
    assert round(locked_knob.percent(), 2) == 0.50
    assert locked_knob.state == LockableKnob.STATE_UNLOCKED

def test_state_changes(locked_knob: LockableKnob):
    # Unlocked
    assert locked_knob.state == LockableKnob.STATE_UNLOCKED

    locked_knob.request_unlock()
    assert locked_knob.state == LockableKnob.STATE_UNLOCKED

    locked_knob.lock()
    assert locked_knob.state == LockableKnob.STATE_LOCKED
    
    # locked
    locked_knob.lock()
    assert locked_knob.state == LockableKnob.STATE_LOCKED

    locked_knob.request_unlock()
    assert locked_knob.state == LockableKnob.STATE_UNLOCK_REQUESTED

    # Unlock requested
    
    locked_knob.request_unlock()
    assert locked_knob.state == LockableKnob.STATE_UNLOCK_REQUESTED

    locked_knob.lock()
    assert locked_knob.state == LockableKnob.STATE_LOCKED


# MultiModeKnob tests


def test_next_mode(multimode_knob: MultiModeKnob):
    assert multimode_knob.current_mode == 1
    assert multimode_knob.next_mode() == 2
    assert multimode_knob.current_mode == 2
    assert multimode_knob.next_mode() == 0
    assert multimode_knob.current_mode == 0
    assert multimode_knob.next_mode() == 1


def test_percent_by_mode(mockHardware: MockHardware, multimode_knob: MultiModeKnob):
    # knob starts in the middle, mode 1
    assert round(multimode_knob.percent(mode=0), 2) == 0
    assert round(multimode_knob.percent(mode=1), 2) == 0.50
    assert round(multimode_knob.percent(mode=2), 2) == 0

    # change to mode 2, then move the knob
    multimode_knob.next_mode()
    mockHardware.set_ADC_u16_value(multimode_knob, MAX_UINT16 / 3)

    assert round(multimode_knob.percent(mode=0), 2) == 0
    assert round(multimode_knob.percent(mode=1), 2) == 0.50
    assert round(multimode_knob.percent(mode=2), 2) == 0.67

    # change to mode 0, then move the knob
    multimode_knob.next_mode()
    mockHardware.set_ADC_u16_value(multimode_knob, MAX_UINT16 / 4)

    assert round(multimode_knob.percent(mode=0), 2) == 0
    assert round(multimode_knob.percent(mode=1), 2) == 0.50
    assert round(multimode_knob.percent(mode=2), 2) == 0.67

    # change to mode 1, then move the knob
    multimode_knob.next_mode()
    mockHardware.set_ADC_u16_value(multimode_knob, MAX_UINT16 / 5)

    assert round(multimode_knob.percent(mode=0), 2) == 0
    assert round(multimode_knob.percent(mode=1), 2) == 0.80
    assert round(multimode_knob.percent(mode=2), 2) == 0.67


def test_choice_by_mode(mockHardware: MockHardware, multimode_knob: MultiModeKnob):
    # knob starts in the middle, mode 1
    assert multimode_knob.choice([1, 2, 3], mode=0) == 1
    assert multimode_knob.choice([1, 2, 3], mode=1) == 2
    assert multimode_knob.choice([1, 2, 3], mode=2) == 1

    # change to mode 2, then move the knob
    multimode_knob.next_mode()
    mockHardware.set_ADC_u16_value(multimode_knob, MAX_UINT16 / 4)

    assert multimode_knob.choice([1, 2, 3], mode=0) == 1
    assert multimode_knob.choice([1, 2, 3], mode=1) == 2
    assert multimode_knob.choice([1, 2, 3], mode=2) == 3

    # change to mode 0, then move the knob
    multimode_knob.next_mode()
    mockHardware.set_ADC_u16_value(multimode_knob, MAX_UINT16 / 4 * 2)

    assert multimode_knob.choice([1, 2, 3], mode=0) == 1
    assert multimode_knob.choice([1, 2, 3], mode=1) == 2
    assert multimode_knob.choice([1, 2, 3], mode=2) == 3

    # change to mode 1, then move the knob
    multimode_knob.next_mode()
    mockHardware.set_ADC_u16_value(multimode_knob, MAX_UINT16 / 4 * 3)

    assert multimode_knob.choice([1, 2, 3], mode=0) == 1
    assert multimode_knob.choice([1, 2, 3], mode=1) == 1
    assert multimode_knob.choice([1, 2, 3], mode=2) == 3


def test_read_position_by_mode(mockHardware: MockHardware, multimode_knob: MultiModeKnob):
    pass  # TODO
