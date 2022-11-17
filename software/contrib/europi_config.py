from config_points import ConfigPointsBuilder
from europi_script import EuroPiScript


class EuroPiConfig(EuroPiScript):
    @classmethod
    def display_name(cls):
        return "EuroPi"

    @classmethod
    def config_points(cls, config_builder: ConfigPointsBuilder):
        return config_builder.with_choice(
            name="pico_model", choices=["pico", "pico w"], default="pico"
        )
