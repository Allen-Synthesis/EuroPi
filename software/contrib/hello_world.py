from time import sleep
from europi import oled, b1, din
from europi_script import EuroPiScript


class HelloWorld(EuroPiScript):
    def __init__(self):
        super().__init__()
        state = self.load_state_json()

        self.counter = state.get("counter", 0)
        self.enabled = state.get("enabled", True)

        din.handler(self.increment_counter)
        b1.handler(self.toggle_enablement)

    @classmethod
    def display_name(cls):
        return "Hello World"

    def increment_counter(self):
        if self.enabled:
            self.counter += 1
            self.save_state()

    def toggle_enablement(self):
            self.enabled = not self.enabled
            self.save_state()

    def save_state(self):
        """Save the current state variables as JSON."""
        # Don't save if it has been less than 5 seconds since last save.
        if self.last_saved() < 5000:
            return

        state = {
            "counter": self.counter,
            "enabled": self.enabled,
        }
        self.save_state_json(state)

    def main(self):
        while True:
            oled.centre_text(f"Hello world\n{self.counter}")
            sleep(1)

if __name__ == "__main__":
    HelloWorld().main()
