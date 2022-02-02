from europi import *
from random import randint
from time import sleep

# Reset EuroPi to a default state
# Clears the screen, sets all CV outputs to 0v and resets the handlers for buttons and digital input
reset_state()

level  = cv6
timbre = cv2
morph  = cv4
harmo  = cv5

step = 0
harmo.off()

while True:

    # Vary the speed using knob1 (k1)
    delay = 1 - (k1.read_position(100)/100)

    # Write the delay between cycles to the screen
    oled.clear()
    oled.text("Step: " + str(step),0,0,1)
    oled.text("Delay: " + str(delay),0,10,1)
    oled.show()

    # Set level to 5v
    level.voltage(5)

    # On every 4th step, set timbre to a random voltage between 0 and 5
    if step % 4 == 0:
        timbre.voltage(randint(0,5))

    # On every 8th step, set timbre to a random voltage between 0 and 5
    if step % 8 == 0:
        morph.voltage(randint(0,5))
    
    # On every 16th step, toggle the value
    if step % 16 == 0:
        harmo.toggle()

    sleep(delay)

    level.off()
    timbre.off()
    morph.off()
    sleep(delay)

    step +=1
