from europi import *
from time import sleep_ms, ticks_diff, ticks_ms
from random import randint

'''
Step Sequencer (Inspired by Mutable Grids)
author: Nik Ansell (github.com/gamecat69)
date: 2022-02-03
labels: sequencer, triggers

A very basic EuroPi step sequencer inspired by Grids from Mutable Instruments.
Demo video: TBC

Contains pre-loaded patterns that are cycled through using knob 2.
Includes a feature to toggle randomized high-hat patterns using button 1.
The script needs a clock source in the digital input to play.
Knob 1 can also be used as a clock divider.

digital_in: clock in
analog_in: unused

knob_1: clock divider (1,2,3,4,5,6,7,8,16,32)
knob_2: select pre-loaded drum pattern

button_1: toggle randomized hi-hats on / off
button_2: unused

output_1: trigger 1 / Bass Drum
output_2: trigger 2 / Snare Drum
output_3: trigger 3 / Hi-Hat
output_4: unused
output_5: unused
output_6: unused

'''

'''
To do / Ideas:

- Add more pre-loaded drum patterns
- Add a ratchet function
- Provide auto-generated CV waves/Random from outputs 4-6
- Reduce screen flicker
'''

# Overclock the Pico for improved performance.
machine.freq(250_000_000)

class mainClass:
    def __init__(self):

        # Initialize sequencer pattern arrays        
        self.BD=[]
        self.SN=[]
        self.HH=[]

        # Initialize variables
        self.step = 0
        self.step_length = 16
        self.trigger_duration_ms = 50
        self.clock_step = 0
        self.clock_division = 1
        self.pattern = 0
        self.random_HH = False

        # Pre-loaded patterns
        self.BD.append("1000100010001000")
        self.SN.append("0000100000000000")
        self.HH.append("0001000000000000")

        self.BD.append("1000100010001000")
        self.SN.append("0000100000000000")
        self.HH.append("0001001000000000")

        self.BD.append("1000100010001000")
        self.SN.append("0000100000001000")
        self.HH.append("0000100010001001")

        self.BD.append("1000100010001000")
        self.SN.append("0000100000001000")
        self.HH.append("1111111111111111")

        # Triggered when button 1 is pressed. Toggle random HH feature
        @b1.handler
        def toggle_HH_Randomization():
            self.random_HH = not self.random_HH

        # Triggered on each clock into digital input. Output triggers.
        @din.handler
        def clockTrigger():
            self.setClockDivision()
            self.updateScreen()
            
            if self.clock_step % self.clock_division == 0:
                
                self.pattern = k2.read_position()
            
                cv1.value(int(self.BD[self.pattern][self.step]))
                cv2.value(int(self.SN[self.pattern][self.step]))

                # If randomize HH is ON:
                if self.random_HH:
                    self.t=''
                    self.p=[]
                    for i in range(0, self.step_length):
                        self.t += str(randint(0, 1))
                    self.p.append(self.t)
                    cv3.value(int(self.p[0][self.step]))
                else:
                    cv3.value(int(self.HH[self.pattern][self.step]))
                sleep_ms(self.trigger_duration_ms)
                cv1.off()
                cv2.off()
                cv3.off()
    
            if self.clock_step < 128:
                self.clock_step +=1
            else:
                self.clock_step = 0
    
            if self.step < self.step_length - 1:
                self.step += 1
            else:
                self.step = 0
    
    def main(self):
        while True:
            self.setClockDivision()
            self.updateScreen()
            sleep_ms(100)

    def setClockDivision(self):
        k1Val = k1.read_position()
        if int(k1Val) <= 1:
            self.clock_division = 1
        elif k1Val >= 90:
            self.clock_division = 32
        elif k1Val >= 80:
            self.clock_division = 16           
        elif k1Val >= 70:
            self.clock_division = 8 
        elif k1Val >= 60:
            self.clock_division = 7
        elif k1Val >= 50:
            self.clock_division = 6           
        elif k1Val >= 40:
            self.clock_division = 5 
        elif k1Val >= 30:
            self.clock_division = 4               
        elif k1Val >= 20:
            self.clock_division = 3 
        else:
            self.clock_division = 2

    def updateScreen(self):
        oled.clear()
        oled.text('S:' + str(self.step) + ' ' + 'CD:' + str(self.clock_division), 0, 0, 1)
        oled.text('Pattern: ' + str(self.pattern), 0, 10, 1)
        oled.text('HHR: ' + str(self.random_HH), 0, 20, 1)
        oled.show()

# Reset module display state.
reset_state()
ct = mainClass()
ct.main()


