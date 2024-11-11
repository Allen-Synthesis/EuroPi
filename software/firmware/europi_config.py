import configuration
from configuration import ConfigFile, ConfigSpec

# Pico machine CPU freq.
# Default pico CPU freq is 125_000_000 (125mHz)
PICO_DEFAULT_CPU_FREQ = 125_000_000
OVERCLOCKED_CPU_FREQ = 250_000_000


class EuroPiConfig:
    """This class provides EuroPi's global config points.

    To override the default values, create /config/EuroPiConfig.json on the Raspberry Pi Pico
    and populate it with a JSON object. e.g. if your build has the oled mounted upside-down compared
    to normal, the contents of /config/EuroPiConfig.json should look like this:

    {
        "ROTATE_DISPLAY": true
    }
    """

    @classmethod
    def config_points(cls):
        # fmt: off
        return [
            # EuroPi revision -- this is currently unused, but reserved for future expansion
            configuration.choice(
                name="EUROPI_MODEL",
                choices = ["europi"],
                default="europi"
            ),

            # CPU & board settings
            configuration.choice(
                name="PICO_MODEL",
                choices=["pico", "pico w"],
                default="pico"
            ),
            configuration.choice(
                name="CPU_FREQ",
                choices=[PICO_DEFAULT_CPU_FREQ, OVERCLOCKED_CPU_FREQ],
                default=OVERCLOCKED_CPU_FREQ,
            ),

            # Display settings
            configuration.boolean(
                name="ROTATE_DISPLAY",
                default=False
            ),
            configuration.integer(
                name="DISPLAY_WIDTH",
                minimum=8,
                maximum=1024,
                default=128
            ),
            configuration.integer(
                name="DISPLAY_HEIGHT",
                minimum=8,
                maximum=1024,
                default=32
            ),
            configuration.choice(
                name="DISPLAY_SDA",
                choices=[0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 26],
                default=0,
            ),
            configuration.choice(
                name="DISPLAY_SCL",
                choices=[1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 27],
                default=1,
            ),
            configuration.integer(
                name="DISPLAY_CHANNEL",
                minimum=0,
                maximum=1,
                default=0
            ),

            # I/O voltage settings
            configuration.floatingPoint(
                name="MAX_OUTPUT_VOLTAGE",
                minimum=1.0,
                maximum=10.0,
                default=10.0
            ),
            configuration.floatingPoint(
                name="MAX_INPUT_VOLTAGE",
                minimum=1.0,
                maximum=12.0,
                default=12.0
            ),
            configuration.floatingPoint(
                name="GATE_VOLTAGE",
                minimum=1.0,
                maximum=10.0,
                default=5.0
            ),

            # Menu settings
            configuration.boolean(
                name="MENU_AFTER_POWER_ON",
                default=False
            ),
        ]
        # fmt: on


def load_europi_config():
    return ConfigFile.load_config(EuroPiConfig, ConfigSpec(EuroPiConfig.config_points()))
