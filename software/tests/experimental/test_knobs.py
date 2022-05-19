import pytest
from experimental.knobs import LockableKnob, KnobBank
from europi import k1, MAX_UINT16
from machine import ADC

from mock_hardware import MockHardware


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


def test_access_percent():
    assert False


def test_access_choice():
    assert False


def test_access_range():
    assert False


def test_access_read_position():
    assert False


# Disabled Knob Tests


# KnobBank tests


@pytest.fixture
def knob_bank(mockHardware: MockHardware):
    kb = KnobBank(k1, [("param1", None), ("param2", MAX_UINT16)])

    # start the knob in the middle
    mockHardware.set_ADC_u16_value(k1, MAX_UINT16 / 2)

    return kb


def test_next_mode(knob_bank: KnobBank):
    assert knob_bank.index == 1
    knob_bank.next()
    assert knob_bank.index == 2
    knob_bank.next()
    assert knob_bank.index == 0
    knob_bank.next()
    assert knob_bank.index == 1


def test_access_by_index(mockHardware: MockHardware, knob_bank: KnobBank):
    # knob starts in the middle, knob 1
    assert round(knob_bank.knobs[0].percent(), 2) == 0
    assert round(knob_bank.knobs[1].percent(), 2) == 0.50
    assert round(knob_bank.knobs[2].percent(), 2) == 0
    assert round(knob_bank.current.percent(), 2) == 0.50

    # change to knob 2, then move the knob
    knob_bank.next()
    mockHardware.set_ADC_u16_value(knob_bank.current, MAX_UINT16 / 3)

    assert round(knob_bank.knobs[0].percent(), 2) == 0
    assert round(knob_bank.knobs[1].percent(), 2) == 0.50
    assert round(knob_bank.knobs[2].percent(), 2) == 0
    assert round(knob_bank.current.percent(), 2) == 0

    mockHardware.set_ADC_u16_value(knob_bank.current, MAX_UINT16)

    assert round(knob_bank.knobs[0].percent(), 2) == 0
    assert round(knob_bank.knobs[1].percent(), 2) == 0.50
    assert round(knob_bank.knobs[2].percent(), 2) == 0
    assert round(knob_bank.current.percent(), 2) == 0

    mockHardware.set_ADC_u16_value(knob_bank.current, MAX_UINT16 / 3)

    assert round(knob_bank.knobs[0].percent(), 2) == 0
    assert round(knob_bank.knobs[1].percent(), 2) == 0.50
    assert round(knob_bank.knobs[2].percent(), 2) == 0.67
    assert round(knob_bank.current.percent(), 2) == 0.67

    # change to knob 0 (disabled), then move the knob
    knob_bank.next()

    mockHardware.set_ADC_u16_value(knob_bank.current, MAX_UINT16)

    assert round(knob_bank.knobs[0].percent(), 2) == 0
    assert round(knob_bank.knobs[1].percent(), 2) == 0.50
    assert round(knob_bank.knobs[2].percent(), 2) == 0.67
    assert round(knob_bank.current.percent(), 2) == 0

    mockHardware.set_ADC_u16_value(knob_bank.current, MAX_UINT16 / 4)

    assert round(knob_bank.knobs[0].percent(), 2) == 0
    assert round(knob_bank.knobs[1].percent(), 2) == 0.50
    assert round(knob_bank.knobs[2].percent(), 2) == 0.67
    assert round(knob_bank.current.percent(), 2) == 0

    # change to knob 1, then move the knob
    knob_bank.next()
    mockHardware.set_ADC_u16_value(knob_bank.current, MAX_UINT16 / 5)

    assert round(knob_bank.knobs[0].percent(), 2) == 0
    assert round(knob_bank.knobs[1].percent(), 2) == 0.50
    assert round(knob_bank.knobs[2].percent(), 2) == 0.67
    assert round(knob_bank.current.percent(), 2) == 0.50

    mockHardware.set_ADC_u16_value(knob_bank.current, MAX_UINT16 / 2)

    assert round(knob_bank.knobs[0].percent(), 2) == 0
    assert round(knob_bank.knobs[1].percent(), 2) == 0.50
    assert round(knob_bank.knobs[2].percent(), 2) == 0.67
    assert round(knob_bank.current.percent(), 2) == 0.50

    mockHardware.set_ADC_u16_value(knob_bank.current, MAX_UINT16 / 5)

    assert round(knob_bank.knobs[0].percent(), 2) == 0
    assert round(knob_bank.knobs[1].percent(), 2) == 0.80
    assert round(knob_bank.knobs[2].percent(), 2) == 0.67
    assert round(knob_bank.current.percent(), 2) == 0.80


def test_access_by_name(mockHardware: MockHardware, knob_bank: KnobBank):
    # knob starts in the middle, knob 1
    assert round(knob_bank.param1.percent(), 2) == 0.50
    assert round(knob_bank.param2.percent(), 2) == 0
    assert round(knob_bank.current.percent(), 2) == 0.50

    # change to knob 2, then move the knob
    knob_bank.next()
    mockHardware.set_ADC_u16_value(knob_bank.current, MAX_UINT16 / 3)

    assert round(knob_bank.param1.percent(), 2) == 0.50
    assert round(knob_bank.param2.percent(), 2) == 0
    assert round(knob_bank.current.percent(), 2) == 0

    mockHardware.set_ADC_u16_value(knob_bank.current, MAX_UINT16)

    assert round(knob_bank.param1.percent(), 2) == 0.50
    assert round(knob_bank.param2.percent(), 2) == 0
    assert round(knob_bank.current.percent(), 2) == 0

    mockHardware.set_ADC_u16_value(knob_bank.current, MAX_UINT16 / 3)

    assert round(knob_bank.param1.percent(), 2) == 0.50
    assert round(knob_bank.param2.percent(), 2) == 0.67
    assert round(knob_bank.current.percent(), 2) == 0.67
