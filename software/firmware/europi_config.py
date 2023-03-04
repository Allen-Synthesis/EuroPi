import configuration
from configuration import ConfigFile, ConfigSpec

# Pico machine CPU freq.
# Default pico CPU freq is 125_000_000 (125mHz)
PICO_DEFAULT_CPU_FREQ = 125_000_000
OVERCLOCKED_CPU_FREQ = 250_000_000


class EuroPiConfig:
    """This class provides EuroPi's global config points."""

    @classmethod
    def config_points(cls):
        return [
            configuration.choice(name="pico_model", choices=["pico", "pico w"], default="pico"),
            configuration.choice(
                name="cpu_freq",
                choices=[PICO_DEFAULT_CPU_FREQ, OVERCLOCKED_CPU_FREQ],
                default=OVERCLOCKED_CPU_FREQ,
            ),
        ]


def load_europi_config():
    return ConfigFile.load_config(EuroPiConfig, ConfigSpec(EuroPiConfig.config_points()))
