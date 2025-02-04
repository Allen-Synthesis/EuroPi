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
"""A EuroPi re-imagining of Traffic by Jasmine & Olive Trees

Two gate inputs are sent to AIN and DIN, their values multiplied by gains controlled by K1 and K2,
and the summed & differenced outputs sent to the outputs
"""

from europi import *
from europi_script import EuroPiScript

from experimental.a_to_d import AnalogReaderDigitalWrapper
from experimental.knobs import KnobBank
from experimental.screensaver import OledWithScreensaver

ssoled = OledWithScreensaver()

class Traffic(EuroPiScript):
    def __init__(self):
        super().__init__()

        state = self.load_state_json()

        # Button handlers to change the active channel for setting gains
        self.channel_markers = ['>', ' ', ' ']    # used to indicate the editable channel on the screen
        @b1.handler
        def b1_rising():
            """Activate channel b controls while b1 is held
            """
            ssoled.notify_user_interaction()
            self.k1_bank.set_current("channel_b")
            self.k2_bank.set_current("channel_b")
            self.channel_markers[0] = ' '
            self.channel_markers[1] = '>'
            self.channel_markers[2] = ' '

        @b2.handler
        def b2_rising():
            """Activate channel c controls while b1 is held
            """
            ssoled.notify_user_interaction()
            self.k1_bank.set_current("channel_c")
            self.k2_bank.set_current("channel_c")
            self.channel_markers[0] = ' '
            self.channel_markers[1] = ' '
            self.channel_markers[2] = '>'

        def either_button_falling():
            """Revert to channel a when the button is released
            """
            self.k1_bank.set_current("channel_a")
            self.k2_bank.set_current("channel_a")
            self.channel_markers[0] = '>'
            self.channel_markers[1] = ' '
            self.channel_markers[2] = ' '
            self.save_state()
        b1.handler_falling(either_button_falling)
        b2.handler_falling(either_button_falling)


        # Input trigger handlers
        self.input1_trigger_at = time.ticks_ms()
        self.input2_trigger_at = self.input1_trigger_at
        @din.handler
        def din1_rising():
            self.input1_trigger_at = time.ticks_ms()

            # Set the all-triggers output high
            self.last_output_trigger_at = self.input1_trigger_at
            cv6.on()

        def din2_rising():
            self.input2_trigger_at = time.ticks_ms()

            # Set the all-triggers output high
            self.last_output_trigger_at = self.input2_trigger_at
            cv6.on()

        self.k1_bank = (
            KnobBank.builder(k1) \
            .with_unlocked_knob("channel_a") \
            .with_locked_knob("channel_b", initial_percentage_value=state.get("gain_b1", 0.5)) \
            .with_locked_knob("channel_c", initial_percentage_value=state.get("gain_c1", 0.5)) \
            .build()
        )

        self.k2_bank = (
            KnobBank.builder(k2) \
            .with_unlocked_knob("channel_a") \
            .with_locked_knob("channel_b", initial_percentage_value=state.get("gain_b2", 0.5)) \
            .with_locked_knob("channel_c", initial_percentage_value=state.get("gain_c2", 0.5)) \
            .build()
        )

        self.din1 = din
        self.din2 = AnalogReaderDigitalWrapper(ain, cb_rising=din2_rising)

        # we fire a trigger on CV6, so keep track of the previous outputs so we know when something's changed
        self.last_output_trigger_at = time.ticks_ms()

    def save_state(self):
        state = {
            "gain_b1": self.k1_bank["channel_b"].percent(samples=1024),
            "gain_b2": self.k2_bank["channel_b"].percent(samples=1024),
            "gain_c1": self.k1_bank["channel_c"].percent(samples=1024),
            "gain_c2": self.k2_bank["channel_c"].percent(samples=1024)
        }
        self.save_state_json(state)

    def main(self):
        TRIGGER_DURATION = 10   # 10ms triggers every time we get a rising edge on either input channel

        while True:
            self.din2.update()

            gain_a1 = round(self.k1_bank["channel_a"].percent(samples=1024), 3)
            gain_a2 = round(self.k2_bank["channel_a"].percent(samples=1024), 3)

            gain_b1 = round(self.k1_bank["channel_b"].percent(samples=1024), 3)
            gain_b2 = round(self.k2_bank["channel_b"].percent(samples=1024), 3)

            gain_c1 = round(self.k1_bank["channel_c"].percent(samples=1024), 3)
            gain_c2 = round(self.k2_bank["channel_c"].percent(samples=1024), 3)

            # calculate the outputs
            delta_t = time.ticks_diff(self.input1_trigger_at, self.input2_trigger_at)
            if delta_t > 0 or abs(delta_t) <= 50:       # assume triggers within 50ms are simultaneous
                # din received a trigger more recently than ain
                out_a = MAX_OUTPUT_VOLTAGE * gain_a1
                out_b = MAX_OUTPUT_VOLTAGE * gain_b1
                out_c = MAX_OUTPUT_VOLTAGE * gain_c1
            else:
                # ain received a trigger more recently than din
                out_a = MAX_OUTPUT_VOLTAGE * gain_a2
                out_b = MAX_OUTPUT_VOLTAGE * gain_b2
                out_c = MAX_OUTPUT_VOLTAGE * gain_c2

            cv1.voltage(out_a)
            cv2.voltage(out_b)
            cv3.voltage(out_c)
            cv4.voltage(abs(out_a - out_b))
            cv5.voltage(abs(out_a - out_c))

            now = time.ticks_ms()
            if time.ticks_diff(now, self.last_output_trigger_at) > TRIGGER_DURATION:
                cv6.off()

            # show the current gains * outputs, marking the channel we're controlling via the knobs & buttons
            ssoled.centre_text(f"{self.channel_markers[0]} A {gain_a1:0.3f} {gain_a2:0.3f}\n{self.channel_markers[1]} B {gain_b1:0.3f} {gain_b2:0.3f}\n{self.channel_markers[2]} C {gain_c1:0.3f} {gain_c2:0.3f}")


if __name__ == "__main__":
    Traffic().main()
