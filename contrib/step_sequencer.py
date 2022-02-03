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
- Auto reset when the clock-input stops
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
        self.last_clock_input = 0
        # ------------------------
        # Pre-loaded patterns
        # ------------------------
        # 0
        self.BD.append("1000100010001000")
        self.SN.append("0000000000000000")
        self.HH.append("0000000000000000")

        # 1
        self.BD.append("1000100010001000")
        self.SN.append("0000100000000000")
        self.HH.append("0001000000000000")

        # 2
        self.BD.append("1000100010001000")
        self.SN.append("0000100000000000")
        self.HH.append("0001001000000000")

        # 3
        self.BD.append("1000100010001000")
        self.SN.append("0000100000001000")
        self.HH.append("0000100010001001")

        # 4
        self.BD.append("1000100010001000")
        self.SN.append("0000100000001000")
        self.HH.append("1111111111111111")

        # Source: https://docs.google.com/spreadsheets/d/19_3BxUMy3uy1Gb0V8Wc-TcG7q16Amfn6e8QVw4-HuD0/edit#gid=0
        # 5 Billie Jean
        self.BD.append("1000000010000000")
        self.SN.append("0000100000001000")
        self.HH.append("1010101010101010")

        # 6 Funky Drummer
        self.BD.append("1010001000100100")
        self.SN.append("0000100101011001")
        self.HH.append("0000000100000100")

        # 7 Impeach The President
        self.BD.append("1000000110000010")
        self.SN.append("0000100000001000")
        self.HH.append("1010101110001010")

        # 8 When the Levee Breaks
        self.BD.append("1100000100110000")
        self.SN.append("0000100000001000")
        self.HH.append("1010101010101010")

        # 9 Walk this way
        self.BD.append("1000000110100000")
        self.SN.append("0000100000001000")
        self.HH.append("0010101010101010")

        # 10 Its a new day
        self.BD.append("1010000000110001")
        self.SN.append("0000100000001000")
        self.HH.append("1010101010101010")

        # 11 Papa was Too
        self.BD.append("1000000110100001")
        self.SN.append("0000100000001000")
        self.HH.append("0000100010101011")

        # 12 The Big Beat
        self.BD.append("1001001010000000")
        self.SN.append("0000100000001000")
        self.HH.append("0000100000001000")

        # 13 Ashleys Roachclip
        self.BD.append("1010001001100000")
        self.SN.append("0000100000001000")
        self.HH.append("1010101010001010")

        # 14 Synthetic Substitution
        self.BD.append("1010000101110001")
        self.SN.append("0000100000001000")
        self.HH.append("1010101010001010")

        # Triggered when button 1 is pressed. Toggle random HH feature
        @b1.handler
        def toggle_HH_Randomization():
            self.random_HH = not self.random_HH

        # Triggered on each clock into digital input. Output triggers.
        @din.handler
        def clockTrigger():
            #self.setClockDivision()
            self.updateScreen()
            self.last_clock_input = ticks_ms()
            
            if self.clock_step % self.clock_division == 0:
                
                # Prevent the pattern number from going higher than the max number of patterns
                if k2.read_position() <= len(self.BD)-1:
                    self.pattern = k2.read_position()
                else:
                    self.pattern = len(self.BD)-1

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
            #self.setClockDivision()
            self.updateScreen()
            self.reset_timeout = 500
            # If I have been stopped for longer than reset_timeout, reset the steps and clock_step to 0
            if ticks_diff(ticks_ms(), self.last_clock_input) > self.reset_timeout:
                self.step = 0
                self.clock_step = 0
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
        #oled.text('S:' + str(self.step) + ' ' + 'CD:' + str(self.clock_division), 0, 0, 1)
        oled.text('S:' + str(self.step) + ' ', 0, 0, 1)
        oled.text('Pattern: ' + str(self.pattern) + ' / ' + str(len(self.BD)-1), 0, 10, 1)
        oled.text('HHR: ' + str(self.random_HH), 0, 20, 1)
        oled.show()

# Reset module display state.
reset_state()
ct = mainClass()
ct.main()
