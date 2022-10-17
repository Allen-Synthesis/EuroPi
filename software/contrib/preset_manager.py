from time import sleep
from europi import *
from europi_script import EuroPiScript


class PresetManager(EuroPiScript):
    def __init__(self):
        super().__init__()
        state = self.load_state_json()

        self.presets = state.get(
            "presets",
            [
                self.create_blank_preset("preset one"),
                self.create_blank_preset("preset two"),
                self.create_blank_preset("preset three"),
            ],
        )  # [[preset name, [preset values]], [preset name 2, [preset values 2]]
        self.loaded_preset = state.get("loaded preset", 0)
        self.selected_preset = k1.read_position(7) - 1
        self.selected_letter = 0
        self.screen = 1

        self.old_k2 = 0

        self.resolution = 1000

        self.box_width = int(OLED_WIDTH / 3)
        self.box_height = int(OLED_HEIGHT / 2.8)

        self.list_line_height = CHAR_HEIGHT + 4

        self.output_multiplier = MAX_OUTPUT_VOLTAGE / self.resolution

        b1.handler(self.back_button)
        b2.handler(self.enter_button)

        self.confirm_delete = False

        self.characters = "aabcdefghijklmnopqrstuvwxyz0123456789  "
        self.number_of_characters = len(self.characters)
        self.max_characters = 16

    def create_blank_preset(self, name):
        return [str(name), [0, 0, 0, 0, 0, 0]]

    def save_state(self):
        """Save the current state variables as JSON."""
        # Don't save if it has been less than 5 seconds since last save.
        if self.last_saved() < 5000:
            return
        state = {"presets": self.presets, "loaded preset": self.loaded_preset}
        self.save_state_json(state)

    def back_button(self):
        self.save_state()

        self.screen -= 1

        if self.screen == -3:  # Confirm delete
            self.confirm_delete = True

    def enter_button(self):
        if self.screen < 1:
            self.screen += 1
        else:
            None  # Furthest forward screen already reached

        if self.screen == 1:
            self.load_new_preset()

        self.save_state()

    def update_current_value(self, values):
        old_selected_preset = self.selected_preset
        self.selected_preset = k1.read_position(7) - 1
        if self.selected_preset != -1:
            if (
                self.selected_preset != old_selected_preset
            ):  # When selected preset is changed, take a snapshot of k2
                self.old_k2 = k2.read_position(self.resolution)
            else:
                if (
                    abs(k2.read_position(self.resolution, 512) - self.old_k2) > 4
                ):  # k2 must change to allow value to be updated to prevent updating every value while scrolling
                    values[self.selected_preset] = k2.read_position(self.resolution)
        else:
            None

    def draw_current_preset(self):
        oled.fill(0)

        name = self.presets[self.loaded_preset][0]
        values = self.presets[self.loaded_preset][1]

        oled.text(name, int((OLED_WIDTH - (len(name) * CHAR_WIDTH)) / 2), 0, 1)

        self.update_current_value(values)

        for index, value in enumerate(values):
            x = int((index % 3) * self.box_width)
            y = int((index // 3) * self.box_height) + self.box_height - 1
            oled.rect(
                x, y, self.box_width, self.box_height, 1
            ) if index != self.selected_preset else oled.fill_rect(
                x, y, self.box_width, self.box_height, 1
            )
            oled.text(
                str((self.value_to_voltage(value)))[:4],
                (x + 2),
                (y + 2),
                1 if index != self.selected_preset else 0,
            )
        oled.show()

    def value_to_voltage(self, value):
        return value * self.output_multiplier

    def update_outputs(self):
        values = self.presets[self.loaded_preset][1]
        for cv_value in zip(cvs, values):
            cv_value[0].voltage(self.value_to_voltage(cv_value[1]))

    def draw_preset_list(self):
        oled.fill(0)

        positions = len(self.presets) + 1
        self.hovered_preset = k1.read_position(positions)

        vertical_offset = -(self.hovered_preset * self.list_line_height) + 1
        oled.fill_rect(0, 0, OLED_WIDTH, self.list_line_height, 1)
        for index, preset in enumerate(self.presets):
            name = preset[0]
            oled.text(name, 0, vertical_offset, 1 if self.hovered_preset != index else 0)

            vertical_offset += self.list_line_height
        if self.hovered_preset == (positions - 1):
            colour = 0
            self.create_new_preset = True
        else:
            colour = 1
            self.create_new_preset = False
        oled.text("NEW PRESET", 0, vertical_offset, colour)
        oled.show()

    def load_new_preset(self):
        if self.create_new_preset:
            self.presets.append(self.create_blank_preset("blank preset"))
            self.loaded_preset = -1
        else:
            self.loaded_preset = self.hovered_preset

    def draw_rename_screen(self):
        if not self.create_new_preset:
            oled.fill(0)

            name = self.presets[self.hovered_preset][0]
            name_list = list(name)
            while len(name_list) < self.max_characters:
                name_list.append(" ")

            old_selected_letter = self.selected_letter
            self.selected_letter = k1.read_position(self.max_characters)
            if old_selected_letter != self.selected_letter:
                self.old_k2 = k2.read_position(len(self.characters) + 1)
            else:
                if k2.read_position(len(self.characters) + 1) != self.old_k2:
                    name_list[self.selected_letter] = self.characters[
                        k2.read_position(self.number_of_characters)
                    ]
                    self.presets[self.hovered_preset][0] = "".join(name_list)

            oled.fill_rect((self.selected_letter * CHAR_WIDTH), 0, CHAR_WIDTH, (CHAR_HEIGHT + 2), 1)
            for index, letter in enumerate(name_list):
                oled.text(
                    letter, (index * CHAR_WIDTH), 1, 0 if self.selected_letter == index else 1
                )

            oled.text("< DELETE", 0, 24, 1)
        else:
            self.screen = 0  # If a user tries to go to the rename screen while hovering over 'NEW PRESET' they are kept on the preset list screen

    def hover_delete(self):
        oled.fill(0)
        oled.fill_rect(0, 22, 128, 32, 1)
        oled.text("CANCEL >", 64, 0, 1)
        oled.text("< CONFIRM DELETE?", 0, 24, 0)
        oled.show()

    def update_ui(self):
        if self.confirm_delete:
            if len(self.presets) > 1:
                if self.hovered_preset == self.loaded_preset:
                    self.loaded_preset = 0
                self.presets.remove(self.presets[self.hovered_preset])
            else:
                oled.centre_text('Cannot delete\nlast remaining\npreset!')
                sleep(1)
            self.screen = 0
            self.confirm_delete = False

        if self.screen == -2:  # Delete
            self.draw_rename_screen()
            self.hover_delete()
        elif self.screen == -1:  # Rename
            self.draw_rename_screen()
            oled.show()
        elif self.screen == 0:  # List of presets
            self.draw_preset_list()
        elif self.screen == 1:  # List of presets
            self.draw_current_preset()

    def main(self):
        oled.fill(0)
        while True:
            self.update_ui()
            self.update_outputs()
            sleep(0.001)


if __name__ == "__main__":
    PresetManager().main()
