from europi import *
import machine
from europi_script import EuroPiScript
from time import ticks_diff, ticks_ms

'''
NoddyHolder
author: Sean Bechhofer (github.com/seanbechhofer)
date: 2022-03-26
labels: sample & hold, trigger & hold

Two channels of sample and hold/trigger and hold. 

Digital in: Gate
Analog in: CV

Output 1: Gate
Output 2: Sample and Hold based on Gate and CV
Output 3: Trigger and Hold based on Gate and CV

Output 4: Inverted Gate
Output 5: Sample and Hold based on Inverted Gate and CV
Output 6: Trigger and Hold based on Inverted Gate and CV

digital_in: gate
analog_in: cv

knob_1: Not used
knob_2: Not used

button_1: Not used
button_2: Not used

output_1: gate 
output_2: s&h
output_3: t&h
output_4: inverted gate
output_5: s&h using inverted gate
output_6: t&h using inverted gate

'''
# Version number

VERSION="1.0"


class NoddyHolder(EuroPiScript):
    def __init__(self):
        # Overclock the Pico for improved performance.
        machine.freq(250_000_000)

        self.gate = False
        # Keep track of values for display, S&H and T&H for each
        # channel
        self.channel_1 = [0,-1]
        self.channel_2 = [0,-1]
        
        # Triggered when din goes HIGH.
        @din.handler
        def dinTrigger():
            self.gate = True
            # Sample input
            sample = ain.read_voltage()
            # Set mirrored gate HIGH
            cv1.on()
            # Set inverse gate LOW
            cv4.off()

            # Set S&H to sample
            cv2.voltage(sample)
            self.channel_1[0] = sample
            # Channel 1 is now tracking
            
            self.channel_1[1] = -1
            # Set T&H of inverted gate to sample
            cv6.voltage(sample)
            self.channel_2[1] = sample
            self.update_screen()


        @din.handler_falling
        def dinTriggerEnd():
            self.gate = False
            # Sample input
            sample = ain.read_voltage()
            # Set mirrored gate LOW
            cv1.off()
            # Set inverse gate HIGH
            cv4.on()

            # Set T&H of gate to sample
            cv3.voltage(sample)
            self.channel_1[1] = sample
            # Set S&H of inverted gate to sample
            cv5.voltage(sample)
            self.channel_2[0] = sample
            # Channel 2 is now tracking
            self.channel_2[1] = -1
            self.update_screen()

    def update(self):
        # Sample input
        sample = ain.read_voltage()
        if self.gate:
            # Pass sample to T&H
            cv3.voltage(sample)
        else:
            # Pass sample to inverted T&H 
            cv6.voltage(sample)

    def main(self):
        self.update_screen()
        while True:
            self.update()
            
    def update_screen(self):
        oled.fill(0)
        oled.text(f"Noddy v{VERSION}",0,0,1)
        oled.text("1",0,8,1)
        oled.text("2",0,16,1)

        if self.gate:
            oled.fill_rect(10,8,10,6,1)
        else:
            oled.fill_rect(10,16,10,6,1)
            
        oled.text(f"S:{self.channel_1[0]:.2f}",25,8,1)
        oled.text(f"S:{self.channel_2[0]:.2f}",25,16,1)

        if self.gate:
            oled.text(f"T:T",80,8,1)
            oled.text(f"T:{self.channel_2[1]:.2f}",80,16,1)
        else:
            oled.text(f"T:{self.channel_1[1]:.2f}",80,8,1)
            oled.text(f"T:T",80,16,1)
        oled.show()

if __name__ == "__main__":
    NoddyHolder().main()
