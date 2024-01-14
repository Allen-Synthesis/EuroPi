from machine import bootloader, reset
from europi_script import EuroPiScript
from europi import b1, b2, oled
from os import remove


class UpdateFirmware(EuroPiScript):
    @classmethod
    def display_name(cls):
        """Push this script to the end of the menu."""
        return "~Update Firmware"
        
    def back(self):
        try:
            remove('saved_state_BootloaderMenu.txt')
        except OSError:
            print('OSError: File Not Found')
        reset()
    
    def enter_bootloader(self):
        bootloader()
        
    def main(self):
        b1.handler(self.back)
        b2.handler(self.enter_bootloader)
        
        oled.fill(0)
        oled.text('B1 = Back',0,6)
        oled.text('B2 = Bootloader',0,18)
        oled.show()
        
if __name__ == "__main__":
    UpdateFirmware().main()
    