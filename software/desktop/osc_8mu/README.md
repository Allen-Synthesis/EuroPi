# OSC 8mu Interface

This program is intended to be run on a laptop or desktop with a
[Music Thing Modular 8mu](https://www.musicthing.co.uk/8mu_page/)
connected to it.  It converts the MIDI outputs from 8mu into OSC
messages that can be consumed by EuroPi when properly set up.

## Requirements

### EuroPi

Your EuroPi module must be equipped with a Pico W or Pico 2 W instead
of the standard Pico.

EuroPi's WiFi [must be configured](/software/CONFIGURATION.md#wifi-connection)
with either
1. your computer connected directly to EuroPi's access point, or
2. both your computer and EuroPi connected to the same external network.

Power on EuroPi and run the [`OSC Interface`](/software/contrib/osc_control.md)
program, making note of EuroPi's IP address displayed on the OLED.

### Laptop/Desktop

You must have Python3 installed on your computer, with the following
modules:
- `mido`
- `rtmidi` (via the `python-rtmidi` PyPI package)

To install these, use `pip3` (or `pip`):
```bash
pip3 install mido
pip3 install python-rtmidi
```

Finally, you must own a Music Thing Modular 8mu and have it connected to
your computer using a USB-C cable.

## Running the program

Once EuroPi is running the `OSC Interface` program, start `osc_8mu`
on your desktop by running
```bash
cd /path/to/EuroPi/software/desktop
python3 osc_8mu.py --ip <EuroPi's IP address>
```

Depending on the configuration of 8mu you may need to specify what MIDI
controls will control each output of EuroPi.  For example, if you have
configured 8mu to use controls 20-28 for the sliders, you will need
to run `osc_8mu` with the following command:
```bash
python3 osc_8mu.py --ip 192.168.4.1 --cv1 20 --cv2 21 --cv3 22 --cv4 23 --cv5 24 --cv6 24
```

To override the UDP port, use the `-p|--port` argument. By default `osc_8mu` will use
port 9000 to send UDP packets to EuroPi.

For more information about the available parameters, run
```bash
python3 osc_8mu.py --help
```

## MIDI to OSC to EuroPi conversion

The 8mu slider position is reported as a MIDI value from `0` to `127`. This is converted
to a `0.0` to `1.0` value for OSC, which is then multiplied by `MAX_OUTPUT_VOLTAGE` on
EuroPi to set the value of the output channel. Obviously 128 positions in the MIDI source
doesn't provide super-fine resolution on EuroPi's voltage.

To work around this the `-s|--scale` parameter can be set to provide an additional
scale factor during the MIDI to OSC conversion:

```
X_midi <- Read from 8mu: 0-127

X_osc = X_midi / 127.0 * scale
V_out = X_osc * MAX_OUTPUT_VOLTAGE
```

For example, setting `scale` to 0.1 will reduce EuroPi's output range from 0-10V
to 0-1V, but will compress all 128 steps within the 1V range, allowing finer control
over a smaller voltage range.
