from hardware.io import AnalogueReader

class Knob(AnalogueReader):
    """A class for handling the reading of knob voltage and position.

    Read_position has a default value of 100, meaning if you simply use
    ``kx.read_position()`` you will return a whole number percent style value
    from 0-100.

    There is also the optional parameter of ``samples`` (which must come after the
    normal parameter), the same as the analogue input uses (the knob positions
    are 'read' via an analogue to digital converter). It has a default value
    of 256, but you can use higher or lower depending on if you value speed or
    accuracy more. If you really want to avoid 'noise' which would present as
    a flickering value despite the knob being still, then I'd suggest using
    higher samples (and probably a smaller number to divide the position by).
    The default ``samples`` value can also be set using the ``set_samples()``
    method, which will then be used on all analogue read calls for that
    component.

    An optional ``deadzone`` parameter can be used to place deadzones at both
    positions (all the way left and right) of the knob to make sure the full range
    is available on all builds. The default value is 0.01 (resulting in 1% of the
    travel used as deadzone on each side). There is usually no need to change this.

    Additionally, the ``choice()`` method can be used to select a value from a
    list of values based on the knob's position::

        def clock_division(self):
            return k1.choice([1, 2, 3, 4, 5, 6, 7, 8, 16, 32])

    When the knob is all the way to the left, the return value will be ``1``,
    at 12 o'clock it will return the mid point value of ``5`` and when fully
    clockwise, the last list item of ``32`` will be returned.

    The ADCs used to read the knob position are only 12 bit, which means that
    any read_position value above 4096 (2^12) will not actually be any finer
    resolution, but will instead just go up in steps. For example using 8192
    would only return values which go up in steps of 2.
    """

    def __init__(self, pin, deadzone=0.01):
        super().__init__(pin, deadzone=deadzone)

    def percent(self, samples=None, deadzone=None):
        """Return the knob's position as relative percentage."""
        # Reverse range to provide increasing range.
        return 1.0 - super().percent(samples, deadzone)

    def read_position(self, steps=100, samples=None, deadzone=None):
        """Returns the position as a value between zero and provided integer."""
        return self.range(steps, samples, deadzone)
