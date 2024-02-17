import configuration
from configuration import ConfigFile, ConfigSpec

# Pico machine CPU freq.
# Default pico CPU freq is 125_000_000 (125mHz)
PICO_DEFAULT_CPU_FREQ = 125_000_000
OVERCLOCKED_CPU_FREQ = 250_000_000


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
            configuration.choice(
                name="display_sda",
                choices=[0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 26],
                default=0,
            ),
            configuration.choice(
                name="display_scl",
                choices=[1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 27],
                default=1,
            ),
            configuration.integer(
                name="display_channel",
                range=range(0, 2),
                default=0
            ),

            # Synthesizer family settings
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
