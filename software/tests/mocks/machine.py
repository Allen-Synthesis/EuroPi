

class ADC:
    def __init__(self, *args):
        pass
    
    def read_u16(self, *args):
        pass

class I2C:
    def __init__(self, channel, sda, scl, freq, *args):
        pass

    def scan(self):
        return []

class Pin:
    IN = 'in'

    def __init__(self, id, *args):
        pass

    def irq(self, handler=None, trigger=None):
        pass
    
    def value(self):
        return 1  # default unpressed state

class PWM:
    def __init__(self, *args):
        pass

    def freq(self, f):
        pass

    def duty_u16(self, f):
        pass


def freq(_):
    pass
