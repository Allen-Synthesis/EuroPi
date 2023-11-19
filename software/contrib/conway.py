#!/usr/bin/env python3
"""Implements Conway's Game of Life as a pseudo-random LFO kernel

Outputs 1-3 are 0-10V control voltages, outputs 4-6 are 5V gates

@author Chris I-B <ve4cib@gmail.com>
@year   2023

Throughout the program we frequently use `>> 3` instead of `//8` for doing integer division when converting
from bit indices to byte indices.
"""

from europi import *
from europi_script import EuroPiScript
from random import random as rnd

def clamp(x, low, hi):
    """Clamp a value to lie between low and hi
    """
    if x < low:
        return low
    elif x > hi:
        return hi
    else:
        return x

def get_bit(arr, index):
    """Get the value of the bit at the nth position in a bytearray

    Bytes are stored most significant bit first, so the 8th bit of [1] comes immediately after
    the first bit of [0]:
        [ B0b7 B0b6 B0b5 B0b4 B0b3 B0b2 B0b1 B0b0 B1b7 B1b6 ... ]
    """
    mask = 1 << ((8-index-1) % 8)
    byte = arr[index >> 3]
    bit = 1 if byte & mask else 0
    return bit

def set_bit(arr, index, value):
    """Set the bit at the nth position in a bytearray

    Bytes are stored most significant bit first, so the 8th bit of [1] comes immediately after
    the first bit of [0]:
        [ B0b7 B0b6 B0b5 B0b4 B0b3 B0b2 B0b1 B0b0 B1b7 B1b6 ... ]
    """
    byte = arr[index >> 3]
    mask = 1 << ((8-index-1) % 8)
    if value:
        byte = byte | mask
    else:
        byte = byte & ~mask
    arr[index >> 3] = byte

def stdev(l):
    """Return the standard deviation of a list of values

    @param l  The list of numbers we want to calculate the standard deviation of

    @return The standard deviation of the values in @l
    """
    mean = sum(l)/len(l)
    return ( sum([((x - mean) ** 2) for x in l]) / len(l) )**0.5

# How many pixels are on the screen
NUM_PIXELS = OLED_HEIGHT * OLED_WIDTH

# How many volts are our gate outputs?
GATE_VOLTAGE = 5

class Conway(EuroPiScript):
    def __init__(self):
        # For ease of blitting, store the field as a bit array
        # Each byte is 8 horizontally adjacent pixels, with the most significant bit
        # on the left
        self.field = bytearray(NUM_PIXELS >> 3)
        self.next_field = bytearray(NUM_PIXELS >> 3)

        # Keep 2 separate frame buffer instances so we don't need to recreate the FB objects when we draw
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

        # Set to True if we want to clear the field & respawn
        self.reset_requested = False

        # keep the last few changes in population in a list to check if it's oscillating predictably
        self.population_deltas = []
        self.MAX_DELTAS = 12

        @b1.handler
        def on_b1():
            self.reset_requested = True

        @b2.handler
        def on_b2():
            self.reset_requested = True

        @din.handler
        def on_din():
            self.reset_requested = True

    def get_neigbour_indices(self, index):
        """Get the indices of the 8 bits adjacent to the given index

        If we're on the top/left/bottom/right edge, wrap arround to the opposite row/column, treating the world
        as a torus

        Unfortunately we don't have enough RAM to save this in a lookup table, so we have to recalculate it
        every time, which slows down the simulation
        """
        row = index // OLED_WIDTH
        col = index % OLED_WIDTH

        def rowcol2index(r, c):
            return (r % OLED_HEIGHT) * OLED_WIDTH + (c % OLED_WIDTH)

        neighbours = []

        for i in range(-1, 2):
            for j in range(-1, 2):
                if i != 0 or j != 0:
                    neighbours.append(rowcol2index(row+i, col+j))

        return neighbours

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

    def random_spawn(self, fill_level):
        """Randomly spawn cells on the field

        The probablility of any space being set to True is equal to fill_level

        @param fill_level  A [0, 1] value indicating the odds of any space being filled
        """
        for i in range(NUM_PIXELS):
            x = rnd()
            # if the space isn't already filled and we want to fill it...
            if x < fill_level and not get_bit(self.field, i):
                set_bit(self.field, i, True)
                set_bit(self.next_field, i, True)
                self.num_alive = self.num_alive + 1
                self.changed_spaces.add(i)
                neighbourhood = self.get_neigbour_indices(i)
                for n in neighbourhood:
                    self.changed_spaces.add(n)

    def reset(self):
        """Clear the whole field and spawn random data in it
        """
        for i in range(len(self.field)):
            self.field[i] = 0x00
            self.next_field[i] = 0x00

        self.num_alive = 0
        self.population_deltas = []
        self.random_spawn(self.calculate_spawn_level())

    def draw(self):
        """Show the current playing field on the OLED
        """
        oled.blit(self.frame, 0, 0)
        oled.show()

    def tick(self):
        """Calculate the state of the next generation

        This checks the regions around every changed space in the previous generation, updating the
        total population and counting how many births & deaths this generation had.

        If a reset was requested, the field is cleared & randomly reset _before_ calculating the new generation
        """
        self.num_born = 0
        self.num_died = 0

        if self.reset_requested:
            self.reset_requested = False
            self.reset()

        new_changes = set()
        for bit_index in self.changed_spaces:
            neighbourhood = self.get_neigbour_indices(bit_index)
            num_neighbours = 0
            for n in neighbourhood:
                if get_bit(self.field, n):
                    num_neighbours = num_neighbours + 1

            if get_bit(self.field, bit_index):
                if num_neighbours == 2 or num_neighbours == 3:        # happy cell, stays alive
                    set_bit(self.next_field, bit_index, True)
                else:                                                 # sad cell, dies
                    set_bit(self.next_field, bit_index, False)
                    self.num_died = self.num_died + 1
                    self.num_alive = self.num_alive - 1

                    new_changes.add(bit_index)
                    for n in neighbourhood:
                        new_changes.add(n)
            else:
                if num_neighbours == 3:                               # baby cell is born!
                    set_bit(self.next_field, bit_index, True)
                    self.num_alive = self.num_alive + 1
                    self.num_born = self.num_born + 1

                    new_changes.add(bit_index)
                    for n in neighbourhood:
                        new_changes.add(n)
                else:                                                 # empty space remains empty
                    set_bit(self.next_field, bit_index, False)

        # swap field & next_field so we don't need to copy between arrays
        tmp = self.next_field
        self.next_field = self.field
        self.field = tmp

        tmp = self.next_frame
        self.next_frame = self.frame
        self.frame = tmp

        self.changed_spaces = new_changes

    def check_for_stasis(self):
        """Check the population changes over time to see if we've reached a state of stasis
        """
        # we must have at least MAX_DELTAS generations of data
        if len(self.population_deltas) < self.MAX_DELTAS:
            return False

        # if there are no changes, we've reached static stasis
        if len(self.changed_spaces) == 0:
            return True

        # if the population is oscillating up and down predicatbly, we've probably reached stasis
        # check for 2, 3, and 4 step repetitions
        for pattern_length in range(2, 5):
            sums = []
            for i in range(self.MAX_DELTAS // pattern_length):
                sums.append(sum(self.population_deltas[i*pattern_length:i*pattern_length+pattern_length]))

            # check the standard deviation
            deviation = stdev(sums)
            if deviation <= 1:
                return True

        return False


    def main(self):
        """The main loop for the program

        Handles setting the CV output, drawing to the OLED, and triggering the simulation
        """
        turn_off_all_cvs()
        self.random_spawn(self.calculate_spawn_level())

        in_stasis = False

        while True:
            # turn off the stasis gate while we calculate the next generation
            cv6.voltage(0)

            # turn on the FPS gate when we start calculating
            cv4.voltage(GATE_VOLTAGE)

            # calculate the next generation
            self.tick()

            # turn off the FPS gate when we're done calculating but before we draw
            cv4.voltage(0)

            # show the results on the OLED
            self.draw()

            # check for stasis consitions
            self.population_deltas.append(self.num_born - self.num_died)
            if len(self.population_deltas) > self.MAX_DELTAS:
                self.population_deltas.pop(0)
            in_stasis = self.check_for_stasis()

            cv1.voltage(MAX_OUTPUT_VOLTAGE * self.num_alive / (NUM_PIXELS))
            cv2.voltage(MAX_OUTPUT_VOLTAGE * self.num_born / self.num_alive)
            cv3.voltage(MAX_OUTPUT_VOLTAGE * self.num_died / self.num_alive)
            cv5.voltage(GATE_VOLTAGE if self.num_born > self.num_died else 0)

            # If we've achieved statis, set CV6
            if in_stasis:
                cv6.voltage(GATE_VOLTAGE)

if __name__ == "__main__":
    Conway().main()
