from europi import Knob, MAX_UINT16


class LockableKnob(Knob):
    STATE_UNLOCKED = 0
    STATE_UNLOCK_REQUESTED = 1
    STATE_LOCKED = 2

    def __init__(self, knob, initial_value=None, threshold=0.05):
        super().__init__(knob._pin_id)
        self.value = initial_value
        if initial_value == None:
            self.state = LockableKnob.STATE_UNLOCKED
        else:
            self.state = LockableKnob.STATE_LOCKED
        self.threshold = int(threshold * MAX_UINT16)

    def _sample_adc(self, samples=None, **kwargs):
        # print(f"mm_sample: mode: {mode} samples: {samples}, kwargs: {kwargs}, values: {self.values}")

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


