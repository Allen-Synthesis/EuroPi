"""Shared classes for quantization support

    @author Chris Iverach-Brereton <ve4cib@gmail.com>
    @year   2023
"""
class Quantizer:
    """Represents a set of semitones we can quantize input voltages to

    By default this represents a chromatic scale, with all notes enabled.  Notes can be changed
    by setting scale[n] = True/False, where n is the index of the semitone to toggle
    """

    def __init__(self, notes=None):
        """Constructor; can specify what notes are enabled/disabled

        Undesired results may happen if you use an array that's not of length 12

        @param notes  A boolean array of length 12 indicating what semitones are enabled (True)
                      or disabled (False)
        """
        if notes is None:
            self.notes = [True]*12
        else:
            self.notes = notes

    def __getitem__(self, n):
        return self.notes[n]

    def __setitem__(self, n, value):
        self.notes[n] = value

    def __len__(self):
        return len(self.notes)

    def quantize(self, analog_in):
        """Take an analog input voltage and round it to the nearest note on our scale

        @param analog_in  The input voltage to quantize, as a float

        @return A tuple of the form (voltage, note) where voltage is
                the raw voltage to output, and note is a value from
                0-11 indicating the semitone
        """
        # first get the closest chromatic voltage to the input
        nearest_chromatic_volt = round(analog_in / VOLTS_PER_SEMITONE) * VOLTS_PER_SEMITONE

        # then convert that to a 0-12 value indicating the nearest semitone
        base_volts = int(nearest_chromatic_volt)
        nearest_semitone = (nearest_chromatic_volt - base_volts) / VOLTS_PER_SEMITONE

        # go through our scale and determine the nearest on-scale note
        nearest_on_scale = 0
        best_delta = 255
        for note in range(len(self.notes)):
            if self.notes[note]:
                delta = abs(nearest_semitone - note)
                if delta < best_delta:
                    nearest_on_scale = note
                    best_delta = delta

        volts = base_volts + nearest_on_scale * VOLTS_PER_SEMITONE

        return (volts, nearest_on_scale)

class CommonScales:
    """A collection of common scales that can be used in other scripts to support quantization
    """
    #                         C      C#     D      D#     E      F      F#     G      G#     A      A#     B
    Chromatic    = Quantizer([True,  True,  True,  True,  True,  True,  True,  True,  True,  True,  True,  True])
    NatMajor     = Quantizer([True,  False, True,  False, True,  True,  False, True,  False, True,  False, True])
    HarMajor     = Quantizer([True,  False, True,  False, True,  True,  False, True,  True,  False, True,  False])
    Major135     = Quantizer([True,  False, False, False, True,  False, False, True,  False, False, False, False])
    Major1356    = Quantizer([True,  False, False, False, True,  False, False, True,  False, True,  False, False])
    Major1357    = Quantizer([True,  False, False, False, True,  False, False, True,  False, False, False, True])

    NatMinor     = Quantizer([True,  False, True,  True,  False, True,  False, True,  True,  False, True,  False])
    HarMinor     = Quantizer([True,  False, True,  True,  False, True,  False, True,  True,  False, False, True])
    Minor135     = Quantizer([True,  False, False, True,  False, False, False, True,  False, False, False, False])
    Minor1356    = Quantizer([True,  False, False, True,  False, False, False, True,  True,  False, False, False])
    Minor1357    = Quantizer([True,  False, False, True,  False, False, False, True,  False, False, True,  False])

    ## 1-b3-4-b5-5-b7
    MajorBlues   = Quantizer([True,  False, True,  True,  True,  False, False, True,  False, True,  False, False])
    ## 1-2-b3-3-5-6
    MinorBlues   = Quantizer([True,  False, False, True,  False, True,  True,  True,  False,  False, True,  False])

    WholeTone    = Quantizer([True,  False, True,  False, True,  False, True,  False, True,  False, True,  False])
    Pentatonic   = Quantizer([True,  False, True,  False, True,  False, False, True,  False, True,  False, False])
    Dominant7    = Quantizer([True,  False, False, False, True,  False, False, True,  False, False, True,  False])
