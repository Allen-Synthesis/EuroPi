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
"""Support functions to allow using a bytearray as a bit array.

Micropython doesn't appear to have a native bitarray implementation, so this
module serves as a loose framework on top of the bytearray object to allow
easier bit-level access.
"""


def make_bit_array(length):
    """Create a bit array that contains at least @length bits

    The resulting byte array will have a length rounded up to the
    next byte if @length is not divisible by 8

    @param length  The number of bits in the array

    @return A bytearray containing at least @length bits
    """
    # Use bitwise operations instead of integer division and modulo operations to keep things fast
    if length & 0x07:
        byte_length = (length >> 3) + 1
    else:
        byte_length = length >> 3
    return bytearray(byte_length)


def get_bit(arr, index):
    """Get the value of the bit at the nth position in a bytearray

    Bytes are stored most significant bit first, so the 8th bit of [1] comes immediately after
    the first bit of [0]:
        [ B0b7 B0b6 B0b5 B0b4 B0b3 B0b2 B0b1 B0b0 B1b7 B1b6 ... ]

    @param arr    The bytearray to operate on
    @param index  The bit index to retrieve

    @return 0 or 1, depending on the state at position @index
    """
    # Use bitwise operations instead of integer division and modulo operations to keep things fast
    byte = arr[index >> 3]
    mask = 1 << ((8 - index - 1) & 0x07)
    bit = 1 if byte & mask else 0
    return bit


def set_bit(arr, index, value):
    """Set the bit at the nth position in a bytearray

    Bytes are stored most significant bit first, so the 8th bit of [1] comes immediately after
    the first bit of [0]:
        [ B0b7 B0b6 B0b5 B0b4 B0b3 B0b2 B0b1 B0b0 B1b7 B1b6 ... ]

    @param arr    The bytearray to operate on
    @param index  The bit position within the array
    @param value  A truthy value indicating whether the bit should be set to 1 or 0
    """
    # Use bitwise operations instead of integer division and modulo operations to keep things fast
    byte = arr[index >> 3]
    mask = 1 << ((8 - index - 1) & 0x07)
    if value:
        byte = byte | mask
    else:
        byte = byte & ~mask
    arr[index >> 3] = byte


def set_all_bits(arr, value=0):
    """Set all bits in the array to the same value

    @param arr    The bytearray to reset
    @param value  A truthy value indicating whether all bits should be set to 0 or 1
    """
    for i in range(len(arr)):
        if value:
            arr[i] = 0xFF
        else:
            arr[i] = 0x00
