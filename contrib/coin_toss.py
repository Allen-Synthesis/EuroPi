from europi import *
from random import random
from utime import sleep_ms, ticks_ms

DEBUG = True
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
        
        @b2.handler
        def toggle_gate():
            self.gate_mode = not self.gate_mode
            [o.off() for o in cvs]

    def tempo(self):
        """Read the current tempo set by k1 within set range."""
        return round((k1.percent() * (MAX_BPM - MIN_BPM)) + MIN_BPM, 1)

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
            # FIXME: this will get stuck in an infinite loop when no signal present.
            while din.value(): pass
            return

    def toss(self, a, b):
        coin = random()
        threshold = k2.percent()
        if self.gate_mode:
            a.value(coin > threshold)
            b.value(coin < threshold)
        else:
            trigger(a if coin > threshold else b)
        return coin

    def main(self):
        # Start the main loop.
        while True:
            coin1 = self.toss(cv1, cv3)
            self.debug(coin1)
            self.wait()
    
    def debug(self, c1):
        if DEBUG:
            print(f"COIN1: {c1:>.2f}  THRESH: {k2.percent():>.2f}")


if __name__ == '__main__':
    [o.off() for o in cvs]
    coin_toss = CoinToss()
    coin_toss.main()
