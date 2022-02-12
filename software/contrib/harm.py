from europi import *

# Overclock the Pico for improved performance.
machine.freq(250_000_000)

class harmonize:
    def __init__(self):
        self.inputVoltage = 0
        self.inputCounter = 0
        self.inputCounterMax = 50
        self.inputCounterArray = [0] * (self.inputCounterMax +1)
        self.maxVoltage = 10
        self.octave_minus_2 = 0
        self.octave_minus_1 = 0
        self.octave_zero = 0
        self.octave_plus_1 = 0
        self.octave_plus_2 = 0
        self.notes = []

        self.counter = 0

        self.generateNotes()
        print(self.notes)
        self.processInput()

    def main(self):
        while True:

            if self.counter % 8 == 0:
                self.processInput()

            self.updateScreen()

            if self.counter < 1024:
                self.counter += 1
            else:
                self.counter = 0        

    def generateNotes(self):
        v = 0
        while v <= 10:
            self.notes.append(v)
            v += (1/12)

    def closestMatch(self, voltage):
        return self.notes[min(range(len(self.notes)), key = lambda i: abs(self.notes[i]-voltage))]

    def processInput(self):
        #self.inputVoltage = ain.read_voltage()
        #self.inputVoltage = round(ain.read_voltage(), 4)
        self.inputVoltage = self.closestMatch(round(ain.read_voltage(), 4))
        #print('Input: ' + str(self.inputVoltage))
        #print('Match: ' + str(self.match))
        #self.inputVoltage = self.match
        #print('Counter: ' + str(self.counter))
        #self.inputCounterArray[self.inputCounter] = round(ain.read_voltage(),1)

        #if self.inputCounter > 1:
        #    self.inputVoltage = sum(self.inputCounterArray) / len(self.inputCounterArray)
        #else:
        #    self.inputVoltage = self.inputCounterArray[self.inputCounter]
        self.octave_zero = self.inputVoltage
        
        if self.inputVoltage >= 2:
            self.octave_minus_2 = self.inputVoltage - 2
        else:
            self.octave_minus_2 = 0

        if self.inputVoltage >= 1:
            self.octave_minus_1 = self.inputVoltage - 2
        else:
            self.octave_minus_1 = 0

        if self.inputVoltage +1 <= self.maxVoltage:
            self.octave_plus_1 = self.inputVoltage + 1
        else:
            self.octave_plus_1 = 0

        if self.inputVoltage +2 <= self.maxVoltage:
            self.octave_plus_2 = self.inputVoltage + 2 
        else:
            self.octave_plus_2 = 0

        #print('1: ' + str(self.octave_minus_2))
        #print('2: ' + str(self.octave_minus_1))
        #print('3: ' + str(self.octave_zero))
        #print('4: ' + str(self.octave_plus_1))
        #print('5: ' + str(self.octave_plus_2))

        cv1.voltage(self.octave_minus_2)
        cv2.voltage(self.octave_minus_1)
        cv3.voltage(self.octave_zero)
        cv4.voltage(self.octave_plus_1)
        cv5.voltage(self.octave_plus_2)

        if self.inputCounter < self.inputCounterMax:
            self.inputCounter +=1
        else:
            self.inputCounter = 0

    def updateScreen(self):
        #oled.clear() - dont use this, it causes the screen to flicker!
        oled.fill(0)
        oled.text('Input: ' + str(self.inputVoltage),0,0,1)
        oled.show()

hm = harmonize()
hm.main()