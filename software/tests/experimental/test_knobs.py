import pytest
from experimental.knobs import LockableKnob, KnobBank, DEFAULT_THRESHOLD
from europi import k1, MAX_UINT16
from machine import ADC

from mock_hardware import MockHardware

# locked knob tests


@pytest.fixture
def lockable_knob(mockHardware: MockHardware):
    k = LockableKnob(k1)

    # start the knob in the middle
    mockHardware.set_ADC_u16_value(k, MAX_UINT16 / 2)

    return k


def test_starting_state(lockable_knob: LockableKnob):
    assert lockable_knob.state == LockableKnob.STATE_UNLOCKED
    assert LockableKnob(k1).state == LockableKnob.STATE_UNLOCKED
    assert LockableKnob(k1, initial_uint16_value=0).state == LockableKnob.STATE_LOCKED


@pytest.mark.parametrize(
    "initial_uint16_value, expected_percent",
    [
        (MAX_UINT16 / 1, 0.00),
        (MAX_UINT16 / 3 * 2, 0.33),
        (MAX_UINT16 / 2, 0.50),
        (MAX_UINT16 / 3, 0.67),
        (MAX_UINT16 / 4, 0.75),
        (MAX_UINT16 * 0, 1.00),
    ],
)
def test_initial_uint16_value(initial_uint16_value, expected_percent):
    lockable_knob = LockableKnob(k1, initial_uint16_value=initial_uint16_value)
    assert lockable_knob.state == LockableKnob.STATE_LOCKED
    assert round(lockable_knob.percent(deadzone=0), 2) == expected_percent


@pytest.mark.parametrize(
    "initial_percentage_value, expected_percent, expected_percent_default_deadzone",
    [
        (0.0, 0.00, 0.00),
        (0.33, 0.33, 0.33),
        (0.50, 0.50, 0.50),
        (0.67, 0.67, 0.67),
        (0.75, 0.75, 0.76),
        (1.00, 1.00, 1.00),
    ],
)
def test_initial_percentage_value(
    initial_percentage_value, expected_percent, expected_percent_default_deadzone
):
    lockable_knob = LockableKnob(k1, initial_percentage_value=initial_percentage_value)
    assert lockable_knob.state == LockableKnob.STATE_LOCKED
    assert round(lockable_knob.percent(deadzone=0.01), 2) == expected_percent_default_deadzone
    assert round(lockable_knob.percent(deadzone=0.0), 2) == expected_percent


def test_initial_uint16_value_overrides_percentage():
    lockable_knob = LockableKnob(k1, initial_uint16_value=MAX_UINT16, initial_percentage_value=1)
    assert lockable_knob.state == LockableKnob.STATE_LOCKED
    assert round(lockable_knob.percent(deadzone=0.01), 2) == 0
    assert round(lockable_knob.percent(deadzone=0.0), 2) == 0


def test_unlocked_knob_changes_value(mockHardware: MockHardware, lockable_knob: LockableKnob):
    assert lockable_knob.state == LockableKnob.STATE_UNLOCKED
    assert round(lockable_knob.percent(deadzone=0.01), 2) == 0.50
    assert round(lockable_knob.percent(deadzone=0.0), 2) == 0.50

    mockHardware.set_ADC_u16_value(lockable_knob, MAX_UINT16 / 3)
    assert round(lockable_knob.percent(deadzone=0.01), 2) == 0.67
    assert round(lockable_knob.percent(deadzone=0.0), 2) == 0.67


def test_locked_knob_stays_constant(mockHardware: MockHardware, lockable_knob: LockableKnob):
    assert round(lockable_knob.percent(deadzone=0.01), 2) == 0.50
    assert round(lockable_knob.percent(deadzone=0.0), 2) == 0.50

    lockable_knob.lock()
    assert lockable_knob.state == LockableKnob.STATE_LOCKED

    mockHardware.set_ADC_u16_value(lockable_knob, MAX_UINT16 / 3)
    assert round(lockable_knob.percent(deadzone=0.01), 2) == 0.50
    assert round(lockable_knob.percent(deadzone=0.0), 2) == 0.50


def test_request_unlock_outside_threshold(mockHardware: MockHardware, lockable_knob: LockableKnob):
    assert round(lockable_knob.percent(deadzone=0.01), 2) == 0.50
    assert round(lockable_knob.percent(deadzone=0.0), 2) == 0.50

    lockable_knob.lock()
    mockHardware.set_ADC_u16_value(lockable_knob, 0)
    lockable_knob.request_unlock()

    assert round(lockable_knob.percent(deadzone=0.01), 2) == 0.50
    assert round(lockable_knob.percent(deadzone=0.0), 2) == 0.50


def test_request_unlock_within_threshold(mockHardware: MockHardware, lockable_knob: LockableKnob):
    assert round(lockable_knob.percent(deadzone=0.01), 2) == 0.50
    assert round(lockable_knob.percent(deadzone=0.0), 2) == 0.50

    lockable_knob.lock()
    mockHardware.set_ADC_u16_value(lockable_knob, 0)
    lockable_knob.request_unlock()

    assert round(lockable_knob.percent(deadzone=0.01), 2) == 0.50
    assert round(lockable_knob.percent(deadzone=0.0), 2) == 0.50
    assert lockable_knob.state == LockableKnob.STATE_UNLOCK_REQUESTED

    mockHardware.set_ADC_u16_value(lockable_knob, (MAX_UINT16 / 2) + 10)
    assert round(lockable_knob.percent(deadzone=0.01), 2) == 0.50
    assert round(lockable_knob.percent(deadzone=0.0), 2) == 0.50
    assert lockable_knob.state == LockableKnob.STATE_UNLOCKED


def test_state_changes(lockable_knob: LockableKnob):
    # Unlocked
    assert lockable_knob.state == LockableKnob.STATE_UNLOCKED

    lockable_knob.request_unlock()
    assert lockable_knob.state == LockableKnob.STATE_UNLOCKED

    lockable_knob.lock()
    assert lockable_knob.state == LockableKnob.STATE_LOCKED

    # locked
    lockable_knob.lock()
    assert lockable_knob.state == LockableKnob.STATE_LOCKED

    lockable_knob.request_unlock()
    assert lockable_knob.state == LockableKnob.STATE_UNLOCK_REQUESTED

    # Unlock requested

    lockable_knob.request_unlock()
    assert lockable_knob.state == LockableKnob.STATE_UNLOCK_REQUESTED

    lockable_knob.lock()
    assert lockable_knob.state == LockableKnob.STATE_LOCKED


def test_access_percent(mockHardware: MockHardware, lockable_knob: LockableKnob):
    assert round(lockable_knob.percent(deadzone=0.01), 2) == 0.50
    assert round(lockable_knob.percent(deadzone=0.0), 2) == 0.50

    mockHardware.set_ADC_u16_value(lockable_knob, MAX_UINT16)
    assert round(lockable_knob.percent(deadzone=0.01), 2) == 0
    assert round(lockable_knob.percent(deadzone=0.0), 2) == 0

    mockHardware.set_ADC_u16_value(lockable_knob, 0)
    assert round(lockable_knob.percent(deadzone=0.01), 2) == 1
    assert round(lockable_knob.percent(deadzone=0.0), 2) == 1


def test_access_choice(mockHardware: MockHardware, lockable_knob: LockableKnob):
    assert lockable_knob.choice([1, 2, 3]) == 2

    mockHardware.set_ADC_u16_value(lockable_knob, MAX_UINT16)
    assert lockable_knob.choice([1, 2, 3]) == 1

    mockHardware.set_ADC_u16_value(lockable_knob, 0)
    assert lockable_knob.choice([1, 2, 3]) == 3


def test_access_range(mockHardware: MockHardware, lockable_knob: LockableKnob):
    assert lockable_knob.range() == 49

    mockHardware.set_ADC_u16_value(lockable_knob, MAX_UINT16)
    assert lockable_knob.range() == 0

    mockHardware.set_ADC_u16_value(lockable_knob, 0)
    assert lockable_knob.range() == 99


def test_access_read_position(mockHardware: MockHardware, lockable_knob: LockableKnob):
    assert lockable_knob.read_position(deadzone=0.01) == 49
    assert lockable_knob.read_position(deadzone=0.0) == 49

    mockHardware.set_ADC_u16_value(lockable_knob, MAX_UINT16)
    assert lockable_knob.read_position(deadzone=0.01) == 0
    assert lockable_knob.read_position(deadzone=0.0) == 0

    mockHardware.set_ADC_u16_value(lockable_knob, 0)
    assert lockable_knob.read_position(deadzone=0.01) == 99
    assert lockable_knob.read_position(deadzone=0.0) == 99


# Disabled Knob Tests


# KnobBank tests


@pytest.fixture
def knob_bank(mockHardware: MockHardware):
    kb = (
        KnobBank.builder(k1)
        .with_disabled_knob()
        .with_unlocked_knob("param1")
        .with_locked_knob("param2", initial_uint16_value=MAX_UINT16 / 3)
        .build()
    )

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


def test_access_by_name(mockHardware: MockHardware, knob_bank: KnobBank):
    # knob starts in the middle, knob 1
    assert round(knob_bank.param1.percent(deadzone=0.01), 2) == 0.50
    assert round(knob_bank.param1.percent(deadzone=0.0), 2) == 0.50
    assert round(knob_bank.param2.percent(deadzone=0.01), 2) == 0.67
    assert round(knob_bank.param2.percent(deadzone=0.0), 2) == 0.67
    assert round(knob_bank.current.percent(deadzone=0.01), 2) == 0.50
    assert round(knob_bank.current.percent(deadzone=0.0), 2) == 0.50

    # change to knob 2, then move the knob
    knob_bank.next()
    mockHardware.set_ADC_u16_value(knob_bank.current, MAX_UINT16 / 3)

    assert round(knob_bank.param1.percent(deadzone=0.01), 2) == 0.50
    assert round(knob_bank.param1.percent(deadzone=0.0), 2) == 0.50
    assert round(knob_bank.param2.percent(deadzone=0.01), 2) == 0.67
    assert round(knob_bank.param2.percent(deadzone=0.0), 2) == 0.67
    assert round(knob_bank.current.percent(deadzone=0.01), 2) == 0.67
    assert round(knob_bank.current.percent(deadzone=0.0), 2) == 0.67

    mockHardware.set_ADC_u16_value(knob_bank.current, MAX_UINT16)

    assert round(knob_bank.param1.percent(deadzone=0.01), 2) == 0.50
    assert round(knob_bank.param1.percent(deadzone=0.0), 2) == 0.50
    assert round(knob_bank.param2.percent(deadzone=0.01), 2) == 0
    assert round(knob_bank.param2.percent(deadzone=0.0), 2) == 0
    assert round(knob_bank.current.percent(deadzone=0.01), 2) == 0
    assert round(knob_bank.current.percent(deadzone=0.0), 2) == 0

    mockHardware.set_ADC_u16_value(knob_bank.current, MAX_UINT16 / 3)

    assert round(knob_bank.param1.percent(deadzone=0.01), 2) == 0.50
    assert round(knob_bank.param1.percent(deadzone=0.0), 2) == 0.50
    assert round(knob_bank.param2.percent(deadzone=0.01), 2) == 0.67
    assert round(knob_bank.param2.percent(deadzone=0.0), 2) == 0.67
    assert round(knob_bank.current.percent(deadzone=0.01), 2) == 0.67
    assert round(knob_bank.current.percent(deadzone=0.0), 2) == 0.67


def test_access_by_index(mockHardware: MockHardware, knob_bank: KnobBank):
    # knob starts in the middle, knob 1
    assert round(knob_bank.knobs[0].percent(deadzone=0.01), 2) == 0
    assert round(knob_bank.knobs[0].percent(deadzone=0.0), 2) == 0
    assert round(knob_bank.knobs[1].percent(deadzone=0.01), 2) == 0.50
    assert round(knob_bank.knobs[1].percent(deadzone=0.0), 2) == 0.50
    assert round(knob_bank.knobs[2].percent(deadzone=0.01), 2) == 0.67
    assert round(knob_bank.knobs[2].percent(deadzone=0.0), 2) == 0.67
    assert round(knob_bank.current.percent(deadzone=0.01), 2) == 0.50
    assert round(knob_bank.current.percent(deadzone=0.0), 2) == 0.50

    # change to knob 2, then move the knob
    knob_bank.next()
    mockHardware.set_ADC_u16_value(knob_bank.current, MAX_UINT16 / 3)

    assert round(knob_bank.knobs[0].percent(deadzone=0.01), 2) == 0
    assert round(knob_bank.knobs[0].percent(deadzone=0.0), 2) == 0
    assert round(knob_bank.knobs[1].percent(deadzone=0.01), 2) == 0.50
    assert round(knob_bank.knobs[1].percent(deadzone=0.0), 2) == 0.50
    assert round(knob_bank.knobs[2].percent(deadzone=0.01), 2) == 0.67
    assert round(knob_bank.knobs[2].percent(deadzone=0.0), 2) == 0.67
    assert round(knob_bank.current.percent(deadzone=0.01), 2) == 0.67
    assert round(knob_bank.current.percent(deadzone=0.0), 2) == 0.67

    mockHardware.set_ADC_u16_value(knob_bank.current, MAX_UINT16)

    assert round(knob_bank.knobs[0].percent(deadzone=0.01), 2) == 0
    assert round(knob_bank.knobs[0].percent(deadzone=0.0), 2) == 0
    assert round(knob_bank.knobs[1].percent(deadzone=0.01), 2) == 0.50
    assert round(knob_bank.knobs[1].percent(deadzone=0.0), 2) == 0.50
    assert round(knob_bank.knobs[2].percent(deadzone=0.01), 2) == 0
    assert round(knob_bank.knobs[2].percent(deadzone=0.0), 2) == 0
    assert round(knob_bank.current.percent(deadzone=0.01), 2) == 0
    assert round(knob_bank.current.percent(deadzone=0.0), 2) == 0

    mockHardware.set_ADC_u16_value(knob_bank.current, MAX_UINT16 / 3)

    assert round(knob_bank.knobs[0].percent(deadzone=0.01), 2) == 0
    assert round(knob_bank.knobs[0].percent(deadzone=0.0), 2) == 0
    assert round(knob_bank.knobs[1].percent(deadzone=0.01), 2) == 0.50
    assert round(knob_bank.knobs[1].percent(deadzone=0.0), 2) == 0.50
    assert round(knob_bank.knobs[2].percent(deadzone=0.01), 2) == 0.67
    assert round(knob_bank.knobs[2].percent(deadzone=0.0), 2) == 0.67
    assert round(knob_bank.current.percent(deadzone=0.01), 2) == 0.67
    assert round(knob_bank.current.percent(deadzone=0.0), 2) == 0.67

    # change to knob 0 (disabled), then move the knob
    knob_bank.next()

    mockHardware.set_ADC_u16_value(knob_bank.current, MAX_UINT16)

    assert round(knob_bank.knobs[0].percent(deadzone=0.01), 2) == 0
    assert round(knob_bank.knobs[0].percent(deadzone=0.0), 2) == 0
    assert round(knob_bank.knobs[1].percent(deadzone=0.01), 2) == 0.50
    assert round(knob_bank.knobs[1].percent(deadzone=0.0), 2) == 0.50
    assert round(knob_bank.knobs[2].percent(deadzone=0.01), 2) == 0.67
    assert round(knob_bank.knobs[2].percent(deadzone=0.0), 2) == 0.67
    assert round(knob_bank.current.percent(deadzone=0.01), 2) == 0
    assert round(knob_bank.current.percent(deadzone=0.0), 2) == 0

    mockHardware.set_ADC_u16_value(knob_bank.current, MAX_UINT16 / 4)

    assert round(knob_bank.knobs[0].percent(deadzone=0.01), 2) == 0
    assert round(knob_bank.knobs[0].percent(deadzone=0.0), 2) == 0
    assert round(knob_bank.knobs[1].percent(deadzone=0.01), 2) == 0.50
    assert round(knob_bank.knobs[1].percent(deadzone=0.0), 2) == 0.50
    assert round(knob_bank.knobs[2].percent(deadzone=0.01), 2) == 0.67
    assert round(knob_bank.knobs[2].percent(deadzone=0.0), 2) == 0.67
    assert round(knob_bank.current.percent(deadzone=0.01), 2) == 0
    assert round(knob_bank.current.percent(deadzone=0.0), 2) == 0

    # change to knob 1, then move the knob
    knob_bank.next()
    mockHardware.set_ADC_u16_value(knob_bank.current, MAX_UINT16 / 5)

    assert round(knob_bank.knobs[0].percent(deadzone=0.01), 2) == 0
    assert round(knob_bank.knobs[0].percent(deadzone=0.0), 2) == 0
    assert round(knob_bank.knobs[1].percent(deadzone=0.01), 2) == 0.50
    assert round(knob_bank.knobs[1].percent(deadzone=0.0), 2) == 0.50
    assert round(knob_bank.knobs[2].percent(deadzone=0.01), 2) == 0.67
    assert round(knob_bank.knobs[2].percent(deadzone=0.0), 2) == 0.67
    assert round(knob_bank.current.percent(deadzone=0.01), 2) == 0.50
    assert round(knob_bank.current.percent(deadzone=0.0), 2) == 0.50

    mockHardware.set_ADC_u16_value(knob_bank.current, MAX_UINT16 / 2)

    assert round(knob_bank.knobs[0].percent(deadzone=0.01), 2) == 0
    assert round(knob_bank.knobs[0].percent(deadzone=0.0), 2) == 0
    assert round(knob_bank.knobs[1].percent(deadzone=0.01), 2) == 0.50
    assert round(knob_bank.knobs[1].percent(deadzone=0.0), 2) == 0.50
    assert round(knob_bank.knobs[2].percent(deadzone=0.01), 2) == 0.67
    assert round(knob_bank.knobs[2].percent(deadzone=0.0), 2) == 0.67
    assert round(knob_bank.current.percent(deadzone=0.01), 2) == 0.50
    assert round(knob_bank.current.percent(deadzone=0.0), 2) == 0.50

    mockHardware.set_ADC_u16_value(knob_bank.current, MAX_UINT16 / 5)

    assert round(knob_bank.knobs[0].percent(deadzone=0.01), 2) == 0
    assert round(knob_bank.knobs[0].percent(deadzone=0.0), 2) == 0
    assert round(knob_bank.knobs[1].percent(deadzone=0.01), 2) == 0.81
    assert round(knob_bank.knobs[1].percent(deadzone=0.0), 2) == 0.80
    assert round(knob_bank.knobs[2].percent(deadzone=0.01), 2) == 0.67
    assert round(knob_bank.knobs[2].percent(deadzone=0.0), 2) == 0.67
    assert round(knob_bank.current.percent(deadzone=0.01), 2) == 0.81
    assert round(knob_bank.current.percent(deadzone=0.0), 2) == 0.80


# KnobBank.Builder tests


def test_builder():
    kb = (
        KnobBank.builder(k1)
        .with_disabled_knob()
        .with_unlocked_knob("param1")
        .with_locked_knob("param2", initial_uint16_value=MAX_UINT16)
        .build()
    )

    assert len(kb.knobs) == 3
    assert kb.index == 1
    assert kb.param2._sample_adc() == MAX_UINT16


def test_builder_threshold_from_choice_count():
    kb = (
        KnobBank.builder(k1)
        .with_unlocked_knob("param1", threshold_from_choice_count=7)
        .with_locked_knob("param2", initial_uint16_value=MAX_UINT16)
        .build()
    )

    assert len(kb.knobs) == 2
    assert kb.index == 0
    assert kb.param1.threshold == int(1 / 7 * MAX_UINT16)
    assert kb.param2.threshold == int(DEFAULT_THRESHOLD * MAX_UINT16)
