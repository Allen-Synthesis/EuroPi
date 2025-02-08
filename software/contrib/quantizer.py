# Copyright 2023 Allen Synthesis
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
"""Equal-temperment quantizer for the EuroPi

Features configurable intervals for multiple outputs and customizable scale

  @author Chris Iverach-Brereton <ve4cib@gmail.com>
  @date   2023-02-12
"""

from europi import *
from europi_script import EuroPiScript

from experimental.quantizer import Quantizer, VOLTS_PER_OCTAVE, VOLTS_PER_SEMITONE, SEMITONES_PER_OCTAVE
from experimental.screensaver import Screensaver

import time

## Whe in triggered mode we only quantize when we receive an external clock signal
MODE_TRIGGERED=0

## In continuous mode the digital input is ignored and we quantize the input
#  at the highest rate possible
MODE_CONTINUOUS=1

## How many milliseconds of idleness do we need before we trigger the screensaver?
#
#  =20 minutes
SCREENSAVER_TIMEOUT_MS = 1000 * 60 * 20


SELECT_OPTION_Y = 16
HALF_CHAR_WIDTH = int(CHAR_WIDTH / 2)

class ScreensaverScreen(Screensaver):
    """Blank the screen when idle

    Eventually it might be neat to have an animation, but that's
    not necessary for now
    """
    def __init__(self, quantizer):
        super().__init__()
        self.quantizer = quantizer

    def on_button1(self):
        self.quantizer.active_screen = self.quantizer.kb

class KeyboardScreen:
    """Draws a pretty keyboard and indicates what notes are enabled
    and what note is being played as the primary output
    """

    def __init__(self, quantizer):
        self.quantizer = quantizer
        self.highlight_note = 0

        # X, Y, bw
        self.enable_marks = [
            (  8, 2, 0),
            ( 17, 2, 1),
            ( 26, 2, 0),
            ( 35, 2, 1),
            ( 43, 2, 0),
            ( 59, 2, 0),
            ( 69, 2, 1),
            ( 77, 2, 0),
            ( 85, 2, 1),
            ( 94, 2, 0),
            (103, 2, 1),
            (112, 2, 0)
        ]

        self.playing_marks = [
            (  8, 20, 0),
            ( 17, 15, 1),
            ( 26, 20, 0),
            ( 35, 15, 1),
            ( 43, 20, 0),
            ( 59, 20, 0),
            ( 69, 15, 1),
            ( 77, 20, 0),
            ( 85, 15, 1),
            ( 94, 20, 0),
            (103, 15, 1),
            (112, 20, 0)
        ]

    def draw(self):
        # a 128x32 keyboard image
        # see https://github.com/Allen-Synthesis/EuroPi/blob/main/software/oled_tips.md
        # and https://github.com/novaspirit/img2bytearray
        KB_HEIGHT = 32
        KB_WIDTH = 128
        kb=b'\x07\xff\xc0\x7f\xe0?\xfe\xff\xf8\x0f\xfc\x07\xfe\x03\xff\xe0\x07\xff\xc0\x7f\xe0?\xfe\xff\xf8\x0f\xfc\x07\xfe\x03\xff\xe0\x07\xff\xc0\x7f\xe0?\xfe\xff\xf8\x0f\xfc\x07\xfe\x03\xff\xe0\x07\xff\xc0\x7f\xe0?\xfe\xff\xf8\x0f\xfc\x07\xfe\x03\xff\xe0\x07\xff\xc0\x7f\xe0?\xfe\xff\xf8\x0f\xfc\x07\xfe\x03\xff\xe0\x07\xff\xc0\x7f\xe0?\xfe\xff\xf8\x0f\xfc\x07\xfe\x03\xff\xe0\x07\xff\xc0\x7f\xe0?\xfe\xff\xf8\x0f\xfc\x07\xfe\x03\xff\xe0\x07\xff\xc0\x7f\xe0?\xfe\xff\xf8\x0f\xfc\x07\xfe\x03\xff\xe0\x07\xff\xc0\x7f\xe0?\xfe\xff\xf8\x0f\xfc\x07\xfe\x03\xff\xe0\x07\xff\xc0\x7f\xe0?\xfe\xff\xf8\x0f\xfc\x07\xfe\x03\xff\xe0\x07\xff\xc0\x7f\xe0?\xfe\xff\xf8\x0f\xfc\x07\xfe\x03\xff\xe0\x07\xff\xc0\x7f\xe0?\xfe\xff\xf8\x0f\xfc\x07\xfe\x03\xff\xe0\x07\xff\xc0\x7f\xe0?\xfe\xff\xf8\x0f\xfc\x07\xfe\x03\xff\xe0\x07\xff\xc0\x7f\xe0?\xfe\xff\xf8\x0f\xfc\x07\xfe\x03\xff\xe0\x07\xff\xc0\x7f\xe0?\xfe\xff\xf8\x0f\xfc\x07\xfe\x03\xff\xe0\x07\xff\xc0\x7f\xe0?\xfe\xff\xf8\x0f\xfc\x07\xfe\x03\xff\xe0\x07\xff\xc0\x7f\xe0?\xfe\xff\xf8\x0f\xfc\x07\xfe\x03\xff\xe0\x07\xff\xc0\x7f\xe0?\xfe\xff\xf8\x0f\xfc\x07\xfe\x03\xff\xe0\x07\xff\xc0\x7f\xe0?\xfe\xff\xf8\x0f\xfc\x07\xfe\x03\xff\xe0\x07\xff\xc0\x7f\xe0?\xfe\xff\xf8\x0f\xfc\x07\xfe\x03\xff\xe0\x07\xff\xc0\x7f\xe0?\xfe\xff\xf8\x0f\xfc\x07\xfe\x03\xff\xe0\x07\xff\xc0\x7f\xe0?\xfe\xff\xf8\x0f\xfc\x07\xfe\x03\xff\xe0\x07\xff\xc0\x7f\xe0?\xfe\xff\xf8\x0f\xfc\x07\xfe\x03\xff\xe0\x07\xff\xfb\xff\xfd\xff\xfe\xff\xff\x7f\xff\xbf\xff\xdf\xff\xe0\x07\xff\xfb\xff\xfd\xff\xfe\xff\xff\x7f\xff\xbf\xff\xdf\xff\xe0\x07\xff\xfb\xff\xfd\xff\xfe\xff\xff\x7f\xff\xbf\xff\xdf\xff\xe0\x07\xff\xfb\xff\xfd\xff\xfe\xff\xff\x7f\xff\xbf\xff\xdf\xff\xe0\x07\xff\xfb\xff\xfd\xff\xfe\xff\xff\x7f\xff\xbf\xff\xdf\xff\xe0\x07\xff\xfb\xff\xfd\xff\xfe\xff\xff\x7f\xff\xbf\xff\xdf\xff\xe0\x07\xff\xfb\xff\xfd\xff\xfe\xff\xff\x7f\xff\xbf\xff\xdf\xff\xe0\x07\xff\xfb\xff\xfd\xff\xfe\xff\xff\x7f\xff\xbf\xff\xdf\xff\xe0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'

        # read the encoder value from knob 1 so we know what key to highlight
        self.highlight_note = k1.range(len(self.quantizer.scale))

        # draw the keyboard image to the screen
        img = bytearray(kb)
        imgFB = FrameBuffer(img, KB_WIDTH, KB_HEIGHT, MONO_HLSB)
        oled.blit(imgFB,0,0)

        # mark the enabled notes with a .
        for i in range(len(self.quantizer.scale)):
            if self.quantizer.scale[i]:
                oled.text('.', *self.enable_marks[i])

        # mark the active note with a +
        k = self.quantizer.current_note
        oled.text('+', self.playing_marks[k][0], self.playing_marks[k][1], self.playing_marks[k][2])

        # clear the bottom of the screen and mark the togglable key with a line
        oled.fill_rect(0, OLED_HEIGHT-2, OLED_WIDTH, 2, 0)
        oled.fill_rect(self.enable_marks[self.highlight_note][0], OLED_HEIGHT-1, 7, 1, 1)

        oled.show()

    def on_button1(self):
        self.quantizer.scale[self.highlight_note] = not self.quantizer.scale[self.highlight_note]
        self.quantizer.save()

class MenuScreen:
    """Advanced menu options screen
    """

    def __init__(self, quantizer):
        self.quantizer = quantizer
        self.menu_item = 0

        self.menu_items = [
            ModeChooser(quantizer),
            RootChooser(quantizer),
            OctaveChooser(quantizer),
            IntervalChooser(quantizer, 2),
            IntervalChooser(quantizer, 3),
            IntervalChooser(quantizer, 4),
            IntervalChooser(quantizer, 5)
        ]

    def draw(self):
        self.menu_item = k1.range(len(self.menu_items))
        self.menu_items[self.menu_item].draw()

    def on_button1(self):
        self.menu_items[self.menu_item].on_button1()

class ModeChooser:
    """Used by MenuScreen to choose the operating mode
    """
    def __init__(self, quantizer):
        self.quantizer = quantizer

        self.mode_names = [
            "Triggered",
            "Continuous"
        ]

    def read_mode(self, mode='integer'):
        if mode == 'string':
            return k2.choice(self.mode_names)
        else:
            return k2.range(len(self.mode_names))

    def on_button1(self):
        new_mode = self.read_mode()
        self.quantizer.mode = new_mode
        self.quantizer.save()

    def draw(self):
        oled.fill(0)
        oled.text(f"Mode", 0, 0)

        current_mode = self.mode_names[self.quantizer.mode]
        new_mode = self.read_mode(mode='string')
        QuantizerScript.choose_option(self, new_mode, current_mode, self.mode_names)

        oled.show()

class RootChooser:
    """Used by MenuScreen to choose the transposition offset
    """
    def __init__(self, quantizer):
        self.quantizer = quantizer
        self.root_names = [
            "C ",
            "C#",
            "D ",
            "D#",
            "E ",
            "F ",
            "F#",
            "G ",
            "G#",
            "A ",
            "A#",
            "B "
        ]

    def read_root(self, mode='integer'):
        if mode == 'string':
            return k2.choice(self.root_names)
        else:
            return k2.range(len(self.root_names))

    def on_button1(self):
        new_root = self.read_root()
        self.quantizer.root = new_root
        self.quantizer.save()

    def draw(self):
        oled.fill(0)
        oled.text(f"Transpose", 0, 0)

        new_root = self.read_root(mode='string')
        current_root = self.root_names[self.quantizer.root]
        QuantizerScript.choose_option(self, new_root, current_root, self.root_names)

        oled.show()

class OctaveChooser:
    """Used by MenuScreen to choose the octave offset
    """
    def __init__(self, quantizer):
        self.quantizer = quantizer
        self.octave_texts = ['-4', '-3', '-2', '-1', '0', '+1', '+2', '+3', '+4']
        self.octave_text_y = 12

    def read_octave(self, mode='integer'):
        if mode == 'string':
            return k2.choice(self.octave_texts)
        else:
            return k2.range(9) - 4  # result should be -1 to +2

    def on_button1(self):
        new_octave = self.read_octave()
        self.quantizer.octave = new_octave
        self.quantizer.save()

    def draw(self):
        oled.fill(0)
        oled.text(f"Octave", 0, 0)

        new_octave = self.read_octave(mode='string')
        current_octave = self.quantizer.octave

        if current_octave > 0:
            current_octave = '+' + str(current_octave)
        else:
            current_octave = str(current_octave)

        QuantizerScript.choose_option(self, new_octave, current_octave, self.octave_texts)

        oled.show()

class IntervalChooser:
    """Used by MenuScreen to choose the interval offset for a given output
    """
    def __init__(self, quantizer, n):
        self.quantizer = quantizer
        self.n = n
        self.interval_names = [
            "-Pe 8",
            "-MA 7",
            "-mi 7",
            "-MA 6",
            "-mi 6",
            "-Pe 5",
            "-Di 5",
            "-Pe 4",
            "-MA 3",
            "-mi 3",
            "-MA 2",
            "-mi 2",
            "Pe 1",
            "+mi 2",
            "+MA 2",
            "+mi 3",
            "+MA 3",
            "+Pe 4",
            "+Di 5",
            "+Pe 5",
            "+mi 6",
            "+MA 6",
            "+mi 7",
            "+MA 7",
            "+Pe 8"
        ]


    def read_interval(self, mode='integer'):
        if mode == 'string':
            return k2.choice(self.interval_names)
        else:
            return k2.range(len(self.interval_names)) - 12

    def on_button1(self):
        new_interval = self.read_interval()
        self.quantizer.intervals[self.n-2] = new_interval
        self.quantizer.save()

    def draw(self):
        oled.fill(0)
        oled.text(f"Output {self.n}", 0, 0)

        new_interval = self.read_interval(mode='string')
        current_interval = self.interval_names[self.quantizer.intervals[self.n-2]+12]
        QuantizerScript.choose_option(self, new_interval, current_interval, self.interval_names)

        oled.show()

class QuantizerScript(EuroPiScript):
    """The main EuroPi program. Uses Scale to quantize incoming analog voltages
    and round them to the nearest note on the scale.

    Primary output is on cv1, with cv2-5 as aux outputs shifted up/down a fixed
    number of semitones.  cv6 outputs a gate/trigger.
    """
    def __init__(self):
        super().__init__()

        # keep track of the last time the user interacted with the module
        # if we're idle for too long, start the screensaver
        self.last_interaction_time = time.ticks_ms()

        # Continious quantizing, or only on an external trigger?
        self.mode = MODE_TRIGGERED

        # What semitone is the root of the scale?
        # 0 = C, 1 = C#/Db, 2 = D, etc...
        # This is used to transpose the output up the given number of semitones
        self.root = 0

        # What octave are we outputting?
        self.octave = 0

        # Outputs 2-5 output the same note, shifted up or down by
        # a fixed number of semitones
        self.intervals = [0, 0, 0, 0]
        self.aux_outs = [cv2, cv3, cv4, cv5]

        # The current scale we're quantizing to
        self.scale = Quantizer()

        # The input/output voltages
        self.input_voltage = 0.0
        self.output_voltage = 0.0

        # The semitone we're currently outputting on cv1 (0-11)
        self.current_note = 0

        # GUI/user interaction
        self.kb = KeyboardScreen(self)
        self.menu = MenuScreen(self)
        self.screensaver = ScreensaverScreen(self)
        self.active_screen = self.kb

        self.screen_centre = int(OLED_WIDTH / 2)

        self.load()

        # connect event handlers for the rising & falling clock edges + button presses

        @din.handler
        def on_rising_clock():
            """Handler for the rising edge of the input clock
            """
            if self.mode == MODE_TRIGGERED:
                self.read_quantize_output()
                cv6.on()

        @din.handler_falling
        def on_falling_clock():
            """Handler for the falling edge of the input clock
            """
            if self.mode == MODE_TRIGGERED:
                cv6.off()

        @b1.handler
        def on_b1_press():
            """Handler for pressing button 1

            Button 1 is used for the main interaction and is passed to
            the current display for user interaction
            """
            self.last_interaction_time = time.ticks_ms()
            self.active_screen.on_button1()

        @b2.handler
        def on_b2_press():
            """Handler for pressing button 2

            Button 2 is used to cycle between screens
            """
            self.last_interaction_time = time.ticks_ms()

            if self.active_screen == self.kb:
                self.active_screen = self.menu
            else:
                self.active_screen = self.kb

    def load(self):
        """Load the persistent settings from storage and apply them
        """
        state = self.load_state_json()

        loaded_scale = state.get("scale", [True]*12)  # default to a chromatic scale
        self.scale.notes = loaded_scale

        self.root = state.get("root", self.root)
        self.octave = state.get("octave", self.octave)
        self.intervals = state.get("intervals", self.intervals)
        self.mode = state.get("mode", self.mode)

    def save(self):
        """Save the current settings to persistent storage
        """
        state = {
            "scale": self.scale.notes,
            "root": self.root,
            "octave": self.octave,
            "intervals": self.intervals,
            "mode": self.mode
        }
        self.save_state_json(state)

    @classmethod
    def display_name(cls):
        return "Quantizer"

    def quantize(self, analog_in):
        """Take an analog signal and process it

        Sets self.current_note and self.output_voltage
        """

        (volts, semitone) = self.scale.quantize(analog_in)

        # apply our octave & transposition offsets
        volts = volts + self.octave * VOLTS_PER_OCTAVE + self.root * VOLTS_PER_SEMITONE

        self.output_voltage = volts
        self.current_note = semitone

    def read_quantize_output(self):
        """Read the input signal, quantize it, set outputs 1-5 accordingly

        Called by the main loop in continuous mode or the rising clock handler
        in triggered mode
        """
        self.input_voltage = ain.read_voltage(500)   # increase the number of samples to help reduce noise
        self.quantize(self.input_voltage)

        cv1.voltage(self.output_voltage)

        for i in range(len(self.aux_outs)):
            self.aux_outs[i].voltage(self.output_voltage + self.intervals[i] * VOLTS_PER_SEMITONE)

    def choose_option(self, new_item, current_item, all_items):
        item_widths = []
        for item_text in all_items:
            if item_text == new_item:
                offset = -int(sum(item_widths) + (CHAR_WIDTH * (len(item_widths))) + (CHAR_WIDTH * (len(item_text) / 2)) - (OLED_WIDTH / 2))
            item_widths.append(len(item_text) * CHAR_WIDTH)

        x = offset

        for index, item_text in enumerate(all_items):
            item_text_width = item_widths[index]
            if item_text == current_item:
                oled.fill_rect((x - 1), SELECT_OPTION_Y, (item_text_width + 3), (CHAR_HEIGHT + 4), 1)
                oled.text(item_text, x, (SELECT_OPTION_Y + 2), 0)
            elif item_text == new_item:
                oled.rect((x - 1), SELECT_OPTION_Y, (item_text_width + 3), (CHAR_HEIGHT + 4), 1)
                oled.text(item_text, x, (SELECT_OPTION_Y + 2), 1)
            else:
                oled.text(item_text, x, (SELECT_OPTION_Y + 2), 1)
            x += item_text_width + CHAR_WIDTH

    def main(self):
        """The main loop; reads from ain, sets the output voltages
        """

        while True:
            # Check if we've been idle for too long; if so, blank the screen
            # to prevent burn-in
            now = time.ticks_ms()
            if time.ticks_diff(now, self.last_interaction_time) > SCREENSAVER_TIMEOUT_MS:
                self.active_screen = self.screensaver

            if self.mode == MODE_CONTINUOUS:
                # clear the previous trigger
                cv6.off()

                # Read the new voltage and output it
                last_output = self.output_voltage
                self.read_quantize_output()

                if last_output != self.output_voltage:
                    cv6.on()

                # In continuous mode we fall back to a 100Hz internal clock
                # that effectively simulates a very high-speed input trigger
                # Note that this rate has to be long enough for the trigger on
                # cv6 to be useful to other modules.  A 10ms trigger is a
                # reasonable compromise between high-speed input signal processing
                # and keeping the code simple
                CYCLE_RATE = 0.01
                time.sleep(CYCLE_RATE)

            self.active_screen.draw()

if __name__ == "__main__":
    QuantizerScript().main()
