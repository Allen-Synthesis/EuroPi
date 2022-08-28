from time import sleep

try:
    import time
    from software.firmware import europi
    from software.firmware.europi_script import EuroPiScript
except ImportError:
    import europi
    import utime as time
    from europi_script import EuroPiScript



class Clock(EuroPiScript):
    MIN_BPM = 20
    MAX_BPM = 240
    TRIGGER_DURATION = 15
    PPQN = 4
    MINUTE = 60000  # in milliseconds

    EDIT_PARAM = [
        'None', 'BPM'
    ]

    def __init__(self):
        self._update_display = True
        self._configure_bpm = False

        self._bpm = 200
        self._last_trigger = time.ticks_add(time.ticks_ms(), self.TRIGGER_DURATION)
        self.clock_deadlines = time.ticks_add(time.ticks_ms(), self.sleep_period)

        self._prev_k2 = None

    @property
    def sleep_period(self):
        return int((self.MINUTE / self._bpm / self.PPQN))
    
    def config_params(self):
        if europi.k1.choice(self.EDIT_PARAM, samples=1) == 'BPM':
            self._bpm = europi.k2.range(self.MAX_BPM - self.MIN_BPM + 1, samples=10) + self.MIN_BPM
            self._update_display = True
    
    def trigger_clocks(self):
        # Check to turn off trigger pulses.
        if time.ticks_diff(time.ticks_ms(), self._last_trigger) > 0:
            europi.cv2.off()
            self._last_trigger = time.ticks_add(time.ticks_ms(), self.TRIGGER_DURATION)

        # Trigger when deadline exceeded.
        deadline_exceeded = time.ticks_diff(time.ticks_ms(), self.clock_deadlines)
        if deadline_exceeded > 0:
            europi.cv2.on()
            self.clock_deadlines = time.ticks_add(time.ticks_ms(), self.sleep_period-1)

    def display(self):
        if self._update_display is False:
            return

        europi.oled.fill(0)
        europi.oled.text(f"{self._bpm} | {self.sleep_period * 4}", 30, 10)
        europi.oled.show()

        self._update_display = False

    def main(self):
        while True:
            self.config_params()
            self.trigger_clocks()
            self.display()



# if __name__ == "__main__":
#     Clock().main()

Clock().main()
