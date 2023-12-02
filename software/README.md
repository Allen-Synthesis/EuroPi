# EuroPi Software

See the EuroPi firmware API documentation here: https://allen-synthesis.github.io/EuroPi/generated/europi.html

## Testing

In order to run the automated tests locally you'll need to install the development dependencies in a virtual
environment. Our deployment uses Python 3.8. Install the development requirements with:

```console
$ pip install -r software/requirements_dev.txt
```

You can then run the tests locally with:

 ```console
 $ pytest
 ```

 ### Updating the development requirements

Occasionally, a new requirement is added, or an existing requirement needs to be updated. To do so, first add or update
the requirements in ``software/requirements_dev.in``. Be sure that any newly added requirements are pinned to a specific
version. Then, regenerate the ``requirements_dev.txt`` by executing the tool ``pip-compile``:

```console
$ pip-compile software/requirements_dev.in
```

Both the ``software/requirements_dev.in`` and the generated ``software/requirements_dev.txt`` files should be committed.

## Configuration Customization

Certain properties of the module, such as screen rotation, CPU clock speed, and Raspberry Pi Pico model, can be
set using a static configuration file.  This file is located at `/config/config_EuroPiConfig.json` on the
Raspberry Pi Pico. If this file does not exist, default settings will be loaded.  The following shows the
default configuration:
```json
{
    "europo_model": "europi",
    "pico_model": "pico",
    "cpu_freq": 250000000,
    "rotate_display": false,
    "display_width": 128,
    "display_height": 32,
    "volts_per_octave": 1.0,
    "max_output_voltage": 10,
    "max_input_voltage": 12
}
```

- `europo_model` specifies the type of EuroPi module. Currently only `"europi"` is supported, but in future this
  may be expanded to include `"europi_lc"` for the low-cost version and `"europi_x"` for the larger version with
  more jacks
- `pico_model` must be one of `"pico"` or `"pico w"`
- `cpu_freq` must be one of `250000000` or `125000000`
- `rotate_display` must be one of `false` or `true`
- `display_width` is the width of the screen in pixels. The standard EuroPi screen is 128 pixels wide
- `display_height` is the height of the screen in pixels. The standard EuroPi screen is 32 pixels tall
- `volts_per_octave` must be one of `1.0` (Eurorack standard) or `1.2` (Buchla standard)
- `max_output_voltage` is an integer in the range `[0, 10]` indicating the maximum voltage CV output can generate.
  The hardware is capable of 10V maximum
- `max_input_voltage` is an integer in the range `[0, 12]` indicating the maximum allowed voltage into the `ain` jack.
  The hardware is capable of 12V maximum
