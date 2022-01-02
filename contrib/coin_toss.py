from europi import *
from random import random
from utime import sleep_ms, ticks_ms

MAX_BPM = 280
MIN_BPM = 20


def trigger(output, delay=10):
    output.on()
    sleep_ms(delay)
    output.off()


class CoinToss:
    def __init__(self):
        self.gate_mode = True
        self.internal_clock = True
        self._prev_clock = 0

        @b1.handler
        def toggle_clock():
            self.internal_clock = not self.internal_clock

        @b2.handler
        def toggle_gate():
            self.gate_mode = not self.gate_mode
            [o.off() for o in cvs]

    def tempo(self):
        """Read the current tempo set by k1 within set range."""
        return round((k1.percent() * (MAX_BPM - MIN_BPM)) + MIN_BPM)

    def get_next_deadline(self):
        """Get the deadline for next clock tick whole note."""
        # The duration of a quarter note in ms for the current tempo.
        wait_ms = int(((60 / self.tempo()) / 4) * 1000)
        return ticks_ms() + wait_ms

    def wait(self):
        """Pause script execution waiting for next quarter note in the clock cycle."""
        if self.internal_clock:
            deadline = self.get_next_deadline()
            while True:
                if ticks_ms() > deadline:
                    return
        else:  # External clock
            # Loop until digital in goes high (clock pulse received).
            while not self.internal_clock:
                if din.value() != self._prev_clock:
                    self._prev_clock = 1 if self._prev_clock == 0 else 0
                    if self._prev_clock == 0:
                        return

    def toss(self, a, b, shape):
        coin = random()
        # Sum the knob2 and analogue input values to determine threshold.
        self.threshold = clamp(k2.percent() + (ain.read_voltage() / 12), 0, 0.999)
        if self.gate_mode:
            a.value(coin > self.threshold)
            b.value(coin < self.threshold)
        else:
            trigger(a if coin > self.threshold else b)

        # Draw a coin shape for coin toss
        oled.text(shape, 5, int(coin * OLED_HEIGHT), 1)

    def main(self):
        # Start the main loop.
        counter = 0
        while True:
            # Scroll and clear new screen area.
            oled.scroll(10, 0)
            oled.fill_rect(0, 0, 10, OLED_HEIGHT, 0)

            self.toss(cv1, cv3, "o")
            if counter % 4 == 0:
                self.toss(cv4, cv6, "x")

            # Draw threshold line
            oled.hline(0, int(self.threshold * OLED_HEIGHT), 10, 1)
            oled.show()

            counter += 1
            self.wait()


if __name__ == '__main__':
    [o.off() for o in cvs]
    oled.clear()
    oled.show()

    coin_toss = CoinToss()
    coin_toss.main()
