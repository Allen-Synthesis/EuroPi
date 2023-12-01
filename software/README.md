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
    "pico_model": "pico",
    "cpu_freq": 250000000,
    "rotate_display": false,
    "volts_per_octave": 1.0
}
```

- `pico_model` must be one of `"pico"` or `"pico w"`
- `cpu_freq` must be one of `250000000` or `125000000`
- `rotate_display` must be one of `false` or `true`
- `volts_per_octave` must be one of `1.0` (Eurorack standard) or `1.2` (Buchla standard)
