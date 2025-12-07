#!/usr/bin/env python3
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
Desktop-side client for the Music Thing Modular 8mu for EuroPi

This script is intended to be run on a desktop/laptop computer to provide an
interface between 8mu and EuroPi.

EuroPi must be running the `OSC Interface` program.

Prerequisites:
- python-rtmidi and mido, installed with pip
"""

import argparse
import mido
import re
import socket
import struct
import threading
import time


class MusicThing8muToEuroPi:
    """The main interface class between 8mu and EuroPi"""

    # regex to help identify what midi device we want to open
    music_thing_midi_name_re = re.compile(r".*Music Thing m0 Plus.*")

    # regex for validating IPv4 addresses
    ipv4_re = re.compile(r"^((25[0-5]|(2[0-4]|1\d|[1-9]|)\d)\.?\b){4}$")

    def __init__(
        self,
        europi_ip: str,
        osc_port: int,
        europi_namespace: str,
        controls: dict[int, int],
        scale: float = 1.0,
        debug: bool = False,
    ):
        """
        Create the interface between 8mu and EuroPi

        @param europi_ip  EuroPi's IP address (must be accessible from the computer
                          you're running this script on)
        @param osc_port  The UDP port we're going to use to send data to EuroPi on
        @param europi_namespace  The OSC namespace that the destination EuroPi is using
        @param controls  A dict that maps MIDI controls to CV1-6
        @param debug  Enable additional debugging output

        @exception ValueError if port is out of range, or IP address is invalid
        @exception FileNotFoundError if the 8mu was not found in the MIDI inputs
        """
        self.debug = debug

        if osc_port < 0 or osc_port > 65535:
            raise ValueError(f"Port number {osc_port} is out of range")
        if not re.match(self.ipv4_re, europi_ip):
            raise ValueError(f"Invalid IP address {europi_ip}")

        self.osc_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.osc_port = osc_port
        self.europi_ip = europi_ip
        self.europi_namespace = europi_namespace.strip().rstrip("/")

        self.scale = scale
        self.controls = controls

        self.midi_readings_lock = threading.Lock()
        self.midi_readings = {}

        if not self.europi_namespace.startswith("/"):
            self.europi_namespace = f"/{self.europi_namespace}"

        inputs = mido.get_input_names()
        self.midi_in = None
        for midi_in in inputs:
            if re.match(self.music_thing_midi_name_re, midi_in):
                self.midi_in = mido.open_input(midi_in)
                break

        if self.midi_in is None:
            raise FileNotFoundError("No compatible MIDI devices found")

        self.midi_in.callback = self.on_8mu_slider

    def on_8mu_slider(self, msg: mido.Message):
        if not msg.control in self.controls.keys():
            if self.debug:
                print(f"Ignoring message {msg}")
            return

        if self.debug:
            print(f"Processing message {msg}")

        cv_out = self.controls[msg.control]
        osc_value = msg.value / 127.0 * self.scale  # convert to 0-1 float
        address = f"{self.europi_namespace}/cv{cv_out}"

        self.midi_readings_lock.acquire()
        self.midi_readings[address] = osc_value
        self.midi_readings_lock.release()

    def encode_packet(self, address: str, value: float) -> bytearray:
        """
        Encode an OSC packet for transmission

        @param address  The OSC address to send to
        @param value  The value to send
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
        data.append(ord("f"))  # send as a float16
        data.append(0)
        pad_length(data)

        # value
        bytes = struct.pack(">f", value)
        for b in bytes:
            data.append(b)

        return bytearray(data)

    def spin(self):
        while True:
            time.sleep(0.01)

            packets = []
            self.midi_readings_lock.acquire()
            for address in self.midi_readings.keys():
                packets.append(self.encode_packet(address, self.midi_readings[address]))
            self.midi_readings_lock.release()

            # bundle header + all-zero timestamp
            bundle = "#bundle\0\0\0\0\0\0\0\0\0".encode("utf-8")
            for p in packets:
                bundle += len(p).to_bytes(length=4, byteorder="big")
                bundle += p

            try:
                if self.debug:
                    print(f"Sending bundle {bundle}")
                self.osc_socket.sendto(bundle, (self.europi_ip, self.osc_port))
            except Exception as err:
                print(err)


def main():
    parser = argparse.ArgumentParser(
        prog="osc_8mu",
        description="Music Thing Modular 8mu to OSC adapter (for EuroPi)",
        epilog="(c) 2025 Allen Synthesis",
    )
    parser.add_argument(
        "-p",
        "--port",
        dest="port",
        action="store",
        type=int,
        default=9000,
        help="The UDP port to send OSC packets on. Default: 9000",
    )
    parser.add_argument(
        "-n",
        "--namespace",
        dest="namespace",
        action="store",
        type=str,
        default="/europi",
        help="EuroPi's OSC namespace. Default: /europi",
    )
    parser.add_argument(
        "-i",
        "--ip",
        dest="ip_addr",
        action="store",
        type=str,
        default="192.168.4.1",
        help="EuroPi's IP address. Default: 192.168.4.1",
    )
    parser.add_argument(
        "-s",
        "--scale",
        dest="scale",
        action="store",
        type=float,
        default=1.0,
        help="MIDI to EuroPi scale factor. Default: 1.0",
    )
    parser.add_argument(
        "-d",
        "--debug",
        dest="debug",
        action="store_true",
        help="Enable additional debugging output",
    )

    # midi controls to EuroPi CVs
    parser.add_argument(
        "-1",
        "--cv1",
        dest="cv1",
        action="store",
        type=int,
        default=34,
        help="MIDI control to change CV1. Default: 34",
    )
    parser.add_argument(
        "-2",
        "--cv2",
        dest="cv2",
        action="store",
        type=int,
        default=35,
        help="MIDI control to change CV2. Default: 35",
    )
    parser.add_argument(
        "-3",
        "--cv3",
        dest="cv3",
        action="store",
        type=int,
        default=36,
        help="MIDI control to change CV3. Default: 36",
    )
    parser.add_argument(
        "-4",
        "--cv4",
        dest="cv4",
        action="store",
        type=int,
        default=37,
        help="MIDI control to change CV4. Default: 37",
    )
    parser.add_argument(
        "-5",
        "--cv5",
        dest="cv5",
        action="store",
        type=int,
        default=38,
        help="MIDI control to change CV5. Default: 38",
    )
    parser.add_argument(
        "-6",
        "--cv6",
        dest="cv6",
        action="store",
        type=int,
        default=39,
        help="MIDI control to change CV6. Default: 39",
    )

    args = parser.parse_args()

    print("Starting 8mu to OSC adapter...")

    mtm8mu = MusicThing8muToEuroPi(
        args.ip_addr,
        args.port,
        args.namespace,
        {
            args.cv1: 1,
            args.cv2: 2,
            args.cv3: 3,
            args.cv4: 4,
            args.cv5: 5,
            args.cv6: 6,
        },
        scale=args.scale,
        debug=args.debug,
    )

    print("Press CTRL+C to terminate")

    mtm8mu.spin()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Exiting")
