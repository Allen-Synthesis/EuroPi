"""
Equal-temperment quantizer for the EuroPi with configurable intervals
for multiple outputs and customizable scale
"""

from europi import *
from europi_script import EuroPiScript
from time import sleep

# 1.0V/O is the Eurorack/Moog standard, but Buchla uses 1.2V/O
# Just in case someone needs Buchla compatibility, make this editable
VOLTS_PER_OCTAVE = 1.0
SEMITONES_PER_OCTAVE = 12
VOLTS_PER_SEMITONE = VOLTS_PER_OCTAVE / float(SEMITONES_PER_OCTAVE)

# Operating modes; when in mode 0 we require a trigger signal
# When in mode 1 we quantize continuously
MODE_TRIGGERED=0
MODE_CONTINUOUS=1

def linear_rescale(x, old_min, old_max, new_min, new_max):
    return (x-old_min) / (old_max-old_min) * (new_max - new_min) + new_min

# Draws a pretty keyboard and indicates what notes are active
# and what note is being played
class KeyboardScreen:
    def __init__(self, quantizer):
        self.quantizer = quantizer
        
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
        kb=b'\x07\xff\xc0\x7f\xe0?\xfe\xff\xf8\x0f\xfc\x07\xfe\x03\xff\xe0\x07\xff\xc0\x7f\xe0?\xfe\xff\xf8\x0f\xfc\x07\xfe\x03\xff\xe0\x07\xff\xc0\x7f\xe0?\xfe\xff\xf8\x0f\xfc\x07\xfe\x03\xff\xe0\x07\xff\xc0\x7f\xe0?\xfe\xff\xf8\x0f\xfc\x07\xfe\x03\xff\xe0\x07\xff\xc0\x7f\xe0?\xfe\xff\xf8\x0f\xfc\x07\xfe\x03\xff\xe0\x07\xff\xc0\x7f\xe0?\xfe\xff\xf8\x0f\xfc\x07\xfe\x03\xff\xe0\x07\xff\xc0\x7f\xe0?\xfe\xff\xf8\x0f\xfc\x07\xfe\x03\xff\xe0\x07\xff\xc0\x7f\xe0?\xfe\xff\xf8\x0f\xfc\x07\xfe\x03\xff\xe0\x07\xff\xc0\x7f\xe0?\xfe\xff\xf8\x0f\xfc\x07\xfe\x03\xff\xe0\x07\xff\xc0\x7f\xe0?\xfe\xff\xf8\x0f\xfc\x07\xfe\x03\xff\xe0\x07\xff\xc0\x7f\xe0?\xfe\xff\xf8\x0f\xfc\x07\xfe\x03\xff\xe0\x07\xff\xc0\x7f\xe0?\xfe\xff\xf8\x0f\xfc\x07\xfe\x03\xff\xe0\x07\xff\xc0\x7f\xe0?\xfe\xff\xf8\x0f\xfc\x07\xfe\x03\xff\xe0\x07\xff\xc0\x7f\xe0?\xfe\xff\xf8\x0f\xfc\x07\xfe\x03\xff\xe0\x07\xff\xc0\x7f\xe0?\xfe\xff\xf8\x0f\xfc\x07\xfe\x03\xff\xe0\x07\xff\xc0\x7f\xe0?\xfe\xff\xf8\x0f\xfc\x07\xfe\x03\xff\xe0\x07\xff\xc0\x7f\xe0?\xfe\xff\xf8\x0f\xfc\x07\xfe\x03\xff\xe0\x07\xff\xc0\x7f\xe0?\xfe\xff\xf8\x0f\xfc\x07\xfe\x03\xff\xe0\x07\xff\xc0\x7f\xe0?\xfe\xff\xf8\x0f\xfc\x07\xfe\x03\xff\xe0\x07\xff\xc0\x7f\xe0?\xfe\xff\xf8\x0f\xfc\x07\xfe\x03\xff\xe0\x07\xff\xc0\x7f\xe0?\xfe\xff\xf8\x0f\xfc\x07\xfe\x03\xff\xe0\x07\xff\xc0\x7f\xe0?\xfe\xff\xf8\x0f\xfc\x07\xfe\x03\xff\xe0\x07\xff\xc0\x7f\xe0?\xfe\xff\xf8\x0f\xfc\x07\xfe\x03\xff\xe0\x07\xff\xfb\xff\xfd\xff\xfe\xff\xff\x7f\xff\xbf\xff\xdf\xff\xe0\x07\xff\xfb\xff\xfd\xff\xfe\xff\xff\x7f\xff\xbf\xff\xdf\xff\xe0\x07\xff\xfb\xff\xfd\xff\xfe\xff\xff\x7f\xff\xbf\xff\xdf\xff\xe0\x07\xff\xfb\xff\xfd\xff\xfe\xff\xff\x7f\xff\xbf\xff\xdf\xff\xe0\x07\xff\xfb\xff\xfd\xff\xfe\xff\xff\x7f\xff\xbf\xff\xdf\xff\xe0\x07\xff\xfb\xff\xfd\xff\xfe\xff\xff\x7f\xff\xbf\xff\xdf\xff\xe0\x07\xff\xfb\xff\xfd\xff\xfe\xff\xff\x7f\xff\xbf\xff\xdf\xff\xe0\x07\xff\xfb\xff\xfd\xff\xfe\xff\xff\x7f\xff\xbf\xff\xdf\xff\xe0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        
        # draw the keyboard image to the screen
        img = bytearray(kb)
        imgFB = FrameBuffer(img, 128, 32, MONO_HLSB)
        oled.blit(imgFB,0,0)
        
        # mark the enabled notes with a .
        for i in range(len(self.quantizer.scale)):
            if self.quantizer.scale[i]:
                oled.text('.', self.enable_marks[i][0], self.enable_marks[i][1], self.enable_marks[i][2])
        
        # mark the active note with a @
        k = self.quantizer.current_note
        oled.text('+', self.playing_marks[k][0], self.playing_marks[k][1], self.playing_marks[k][2])
        
        # clear the bottom of the screen and mark the togglable key with a line
        oled.fill_rect(0, 30, 128, 32, 0)
        oled.fill_rect(self.enable_marks[self.quantizer.highlight_note][0], 31, 7, 1, 1)
        
        oled.show()
        
    def on_button1(self):
        self.quantizer.scale[self.quantizer.highlight_note] = not self.quantizer.scale[self.quantizer.highlight_note]
        self.quantizer.save()

class MenuScreen:
    def __init__(self, quantizer):
        self.quantizer = quantizer
        
        self.menu_items = [
            ModeChooser(quantizer),
            RootChooser(quantizer),
            IntervalChooser(quantizer, 2),
            IntervalChooser(quantizer, 3),
            IntervalChooser(quantizer, 4),
            IntervalChooser(quantizer, 5)
        ]
        
    def draw(self):
        self.menu_items[self.quantizer.menu_item].draw()
        
    def on_button1(self):
        self.menu_items[self.quantizer.menu_item].on_button1()

class ModeChooser:
    def __init__(self, quantizer):
        self.quantizer = quantizer
        
        self.mode_names = [
            "Trig.",
            "Cont."
        ]
        
    def read_knob(self):
        knob = k2.read_position()
        new_mode = round(linear_rescale(knob, 0, 100, 0, 1))
        return new_mode
        
    def on_button1(self):
        new_mode = self.read_knob()
        self.quantizer.mode = new_mode
        self.quantizer.save()
        
    def draw(self):
        new_mode = self.read_knob()
        oled.fill(0)
        oled.text(f"-- Mode --", 0, 0)
        oled.text(f"{self.mode_names[self.quantizer.mode]} <- {self.mode_names[new_mode]}", 0, 10)
        oled.show()
    
class RootChooser:
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
        
    def read_knob(self):
        knob = k2.read_position()
        new_root = round(linear_rescale(knob, 0, 100, 0, 11))
        return new_root
    
    def on_button1(self):
        new_root = self.read_knob()
        self.quantizer.root = new_root
        self.quantizer.save()
        
    def draw(self):
        new_root = self.read_knob()
        oled.fill(0)
        oled.text(f"-- Root --", 0, 0)
        oled.text(f"{self.root_names[self.quantizer.root]} <- {self.root_names[new_root]}", 0, 10)
        oled.show()

class IntervalChooser:
    def __init__(self, quantizer, n):
        self.quantizer = quantizer
        self.n = n
        self.interval_names = [
            "-P8",
            "-M7",
            "-m7",
            "-M6",
            "-m6",
            "-P5",
            "-d5",
            "-P4",
            "-M3",
            "-m3",
            "-M2",
            "-m2",
            " P1",
            "+m2",
            "+M2",
            "+m3",
            "+M3",
            "+P4",
            "+d5",
            "+P5",
            "+m6",
            "+M6",
            "+m7",
            "+M7",
            "+P8"
        ]
        
    def read_knob(self):
        knob = k2.read_position()
        new_interval = round(linear_rescale(knob, 0, 100, 0, len(self.interval_names)-1))
        new_interval = new_interval - 12
        return new_interval
    
    def on_button1(self):
        new_interval = self.read_knob()
        self.quantizer.intervals[self.n-2] = new_interval
        self.quantizer.save()
        
    def draw(self):
        new_interval = self.read_knob()
        oled.fill(0)
        oled.text(f"-- Output {self.n} --", 0, 0)
        oled.text(f"{self.interval_names[self.quantizer.intervals[self.n-2]+12]} <- {self.interval_names[new_interval+12]}", 0, 10)
        oled.show()

class Quantizer(EuroPiScript):
    def __init__(self):
        super().__init__()
        
        self.mode = MODE_TRIGGERED
        
        # What semitone is the root of the scale?
        # 0 = C, 1 = C#/Db, 2 = D, etc...
        self.root = 0
        
        # Outputs 2-5 output the same note, shifted up or down by
        # a fixed number of semitones
        self.intervals = [0, 0, 0, 0]
        self.aux_outs = [cv2, cv3, cv4, cv5]
        
        # The current scale we're quantizing to
        # Initially a chromatic scale, but this can be changed
        # TODO: load the last-used scale from memory on startup
        self.scale = [True]*12
        
        # The input/output voltages
        self.input_voltage = 0.0
        self.output_voltage = 0.0
        
        # The semitone we're currently outputting on cv1 (0-11)
        self.current_note = 0
        
        # GUI/user interaction
        self.kb = KeyboardScreen(self)
        self.menu = MenuScreen(self)
        self.active_screen = self.kb
        
        self.highlight_note = 0         # the note on the keyboard view we can toggle now
        self.menu_item = 0              # the active item from the advanced menu
        
        self.load()
        
    def load(self):
        state = self.load_state_json()
        
        self.scale = state.get("scale", self.scale)
        self.root = state.get("root", self.root)
        self.intervals = state.get("intervals", self.intervals)
        self.mode = state.get("mode", self.mode)
    
    def save(self):
        state = {
            "scale": self.scale,
            "root": self.root,
            "intervals": self.intervals,
            "mode": self.mode
        }
        self.save_state_json(state)
        
    @classmethod
    def display_name(cls):
        return "Quantizer"
        
    def quantize(self, analog_in):
        # first get the closest chromatic voltage to the input
        nearest_chromatic_volt = round(analog_in / VOLTS_PER_SEMITONE) * VOLTS_PER_SEMITONE
        
        # then convert that to a 0-12 value indicating the nearest semitone
        base_volts = int(nearest_chromatic_volt)
        nearest_semitone = (nearest_chromatic_volt - base_volts) / VOLTS_PER_SEMITONE
        
        # go through our scale and determine the nearest on-scale note
        nearest_on_scale = 0
        best_delta = 255
        for note in range(len(self.scale)):
            if self.scale[note]:
                delta = abs(nearest_semitone - note)
                if delta < best_delta:
                    nearest_on_scale = note
                    best_delta = delta
            
        self.current_note = nearest_on_scale
        self.output_voltage = base_volts + nearest_on_scale * VOLTS_PER_SEMITONE
        
    def read_quantize_output(self):
        self.input_voltage = ain.read_voltage(128)
        self.quantize(self.input_voltage)
        
        cv1.voltage(self.output_voltage)
        
        for i in range(len(self.aux_outs)):
            self.aux_outs[i].voltage(self.output_voltage + self.intervals[i] * VOLTS_PER_SEMITONE)
    
    def on_trigger(self):
        if self.mode == MODE_TRIGGERED:
            self.read_quantize_output()
            cv6.on()
            
    def after_trigger(self):
        if self.mode == MODE_TRIGGERED:
            cv6.off()
            
    def on_button1(self):
        self.active_screen.on_button1()
        
    def on_button2(self):
        if self.active_screen == self.kb:
            self.active_screen = self.menu
        else:
            self.active_screen = self.kb
    
    def main(self):
        # connect the trigger handler here instead of the constructor
        # otherwise it will start quantizing as soon as we instantiate the class
        @din.handler
        def on_rising_clock():
            self.on_trigger()
            
        @din.handler_falling
        def on_falling_clock():
            self.after_trigger()
            
        @b1.handler
        def on_b1_press():
            self.on_button1()
            
        @b2.handler
        def on_b2_press():
            self.on_button2()
        
        while True:
            # Update at 100Hz
            CYCLE_RATE = 0.01
            sleep(CYCLE_RATE)
            
            self.highlight_note = round(linear_rescale(k1.read_position(), 0, 100, 0, len(self.scale)-1))
            self.menu_item = round(linear_rescale(k1.read_position(), 0, 100, 0, len(self.menu.menu_items)-1))
            
            if self.mode == MODE_CONTINUOUS:
                cv6.off()
                last_output = self.output_voltage
                self.read_quantize_output()
                
                if last_output != self.output_voltage:
                    cv6.on()
            
            self.active_screen.draw()
    
if __name__ == "__main__":
    Quantizer().main()
