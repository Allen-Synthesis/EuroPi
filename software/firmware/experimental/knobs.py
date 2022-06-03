from collections import OrderedDict
from europi import Knob, MAX_UINT16

DEFAULT_THRESHOLD = 0.05


class LockableKnob(Knob):
    STATE_UNLOCKED = 0
    STATE_UNLOCK_REQUESTED = 1
    STATE_LOCKED = 2

    def __init__(self, knob: Knob, initial_value=None, threshold=DEFAULT_THRESHOLD):
        super().__init__(knob._pin_id)
        self.pin = knob.pin  # Share the ADC
        self.value = initial_value if initial_value != None else 0
        if initial_value == None:
            self.state = LockableKnob.STATE_UNLOCKED
        else:
            self.state = LockableKnob.STATE_LOCKED
        self.threshold = int(threshold * MAX_UINT16)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.pin}, {self.value}, {self.state})"

    def _sample_adc(self, samples=None, **kwargs):
        if self.state == LockableKnob.STATE_LOCKED:
            return self.value

        elif self.state == LockableKnob.STATE_UNLOCKED:
            return super()._sample_adc(samples, **kwargs)

        else:  # STATE_UNLOCK_REQUESTED:
            current_value = super()._sample_adc(samples, **kwargs)
            if abs(self.value - current_value) < self.threshold:
                self.state = LockableKnob.STATE_UNLOCKED
                return current_value
            else:
                return self.value

    def lock(self):
        self.value = self._sample_adc()
        self.state = LockableKnob.STATE_LOCKED

    def request_unlock(self):
        if self.state == LockableKnob.STATE_LOCKED:
            self.state = LockableKnob.STATE_UNLOCK_REQUESTED


class DisabledKnob(LockableKnob):
    def __init__(self, knob: Knob):
        super().__init__(knob, initial_value=MAX_UINT16)

    def request_unlock(self):
        """LockedKnob can never be unlocked"""
        return


class KnobBank:
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
        return self.knobs[self.index]

    def next(self):  # potential race condition: next() and _sample_adc() can both change state
        self.current.lock()
        self.index = (self.index + 1) % len(self.knobs)
        self.current.request_unlock()

    class Builder:
        def __init__(self, knob: Knob) -> None:
            self.knob = knob
            self.knobs_by_name = OrderedDict()
            self.initial_index = None

        def with_disabled_knob(self) -> "KnobBankBuilder":
            self.knobs_by_name[DisabledKnob.__name__] = DisabledKnob(self.knob)
            return self

        def with_locked_knob(
            self, name: str, initial_value, threshold=DEFAULT_THRESHOLD
        ) -> "KnobBankBuilder":
            if name == None:
                raise ValueError("Knob name cannot be None")
            self.knobs_by_name[name] = LockableKnob(
                self.knob, initial_value=initial_value, threshold=threshold
            )
            return self

        def with_unlocked_knob(self, name: str, threshold=DEFAULT_THRESHOLD) -> "KnobBankBuilder":
            if name == None:
                raise ValueError("Knob name cannot be None")
            if self.initial_index != None:
                raise ValueError(f"Second unlocked knob specified: {name}")
            self.knobs_by_name[name] = LockableKnob(self.knob, threshold=threshold)
            self.initial_index = len(self.knobs_by_name) - 1
            return self

        def build(self) -> "KnobBank":
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
