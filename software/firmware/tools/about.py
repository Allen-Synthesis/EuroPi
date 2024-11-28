from europi import *
from europi_script import EuroPiScript
from time import sleep
from version import __version__


class About(EuroPiScript):
    def __init__(self):
        super().__init__()

    def main(self):
        turn_off_all_cvs()

        oled.centre_text(
            f"""EuroPi v{__version__}
{europi_config.EUROPI_MODEL}/{europi_config.PICO_MODEL}
{europi_config.CPU_FREQ}"""
        )

        while True:
            sleep(1)


if __name__ == "__main__":
    About().main()
