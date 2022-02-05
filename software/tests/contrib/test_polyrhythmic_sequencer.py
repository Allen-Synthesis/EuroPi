from ast import Index
import pytest

from polyrhythmic_sequencer import Sequence
from europi import cv1, cv2


@pytest.mark.parametrize(
    "notes, edit, expected",
    [
        (["C0", "E0", "G0", "B0"], (0, "C1"), ["C1", "E0", "G0", "B0"]),
        (["C4", "C3", "C2", "C1"], (1, "D0"), ["C4", "D0", "C2", "C1"]),
        (["C0", "G0", "G0", "C0"], (2, "F#1"), ["C0", "G0", "F#1", "C0"]),
        (["C0", "C0", "C#0", "C#0"], (3, "C1"), ["C0", "C0", "C#0", "C1"]),
    ],
)
def test_edit_step(notes, edit, expected):
    seq = Sequence(notes, cv1, cv2)
    assert seq.notes == notes
    assert seq.step_index == 0
    # edit step
    seq.edit_step(*edit)
    assert seq.notes == expected
    assert seq.step_index == 0


@pytest.mark.parametrize(
    "edit, expected",
    [
        ((5, "C1"), IndexError),
        ((1, "Z0"), AssertionError),
        ((2, "F#99"), AssertionError),
    ],
)
def test_edit_step_error(edit, expected):
    seq = Sequence(["C0", "D#0", "D0", "G0"], cv1, cv2)
    # edit step
    with pytest.raises(expected):
        seq.edit_step(*edit)


@pytest.mark.parametrize(
    "step_index, expected",
    [
        (0, "D#0"),
        (1, "D0"),
        (2, "G0"),
        (3, "C0"),
    ],
)
def test_advance_step(step_index, expected):
    seq = Sequence(["C0", "D#0", "D0", "G0"], cv1, cv2)
    seq.step_index = step_index
    # adcance step
    seq.advance_step()
    assert seq.current_note() == expected



@pytest.mark.parametrize(
    "step_index, expected_note, expected_voltage",
    [
        (0, "D#0", 0.25),
        (1, "D0", 0.16666666666666666),
        (2, "G0", 0.5833333333333333),
        (3, "C2", 2.0),
    ],
)
def test_play_step(step_index, expected_note, expected_voltage):
    seq = Sequence(["C2", "D#0", "D0", "G0"], cv1, cv2)
    seq.step_index = step_index
    # play step
    seq.play_next_step()
    assert seq.current_note() == expected_note, f"{step_index} failed"
    assert seq._pitch_cv(seq.current_note()) == expected_voltage, f"{step_index} failed"

