import machine
from europi_script import EuroPiScript
from europi import b1, b2, oled
from os import remove


class BootloaderMode(EuroPiScript):
    @classmethod
    def display_name(cls):
        """Push this script to the end of the menu."""
        return "~Bootloader Mode"

    def back(self):
        try:
            remove(
                "saved_state_BootloaderMenu.txt"
            )  # This file needs to be removed so that the menu is returned to rather than this script once it's entered bootloader mode
        except OSError:
            print("OSError: File Not Found")
        machine.reset()  # Restart the module so that it will boot back into the menu

    def enter_bootloader(self):
        machine.bootloader()  # Enter bootloader mode

    def main(self):
        b1.handler(self.back)  # Button 1 returns to the menu system
        b2.handler(self.enter_bootloader)  # Button 2 sends the module into bootloader mode

        oled.fill(0)
        oled.text("B1 = Back", 0, 6)
        oled.text("B2 = Bootloader", 0, 18)
        oled.show()


if __name__ == "__main__":
    BootloaderMode().main()
