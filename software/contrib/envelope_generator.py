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

from time import sleep, sleep_ms, ticks_ms, ticks_diff
from math import log


#Output a 10ms trigger to indicate end-of-rise and end-of-fall on CV5/6
TRIGGER_DURATION_MS = 10

#Constants for tracking the direction of the envelope's voltage
DIRECTION_RISING = 1
DIRECTION_FALLING = 0
DIRECTION_SUSTAIN = 3

#Sustain modes
SUSTAIN_MODE_AR = 0
SUSTAIN_MODE_ASR = 1

#Looping modes
LOOPING_MODE_LOOP = 1
LOOPING_MODE_ONCE = 0


class EnvelopeGenerator(EuroPiScript):
    def __init__(self):
        super().__init__()
        state = self.load_state_json()

        self.sustain_mode = state.get("sustain_mode", SUSTAIN_MODE_ASR)
        self.looping_mode = state.get("looping_mode", LOOPING_MODE_ONCE)

        #Milliscond tick of of the most recent end-of-rise and end-of-fall
        #initialized to be 2x trigger duration in the past on startup to prevent roll-over issues
        self.last_rise_end_at = time.ticks_add(time.ticks_ms(), -2*TRIGGER_DURATION_MS)
        self.last_fall_end_at = self.last_rise_end_at

        self.max_output_voltage = europi_config.MAX_OUTPUT_VOLTAGE

        #Distance of envelope voltage from max voltage/0 before 'jumping' to it - prevents large logarithmic calculations
        self.voltage_threshold = 0.1

        #Length of the longest possible envelope (not in any meaningful unit)
        self.max_increment_factor = 256
        self.update_increment_factor()

        #Time in ms between incrementing value of envelope
        self.increment_delay = 1

        #0 will start a new envelope at the current value, 1 will start it from zero
        self.retrig_mode = 0

        #Display refresh rate in ms
        self.display_refresh_rate = 30
        self.last_refreshed_display = self.display_refresh_rate

        self.envelope_display_bounds = [0, 0, int(OLED_WIDTH), int(OLED_HEIGHT / 2)]

        self.direction = DIRECTION_SUSTAIN  # DIRECTION_RISING, DIRECTION_FALLING, or DIRECTION_SUSTAIN
        self.envelope_value = 0

        self.envelope_out = cv2
        self.envelope_inverted_out = cv3
        self.din_copy_out = cv1

        self.sustain_gate = cv4
        self.eor_trigger = cv5
        self.eof_trigger = cv6

        din.handler(self.receive_trigger_rise)
        din.handler_falling(self.receive_trigger_fall)
        b1.handler(self.change_sustain_mode)
        b2.handler(self.change_looping_mode)


    @classmethod
    def display_name(cls):
        return "EnvelopeGen"

    def receive_trigger_rise(self):
        if self.retrig_mode == 1:
            self.envelope_value = 0
        self.direction = 1

    def receive_trigger_fall(self):
        if self.direction == DIRECTION_RISING:
            # Interrupted rise; output the trigger because we've risen as high as we're going to
            self.last_rise_end_at = time.ticks_ms()
        self.direction = DIRECTION_FALLING

    def change_sustain_mode(self):
        self.sustain_mode = 1 - self.sustain_mode
        #Save state to file
        self.save_state()

    def change_looping_mode(self):
        self.looping_mode = 1 - self.looping_mode
        #Save state to file
        self.save_state()

    def copy_digital_input(self):
        self.din_copy_out.value(din.value())

    def difference(self, a, b):
        return abs(a - b)

    def update_increment_factor(self):
        increment_factor_rising = k1.range(self.max_increment_factor, 512) / 2
        self.increment_factor = [(increment_factor_rising + 1), (k2.range(self.max_increment_factor, 256) + 1 + (ain.percent(256) * self.max_increment_factor))]

    def log(self, number):
        return log(max(number, 1))

    def update_envelope_value(self):
        #Envelope rising
        if self.direction == DIRECTION_RISING:
            increment = self.difference(self.envelope_value, self.max_output_voltage) / self.increment_factor[0]
            self.envelope_value += increment
            if self.difference(self.envelope_value, self.max_output_voltage) <= self.voltage_threshold:
                self.envelope_value = self.max_output_voltage
                if self.sustain_mode == 1 and self.looping_mode == 0:
                    self.direction = DIRECTION_SUSTAIN
                else:
                    self.direction = DIRECTION_FALLING
                self.last_rise_end_at = time.ticks_ms()
            else:
                sleep_ms(self.increment_delay)

        #Envelope falling
        elif self.direction == DIRECTION_FALLING:
            increment = self.difference(0, self.envelope_value) / self.increment_factor[1]
            self.envelope_value -= increment
            if self.difference(0, self.envelope_value) <= self.voltage_threshold:
                self.envelope_value = 0
                if self.looping_mode == LOOPING_MODE_ONCE:
                    self.direction = DIRECTION_SUSTAIN
                else:
                    self.direction = DIRECTION_RISING
                self.last_fall_end_at = time.ticks_ms()
            else:
                sleep_ms(self.increment_delay)

        #Update CV output to envelope value
        self.update_output_voltage()


    def update_output_voltage(self):
        self.envelope_out.voltage(self.envelope_value)
        self.envelope_inverted_out.voltage(self.max_output_voltage - self.envelope_value)

        if self.direction == DIRECTION_SUSTAIN:
            self.sustain_gate.on()
        else:
            self.sustain_gate.off()

        now = time.ticks_ms()
        if time.ticks_diff(now, self.last_rise_end_at) <= TRIGGER_DURATION_MS:
            self.eor_trigger.on()
        else:
            self.eor_trigger.off()

        if time.ticks_diff(now, self.last_fall_end_at) <= TRIGGER_DURATION_MS:
            self.eof_trigger.on()
        else:
            self.eof_trigger.off()

    def update_display(self):
        if ticks_diff(ticks_ms(), self.last_refreshed_display) >= self.display_refresh_rate:

            #Draw slope graph axis
            oled.hline(self.envelope_display_bounds[0], self.envelope_display_bounds[3], self.envelope_display_bounds[2], 1)
            oled.vline(self.envelope_display_bounds[0], self.envelope_display_bounds[1], self.envelope_display_bounds[3], 1)
            oled.vline((self.envelope_display_bounds[2] - 1), self.envelope_display_bounds[1], self.envelope_display_bounds[3], 1)

            try:
                rise_width = (self.increment_factor[0] - 1) / ((self.increment_factor[0] - 1) + (self.increment_factor[1] - 1))	#If envelope has zero rise and zero fall this will throw a ZeroDivisonError
                draw_envelope = True
            except ZeroDivisionError:
                draw_envelope = False

            if draw_envelope == True:
                rise_width_pixels = int(rise_width * self.envelope_display_bounds[2])
                fall_width = 1 - rise_width
                fall_width_pixels = int(self.envelope_display_bounds[2] - rise_width_pixels)

                #Generate rise slope pixels
                rise_pixels = []
                for pixel in range(rise_width_pixels):
                    x = pixel / (rise_width_pixels + 1)
                    y = x**2
                    x_pixel = rise_width_pixels - int(x * rise_width_pixels)
                    y_pixel = int(y * (self.envelope_display_bounds[3] - self.envelope_display_bounds[1]))
                    rise_pixels.append((x_pixel, y_pixel))
                rise_pixels.append((self.envelope_display_bounds[0], self.envelope_display_bounds[3]))

                #Generate fall slope pixels
                fall_pixels = []
                for pixel in range(fall_width_pixels):
                    x = pixel / (fall_width_pixels + 1)
                    y = x**2
                    x_pixel = (fall_width_pixels - int(x * fall_width_pixels)) + rise_width_pixels
                    y_pixel = self.envelope_display_bounds[3] - int(y * (self.envelope_display_bounds[3] - self.envelope_display_bounds[1]))
                    fall_pixels.append((x_pixel, y_pixel))
                fall_pixels.append((rise_width_pixels, self.envelope_display_bounds[1]))

                #Draw rise and fall slopes
                for array in [rise_pixels, fall_pixels]:
                    for index, pixel in enumerate(array[:-1]):
                        oled.line(array[index + 1][0], array[index + 1][1], pixel[0], pixel[1], 1)

                #Draw current envelope position
                current_envelope_position = 0
                if self.direction == DIRECTION_RISING or self.direction == DIRECTION_SUSTAIN:
                    current_envelope_position = int((self.envelope_value / self.max_output_voltage) * rise_width_pixels)
                elif self.direction == DIRECTION_FALLING:
                    current_envelope_position = self.envelope_display_bounds[2] - 1 - int((self.envelope_value / self.max_output_voltage) * (self.envelope_display_bounds[2] - rise_width_pixels))
                oled.vline(current_envelope_position, self.envelope_display_bounds[1], (self.envelope_display_bounds[3] - 1), 1)
            else:
                oled.vline(self.envelope_display_bounds[0], self.envelope_display_bounds[1], self.envelope_display_bounds[3], 1)
                oled.hline(self.envelope_display_bounds[0], self.envelope_display_bounds[1], self.envelope_display_bounds[2], 1)
                oled.vline((self.envelope_display_bounds[2] - 1), self.envelope_display_bounds[1], self.envelope_display_bounds[3], 1)

            #Display current envelope direction
            if self.direction == DIRECTION_RISING:
                direction_text = 'rise'
            elif self.direction == DIRECTION_FALLING:
                direction_text = 'fall'
            elif self.direction == DIRECTION_SUSTAIN and self.envelope_value == self.max_output_voltage:
                direction_text = 'hold'
            else:
                direction_text = 'off'
            oled.text(direction_text, 0, 20, 1)

            #Display current envelope mode (AR or ASR)
            if self.sustain_mode == SUSTAIN_MODE_AR:
                sustain_mode_text = 'ar'
            else:
                sustain_mode_text = 'asr'
            oled.text(sustain_mode_text, 50 + (4 if sustain_mode_text == 'ar' else 0), 20, 1)

            #Display current envelope looping mode
            if self.looping_mode == LOOPING_MODE_ONCE:
                looping_mode_text = 'once'
            else:
                looping_mode_text = 'loop'
            oled.text(looping_mode_text, 94, 20, 1)

            oled.show()
            oled.fill(0)
            self.last_refreshed_display = ticks_ms()

    def save_state(self):
        """Save the current state variables as JSON."""
        # Don't save if it has been less than 5 seconds since last save.
        if self.last_saved() < 5000:
            return

        state = {
            "sustain_mode": self.sustain_mode,
            "looping_mode": self.looping_mode,
        }
        self.save_state_json(state)

    def main(self):
        while True:
            self.copy_digital_input()
            self.update_display()
            self.update_increment_factor()
            self.update_envelope_value()

if __name__ == "__main__":
    EnvelopeGenerator().main()
