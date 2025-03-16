# HTTP Interface

This program provides a simple HTTP interface to control the levels of CV1-6.

It requires that your EuroPi have a Raspberry Pi Pico W or Pico 2 W. See
[wireless configuration](/software/CONFIGURATION.md#wifi-connection) for
instructions on configuring the Pico W/Pico 2 W's wifi.

## Accessing the web interface

To access the web interface, connect your device (phone/tablet/desktop/laptop/etc...)
to the same wifi network at EuroPi (or to EuroPi's access point if you have
the wifi interface set up in AP mode).  Then navigate to the IP address
displayed on the screen, e.g. `http://192.168.4.1`.

The web interface has six sliders. Each of these can be moved to set the output voltage
of one of the corresponding outputs.

## I/O Summary

CV1-6 will output voltages as specified by the web interface.

The buttons, knobs, `ain`, and `din` are not used by this program.

## Note on concurrent users

There is no authentication no restriction on the number of concurrent
browser connections. It is recommended to only use one device at a time
to control EuroPi over HTTP.
