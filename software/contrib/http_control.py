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
Serves a simple HTTP page to control the levels of the six CV outputs from a browser

Requires a Pico W or Pico 2 W with a valid wifi setup to work
"""

from europi import *
from europi_script import EuroPiScript

from experimental.http import *

class HttpControl(EuroPiScript):

    def __init__(self):
        super().__init__()

        self.server = HttpServer(80)

        @self.server.request_handler
        def handle_request(connection=None, request=None):
            raise NotImplementedError("WIP - Not implemented yet")

    def main(self):
        if wifi_connection is None:
            raise WifiError("No wifi connection")

        while not wifi_connection.is_connected:
            oled.centre_text(f"""{wifi_connection.ssid}
Waiting for
connection...""")

        oled.centre_text(f"""{wifi_connection.ssid}
{wifi_connection.ip_addr}
Connected""")

        while True:
            self.server.check_requests()


if __name__ == "__main__":
    HttpControl().main()
