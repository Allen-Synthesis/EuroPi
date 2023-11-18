#!/usr/bin/env python3
"""Implements Conway's Game of Life as a pseudo-random LFO kernel
"""

from europi import *
from europi_script import EuroPiScript

import random

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
        # Initially assume everything's changed
        self.changed_spaces = set(list(range(OLED_HEIGHT * OLED_WIDTH)))

        # how many cells were born this tick?
        self.num_born = 0

        # how many cells died this tick?
        self.num_died = 0

        # we want to reshuffle immediately when main() starts
        self.reshuffle = False

        # Have we received a tick on DIN or B2?
        self.tick_recvd = False

        # how many cells are currently alive?
        # this gets updated on every tick
        self.num_alive = 0

        @b1.handler
        def on_b1():
            self.reshuffle = True

        @b2.handler
        def on_b2():
            self.tick_recvd = True

        @din.handler
        def on_din():
            self.tick_recvd = True

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

    def randomize(self):
        self.reshuffle = False

        self.num_born = 0
        self.num_died = 0

        self.changed_spaces = set(list(range(OLED_HEIGHT * OLED_WIDTH)))

        fill_level = k1.percent()
        for row in range(OLED_HEIGHT):
            for col in range(OLED_WIDTH):
                x = random.random()
                self.set_bit(self.field, row * OLED_WIDTH + col, x < fill_level)

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
        self.tick_recvd = False

        self.num_alive = 0
        self.num_born = 0
        self.num_died = 0

        new_changes = set()
        for bit_index in self.changed_spaces:
            neighbours = self.get_neigbour_indices(bit_index)
            num_neighbours = 0
            for n in neighbours:
                if self.get_bit(self.field, n):
                    num_neighbours = num_neighbours + 1

            if self.get_bit(self.field, bit_index):
                if num_neighbours == 2 or num_neighbours == 3:   # happy cell, stays alive
                    self.set_bit(self.next_field, bit_index, True)
                    self.num_alive = self.num_alive + 1
                else:                                    # sad cell, dies
                    self.set_bit(self.next_field, bit_index, False)
                    self.num_died = self.num_died + 1

                    new_changes.add(bit_index)
                    for n in neighbours:
                        new_changes.add(n)
            else:
                if num_neighbours == 3:                      # baby cell is born!
                    self.set_bit(self.next_field, bit_index, True)
                    self.num_alive = self.num_alive + 1
                    self.num_born = self.num_born + 1

                    new_changes.add(bit_index)
                    for n in neighbours:
                        new_changes.add(n)
                else:                                    # empty space remains empty
                    self.set_bit(self.next_field, bit_index, False)

        # TODO: add random additional new cells according to AIN & K2

        # swap field & next_field so we don't need to copy between arrays
        tmp = self.next_field
        self.next_field = self.field
        self.field = tmp

        tmp = self.next_frame
        self.next_frame = self.frame
        self.frame = tmp

        self.changed_spaces = new_changes

    def main(self):
        # turn off all CVs initially
        turn_off_all_cvs()

        self.randomize()

        while True:
            cv6.voltage(5)
            if self.reshuffle:
                self.randomize()
            else:
                self.tick()

            cv6.voltage(0)
            self.draw()
            cv1.voltage(MAX_OUTPUT_VOLTAGE * self.num_alive / (OLED_WIDTH * OLED_HEIGHT))

            cv4.voltage(5 if self.num_born > self.num_died else 0)
            cv5.voltage(5 if self.num_born < self.num_died else 0)

if __name__ == "__main__":
    Conway().main()
