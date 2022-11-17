from config_points import ConfigPointsBuilder
from europi_script import EuroPiScript


class EuroPiConfig(EuroPiScript):
    """This class provides EuroPi's global config points to the Config script. It is not intended to
    be run on its own."""

    @classmethod
    def display_name(cls):
        return "EuroPi"

    @classmethod
    def config_points(cls, config_builder: ConfigPointsBuilder):
        return config_builder.with_choice(
            name="pico_model", choices=["pico", "pico w"], default="pico"
        )
