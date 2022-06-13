from collections import OrderedDict
from europi import Knob, MAX_UINT16

DEFAULT_THRESHOLD = 0.05


class LockableKnob(Knob):
    """A Knob whose state can be locked on the current value. Once locked, reading the knob's
    position will always return the locked value. When unlocking the knob, the value still doesn't
    change until the position of the knob moves to within ``threshold`` percent of the value. This
    prevents large jumps in a stetting when the knob is unlocked.

    :param knob: The knob to wrap.
    :param initial_value: The value to lock the knob at. If a value is provided the new knob is locked, otherwise it is unlocked.
    :param threshold: a decimal between 0 and 1 representing how close the knob must be to the locked value in order to unlock. The percentage is in terms of the knobs full range. Defaults to 5% (0.05)

    """

    STATE_UNLOCKED = 0
    STATE_UNLOCK_REQUESTED = 1
    STATE_LOCKED = 2

    def __init__(self, knob: Knob, initial_value=None, threshold_percentage=DEFAULT_THRESHOLD):
        super().__init__(knob.pin_id)
        self.pin = knob.pin  # Share the ADC
        self.value = initial_value if initial_value != None else 0
        if initial_value == None:
            self.state = LockableKnob.STATE_UNLOCKED
        else:
            self.state = LockableKnob.STATE_LOCKED
        self.threshold = int(threshold_percentage * MAX_UINT16)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.pin}, {self.value}, {self.state})"

    def _sample_adc(self, samples=None):
        if self.state == LockableKnob.STATE_LOCKED:
            return self.value

        elif self.state == LockableKnob.STATE_UNLOCKED:
            return super()._sample_adc(samples)

        else:  # STATE_UNLOCK_REQUESTED:
            current_value = super()._sample_adc(samples)
            if abs(self.value - current_value) < self.threshold:
                self.state = LockableKnob.STATE_UNLOCKED
                return current_value
            else:
                return self.value

    def lock(self, samples=None):
        """Locks this knob at its current state. Makes a call to the underlying knob's
        ``_sample_adc()`` method with the given number of samples."""
        self.value = self._sample_adc(samples=samples)
        self.state = LockableKnob.STATE_LOCKED

    def request_unlock(self):
        """Requests that the knob be unlocked. The knob will unlock the next time a reading of it's
        position is taken that is withing the threshold percentage of the locked value. That is,
        when the knob is moved close to the locked value. If ``lock()`` is called before the knob
        unlocks, the unlock is aborted.
        """
        if self.state == LockableKnob.STATE_LOCKED:
            self.state = LockableKnob.STATE_UNLOCK_REQUESTED


class DisabledKnob(LockableKnob):
    """A ``LockableKnob`` that cannot be unlocked and whose value is unimportant. Useful when
    building multifunction knobs.

    :param knob: The knob to wrap."""

    def __init__(self, knob: Knob):
        super().__init__(knob, initial_value=MAX_UINT16)

    def request_unlock(self):
        """LockedKnob can never be unlocked"""
        return


class KnobBank:
    """A ``KnobBank`` is a group of named 'virtual' ``LockableKnobs`` that share the same physical
    knob. Only one of these knobs is active (unlocked) at a time. This allows for a single knob to
    be used to control many parameters.

    It is recommended that ``KnobBanks`` be created using the ``Builder``, as in::

       k1_bank = (
           KnobBank.builder(k1)
           .with_disabled_knob()
           .with_unlocked_knob("x", threshold=0.02)
           .with_locked_knob("y", initial_value=1)
           .build()
       )

    Knobs can be referenced using their names::

       k1_bank.x.percent()
       k1_bank.y.read_position()

    .. note::
       ``KnobBank`` is not thread safe. It is possible to end up with two unlocked knobs if you call
       ``next()`` and take readings from a knob in two different threads. This can easily happen if
       your script calls ``next()`` in a button handler, while constantly reading the knob state in
       a main loop. The workaround is to set a flag in the button handler and call ``next()`` in the
       main loop.
    """

    def __init__(self, physical_knob: Knob, virtual_knobs, initial_selection) -> None:
        self.index = 0
        self.knobs = []

        for name, knob in virtual_knobs.items():
            setattr(self, name, knob)  # make knob available by its name
            self.knobs.append(knob)
        self.knobs[initial_selection].request_unlock()
        self.index = initial_selection

    @property
    def current(self) -> LockableKnob:
        """The currently active knob."""
        return self.knobs[self.index]

    def next(self):  # potential race condition: next() and _sample_adc() can both change state
        """Select the next knob by locking the current knob, and requesting an unlock on the next in
        the bank."""
        self.current.lock()
        self.index = (self.index + 1) % len(self.knobs)
        self.current.request_unlock()

    class Builder:
        """A convenient interface for creating KnobBanks with consistent initial state."""

        def __init__(self, knob: Knob) -> None:
            self.knob = knob
            self.knobs_by_name = OrderedDict()
            self.initial_index = None

        def with_disabled_knob(self) -> "Builder":
            """Add a ``DisabledKnob`` to the bank. This disables the knob so that no parameters can
            be changed."""
            self.knobs_by_name[DisabledKnob.__name__] = DisabledKnob(self.knob)
            return self

        def with_locked_knob(
            self, name: str, initial_value, threshold_percentage=DEFAULT_THRESHOLD
        ) -> "Builder":
            """Add a ``LockableKnob`` to the bank whose initial state is locked.

            :param name: the name of this virtual knob
            """
            if name == None:
                raise ValueError("Knob name cannot be None")
            self.knobs_by_name[name] = LockableKnob(
                self.knob, initial_value=initial_value, threshold_percentage=threshold_percentage
            )
            return self

        def with_unlocked_knob(
            self, name: str, threshold_percentage=DEFAULT_THRESHOLD
        ) -> "Builder":
            """Add a ``LockableKnob`` to the bank whose initial state is unlocked. This knob will be
            active. Only one unlocked knob may be added to the bank.

            :param name: the name of this virtual knob
            """
            if name == None:
                raise ValueError("Knob name cannot be None")
            if self.initial_index != None:
                raise ValueError(f"Second unlocked knob specified: {name}")
            self.knobs_by_name[name] = LockableKnob(
                self.knob, threshold_percentage=threshold_percentage
            )
            self.initial_index = len(self.knobs_by_name) - 1
            return self

        def build(self) -> "KnobBank":
            """Create the ``KnobBank`` with the specified knobs."""
            if len(self.knobs_by_name) < 0:
                raise ValueError(f"Must specify at least one knob in the bank.")
            if self.initial_index == None:
                self.initial_index = 0
            return KnobBank(
                physical_knob=self.knob,
                virtual_knobs=self.knobs_by_name,
                initial_selection=self.initial_index,
            )

    @staticmethod
    def builder(knob: Knob) -> Builder:
        return KnobBank.Builder(knob)
