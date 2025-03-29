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

        self.sanitize_osc_config()

        self.server = OpenSoundServer(
            recv_port=self.config.RECV_PORT,
            send_port=self.config.SEND_PORT,
            send_addr=self.config.SEND_ADDR,
        )

        self.ui_dirty = False

        @self.server.data_handler
        def on_data_recv(connection=None, data=None):
            if data.address == self.cv1_topic:
                self.set_cv(cv1, data)
            elif data.address == self.cv2_topic:
                self.set_cv(cv2, data)
            elif data.address == self.cv3_topic:
                self.set_cv(cv3, data)
            elif data.address == self.cv4_topic:
                self.set_cv(cv4, data)
            elif data.address == self.cv5_topic:
                self.set_cv(cv5, data)
            elif data.address == self.cv6_topic:
                self.set_cv(cv6, data)
            elif data.address == self.cvs_topic:
                # set all CVs at once
                self.set_cvs(data)

    def sanitize_osc_config(self):
        self.namespace = self.config.NAMESPACE
        if not self.namespace.startswith("/"):
            self.namespace = f"/{self.namespace}"
        if not self.namespace.endswith("/"):
            self.namespace = f"{self.namespace}/"

        def sanitize_topic(param_name):
            topic = ""
            if self.config[param_name].startswith("/"):
                topic = self.config[param_name]
            else:
                topic = f"{self.namespace}{self.config[param_name]}"
            topic = topic.rstrip("/")
            return topic

        self.cv1_topic = sanitize_topic("CV1_TOPIC")
        self.cv2_topic = sanitize_topic("CV2_TOPIC")
        self.cv3_topic = sanitize_topic("CV3_TOPIC")
        self.cv4_topic = sanitize_topic("CV4_TOPIC")
        self.cv5_topic = sanitize_topic("CV5_TOPIC")
        self.cv6_topic = sanitize_topic("CV6_TOPIC")
        self.cvs_topic = sanitize_topic("CVS_TOPIC")
        self.ain_topic = sanitize_topic("AIN_TOPIC")
        self.din_topic = sanitize_topic("DIN_TOPIC")
        self.k1_topic = sanitize_topic("K1_TOPIC")
        self.k2_topic = sanitize_topic("K2_TOPIC")
        self.b1_topic = sanitize_topic("B1_TOPIC")
        self.b2_topic = sanitize_topic("B2_TOPIC")

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
            # OSC namespace & topics
            configuration.string("NAMESPACE", default="/europi/"),
            configuration.string("CV1_TOPIC", default="cv1"),
            configuration.string("CV2_TOPIC", default="cv2"),
            configuration.string("CV3_TOPIC", default="cv3"),
            configuration.string("CV4_TOPIC", default="cv4"),
            configuration.string("CV5_TOPIC", default="cv5"),
            configuration.string("CV6_TOPIC", default="cv6"),
            configuration.string("CVS_TOPIC", default="cvs"),
            configuration.string("AIN_TOPIC", default="ain"),
            configuration.string("DIN_TOPIC", default="din"),
            configuration.string("K1_TOPIC", default="k1"),
            configuration.string("K2_TOPIC", default="k2"),
            configuration.string("B1_TOPIC", default="b1"),
            configuration.string("B2_TOPIC", default="b2"),

            # Network settings
            configuration.integer("RECV_PORT", default=9000, minimum=0, maximum=65535),
            configuration.integer("SEND_PORT", default=9001, minimum=0, maximum=65535),
            configuration.string("SEND_ADDR", default="192.168.4.100"),
        ]

    def on_status_tick(self, timer):
        # send the states of all of our inputs
        self.server.send_data(
            self.k1_topic,
            k1.percent(),
        )
        self.server.send_data(
            self.k2_topic,
            k2.percent(),
        )
        self.server.send_data(
            self.ain_topic,
            ain.percent(),
        )
        self.server.send_data(
            self.b1_topic,
            b1.value() != 0,
        )
        self.server.send_data(
            self.b2_topic,
            b2.value() != 0,
        )
        self.server.send_data(
            self.din_topic,
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
