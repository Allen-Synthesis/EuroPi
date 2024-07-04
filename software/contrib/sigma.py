#!/usr/bin/env python3
"""Gaussian-based, clocked, quantized CV generator

Inspired by Magnetic Freak's Gaussian module.

@author  Chris Iverach-Brereton
@year    2024
"""

from europi import *
from europi_script import EuroPiScript

from experimental.random_extras import normal

def bisect_left(a, x, lo=0, hi=None, *, key=None):
    """Return the index where to insert item x in list a, assuming a is sorted.

    The return value i is such that all e in a[:i] have e < x, and all e in
    a[i:] have e >= x.  So if x already appears in the list, a.insert(i, x) will
    insert just before the leftmost x already there.

    Optional args lo (default 0) and hi (default len(a)) bound the
    slice of a to be searched.

    A custom key function can be supplied to customize the sort order.

    Copied from https://github.com/python/cpython/blob/3.12/Lib/bisect.py
    """

    if lo < 0:
        raise ValueError('lo must be non-negative')
    if hi is None:
        hi = len(a)
    # Note, the comparison uses "<" to match the
    # __lt__() logic in list.sort() and in heapq.
    if key is None:
        while lo < hi:
            mid = (lo + hi) // 2
            if a[mid] < x:
                lo = mid + 1
            else:
                hi = mid
    else:
        while lo < hi:
            mid = (lo + hi) // 2
            if key(a[mid]) < x:
                lo = mid + 1
            else:
                hi = mid
    return lo


class VoltageBin:
    """Quantizes a random voltage to the closest bin"""
    def __init__(self, name, bins):
        """Create a new set of bins

        @param name  The human-readable display name for this set of bins
        @param bins  A list of voltages we are allowed to output
        """
        self.name = name
        self.bins = [float(b) for b in bins]
        self.bins.sort()

    def __str__(self):
        return self.name

    def closest(self, v):
        """Quantize an input voltage to the closest bin. If two bins are equally close, choose the lower one.

        Our internal bins are sorted, so we can do a binary search for that sweet, sweet O(log(n)) efficiency

        @param v  A voltage in the range 0-10 to quantize
        @return   The closest voltage bin to @v
        """
        i = bisect_left(self.bins, v)
        if i == 0:
            return self.bins[0]
        if i == len(self.bins):
            return self.bins[-1]
        prev = self.bins[i - 1]
        next = self.bins[i + 1]
        if abs(v - next) < abs(v - prev):
            return next
        else:
            return prev


class Sigma(EuroPiScript):
    """The main class for this script

    Handles all I/O, renders the UI
    """

    ## Voltage bins for bin mode
    voltage_bins = [
        VoltageBin("Bin 2", [0, 10]),
        VoltageBin("Bin 3", [0, 5, 10]),
        VoltageBin("Bin 6", [0, 2, 4, 6, 8, 10]),
        VoltageBin("Bin 7", [0, 1.7, 3.4, 5, 6.6, 8.3, 10]),
        VoltageBin("Bin 9", [0, 1.25, 2.5, 3.75, 5, 6.25, 7.5, 8.75, 10])
    ]

    def __init__(self):
        super().__init__()

    def main(self):
        while True:
            pass

if __name__ == "__main__":
    Sigma().main()
