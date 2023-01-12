import configuration


class EuroPiConfig:
    """This class provides EuroPi's global config points to the Config script."""

    @classmethod
    def display_name(cls):
        return "EuroPi"

    @classmethod
    def config_points(cls):
        return [configuration.choice(name="pico_model", choices=["pico", "pico w"], default="pico")]
