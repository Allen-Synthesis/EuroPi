# Copyright 2025 Allen Synthesis
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
Open Sound Control over UDP implementation.

See
- https://opensoundcontrol.stanford.edu/
- https://hexler.net/touchosc/manual/introduction
"""

from europi_log import *
import socket
import struct

import europi


def align_next_word(n):
    """
    Return the index of the next word-alined byte

    We assume 4-byte/32-bit words. If we're already word-aligned,
    we increment to the next one

    @param n  The current index in a byte array
    """
    return n + (4 - (n % 4)) % 4


class OpenSoundPacket:
    """
    A container object for the Open Sound Control packet(s) we receive.

    Contains the address of the message and the data

    @property address  The address string of the packet
    @property values  The values included in the packet
    """

    def __init__(self, data: bytes):
        """
        Read the raw packet and create this container

        The raw data consists of the following fields:
            1. leading '/' character
            2. slash-separated address (e.g. foo/bar)
            3. null terminator (0x00 byte)
            4. ',' character
            5. type arguments
                a. "f" character for 32-bit float
                b. "i" character for 32-bit signed integer
                c. "s" character for string (null-terminated)
                d. "b" character for blob (32-bit int -> n, followed by n bytes of data)
                e. assorted non-standard types
            6. null terminator(s)
            7. payload bytes (lengths are type dependent)

        Every argument starts on an 4-aligned byte, so there are
        filler nulls to pad strings out to a multiple of 32 bits

        @param data  The raw byte data read from the UDP socket
        """
        address_end = data.index(b"\0", 1)
        self._address = data[0:address_end].decode("utf-8")
        if self._address.endswith("/"):
            self._address = self._address.rstrip("/")

        types = []
        self._values = []
        type_start = data.index(b",", address_end)
        data_start = data.index(b"\0", type_start)
        data_start = align_next_word(data_start)
        i = type_start + 1
        d = data_start
        while data[i] != 0x00:
            t = chr(data[i])
            if t == "i":
                types.append(int)
                n = (data[d] << 24) | (data[d + 1] << 16) | (data[d + 2] << 8) | data[d + 1]
                self.values.append(n)
                d += 4
            elif t == "f":
                types.append(float)
                n = struct.unpack(">f", data[d : d + 4])[0]
                self.values.append(n)
                d += 4
            elif t == "s" or t == "S":  # include the alternate "S" here
                types.append(str)
                s = ""
                string_end = data.index(b"\0", d)
                for c in range(d, string_end):
                    s += chr(data[c])
                self.values.append(s)
                d = string_end
                d = align_next_word(d)
            elif t == "b":
                # blob; int32 -> n, followed by n bytes
                types.append(bytearray)
                n = (data[d] << 24) | (data[d + 1] << 16) | (data[d + 2] << 8) | data[d + 1]
                d += 4
                b = []
                for i in range(n):
                    b.append(data[d + i])
                d += n
                d = align_next_word(d)
                self.values.append(bytearray(b))
            elif t == "T" or t == "F":
                # zero-byte boolean; skip
                pass
            elif t == "t":
                # 8-byte timestamp; skip
                d += 8
            elif t == "h":
                # 64-bit signed integer
                # treat as a normal int
                types.append(int)
                n = (
                    (data[d] << 56)
                    | (data[d + 1] << 48)
                    | (data[d + 2] << 40)
                    | (data[d + 3] << 32)
                    | (data[d + 4] << 24)
                    | (data[d + 5] << 16)
                    | (data[d + 6] << 8)
                    | data[d + 7]
                )
                self.values.append(n)
                d += 8
            elif t == "c":
                # a single character; treat as a string
                types.append(str)
                self.values.append(
                    data[d + 3].decode()  # data is in the 4th byte; padded with leading zeros
                )
                d += 4
            elif t == "m":
                # 4-byte midi; skip
                d += 4
            elif t == "N":
                # nil; skip
                pass
            elif t == "I":
                # infinity; skip
                pass
            else:
                log_warning(f"Unsupported type {t}", "osc")

            i += 1

    @property
    def values(self) -> list[int | float | str | bytearray]:
        """
        The array of values included in this packet

        We support OSC 1.0 + a subset of 1.1 types
        """
        return self._values

    @property
    def address(self) -> str:
        """This packet's address"""
        return self._address


class OpenSoundServer:
    """
    The OSC server.

    This object owns the socket and is responsible for sending & receiving
    messages

    To use, instantiate the server and assign a callback. Then call
    receive_data() in the main loop:

    ```python
    import europi

    def main():
        srv = OpenSoundServer(9000)

        @srv.data_handler
        def process_data(connection=None, data=None):
            # process the data, send anything back over the connection if needed
            ...

        while True:
            srv.receive_data()
    ```
    """

    def __init__(self, recv_port=9000, send_port=9001, send_addr="192.168.4.100"):
        """
        Create the OSC server

        TouchOSC uses port 9000 by default, so use that here for convenience

        @param port  The UDP port we accept messages on.
        """
        log_info(f"Listening for OSC packets on port {recv_port}", "osc")
        addr = socket.getaddrinfo("0.0.0.0", recv_port)[0][-1]
        self.recv_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.recv_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.recv_socket.settimeout(0)
        self.recv_socket.bind(addr)

        log_info(f"Sending OSC packets to {send_addr}:{send_port}", "osc")
        addr = socket.getaddrinfo(send_addr, send_port)[0][-1]
        self.send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.send_port = send_port
        self.send_addr = send_addr

        self.recv_callback = self.default_callback

    def default_callback(self, connection=None, data: OpenSoundPacket = None):
        """
        Default callback function when we receive data

        Does nothing
        """
        pass

    def data_handler(self, func):
        """
        Decorator for the function to UDP packet reception

        The provided function must accept the following keyword arguments:
        - connection: socket  A socket connection to the client
        - data: str  The request the client sent

        @param func  The function to handle the request.
        """

        def wrapper(*args, **kwargs):
            func(*args, **kwargs)

        self.recv_callback = wrapper
        return wrapper

    def receive_data(self):
        """Check if we have any new data to process, invoke data_handler as needed"""
        while True:
            try:
                (data, connection) = self.recv_socket.recvfrom(1024)
                packet = OpenSoundPacket(data)
                self.recv_callback(connection=connection, data=packet)
            except ValueError as err:
                log_warning(f"Failed to process packet: {err}", "osc")
                break
            except OSError as err:
                break
            except Exception as err:
                # log_warning(f"Failed to process packet. Malformed? {err}", "osc")
                # s = ""
                # for byte in data:
                #     s += f"{byte:02x} "
                # log_debug(f"Raw packet: {s}")
                break

    def send_data(self, address, *args):
        """
        Transmit a packet

        @param address  The OSC address to send to
        @param args  The values to encode in the packet. Allowed types are
                     int, float, bool, str, and bytearray.
                     Bools are converted to 0/1 integers
        """

        def pad_length(arr):
            # pad with nulls until we get to the next multiple of 4
            for i in range((4 - (len(arr) % 4)) % 4):
                arr.append(0)

        data = []
        for ch in address:
            data.append(ord(ch))
        data.append(0)
        pad_length(data)

        # comma denoting start of types
        data.append(ord(","))

        # types
        for arg in args:
            if type(arg) is int or type(arg) is bool:
                data.append(ord("i"))
            elif type(arg) is float:
                data.append(ord("f"))
            elif type(arg) is str:
                data.append(ord("s"))
            elif type(arg) is bytearray:
                data.append(ord("b"))
        data.append(0)
        pad_length(data)

        # values
        for arg in args:
            if type(arg) is int:
                # big-endian, 32-bit int
                data.append((arg >> 24) & 0xFF)
                data.append((arg >> 16) & 0xFF)
                data.append((arg >> 8) & 0xFF)
                data.append(arg & 0xFF)
            elif type(arg) is bool:
                # treat boolean as a 0/1 integer for convenience
                if arg:
                    data.append(0)
                    data.append(0)
                    data.append(0)
                    data.append(1)
                else:
                    data.append(0)
                    data.append(0)
                    data.append(0)
                    data.append(0)
            elif type(arg) is float:
                bytes = struct.pack(">f", arg)
                for b in bytes:
                    data.append(b)
            elif type(arg) is str:
                for ch in arg:
                    data.append(ord(ch))
                data.append(0)
                pad_length(data)
            elif type(arg) is bytearray:
                n = len(arg)
                data.append((n >> 24) & 0xFF)
                data.append((n >> 16) & 0xFF)
                data.append((n >> 8) & 0xFF)
                data.append(n & 0xFF)
                for b in arg:
                    data.append(b)
                pad_length(data)

        try:
            data = bytearray(data)
            self.send_socket.sendto(data, (self.send_addr, self.send_port))
        except OSError:
            pass
        except Exception as err:
            log_warning(f"Failed to send OSC data: {err}", "osc")
