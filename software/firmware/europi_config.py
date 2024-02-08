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
        # fmt: off
        return [
            # EuroPi revision -- this is currently unused, but reserved for future expansion
            configuration.choice(
                name="europi_model",
                choices = ["europi"],
                default="europi"
            ),

            # CPU & board settings
            configuration.choice(
                name="pico_model",
                choices=["pico", "pico w"],
                default="pico"
            ),
            configuration.choice(
                name="cpu_freq",
                choices=[PICO_DEFAULT_CPU_FREQ, OVERCLOCKED_CPU_FREQ],
                default=OVERCLOCKED_CPU_FREQ,
            ),

            # Display settings
            configuration.boolean(
                name="rotate_display",
                default=False
            ),
            configuration.integer(
                name="display_width",
                range=range(8, 1024),
                default=128
            ),
            configuration.integer(
                name="display_height",
                range=range(8, 1024),
                default=32
            ),

            # Synthesizer family settings
            # Normally this is intended for Eurorack compatibility, but being open-source someone may
            # want to use it in an ecosystem that uses different specs
            configuration.choice(
                name="volts_per_octave",
                choices=[MOOG_VOLTS_PER_OCTAVE, BUCHLA_VOLTS_PER_OCTAVE],
                default=MOOG_VOLTS_PER_OCTAVE,
            ),
            configuration.integer(
                name="max_output_voltage",
                range=range(1, 11),
                default=10
            ),
            configuration.integer(
                name="max_input_voltage",
                range=range(1, 13),
                default=12
            ),
            configuration.integer(
                name="gate_voltage",
                range=range(1, 13),
                default=5
            ),
        ]
        # fmt: on


def load_europi_config():
    return ConfigFile.load_config(EuroPiConfig, ConfigSpec(EuroPiConfig.config_points()))
