from europi import Knob, MAX_UINT16


class LockableKnob(Knob):
    STATE_UNLOCKED = 0
    STATE_UNLOCK_REQUESTED = 1
    STATE_LOCKED = 2

    def __init__(self, knob: Knob, initial_value=None, threshold=0.05):
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
            if self.value - self.threshold < current_value and current_value < self.value + self.threshold:
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
    def __init__(self, knob: Knob, names_and_values, include_disabled=True) -> None:
        self.index = 0
        self.knobs = []
        unlocked_count = 0

        if include_disabled:
            self.knobs.append(DisabledKnob(knob))
            self.index = 1

        if len(names_and_values) == 0:
            raise ValueError(f"Must specify at least one knob in the bank: {names_and_values}")

        for index, (name, value) in enumerate(names_and_values, start=len(self.knobs)):
            if name == None:
                raise ValueError(f"Unnamed knob specified: {names_and_values[index]}")
            else:
                if value != None:
                    k = LockableKnob(knob, initial_value=value)
                else:
                    k = LockableKnob(knob)
                    self.index = index
                    unlocked_count += 1
                    if unlocked_count > 1:
                        raise ValueError(f"Second unlocked knobs specified: {name}")
                setattr(self, name, k)  # make knob available by its name
            self.knobs.append(k)
        self.knobs[self.index].request_unlock()

    @property
    def current(self) -> LockableKnob:
        return self.knobs[self.index]

    def next(self):
        self.current.lock()
        self.index = (self.index + 1) % len(self.knobs)
        self.current.request_unlock()

