import os
import time
from collections import OrderedDict

import machine

import europi
from europi import CHAR_HEIGHT, CHAR_WIDTH, Button, reset_state
from europi_script import EuroPiScript

from ui import Menu

SCRIPT_DIR = "/lib/contrib/"
REG_FILE_CODE = 0x8000


def europi_script_classes():
    """Scripts that are included in the menu"""

    from contrib.coin_toss import CoinToss
    from contrib.consequencer import Consequencer
    from contrib.diagnostic import Diagnostic
    from contrib.harmonic_lfos import HarmonicLFOs
    from contrib.hello_world import HelloWorld
    from contrib.polyrhythmic_sequencer import PolyrhythmSeq
    from contrib.radio_scanner import RadioScanner
    from contrib.scope import Scope
    from calibrate import Calibrate

    return [
        CoinToss,
        Consequencer,
        Diagnostic,
        HarmonicLFOs,
        HelloWorld,
        PolyrhythmSeq,
        RadioScanner,
        Scope,

        Calibrate,
    ]


class BootloaderMenu(Menu, EuroPiScript):
    """A Menu which allows the user to select and execute one of the scripts available to this EuroPi. Includes the
    contents of the contrib directory as well as the calibrate script. In addition, handlers are added that allow the
    user to exit the running script by rebooting the board back to this menu. This is achieved with the 'hold one button
    and tap the other' action.
    """

    def __init__(self):
        self.scripts_config = BootloaderMenu._build_scripts_config(europi_script_classes())
        Menu.__init__(
            self,
            items=list(sorted(self.scripts_config.keys())),
            select_func=self.launch,
            select_knob=europi.k2,
            choice_buttons=[europi.b1, europi.b2],
        )
        EuroPiScript.__init__(self)
        self.run_request = None

    @classmethod
    def _is_europi_script(cls, c):
        return issubclass(c, EuroPiScript)

    @staticmethod
    def _build_scripts_config(classes):
        return OrderedDict([(cls.display_name(), cls) for cls in classes if BootloaderMenu._is_europi_script(cls)])

    def launch(self, selected_item):
        self.run_request = selected_item

    def exit_to_menu(self):
        print("exit requested")
        self._reset_state()
        machine.reset()  # TODO why doesn't machine.soft_reset() work anymore?

    def main(self):
        state = self._load_state()

        if state:
            self.run_request = state

        else:

            # let the user make a selection
            old_selected = -1
            while not self.run_request:
                if old_selected != self.selected:
                    old_selected = self.selected
                    self.draw_menu()
                time.sleep(0.1)
            self._save_state(self.run_request)

        # setup the exit handlers, and execute the selection
        europi.b1._handler_both(europi.b2, self.exit_to_menu)
        europi.b2._handler_both(europi.b1, self.exit_to_menu)

        print(f"b1 type: {type(europi.b1)}")
        time.sleep(0.25)
        selected_class = self.scripts_config[self.run_request]
        print(f"running {selected_class.__qualname__}")
        selected_class().main()


def main():
    print("bootloader main() start")
    menu = BootloaderMenu()
    menu.main()


if __name__ == "__main__":
    print("bootloader script")
    main()
