#!/usr/bin/env python3
"""Implements Conway's Game of Life as a pseudo-random LFO kernel
"""

from europi import *
from europi_script import EuroPiScript

import random

def clamp(x, low, hi):
    """Clamp a value to lie between low and hi
    """
    if x < low:
        return low
    elif x > hi:
        return hi
    else:
        return x

class Conway(EuroPiScript):
    def __init__(self):
        # For ease of blitting, store the field as a bit array
        # Each byte is 8 horizontally adjacent pixels, with the most significant bit
        # on the left
        self.field = bytearray(OLED_HEIGHT * OLED_WIDTH // 8)
        self.next_field = bytearray(OLED_HEIGHT * OLED_WIDTH // 8)

        self.frame = FrameBuffer(self.field, OLED_WIDTH, OLED_HEIGHT, MONO_HLSB)
        self.next_frame = FrameBuffer(self.next_field, OLED_WIDTH, OLED_HEIGHT, MONO_HLSB)

        # Simple optimization; keep a list of spaces whose states changed & their neighbours
        # This is initially empty as the field is entirely blank
        self.changed_spaces = set()

        # how many cells were born this tick?
        self.num_born = 0

        # how many cells died this tick?
        self.num_died = 0

        # how many cells are currently alive?
        # this gets updated on every tick and on random spawns
        self.num_alive = 0

        # Set to True if we want to spawn more random cells
        self.spawn_requested = False

        # Set to True if we want to clear the field & respawn
        self.reset_requested = False

        @b1.handler
        def on_b1():
            self.reset_requested = True

        @b2.handler
        def on_b2():
            self.spawn_requested = True

        @din.handler
        def on_din():
            self.reset_requested = True

    def get_bit(self, arr, index):
        """Get the value of the bit at the nth position in a bytearray

        Bytes are stored most significant bit first, so the 8th bit of [1] comes immediately after
        the first bit of [0]:
            [ B0b7 B0b6 B0b5 B0b4 B0b3 B0b2 B0b1 B0b0 B1b7 B1b6 ... ]
        """
        mask = 1 << ((8-index-1) % 8)
        byte = arr[index // 8]
        bit = 1 if byte & mask else 0
        return bit

    def set_bit(self, arr, index, value):
        """Set the bit at the nth position in a bytearray

        Bytes are stored most significant bit first
        """
        byte = arr[index // 8]
        mask = 1 << ((8-index-1) % 8)
        if value:
            byte = byte | mask
        else:
            byte = byte & ~mask
        arr[index // 8] = byte

    def random_spawn(self, fill_level):
        """Randomly spawn cells on the field

        The probablility of any space being set to True is equal to fill_level

        @param fill_level  A [0, 1] value indicating the odds of any space being filled
        """
        for i in range(OLED_WIDTH * OLED_HEIGHT):
            x = random.random()
            # if the space isn't already filled and we want to fill it...
            if x < fill_level and not self.get_bit(self.field, i):
                self.set_bit(self.field, i, True)
                self.set_bit(self.next_field, i, True)
                self.num_alive = self.num_alive + 1
                neighbourhood = self.get_neigbour_indices(i)
                self.changed_spaces.add(i)
                for n in neighbourhood:
                    self.changed_spaces.add(n)

    def reset(self):
        for i in range(len(self.field)):
            self.field[i] = 0x00
            self.next_field[i] = 0x00

        self.num_alive = 0
        self.random_spawn(self.calculate_spawn_level())

    def draw(self):
        oled.blit(self.frame, 0, 0)
        oled.show()

    def get_neigbour_indices(self, index):
        """Get the indices of the 8 bits adjacent to the given index
        """
        row = index // OLED_WIDTH
        col = index % OLED_WIDTH

        neighbours = []
        if row > 0:
            neighbours.append((row-1)*OLED_WIDTH + col)
            if col > 0:
                neighbours.append((row-1)*OLED_WIDTH + col -1)
            if col < OLED_WIDTH -1:
                neighbours.append((row-1)*OLED_WIDTH + col +1)

        if row < OLED_HEIGHT -1:
            neighbours.append((row+1)*OLED_WIDTH + col)
            if col > 0:
                neighbours.append((row+1)*OLED_WIDTH + col -1)
            if col < OLED_WIDTH -1:
                neighbours.append((row+1)*OLED_WIDTH + col +1)

        if col > 0:
            neighbours.append(row*OLED_WIDTH + col -1)

        if col < OLED_WIDTH - 1:
            neighbours.append(row*OLED_WIDTH + col +1)

        return neighbours

    def tick(self):
        self.num_born = 0
        self.num_died = 0

        if self.reset_requested:
            self.reset_requested = False
            self.reset()

        new_changes = set()
        for bit_index in self.changed_spaces:
            neighbours = self.get_neigbour_indices(bit_index)
            num_neighbours = 0
            for n in neighbours:
                if self.get_bit(self.field, n):
                    num_neighbours = num_neighbours + 1

            if self.get_bit(self.field, bit_index):
                if num_neighbours == 2 or num_neighbours == 3:        # happy cell, stays alive
                    self.set_bit(self.next_field, bit_index, True)
                else:                                                 # sad cell, dies
                    self.set_bit(self.next_field, bit_index, False)
                    self.num_died = self.num_died + 1
                    self.num_alive = self.num_alive - 1

                    new_changes.add(bit_index)
                    for n in neighbours:
                        new_changes.add(n)
            else:
                if num_neighbours == 3:                               # baby cell is born!
                    self.set_bit(self.next_field, bit_index, True)
                    self.num_alive = self.num_alive + 1
                    self.num_born = self.num_born + 1

                    new_changes.add(bit_index)
                    for n in neighbours:
                        new_changes.add(n)
                else:                                                 # empty space remains empty
                    self.set_bit(self.next_field, bit_index, False)

        # swap field & next_field so we don't need to copy between arrays
        tmp = self.next_field
        self.next_field = self.field
        self.field = tmp

        tmp = self.next_frame
        self.next_frame = self.frame
        self.frame = tmp

        # If a random spawning was requested, do it here, after calculating the normal generational growth
        if self.spawn_requested:
            self.spawn_requested = False
            self.random_spawn(self.calculate_spawn_level())

        self.changed_spaces = new_changes

    def calculate_spawn_level(self):
        """Calculate what percentage of the field should contain new cells
        """
        base_spawn_level = k1.percent()

        # get the level of AIN, attenuverted by K2
        cv_mod = ain.percent()
        cv_att = k2.percent() * 2 - 1
        cv_mod = cv_mod * cv_att

        spawn_level = clamp(base_spawn_level + cv_mod, 0, 1)
        return spawn_level

    def main(self):
        # turn off all CVs initially
        turn_off_all_cvs()

        # If less than 5% of the field is changing states we may have achieved some kind of statis
        stasis_threshold = 0.05

        fill_level = k1.percent()
        self.random_spawn(self.calculate_spawn_level())

        while True:
            # turn off the stasis gate while we calculate the next generation
            cv6.voltage(0)

            previous_generation = self.num_alive

            self.tick()
            self.draw()

            cv1.voltage(MAX_OUTPUT_VOLTAGE * self.num_alive / (OLED_WIDTH * OLED_HEIGHT))
            cv2.voltage(MAX_OUTPUT_VOLTAGE * self.num_born / self.num_alive)
            cv3.voltage(MAX_OUTPUT_VOLTAGE * self.num_died / self.num_alive)

            cv4.voltage(5 if self.num_born > self.num_died else 0)
            cv5.voltage(5 if self.num_born < self.num_died else 0)

            # If we've achieved statis, set CV6
            if len(self.changed_spaces) == 0 or (
                len(self.changed_spaces) / (OLED_WIDTH * OLED_HEIGHT) < stasis_threshold and self.num_born == self.num_died
            ):
                cv6.voltage(5)

if __name__ == "__main__":
    Conway().main()
