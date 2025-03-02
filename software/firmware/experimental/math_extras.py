#!/usr/bin/env python3
# Copyright 2024 Allen Synthesis
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Assorted mathematical and statistical functions that can be re-used across scripts

Intended to augment Python's standard math library with additional useful functions
"""


def prod(l):
    """
    Calculate the product of all items in a list

    Equivalent the Python3's math.prod

    @param l  An iterable collection of numbers
    @return  The product of all items in the list, or 0 if the list is empty
    """
    if len(l) == 0:
        return 0
    p = 1
    for n in l:
        p = p * n
    return p


def median(l):
    """
    Calculate the median value from an array

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
    """
    Calculate the arithmetic mean value from an array

    @param l  An iterable collection of numbers
    @return  The arithmetic mean of the list, or 0 of the list is empty
    """
    if len(l) == 0:
        return 0
    return sum(l) / len(l)


def geometric_mean(l):
    """
    Calculate the geometric mean value of an array

    @param l  An iterable collection of numbers
    @return  The geometric mean of the list, or 0 of the list is empty
    """
    if len(l) == 0:
        return 0
    return prod(l) ** (1.0 / len(l))


def harmonic_mean(l):
    """
    Calculate the harmonic mean value of an array

    @param l  An iterable collection of numbers
    @return  The harmonic mean of the list, or 0 of the list is empty
    """
    if len(l) == 0:
        return 0
    s = 0
    for n in l:
        s += 1.0 / n
    return len(l) / s


def mode(l):
    """
    Calculate the mode of an array

    The mode is the most-occurring item; if multiple items are tied,
    the median of the tied items is returned

    @param l  An iterable collection of numbers
    @return  The mode of the list, or 0 if the list is empty
    """
    if len(l) == 0:
        return 0
    counts = {}
    for n in l:
        if n in counts:
            counts[n] += 1
        else:
            counts[n] = 1

    max_count = 0
    tied_for_max = []
    for n in l:
        if counts[n] > max_count:
            max_count = counts[n]
            tied_for_max = [n]
        elif counts[n] == max_count:
            tied_for_max.append(n)

    if len(tied_for_max) == 1:
        return tied_for_max[0]
    else:
        tied_for_max.sort()
        return tied_for_max[len(tied_for_max) // 2]


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


def solve_linear_system(m):
    """
    Use gaussian elimination to solve a series of linear equations

    The provided matrix is the augmented matrix representation:
    [
        [k11 k12 k12 ... k1n  a1]
        [k21 k22 k22 ... k2n  a2]
        .
        .
        .
        [kmn kmn kmn ... kmn  am]
    ]

    @param m  The augmented matrix representation of the series of equations. This array is mangled in the process
              of calculation
    @return   A matrix of the coefficients of the equation
    """
    n_eqs = len(m)

    # sort the rows
    for i in range(n_eqs):
        for j in range(i + 1, n_eqs):
            if abs(m[i][i]) < abs(m[j][i]):
                # swap rows i and j with each other
                for k in range(n_eqs + 1):
                    tmp = m[j][k]
                    m[j][k] = m[i][k]
                    m[i][k] = tmp

    # gaussian elimination
    for i in range(n_eqs - 1):
        for j in range(i + 1, n_eqs):
            f = m[j][i] / m[i][i]
            for k in range(n_eqs + 1):
                m[j][k] = m[j][k] - f * m[i][k]

    # back substitution
    results = list(range(n_eqs))
    for i in range(n_eqs - 1, -1, -1):
        results[i] = m[i][n_eqs]
        for j in range(i + 1, n_eqs):
            if i != j:
                results[i] = results[i] - m[i][j] * results[j]
        results[i] = results[i] / m[i][i]

    return results
