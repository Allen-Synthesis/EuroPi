import configuration
from configuration import ConfigFile, ConfigSpec

# Pico machine CPU freq.
# Default pico CPU freq is 125_000_000 (125mHz)
PICO_DEFAULT_CPU_FREQ = 125_000_000
OVERCLOCKED_CPU_FREQ = 250_000_000

# Moog/Eurorack standard is 1.0 volts per octave
MOOG_VOLTS_PER_OCTAVE = 1.0

# Buchla standard is 1.2 volts per octave (0.1 volts per semitone)
BUCHLA_VOLTS_PER_OCTAVE = 1.2

class EuroPiConfig:
    """This class provides EuroPi's global config points.

    To override the default values, create /config/config_EuroPiConfig.json on the Raspberry Pi Pico
    and populate it with a JSON object. e.g. if your build has the oled mounted upside-down compared
    to normal, the contents of /config/config_EuroPiConfig.json should look like this:

    {
        "rotate_display": true
    }
    """

    @classmethod
    def config_points(cls):
        return [
            configuration.choice(name="pico_model", choices=["pico", "pico w"], default="pico"),
            configuration.choice(
                name="cpu_freq",
                choices=[PICO_DEFAULT_CPU_FREQ, OVERCLOCKED_CPU_FREQ],
                default=OVERCLOCKED_CPU_FREQ,
            ),
            configuration.choice(name="rotate_display", choices=[False, True], default=False),
            configuration.choice(
                name="volts_per_octave",
                choices=[MOOG_VOLTS_PER_OCTAVE, BUCHLA_VOLTS_PER_OCTAVE],
                default=MOOG_VOLTS_PER_OCTAVE
            ),
        ]


def load_europi_config():
    return ConfigFile.load_config(EuroPiConfig, ConfigSpec(EuroPiConfig.config_points()))
