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

from experimental.http_server import *
import json


HTML_DOCUMENT = """<!DOCTYPE html>
<html lang="en">
    <head>
        <style>
            body {
                font-family: Montserrat;
                text-align: center;
            }
            h1 {
                font-weight: normal;
                font-size: 2.5rem;
                letter-spacing: 1.75rem;
                padding-left: 1.75rem;
                text-align: center;
            }
            h2 {
                font-weight:  bold;
                font-size: 3.0rem;
            }
            td {
                font-weight: lighter;
                font-size: 2.0rem;
            }
            .content-wrapper {
                margin: 0;
                position: absolute;
                top: 50%;
                align-content: center;
                width: 100%;
                -ms-transform: translateY(-50%);
                transform: translateY(-50%);
            }
            table {
                margin: auto;
            }
        </style>
        <title>
            EuroPi Web Control
        </title>
        <script>
            function on_change() {
                cvs = {
                    "cv1": parseFloat(document.getElementById("cv1").value),
                    "cv2": parseFloat(document.getElementById("cv2").value),
                    "cv3": parseFloat(document.getElementById("cv3").value),
                    "cv4": parseFloat(document.getElementById("cv4").value),
                    "cv5": parseFloat(document.getElementById("cv5").value),
                    "cv6": parseFloat(document.getElementById("cv6").value)
                }
                console.debug(cvs)

                var xhr = new XMLHttpRequest();
                var url = document.URL;
                xhr.open("POST", url, true);
                xhr.setRequestHeader("Content-Type", "text/json");
                xhr.onreadystatechange = function () {
                    if (xhr.readyState === 4 && xhr.status === 200) {
                        var json = JSON.parse(xhr.responseText);
                        console.log(json);
                    }
                };
                var data = JSON.stringify(cvs);
                xhr.send(data);
            }
        </script>
    </head>
    <body>
        <h1>EuroPi Web Control</h1>
        <div class="content-wrapper">
            <table>
                <tr>
                    <td>
                        CV1
                    </td>
                    <td>
                        CV2
                    </td>
                    <td>
                        CV3
                    </td>
                </tr>
                <tr>
                    <td>
                        <input type="range" min="0" max="10" step="0.001" value="0" id="cv1" oninput="on_change()">
                    </td>
                    <td>
                        <input type="range" min="0" max="10" step="0.001" value="0" id="cv2" oninput="on_change()">
                    </td>
                    <td>
                        <input type="range" min="0" max="10" step="0.001" value="0" id="cv3" oninput="on_change()">
                    </td>
                </tr>
                <tr>
                    <td>
                        CV4
                    </td>
                    <td>
                        CV5
                    </td>
                    <td>
                        CV6
                    </td>
                </tr>
                <tr>
                    <td>
                        <input type="range" min="0" max="10" step="0.001" value="0" id="cv4" oninput="on_change()">
                    </td>
                    <td>
                        <input type="range" min="0" max="10" step="0.001" value="0" id="cv5" oninput="on_change()">
                    </td>
                    <td>
                        <input type="range" min="0" max="10" step="0.001" value="0" id="cv6" oninput="on_change()">
                    </td>
                </tr>
            </table>
        </div>
    </body>
</html>"""


class HttpControl(EuroPiScript):

    def __init__(self):
        super().__init__()

        self.server = HttpServer(80)

        @self.server.get_handler
        def handle_get(connection=None, request=None):
            self.server.send_html(
                connection,
                HTML_DOCUMENT,
            )

        @self.server.post_handler
        def handle_post(connection=None, request=None):
            """
            Process a POST request from the client

            The request should look like

                POST / HTTP/1.1
                Host: 10.0.0.167
                User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:135.0) Gecko/20100101 Firefox/135.0
                Accept: */*
                Accept-Language: en-US,en;q=0.5
                Accept-Encoding: gzip, deflate
                Content-Type: text/json
                Content-Length: 63
                Origin: http://10.0.0.167
                Connection: keep-alive
                Referer: http://10.0.0.167/

                {"cv1":7.071,"cv2":8.5,"cv3":0,"cv4":0,"cv5":3.857,"cv6":5.929}

            We only care about the actual JSON body
            """
            try:
                (_, body) = request.split("\r\n\r\n")
                jdata = json.loads(body)

                for i in range(NUM_CVS):
                    cvs[i].voltage(jdata.get(f"cv{i+1}", 0.0))

                self.server.send_json(
                    connection,
                    {
                        "inputs": {
                            "ain": ain.read_voltage(),
                            "din": din.value(),
                            "k1": k1.percent(),
                            "k2": k2.percent(),
                            "b1": b1.value(),
                            "b2": b2.value(),
                        },
                        "outputs": {
                            "cv1": cv1.voltage(),
                            "cv2": cv2.voltage(),
                            "cv3": cv3.voltage(),
                            "cv4": cv4.voltage(),
                            "cv5": cv5.voltage(),
                            "cv6": cv6.voltage(),
                        },
                    },
                    headers=None,
                )
            except ValueError as err:
                log_warn(f"{body} is not valid json")
                self.server.send_error_page(
                    err,
                    connection,
                    status=HttpStatus.BAD_REQUEST,
                )

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
