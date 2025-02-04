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
from europi import *
from europi_script import EuroPiScript
from time import sleep
from version import __version__


class About(EuroPiScript):
    def __init__(self):
        super().__init__()

    def main(self):
        turn_off_all_cvs()

        oled.centre_text(
            f"""EuroPi v{__version__}
{europi_config.EUROPI_MODEL}/{europi_config.PICO_MODEL}
{europi_config.CPU_FREQ}"""
        )

        while True:
            sleep(1)


if __name__ == "__main__":
    About().main()
