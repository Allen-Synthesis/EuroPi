#!/usr/bin/env python3
"""
Additional random functions that are part of standard Python3's random module
but are omitted from MicroPython's implementation

Specifically _not_ called "random.py" to prevent clobbering the standard random import
in other experimental libraries
"""

from math import log, sqrt
import random


def normal(mean=0.0, stdev=1.0):
    """
    Generate a random number with a normal distribution

    Uses the Marsaglia-Tsang algorithm, which isn't a perfectly normal
    distribution, but is likely close enough for EuroPi applications

    @param mean   The desired mean for the distribution
    @param stdev  The standard deviation of the distribution

    @return A floating-point number chosen from a normal distribution with the
            given mean and standard deviation
    """
    x = 0.0
    y = 0.0
    z = 0.0
    while True:
        x = random.random() * 2.0 - 1.0
        y = random.random() * 2.0 - 1.0
        z = x**2 + y**2

        if 0 < z and z <= 1.0:
            break

    q = sqrt(-2.0 * log(z) / z)
    return mean + stdev * x * q


def shuffle(l):
    """
    Re-order the elements of a list in-situ

    @param l  The list to shuffle
    """
    for i in range(len(l)):
        n = random.randint(i, len(l) - 1)
        tmp = l[i]
        l[i] = l[n]
        l[n] = tmp
