#!/usr/bin/env python3
"""Assorted mathematical and statistical functions that can be re-used across scripts

Intended to augment Python's standard math library with additional useful functions
"""


def median(l):
    """Calculate the median value from an array

    This is a cheater median, as we always choose the lower value if the length is even instead of
    averaging the middle two values. This is faster, but mathematically incorrect.

    @param l  An iterable collection of numbers
    @return  The median value from the list, or 0 if the list is empty
    """
    if len(l) == 0:
        return 0
    arr = [i for i in l]
    arr.sort()
    return arr[len(arr) // 2]


def mean(l):
    """Calculate the mean value from an array

    @param l  An iterable collection of numbers
    @return  The mean value of the list, or 0 of the list is empty
    """
    if len(l) == 0:
        return 0
    return sum(l) / len(l)


def rescale(x, old_min, old_max, new_min, new_max, clip=True):
    """
    Convert x in [old_min, old_max] -> y in [new_min, new_max] using linear interpolation

    @param x  The value to convert
    @param old_min  The old (inclusive) minimum
    @param old_max  The old (inclusive) maximum
    @param new_min  The new (inclusive) minimum
    @param new_max  The new (inclusive) maximum
    @param clip     If true, we clip values within the [min, max] range; otherwise we extrapolate based on the ranges
    """
    if clip and x < old_min:
        return new_min
    elif clip and x > old_max:
        return new_max
    else:
        return (x - old_min) * (new_max - new_min) / (old_max - old_min) + new_min
