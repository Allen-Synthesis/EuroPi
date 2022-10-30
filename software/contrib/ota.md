# EuroPi Over the Air - OTA

## Requirements

This needs to use the Pi Pico W to run, as it has the WiFi chip on board.

The minimum micropython build is v1.19.1.169 (nightly), [downloadable from here](https://micropython.org/download/rp2-pico/).

## Setup

Create a file 'netcreds.py' in the root directory (the same as your main.py script). This file should contain the following:

```python
SSID = "your_wifi_ssid"
PASSWORD = "your_wifi_password"
```

You'll also need to copy over the webrepl.py and webrepl_setup.py scripts into the root directory of the pico from https://github.com/micropython/micropython-lib/tree/master/micropython/net/webrepl. This should not be a requirement in MicroPython v1.20 (see https://github.com/micropython/webrepl/issues/71 for more details)

In the Thonny REPL (with your Pico W connected with a wire), run `import webrepl_setup` and follow the instructions to set up the webrepl (setting up a password to access the REPL, etc).

## Usage

When using EuroPi's menu.py, the option 'OTA' should be available. Selecting this will start the WebREPL, allowing you to upload/download files and run scripts over WiFi by using the browser. Simply visit the IP address and port of the Pi Pico W, which should be visible on the OLED display - e.g. `http://<ip_address>:8266`

The code you run will have full access to the EuroPi's CV outputs (and you can import europi), allowing for live audio coding and simplified debugging when creating your own scripts.

For more information about WebREPL, see https://docs.micropython.org/en/latest/esp8266/tutorial/repl.html#webrepl-a-prompt-over-wifi