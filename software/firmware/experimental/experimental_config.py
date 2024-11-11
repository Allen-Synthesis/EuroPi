"""Additional configuration settings for experimental firmware features

Any scripts in firmware/experimental that need editiable, persistent settings should use this. If/when
they're moved out of experimental, their associated settings should be migrated to europi_config.py
"""

import configuration
from configuration import ConfigFile, ConfigSpec

# Moog/Eurorack standard is 1.0 volts per octave
MOOG_VOLTS_PER_OCTAVE = 1.0

# Buchla standard is 1.2 volts per octave (0.1 volts per semitone)
BUCHLA_VOLTS_PER_OCTAVE = 1.2


class ExperimentalConfig:
    """This class provides global config points for experimental features.

    To override the default values, create /config/config_ExperimentalConfig.json on the Raspberry Pi Pico
    and populate it with a JSON object. e.g. if your build needs Buchla compatibility using 1.2V/octave
    quantization, it should look like this:

    {
        "VOLTS_PER_OCTAVE": 1.2
    }
    """

    @classmethod
    def config_points(cls):
        # fmt: off
        return [
            # Quantizer settings
            # Normally this is intended for Eurorack compatibility, but being open-source someone may
            # want to use it in an ecosystem that uses different specs
            configuration.choice(
                name="VOLTS_PER_OCTAVE",
                choices=[MOOG_VOLTS_PER_OCTAVE, BUCHLA_VOLTS_PER_OCTAVE],
                default=MOOG_VOLTS_PER_OCTAVE,
            ),
        ]
        # fmt: on


def load_experimental_config():
    return ConfigFile.load_config(
        ExperimentalConfig, ConfigSpec(ExperimentalConfig.config_points())
    )
