# Open Sound Control (OSC)

This program allows the use of Open Sound Control packets over UDP to control
EuroPi.

## OSC Addresses

The following addresses are used by the program (noting that the `/europi` namespace
can be changed; see below):

- `/europi/cv1`
- `/europi/cv2`
- `/europi/cv3`
- `/europi/cv4`
- `/europi/cv5`
- `/europi/cv6`

All of the above will accept float or integer data. Floats are treated as the 0-1
level for CV control. Integers are treated as boolean on/off signals (0 for off, anything
else for on).

- `/europi/cvs`

The above accepts 6 parameters of either float or integer, and will set all 6 outputs
with a single packet.

**Not yet implemented**

In addition to the input addresses above, EuroPi will broadcast the following addresses
at 10Hz:

- `/europi/ain`: float, the 0-1 input level
- `/europi/k1`: float, the knob position as a value in the range 0-1
- `/europi/k2`: float, the knob position as a value in the range 0-1
- `/europi/din`: integer, a 0/1 value indicating if the input is off or on
- `/europi/b1`: integer, a 0/1 value indicating if the button is pressed or not
- `/europi/b2`: integer, a 0/1 value indicating if the button is pressed or not

## Multiple EuroPi on the same network

If you have more than one EuroPi you may find it desirable to assign each their own
namespace. Otherwise by moving one fader on your OSC input device you may control
all EuroPis at once.

Create `/config/OscControl.json` to set the namespace:

```json
{
    "NAMESPACE": "/europi_1"
}
```

## Changing the port

TouchOSC uses UDP port 9000 by default, so that's what EuroPi looks for. To override
the default with a different port, set the port in `/config/OscControl.json`, e.g.:

```json
{
    "PORT": 6024
}
```

## Configuring TouchOSC

[TouchOSC](https://hexler.net/touchosc) is a commercial program available for a variety
of platforms that allows you to create custom OSC input interfaces.

The simplest way to control EuroPi via TouchOSC is to add six sliders to your panel.
Then edit each slider to set its name to `europi/cvN` where `N` is the number `1` to
`6`.

![TouchOSC Setup](./osc_control-docs/touchosc-setup.png)

_Configuring a slider's name in TouchOSC on Android_

Then configure TouchOSC's `OSC` connection to connect to your EuroPi's IP address. Your
phone/table must either be connected to EuroPi's access point, or both must be connected
to the same wifi network.

Once configured, start TouchOSC's interface by pressing the triangular "Play" button.

![TouchOSC Setup](./osc_control-docs/touchosc-sliders.png)

_TouchOSC's sliders_

EuroPi's OLED will show bars indicating the levels of TouchOSC's sliders

![EuroPi OLED](./osc_control-docs/osc-oled.jpg)

_EuroPi's OLED showing the same slider levels as TouchOSC_
