#!/usr/bin/env python3
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

        @b1.handler_falling
        def b1_falling():
            """Revert to channel a when the button is released
            """
            self.k1_bank.set_current("channel_a")
            self.k2_bank.set_current("channel_a")
            self.channel_markers[0] = '>'
            self.channel_markers[1] = ' '
            self.channel_markers[2] = ' '
            self.save_state()

        @b2.handler_falling
        def b2_falling():
            """Revert to channel a when the button is released
            """
            self.k1_bank.set_current("channel_a")
            self.k2_bank.set_current("channel_a")
            self.channel_markers[0] = '>'
            self.channel_markers[1] = ' '
            self.channel_markers[2] = ' '
            self.save_state()

        @din.handler
        def din1_rising():
            self.in_1 = HIGH
            self.last_trigger_at = time.ticks_ms()

        @din.handler_falling
        def din1_falling():
            self.in_1 = LOW

        def din2_rising():
            self.in_2 = HIGH
            self.last_trigger_at = time.ticks_ms()

        def din2_falling():
            self.in_2 = LOW

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
        self.din2 = AnalogReaderDigitalWrapper(ain, cb_rising=din2_rising, cb_falling=din2_falling)

        self.in_1 = LOW
        self.in_2 = LOW

        # we fire a trigger on CV6, so keep track of the previous outputs so we know when something's changed
        self.last_trigger_at = time.ticks_ms()

        self.channel_markers = ['>', ' ', ' ']

    def save_state(self):
        state = {
            "gain_b1": self.k1_bank["channel_b"].percent(),
            "gain_b2": self.k2_bank["channel_b"].percent(),
            "gain_c1": self.k1_bank["channel_c"].percent(),
            "gain_c2": self.k2_bank["channel_c"].percent()
        }
        self.save_state_json(state)

    def main(self):
        TRIGGER_DURATION = 10   # 10ms triggers every time we get a rising edge on either input channel
        TRIGGER_VOLTAGE = 5     # triggers are 5V

        while True:
            self.din2.update()

            gain_a1 = self.k1_bank["channel_a"].percent()
            gain_a2 = self.k2_bank["channel_a"].percent()

            gain_b1 = self.k1_bank["channel_b"].percent()
            gain_b2 = self.k2_bank["channel_b"].percent()

            gain_c1 = self.k1_bank["channel_c"].percent()
            gain_c2 = self.k2_bank["channel_c"].percent()

            # calculate the outputs, multiplied by half the max output voltage
            # this gives us 0-10V, depending on the gains and input values
            out_a = MAX_OUTPUT_VOLTAGE/2 * (self.in_1 * gain_a1 + self.in_2 * gain_a2)
            out_b = MAX_OUTPUT_VOLTAGE/2 * (self.in_1 * gain_b1 + self.in_2 * gain_b2)
            out_c = MAX_OUTPUT_VOLTAGE/2 * (self.in_1 * gain_c1 + self.in_2 * gain_c2)

            cv1.voltage(out_a)
            cv2.voltage(out_b)
            cv3.voltage(out_c)
            cv4.voltage(abs(out_a - out_b))
            cv5.voltage(abs(out_a - out_c))

            now = time.ticks_ms()
            if time.ticks_diff(now, self.last_trigger_at) > TRIGGER_DURATION:
                cv6.off()
            else:
                cv6.voltage(TRIGGER_VOLTAGE)


            # show the current gains * outputs, marking the channel we're controlling via the knobs & buttons
            ssoled.centre_text(f"{self.channel_markers[0]}{gain_a1:0.2f} {gain_a2:0.2f} {out_a:0.2f}\n{self.channel_markers[1]}{gain_b1:0.2f} {gain_b2:0.2f} {out_b:0.2f}\n{self.channel_markers[2]}{gain_c1:0.2f} {gain_c2:0.2f} {out_c:0.2f}")


if __name__ == "__main__":
    Traffic().main()
