"""
Clock Divider
author: awonak
version: 2.0

Provide 4 divisions of the master clock set by knob 1.

Master clock set by knob 1 will emit a trigger pulse once every quarter note
for the current tempo. Use button 2 to cycle through each digital out enabling
it to set a division from a list of division choices chosen by knob 2.

knob_1: master clock tempo
knob_2: choose the division for the current selected index.
button_2: cycle through the digital
digital_1: first division, default master clock
digital_2: second division, default /2
digital_3: third division, default /4
digital_4: fourth division, default /8

"""

from machine import ADC
from time import sleep

from europi import OLED_HEIGHT, OLED_WIDTH, ain, b1, b2, cv1, cv2, cv3, cv4, cv5, cv6, din, k1, k2, oled
from europi_script import EuroPiScript

import uasyncio as asyncio

from lib.europi import knob_1
from lib.europi import knob_2
from lib.europi import button_2
from lib.europi import digital_outputs
from lib.clock import Clock
from lib.helpers import trigger


DEBUG = False

# Useful divisions to choose from.
DIVISION_CHOICES = [1, 2, 3, 4, 5, 6, 7, 8, 12, 16, 32, 64                                       ]
MAX_DIVISION = max(DIVISION_CHOICES)


class ClockDivider:

    def __init__(self, clock: Clock):
        self.clock = clock

        # Divisions corresponding to each digital output.
        self.divisions = [1, 2, 4, 8]

        # Counters for each clock division (use a copy of the values, not the reference)
        self.counters = self.divisions[:]

        # Selects the Digital Jack to adjust clock division using 0-based index with an
        # extra index to disable config controls.
        self.selected_output = -1
        self._previous_choice = knob_2.choice(len(DIVISION_CHOICES))

    def trigger(self):
        """Emit a trigger for each digital jack within this clock cycle."""
        for i, pin in enumerate(digital_outputs):
            self.counters[i] -= 1
            if self.counters[i] == 0:
                trigger(pin)
                # Reset counter for this division
                self.counters[i] = self.divisions[i]

    def adjust_division(self):
        """When a digital jack is selected, read division choice and update it's division."""
        if self.selected_output >= 0:
            choice = knob_2.choice(len(DIVISION_CHOICES))
            if choice != self._previous_choice:
                self.divisions[self.selected_output] = DIVISION_CHOICES[choice]
                self.counters[self.selected_output] = DIVISION_CHOICES[choice]
                self._previous_choice = choice

    async def start(self):
        # Register button handlers.
        @button_2.handler
        def config_divisions():
            self.selected_output = (self.selected_output + 1) % len(self.divisions)

        # Start the main loop.
        while True:
            # Trigger the digital pin if it's divisible by the counter.
            self.trigger()

            # Set the currently selected digital out's clock division to the value
            # selected by knob 2.
            self.adjust_division()

            self.debug()
            await asyncio.sleep_ms(self.clock.wait_ms())

    def debug(self):
        if DEBUG:
            msg = 'DJ: {}  || Counters: {}  || config: {} || tempo: {} wait: {}'
            print(msg.format(self.divisions, self.counters, self.selected_output, self.clock.tempo, self.clock.wait_ms()))


# Run the script if called directly.
if __name__ == '__main__':
    clock = Clock(knob_1)
    clock_divider = ClockDivider(clock)

    # Main script function
    async def main():
        loop = asyncio.get_event_loop()
        loop.create_task(clock_divider.start())
        loop.run_forever()

    try:
        asyncio.run(main())
    finally:
        asyncio.new_event_loop()
