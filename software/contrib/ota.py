from time import sleep
from europi import oled, b1, din
from europi_script import EuroPiScript
import _webrepl
import network
import netcreds
import os
import webrepl

'''

OTA - Over the Air
author: 303sec (github.com/303sec)
date: 2022-10-30
labels: utility

A script to allow for using MicroPython's WebREPL with the EuroPi.

Using the WebREPL interface allows the Pico to run Python from a browser over WiFi by accessing the IP address and port on the OLED Display, using the password '3ur0P1'.

A Pi Pico W is required for this script to work, with network creds configured in the netcreds.py file.

'''

class OTA(EuroPiScript):
    def __init__(self):
        super().__init__()
        state = self.load_state_json()

    @classmethod
    def display_name(cls):
        return "OTA Flash"

    def main(self):
        if not "Raspberry Pi Pico W" in os.uname().machine:
            while(True):
                oled.centre_text("Requires Pico W")
        try:
            import netcreds
        except:
            while(True):
                oled.centre_text("Requires netcreds.py")

        # Connect to WiFi
        oled.centre_text("Connecting...")        
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        wlan.connect(netcreds.SSID, netcreds.PASSWORD)
        i = 0
        while(network.WLAN(network.STA_IF).status() != 3):
            sleep(1)
            i += 1
            if i == 15:
                while(True):
                    oled.centre_text('Error connecting.')
        status = network.WLAN(network.STA_IF).status()
        webrepl_details = wlan.ifconfig()[0] + '\nPort: 8266'
        oled.centre_text(webrepl_details)
        webrepl.start()

if __name__ == "__main__":
    OTA().main()