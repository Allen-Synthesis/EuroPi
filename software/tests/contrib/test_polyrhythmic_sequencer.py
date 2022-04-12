import pytest

from contrib.polyrhythmic_sequencer import Sequence
from contrib.polyrhythmic_sequencer import PolyrhythmSeq

from europi import cv1, cv2, k2, oled


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


@pytest.mark.parametrize(
    "seq_index, step_index, cur_note, new_note",
    [
        (0, 0, "C0", "D#0"),
        (0, 3, "G0", "F0"),
        (1, 1, "F0", "G1"),
        (1, 3, "C0", "A2"),
    ],
)
def test_script_edit_sequence(seq_index, step_index, cur_note, new_note, monkeypatch):
    # Initialize and validate initial state.
    script = PolyrhythmSeq()
    assert script.page == 0
    assert script.param_index == 0
    assert script._prev_k2 == None
    assert script.seqs[seq_index].notes[step_index] == cur_note

    # Alter script state for test
    script.param_index = step_index
    script.seq = script.seqs[seq_index]
    script._prev_k2 = "C0"

    # Mock out Knob choice response.
    monkeypatch.setattr(k2, "choice", lambda *args: new_note)
    # Mock out Display text wiht noop.
    monkeypatch.setattr(oled, "text", lambda *args: None)

    # Call method under test and validate state changes.
    script.edit_sequence()
    assert script.param_index == step_index
    assert script.seqs[seq_index].notes[step_index] == new_note, f"actual notes: {script.seqs[seq_index].notes}"


@pytest.mark.parametrize(
    "param_index, new_poly",
    [(0, 1), (1, 2), (2, 5), (3, 16)],
)
def test_script_edit_poly(param_index, new_poly, monkeypatch):
    # Initialize and validate initial state.
    script = PolyrhythmSeq()
    assert script.page == 0
    assert script.param_index == 0
    assert script._prev_k2 == None
    # assert script.polys == [8, 3, 2, 5]
    assert script.seq_poly == [2, 1, 1, 0]

    # Alter script state for test
    script.param_index = param_index
    script._prev_k2 = 99

    # Mock out Knob choice response.
    monkeypatch.setattr(k2, "range", lambda *args: new_poly - 1)

    # Call method under test and validate state changes.
    script.edit_poly()
    assert script.polys[param_index] == new_poly, f"actual polys: {script.polys}"
