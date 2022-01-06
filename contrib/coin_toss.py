"""
Coin Toss
author: awonak
date: 2022-01-03

Two pairs of clocked probability gates.

Knob 1 adjusts the master clock speed of gate change probability. Knob 2 moves
the probability thresholed between A and B with a 50% chance at noon. Output 
column 1 (cv1 and cv4) run at 1x speed and output column2 (cv2 and cv5) run at
4x speed for interesting rhythmic patterns. Push button 1 to toggle between
internal and external clock source. Push button 2 to toggle between gate and
trigger mode. Analogue input is summed with the threshold knob value to allow
external threshold control.

digital in: External clock (when in external clock mode)
analogue in: Threshold control (summed with threshold knob)
knob 1: internal clock speed
knob 2: probability threshold
button 1: toggle internal / external clock source
button 2: toggle gate/trigger mode
cv1/cv4: Coin 1 gate output pair when voltage above/below threshold
cv2/cv5: Coin 2 gate output pair when voltage above/below threshold
cv3: Coin 1 clock
cv6: Coin 2 clock

"""
from europi import *
from random import random
from utime import sleep_ms, ticks_ms

MAX_BPM = 280
MIN_BPM = 20

# Constant values for display
FRAME_WIDTH = int(OLED_WIDTH / 8)


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
            """Toggle between internal clock and external clock from digital in."""
            self.internal_clock = not self.internal_clock

        @b2.handler
        def toggle_gate():
            """Toggle between gate and trigger mode."""
            self.gate_mode = not self.gate_mode
            [o.off() for o in cvs]

    def tempo(self):
        """Read the current tempo set by k1 within set range."""
        return round(k1.read_position(MAX_BPM - MIN_BPM) + MIN_BPM)

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
                    # We've detected a new clock value.
                    self._prev_clock = 1 if self._prev_clock == 0 else 0
                    # If the previous value is 0 then we are seeing a high 
                    # value for the first time, break wait and return.
                    if self._prev_clock == 0:
                        return

    def toss(self, a, b, draw=True):
        """If random value is below trigger a, otherwise trigger b.

        If draw is true, then display visualization of the coin toss.
        """
        coin = random()
        # Sum the knob2 and analogue input values to determine threshold.
        self.threshold = clamp(k2.read_position()/100 + ain.read_voltage()/12, 0, 1)
        if self.gate_mode:
            a.value(coin < self.threshold)
            b.value(coin > self.threshold)
        else:
            trigger(a if coin < self.threshold else b)
        
        if not draw:
            return

        # Draw gate/trigger display graphics for coin toss
        h = int(self.threshold * OLED_HEIGHT)
        tick = FRAME_WIDTH if self.gate_mode else 1
        offset = 8  # The amount of negative space before drawing gate.
        if coin < self.threshold:
            oled.fill_rect(offset, 0, tick, h, 1)
        else:
            oled.fill_rect(offset, h, tick, OLED_HEIGHT, 1)


    def main(self):
        # Start the main loop.
        counter = 0
        while True:
            # Scroll and clear new screen area.
            oled.scroll(FRAME_WIDTH, 0)
            oled.fill_rect(0, 0, FRAME_WIDTH, OLED_HEIGHT, 0)

            self.toss(cv1, cv4)
            trigger(cv3)
            if counter % 4 == 0:
                self.toss(cv2, cv5, False)
                trigger(cv6)

            # Draw threshold line
            oled.hline(0, int(self.threshold * OLED_HEIGHT), FRAME_WIDTH, 1)
            oled.show()

            counter += 1
            self.wait()


if __name__ == '__main__':
    # Reset module display state.
    [o.off() for o in cvs]
    oled.clear()
    oled.show()

    coin_toss = CoinToss()
    coin_toss.main()
