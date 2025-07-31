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

from experimental.math_extras import gray_encode

import configuration

class BinaryCounter(EuroPiScript):
    MAX_N = (1 << NUM_CVS) - 1

    MODE_DISCRETE = 0
    MODE_CONTINUOUS = 1
    N_MODES = 2

    def __init__(self):
        super().__init__()
        self.load_state()
        self.state_dirty = False

        self.n = 0
        self.k = int(
            (
                k1.percent() + k2.percent() * ain.percent()
            ) * self.MAX_N
        )

        self.gate_recvd = False

        din.handler(self.on_gate_rise)
        din.handler_falling(self.on_gate_fall)
        b1.handler(self.cycle_mode)
        b2.handler(self.reset)

    @classmethod
    def config_points(cls):
        return [
            # If true, use gray encoding instead of standard binary
            configuration.boolean(
                "USE_GRAY_ENCODING",
                False
            ),
        ]

    def load_state(self):
        cfg = self.load_state_json()
        self.mode = cfg.get("mode", self.MODE_DISCRETE)

    def save_state(self):
        cfg = {
            "mode": self.mode
        }
        self.save_state_json(cfg)
        self.state_dirty = False

    def cycle_mode(self):
        self.mode = (self.mode + 1) % self.N_MODES
        self.state_dirty = True

    def on_gate_rise(self):
        self.gate_recvd = True

    def on_gate_fall(self):
        if self.mode == self.MODE_DISCRETE:
            turn_off_all_cvs()

    def reset(self):
        self.n = 0

    def set_outputs(self):
        if self.config.USE_GRAY_ENCODING:
            n = gray_encode(self.n)
        else:
            n = self.n

        for i in range(NUM_CVS):
            if (n >> i) & 0x01:
                cvs[i].on()
            else:
                cvs[i].off()


    def main(self):
        while True:
            self.k = int(
                (
                    k1.percent() + k2.percent() * ain.percent()
                ) * self.MAX_N
            )
            # minimum of 1; k==0 will do nothing, which isn't interesting
            if self.k == 0:
                self.k = 1

            if self.state_dirty:
                self.save_state()

            if self.gate_recvd:
                self.set_outputs()
                self.n = (self.n + self.k) & self.MAX_N
                self.gate_recvd = False

            oled.centre_text(f"""{'Discrete' if self.mode == self.MODE_DISCRETE else 'Continuous'}
k = {self.k}
{self.n:06b}""")


if __name__ == "__main__":
    BinaryCounter().main()
