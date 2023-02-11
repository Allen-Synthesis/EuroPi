"""
Variable-scale, equal-temperment quantizer for the EuroPi
"""

from europi import *
from europi_script import EuroPiScript
from time import sleep

# 1.0V/O is the Eurorack/Moog standard, but Buchla uses 1.2V/O
# Just in case someone needs Buchla compatibility, make this editable
VOLTS_PER_OCTAVE = 1.0
SEMITONES_PER_OCTAVE = 12
VOLTS_PER_SEMITONE = VOLTS_PER_OCTAVE / float(SEMITONES_PER_OCTAVE)

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
        
        oled.show()
    

class Quantizer(EuroPiScript):
    def __init__(self):
        super().__init__()
        
        # What semitone is the root of the scale?
        # 0 = C, 1 = C#/Db, 2 = D, etc...
        # NOT IMPLEMENTED YET
        self.root = 0
        
        # Outputs 2-5 output the same note, shifted up or down by
        # a fixed number of semitones
        self.intervals = [0, 0, 0, 0]
        self.aux_outs = [cv2, cv3, cv4, cv5]
        
        # The current scale we're quantizing to
        # Initially a chromatic scale, but this can be changed
        # TODO: load the last-used scale from memory on startup
        self.scale = [True]*12
        
        self.input_voltage = 0.0
        self.current_note = 0
        self.output_voltage = 0.0
        
        self.kb = KeyboardScreen(self)
        
    @classmethod
    def display_name(cls):
        return "Quantizer"
    
    def draw_ui(self):
        self.kb.draw()
        
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
        
    def on_trigger(self):
        self.input_voltage = ain.read_voltage(128)
        self.quantize(self.input_voltage)
        
        cv1.voltage(self.output_voltage)
        
        for i in range(len(self.aux_outs)):
            self.aux_outs[i].voltage(self.output_voltage + self.intervals[i] * VOLTS_PER_SEMITONE)
    
    def main(self):
        # connect the trigger handler here instead of the constructor
        # otherwise it will start quantizing as soon as we instantiate the class
        @din.handler
        def on_rising_clock():
            self.on_trigger()
        
        while True:
            # 5ms cycle rate
            CYCLE_RATE = 0.01
            sleep(CYCLE_RATE)
                
            self.draw_ui()
    
if __name__ == "__main__":
    Quantizer().main()