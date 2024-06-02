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
