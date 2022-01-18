from europi import *
from utime import sleep_ms

def test_input():
    oled.centre_text(f"digital:{din.value()}\n analog:{ain.read_voltage()}")

def test_knobs():
    oled.centre_text(f"k1:{k1.read_position()}\n k2:{k2.read_position()}")

def test_buttons():
    oled.centre_text(f"b1:{b1.value()}\n b2:{b2.value()}")

def test_digital_output():
    for idx, output in enumerate(cvs):
        oled.centre_text(f"out {idx+1} on")
        output.on()
        sleep_ms(2000)
        output.off()

def test_analogue_output():
    volts = 0
    while True:
        for output in cvs:
            if volts > 10:
                sleep_ms(20)
                volts = 0
                [o.voltage(0) for o in cvs]
            oled.centre_text(f"outputs rising:\n{volts:0.2f}")
            output.voltage(volts)
            volts += 0.1
            sleep_ms(20)


while True:
    ## Uncomment each function individually to test that part of the EuroPi.
    test_input()
    #test_knobs()
    #test_buttons()
    #test_digital_output()
    #test_analogue_output()
    sleep_ms(10)
