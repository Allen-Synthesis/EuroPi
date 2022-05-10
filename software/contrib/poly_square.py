from europi import *
import machine
from rp2 import PIO, StateMachine, asm_pio
from europi_script import EuroPiScript

'''
Poly Square
author: Tyler Schreiber (github.com/t-schreibs)
date: 2022-05-10
labels: oscillator, poly

A poly square oscillator with detuning & several polyphony modes. The analog
input receives a V/oct and sets the central pitch of the 3 oscillators, and knob
1 sets the spread of the detuning across the oscillators. Knob 2 sets the
polyphony mode of the oscillators, which output on CVs 1-3.

digital_in: unused
analog_in: V/oct

knob_1: detune
knob_2: polyphony mode

button_1: while depressed, 'tuning mode' is turned on; this changes the knob functionality:
    knob_1: coarse tune (up to an octave swing)
    knob_2: fine tune (up to a half step swing)

output_1: oscillator 1
output_2: oscillator 2
output_3: oscillator 3
output_4: unused
output_5: unused
output_6: unused
'''

# Assembly code program for the PIO square oscillator
# Thanks to Ben Everard at HackSpace for the basis of this program: 
# https://hackspace.raspberrypi.com/articles/raspberry-pi-picos-pio-for-mere-mortals-part-3-sound
@asm_pio(sideset_init=PIO.OUT_LOW)
def square_prog():
    # Initialize x & y variables - these are used to count down the 
    # loops which set the length of the square wave's cycle
    label("restart")
    pull(noblock) .side(0)
    mov(x, osr)
    mov(y, isr)
    # Start loop
    # Here, the pin is low, and it will count down y
    # until y=x, then set the pin high and jump to the next section
    label("up_loop")
    jmp(x_not_y, "skip_up")
    nop()         .side(1)
    jmp("down")
    label("skip_up")
    jmp(y_dec, "up_loop")    
    # Mirror the above loop, but with the pin high to form the second
    # half of the square wave
    label("down")
    mov(y, isr)
    label("down_loop")
    jmp(x_not_y, "skip_down")
    nop() .side(0)
    jmp("restart")
    label("skip_down")
    jmp(y_dec, "down_loop")

# Class for managing the settings for a polyphony mode
class PolyphonyMode:
    def __init__(self, name, voltage_offsets):
        self.name = name
        self.voltage_offsets = voltage_offsets   
    
# Class for managing a state machine running the PIO oscillator program
class SquareOscillator:
    def __init__(self, sm_id, pin, max_count, count_freq):
        self._sm = StateMachine(sm_id, square_prog,
            freq=2 * count_freq, sideset_base=Pin(pin))
        # Use exec() to load max count into ISR
        self._sm.put(max_count)
        self._sm.exec("pull()")
        self._sm.exec("mov(isr, osr)")
        self._sm.active(1)
        self._max_count = max_count
        self._count_freq = count_freq

    def set(self, value):
        # Minimum value is -1 (completely turn off), 0 actually still
        # produces a narrow pulse
        value = max(value, -1)
        value = min(value, self._max_count)
        self._sm.put(value)
            
    # Converts Hertz to the value the state machine running the PIO
    # program needs
    def get_pitch(self, hertz):
        return int( -1 * (((self._count_freq / hertz) -
            (self._max_count * 4))/4))

class PolySquare(EuroPiScript):
    def __init__(self):
        # Settings for improved performance
        machine.freq(250_000_000)
        k1.set_samples(32)
        k2.set_samples(32)        
        # PIO settings
        max_count = 1_000_000
        count_freq = 50_000_000
        self.oscillators = [
            SquareOscillator(0, 21, max_count, count_freq),
            SquareOscillator(1, 20, max_count, count_freq),
            SquareOscillator(2, 16, max_count, count_freq)
        ]
        # To add more polyphony modes, include them in this list. The offsets
        # are V/oct offsets (ie, a 5th = 7/12, an octave = 1, etc.). The number
        # of offsets in the tuple must match the length of the self.oscillators
        # list above.
        self.modes = [
            PolyphonyMode("Unison", (0, 0, 0)),
            PolyphonyMode("5th", (0, 0, 7/12)),
            PolyphonyMode("Octave", (0, 0, 1)),
            PolyphonyMode("Power chord", (0, 7/12, 1)),
            PolyphonyMode("Stacked 5ths", (0, 7/12, 14/12)),
            PolyphonyMode("Minor triad", (0, 7/12, 15/12)),
            PolyphonyMode("Major triad", (0, 7/12, 16/12)),
            PolyphonyMode("Diminished", (0, 6/12, 15/12)),
            PolyphonyMode("Augmented", (0, 8/12, 16/12)),
            PolyphonyMode("Major 6th", (0, 4/12, 9/12)),
            PolyphonyMode("Major 7th", (0, 4/12, 11/12)),
            PolyphonyMode("Minor 7th", (0, 3/12, 10/12))
        ]
        self.current_mode = None
        self.ui_update_requested = True
        self.detune_amount = None
        self.coarse_tune = .5
        self.fine_tune = .5
        self.tuning_mode = False
        self.load_state()

        @b1.handler
        def tuning_mode_on():
            self.tuning_mode = True
            self.ui_update_requested = True

        @b1.handler_falling
        def tuning_mode_off():
            self.tuning_mode = False
            self.ui_update_requested = True
            # Saves the tuning settings when the button is released
            self.save_state()
        
    # Converts V/oct signal to Hertz, with 0V = C0
    def get_hertz(self, voltage):
        # Start with A0 because it's a nice, rational number
        a0 = 27.5
        # Subtract 3/4 from the voltage value so that 0V = C0
        return a0 * 2 ** (voltage - 3/4)
    
    # Returns the linear step distance between elements such that all are
    # equally spaced. Ex, for 6 elements between 0 and 100 (inclusive), the
    # step would be 20 (the elements would then be 0, 20, 40, 60, 80, 100).
    def get_step_distance(self, first, last, count):
        return (last - first) / (count - 1)
    
    # Returns the total voltage offset of the current tuning values
    def get_tuning(self):
        return self.coarse_tune - .5 + (self.fine_tune - .5) / 12
    
    # Through-zero detuning of current oscillator based on its position in
    # the list of oscillators - the central oscillator (assuming an odd 
    # number of oscillators) stays in tune while the outer oscillators are 
    # progressively detuned.
    def get_detuning(self, detune_amount, oscillator):
        step_distance = self.get_step_distance(0, 1, len(self.oscillators))
        return detune_amount * (step_distance *
            self.oscillators.index(oscillator) - step_distance)
    
    # Returns a voltage offset for the oscillator based on the current
    # polyphony mode. This allows for things like triads, with the offsets
    # set accordingly.
    def get_offset(self, oscillator):
        return self.modes[self.current_mode].voltage_offsets[
            self.oscillators.index(oscillator)]
    
    # Saves oscillator tuning settings
    def save_state(self):
        settings = {"c": self.coarse_tune, "f": self.fine_tune}
        self.save_state_json(settings)

    # Loads oscillator tuning settings
    def load_state(self):
        settings = self.load_state_json()
        if "c" in settings:
            self.coarse_tune = settings["c"]
        if "f" in settings:
            self.fine_tune = settings["f"]
    
    def update_ui(self):
        if self.tuning_mode:
            text = ("Tuning Mode\ncoarse: " + str(self.coarse_tune - .5) +
                "\nfine: " + str(self.fine_tune - .5))
        else:
            text = "Super Square\n" + self.modes[self.current_mode].name
        oled.centre_text(text)
        self.ui_update_requested = False
    
    # Analog input - V/oct
    # Knob 1 - detune, up to a full half step across all voices
    # Knob 2 - polyphony mode
    # Button 1 - repurposes both knobs for tuning while depressed:
    #   Knob 1 - coarse tune (up to an octave swing)
    #   Knob 2 - fine tune (up to a half step)
    def update_settings(self):
        analog_input = ain.read_voltage(32)
        if self.tuning_mode:
            new_coarse_tune = k1.read_position(24) / 24
            new_fine_tune = k2.read_position(50) / 50
            if (not new_coarse_tune == self.coarse_tune or
                not new_fine_tune == self.fine_tune):
                self.coarse_tune = new_coarse_tune
                self.fine_tune = new_fine_tune
                self.ui_update_requested = True
        else:
            self.detune_amount = k1.read_position(100) / 1200
            new_mode = k2.read_position(len(self.modes))
            if not new_mode == self.current_mode:
                self.ui_update_requested = True
                self.current_mode = new_mode
        for oscillator in self.oscillators:
            # Add up the V/oct from the analog input, the offset from the 
            # polyphony mode, the adjustment from the tuning, and the 
            # adjustment from the detune amount to get the final pitch for 
            # the oscillator
            oscillator.set(oscillator.get_pitch(
                self.get_hertz(
                    analog_input + self.get_offset(oscillator) +
                    self.get_tuning() +
                    self.get_detuning(self.detune_amount, oscillator))))

    def main(self):
        while True:
            self.update_settings()
            if self.ui_update_requested:
                self.update_ui()

# Main script execution
if __name__ == '__main__':
    PolySquare().main()