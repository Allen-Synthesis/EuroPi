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
Interface program for using Open Sound Control to set CV levels

The following addresses & types are used:

- /europi/cv{1-6} float: set raw voltage (0-MAX_OUTPUT_VOLTAGE)
- /europi/cv{1-6} int: set gate on/off (treated as boolean)
- /europi/cvs : as above, but allows all outputs to be set at once

The application settings can be used to change the root namespace
"""

from europi import *
from europi_script import EuroPiScript

import configuration
from machine import Timer

from experimental.osc import *
import experimental.wifi

class OscControl(EuroPiScript):
    def __init__(self):
        super().__init__()

        self.server = OpenSoundServer(
            recv_port=self.config.RECV_PORT,
            send_port=self.config.SEND_PORT,
            send_addr=self.config.SEND_ADDR,
        )
        self.namespace = self.config.NAMESPACE
        if not self.namespace.startswith("/"):
            self.namespace = f"/{self.namespace}"
        if not self.namespace.endswith("/"):
            self.namespace = f"{self.namespace}/"

        self.ui_dirty = False

        @self.server.data_handler
        def on_data_recv(connection=None, data=None):
            if data.address == f"{self.namespace}cv1":
                self.set_cv(cv1, data)
            elif data.address == f"{self.namespace}cv2":
                self.set_cv(cv2, data)
            elif data.address == f"{self.namespace}cv3":
                self.set_cv(cv3, data)
            elif data.address == f"{self.namespace}cv4":
                self.set_cv(cv4, data)
            elif data.address == f"{self.namespace}cv5":
                self.set_cv(cv5, data)
            elif data.address == f"{self.namespace}cv6":
                self.set_cv(cv6, data)
            elif data.address == f"{self.namespace}cvs":
                # set all CVs at once
                self.set_cvs(data)

    def set_cv(self, cv_out, data):
        """
        Set the level for a single CV

        @param cv_out  CV1-6
        @param data  The OpenSoundPacket we're processing
        """
        if type(data.values[0]) is int:
            if data.values[0] == 0:
                cv_out.off()
            else:
                cv_out.on()
        elif type(data.values[0]) is float:
            cv_out.voltage(data.values[0] * europi_config.MAX_OUTPUT_VOLTAGE)
        self.ui_dirty = True

    def set_cvs(data):
        """
        Set the level for all CVs

        @param data  The OpenSoundPacket we're processing
        """
        for i in range(len(cvs)):
            v = data.values[i]
            t = type(data.values[i])
            cv = cvs[i]

            if t is int:
                if v == 0:
                    cv.off()
                else:
                    cv.on()
            elif t is float:
                cv.voltage(v * europi_config.MAX_OUTPUT_VOLTAGE)
        self.ui_dirty = True

    @classmethod
    def config_points(cls):
        return [
            configuration.string("NAMESPACE", default="/europi/"),
            configuration.integer("RECV_PORT", default=9000, minimum=0, maximum=65535),
            configuration.integer("SEND_PORT", default=9001, minimum=0, maximum=65535),
            configuration.string("SEND_ADDR", default="192.168.4.100"),
        ]

    def on_status_tick(self, timer):
        # send the states of all of our inputs
        self.server.send_data(
            f"{self.namespace}k1",
            k1.percent(),
        )
        self.server.send_data(
            f"{self.namespace}k2",
            k2.percent(),
        )
        self.server.send_data(
            f"{self.namespace}ain",
            ain.percent(),
        )
        self.server.send_data(
            f"{self.namespace}b1",
            b1.value() != 0,
        )
        self.server.send_data(
            f"{self.namespace}b2",
            b2.value() != 0,
        )
        self.server.send_data(
            f"{self.namespace}din",
            din.value() != 0,
        )

    def draw(self):
        oled.fill(0)
        width = OLED_WIDTH // 6 -2
        for i in range(len(cvs)):
            cv = cvs[i]
            left = i * OLED_WIDTH // 6
            height = int(max(OLED_HEIGHT * cv.voltage() / europi_config.MAX_OUTPUT_VOLTAGE, 1))

            oled.fill_rect(left + 1, OLED_HEIGHT - height, width, height, 1)
        oled.show()
        self.ui_dirty = False

    def main(self):
        if wifi_connection is None:
            raise experimental.wifi.WifiError("No wifi connection")

        oled.centre_text(f"""{wifi_connection.ip_addr}
waiting...""")

        # start a timer to send our input state at 10Hz
        timer = Timer()
        timer.init(freq=20, mode=Timer.PERIODIC, callback=self.on_status_tick)

        while True:
            self.server.receive_data()
            if self.ui_dirty:
                self.draw()


if __name__ == "__main__":
    OscControl().main()
