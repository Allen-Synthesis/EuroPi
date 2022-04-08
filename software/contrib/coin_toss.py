from europi import *
from random import random
from time import sleep_ms, ticks_ms, ticks_add, ticks_diff
import machine
from europi_script import EuroPiScript

# Internal clock tempo range.
MAX_BPM = 280
MIN_BPM = 20

# Constant values for display.
FRAME_WIDTH = int(OLED_WIDTH / 8)


class CoinToss(EuroPiScript):
    def __init__(self):
        self.gate_mode = True
        self.internal_clock = True
        self._prev_clock = 0
        self._tempo = 0
        self._deadline = 0

        # Overclock the Pico for improved performance.
        machine.freq(250_000_000)
        # machine.freq(125_000_000)  # Default clock speed.


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
        return ticks_add(ticks_ms(), wait_ms)

    def wait(self):
        """Pause script execution waiting for next quarter note in the clock cycle."""
        if self.internal_clock:
            while True:
                if ticks_diff(self._deadline, ticks_ms()) <= 0:
                    self._deadline = self.get_next_deadline()
                    return
        else:  # External clock
            # Loop until digital in goes high (clock pulse received).
            while not self.internal_clock:
                if din.value() != self._prev_clock:
                    # We've detected a new clock value.
                    self._prev_clock = 1 if self._prev_clock == 0 else 0
                    # If the previous value was just set to 1 then we are seeing 
                    # a high value for the first time, break wait and return.
                    if self._prev_clock == 1:
                        return

    def toss(self, a, b, draw=True):
        """If random value is below trigger a, otherwise trigger b.

        If draw is true, then display visualization of the coin toss.
        """
        coin = random()
        # Sum the knob2 and analogue input values to determine threshold.
        read_sum = k2.percent() + ain.read_voltage()/12
        self.threshold = clamp(read_sum, 0, 1)
        if self.gate_mode:
            a.value(coin < self.threshold)
            b.value(coin > self.threshold)
        else:
            (a if coin < self.threshold else b).on()
        
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

            self.toss(cv1, cv2)
            cv3.on()  # First column clock trigger
            if counter % 4 == 0:
                self.toss(cv4, cv5, False)
                cv6.on()  # Second column clock trigger (1/4x speed)
            
            sleep_ms(10)
            if self.gate_mode:
                # Only turn off clock triggers.
                [o.off() for o in (cv3, cv6)]
            else:
                # Turn of all cvs in trigger mode.
                [o.off() for o in cvs]

            # Draw threshold line
            oled.hline(0, int(self.threshold * OLED_HEIGHT), FRAME_WIDTH, 1)
            oled.show()

            counter += 1
            self.wait()

if __name__ == '__main__':
    # Reset module display state.
    coin_toss = CoinToss()
    coin_toss.main()
